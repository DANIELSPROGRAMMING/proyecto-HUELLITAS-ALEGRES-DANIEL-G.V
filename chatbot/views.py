"""Chatbot de Reglas — Huellitas Alegres

Rule-based chatbot that responds with real data from the database.
No external AI or paid APIs. Keyword detection + DB queries.

Implemented for INNOVATECH competition and SENA project presentation.
"""

import json
import re
import unicodedata

import requests

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from productos.models import Producto, CATEGORIAS
from agenda.models import Disponibilidad, Cita
from chatbot.services.nim_client import NimClient
from chatbot.services.nim_formatter import NimResponseFormatter


# ──────────────────────────────────────────────
# NIM context builder — injects real DB data
# into the AI prompt to prevent hallucinations.
# ──────────────────────────────────────────────

def _build_nim_context():
    """Build a concise context block with REAL data from the database.

    This is injected as a second system message so the model knows
    exactly what products, services, and clinic info actually exist.
    """
    info = _get_clinic_info()

    # Product categories with counts
    cat_labels = dict(CATEGORIAS)
    cat_counts = (
        Producto.objects
        .filter(esta_activo=True, cantidad_stock__gt=0)
        .values_list('categoria', flat=True)
    )
    cat_summary = {}
    for cat in cat_counts:
        cat_summary[cat_labels.get(cat, cat)] = cat_summary.get(cat_labels.get(cat, cat), 0) + 1

    # Services
    try:
        from servicios.models import Servicio
        servicios_activos = list(
            Servicio.objects.values_list('nombre', flat=True)
        )
    except Exception:
        servicios_activos = []

    lines = [
        f"Clínica: {info['nombre']}",
        f"Dirección: {info['direccion']}",
        f"Horario: Lun-Vie 7AM-7PM, Sáb 8AM-2PM, Dom cerrado",
        "",
        "Productos por categoría:",
    ]
    for cat, count in sorted(cat_summary.items()):
        lines.append(f"  - {cat}: {count} productos")
    lines.append(f"  Total: {sum(cat_summary.values())} productos activos")

    if servicios_activos:
        lines.append("")
        lines.append(f"Servicios disponibles ({len(servicios_activos)}):")
        for sv in servicios_activos[:15]:
            lines.append(f"  - {sv}")

    lines.append("")
    lines.append("IMPORTANTE: solo menciona productos, servicios y datos que aparezcan en esta lista.")
    return '\n'.join(lines)


# ──────────────────────────────────────────────
# Clinic info — pulled from DB (ConfiguracionClinica model)
# Horarios remain static (not configurable from admin).
# ──────────────────────────────────────────────

STATIC_SCHEDULE = {
    'horario_lun_vie': '7:00 AM — 7:00 PM',
    'horario_sabado': '8:00 AM — 2:00 PM',
    'horario_domingo': 'Cerrado',
}


def _get_clinic_info():
    """Fetch clinic info from ConfiguracionClinica singleton.
    Falls back to defaults if the DB query fails."""
    try:
        from usuarios.models import ConfiguracionClinica
        config = ConfiguracionClinica.get_config()
        return {
            'nombre': config.nombre,
            'direccion': config.direccion,
            'telefono': config.telefono,
        }
    except Exception:
        return {
            'nombre': 'Huellitas Alegres',
            'direccion': 'Consulta nuestra ubicación en la página principal.',
            'telefono': 'Contáctanos por nuestro formulario.',
        }

STATIC_RESPONSES = {
    'bienvenida': (
        '¡Hola! 👋 Soy el asistente de Huellitas Alegres. '
        '¿En qué puedo ayudarte? Puedo informarte sobre precios de productos, '
        'horarios de citas, ubicación de la clínica y más.'
    ),
    'ubicacion': (
        lambda info: (
            f'📍 **{info["nombre"]}**\n'
            f'Dirección: {info["direccion"]}\n'
            f'Teléfono: {info["telefono"]}\n\n'
            f'📅 **Horarios:**\n'
            f'Lunes a Viernes: {STATIC_SCHEDULE["horario_lun_vie"]}\n'
            f'Sábados: {STATIC_SCHEDULE["horario_sabado"]}\n'
            f'Domingos: {STATIC_SCHEDULE["horario_domingo"]}'
        )
    ),
    'horario': (
        lambda info: (
            f'📅 **Horarios de atención:**\n'
            f'Lunes a Viernes: {STATIC_SCHEDULE["horario_lun_vie"]}\n'
            f'Sábados: {STATIC_SCHEDULE["horario_sabado"]}\n'
            f'Domingos: {STATIC_SCHEDULE["horario_domingo"]}'
        )
    ),
    'urgencia': (
        f'🚨 **Línea de urgencias 24/7:** Llama inmediatamente a la clínica.\n\n'
        f'Si tu mascota presenta alguno de estos síntomas, no esperes:\n'
        f'• Dificultad para respirar\n'
        f'• Convulsiones\n'
        f'• Sangrado profuso\n'
        f'• Traumatismo severo\n'
        f'• Envenenamiento sospechado\n\n'
        f'Acude de inmediato a nuestra clínica o llama a la línea de emergencias.'
    ),
    'fallback': (
        'No estoy seguro de entender tu consulta. 😅\n\n'
        'Puedo ayudarte con:\n'
        '• 💊 Precios de productos y medicamentos\n'
        '• 📅 Disponibilidad de citas\n'
        '• 📍 Ubicación y horarios\n'
        '• 🚨 Urgencias\n\n'
        'Intenta con palabras como "precio", "cita", "horario" o "urgencia".'
    ),
    'no_productos': (
        'No encontré productos que coincidan con tu búsqueda. '
        'Intenta con otros términos como "vacuna", "alimento" o "medicamento". 💊'
    ),
    'no_citas': (
        'No hay horarios disponibles en este momento. '
        'Te recomiendo contactar directamente a la clínica o intentar más tarde. 📅'
    ),
}


# ──────────────────────────────────────────────
# Keyword detection
# ──────────────────────────────────────────────

KEYWORD_MAP = {
    # Greetings
    'bienvenida': ['hola', 'buenas', 'buenos dias', 'buenas tardes', 'buenas noches',
                   'hey', 'hi', 'saludos', 'inicio', 'empezar', 'ayuda'],
    # Location & hours
    'ubicacion': ['ubicacion', 'ubicaciones', 'direccion', 'direcciones', 'donde queda', 'donde estan', 'como llego',
                  'ubicar', 'localizar', 'sede', 'clinica esta'],
    'horario': ['horario', 'horarios', 'hora', 'horas', 'abren', 'cierran', 'atienden',
                'que dias', 'lunes', 'sabado', 'domingo', 'turno', 'turnos'],
    # Emergency — includes both singular and plural for quick reply button
    'urgencia': ['urgencia', 'urgencias', 'urgente', 'emergencia', 'emergencias',
                 'emergency', 'desesperado',
                 'no respira', 'convulsion', 'sangrando', 'envenenado', 'morir',
                 'grave', 'desmayo', 'atropellado', 'intoxicado'],
    # Products & prices — includes category names for quick reply buttons
    'producto': ['precio', 'precios', 'vale', 'cuesta', 'costo', 'cuanto',
                 'valor', 'lista', 'catalogo', 'tienda', 'comprar',
                 'producto', 'productos',
                 'vacuna', 'vacunas', 'medicamento', 'medicamentos',
                 'alimento', 'alimentos', 'comida', 'pipeta',
                 'desparasitar', 'antipulgas', 'antibiotico', 'pastilla',
                 'crema', 'shampoo', 'collar', 'juguete', 'arena',
                 'suplemento', 'vitamina', 'suero',
                 'higiene', 'insumos'],
    # Appointments
    'cita': ['cita', 'citas', 'agendar', 'turno', 'turnos', 'disponibilidad',
             'disponible', 'horario disponible', 'reservar', 'programar',
             'consultar', 'consulta', 'veterinario', 'doctor', 'doctora',
             'agendar cita', 'pedir cita', 'solicitar cita'],
}


def _normalize_message(message: str) -> str:
    """Normalize a chat message: strip emojis, remove accents, lowercase.

    quick replies like '📅 Citas' become 'citas' — matching keyword map entries.
    """
    # Remove emojis and special unicode symbols (keep letters, numbers, spaces)
    msg = re.sub(r'[^\w\s]', '', message, flags=re.UNICODE)
    # Remove diacritics/accents: 'Ubicación' → 'Ubicacion'
    msg = unicodedata.normalize('NFD', msg)
    msg = ''.join(c for c in msg if unicodedata.category(c) != 'Mn')
    return msg.lower().strip()


def _detect_intent(message: str) -> str:
    """Detect the user's intent from keywords in the message.

    Returns the intent key or 'fallback' if no keywords match.
    Priority: urgencia > cita > producto > ubicacion/horario > bienvenida > fallback

    Uses word-boundary regex matching to prevent false positives
    (e.g. 'hi' matching inside 'higiene').
    """
    msg = _normalize_message(message)

    # Build word-boundary pattern for each keyword to avoid substring matches
    # e.g. 'hi' should NOT match inside 'higiene'
    def _word_match(keyword: str, text: str) -> bool:
        """Match keyword as a whole word, not a substring."""
        return bool(re.search(rf'\b{re.escape(keyword)}\b', text))

    # Check intents in priority order
    priority_order = ['urgencia', 'cita', 'producto', 'ubicacion', 'horario', 'bienvenida']

    for intent in priority_order:
        keywords = KEYWORD_MAP.get(intent, [])
        for kw in keywords:
            if _word_match(kw, msg):
                return intent

    # Also check for category names directly (word boundary match)
    for val, label in CATEGORIAS:
        if _word_match(val, msg) or _word_match(label.lower(), msg):
            return 'producto'

    return 'fallback'


def _search_products(query: str, limit: int = 5) -> list:
    """Search products by keyword. Returns up to `limit` results.

    Searches in product name, description, and category.
    Producto.objects already filters esta_activo=True via ProductoManager.
    We additionally filter for stock > 0.
    """
    # Search by name first (most relevant)
    products = list(
        Producto.objects
        .filter(cantidad_stock__gt=0, nombre__icontains=query)[:limit]
    )

    # Search description if not enough results
    if len(products) < limit:
        existing_ids = [p.pk for p in products]
        desc_results = Producto.objects.filter(
            cantidad_stock__gt=0,
        ).exclude(pk__in=existing_ids).filter(
            descripcion__icontains=query,
        )[:limit - len(products)]
        products.extend(desc_results)

    # Search category if still not enough
    if len(products) < limit:
        existing_ids = [p.pk for p in products]
        cat_results = Producto.objects.filter(
            cantidad_stock__gt=0,
        ).exclude(pk__in=existing_ids).filter(
            categoria__icontains=query,
        )[:limit - len(products)]
        products.extend(cat_results)

    return products


def _get_available_slots(limit=5) -> list:
    """Get upcoming available slots for appointments.

    Returns up to `limit` Disponibilidad objects that are
    active, future-dated, and not occupied by a Cita.
    """
    from django.utils import timezone as dj_tz

    available = Disponibilidad.objects.filter(
        activa=True,
        fecha__gte=dj_tz.localdate(),
    ).exclude(
        pk__in=Cita.objects.filter(
            estado__in=['Programada', 'Atendida']
        ).values('disponibilidad_id')
    ).select_related('veterinario').order_by('fecha', 'hora_inicio')[:limit]

    return list(available)


def _format_product(products: list) -> str:
    """Format product search results as a readable message."""
    if not products:
        return STATIC_RESPONSES['no_productos']

    lines = ['💊 **Productos encontrados:**\n']
    for p in products:
        cat = p.get_categoria_display()
        lines.append(f'• **{p.nombre}** ({cat}) — ${p.precio:,.0f}')
        if p.cantidad_stock <= 10:
            lines.append(f'  ⚠️ ¡Últimas {p.cantidad_stock} unidades!')
    lines.append('\n¿Necesitas más información sobre alguno? 😊')
    return '\n'.join(lines)


def _format_slots(slots: list) -> str:
    """Format available appointment slots as a readable message."""
    if not slots:
        return STATIC_RESPONSES['no_citas']

    lines = ['📅 **Horarios disponibles:**\n']
    for s in slots:
        vet = s.veterinario.get_full_name() or s.veterinario.email
        lines.append(
            f'• {s.fecha.strftime("%a %d/%m")} '
            f'{s.hora_inicio.strftime("%H:%M")}–{s.hora_fin.strftime("%H:%M")} '
            f'— Dr/a. {vet}'
        )
    lines.append('\n¿Quieres agendar una cita? Inicia sesión para hacerlo. 😊')
    return '\n'.join(lines)


# ──────────────────────────────────────────────
# View
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# Rate limiting — max 30 requests per session per 60 seconds.
# Public endpoint (no auth required). Product info is intentionally
# public: prices and stock levels are visible to any visitor, same as
# a public product catalog. User-specific data (pets, appointments)
# is only shown to authenticated users.
# ──────────────────────────────────────────────

import time

_MAX_CHAT_REQUESTS = 30
_CHAT_WINDOW_SECONDS = 60


@csrf_exempt
@require_POST
def procesar_chat(request):
    """Process a chatbot message and return a JSON response.

    Rate-limited to _MAX_CHAT_REQUESTS per session per _CHAT_WINDOW_SECONDS.
    Public endpoint — no authentication required. Product prices and
    general info are public by design (like a store catalog). Personal
    data is only included for authenticated users.

    Request body (JSON):
        { "message": "¿Cuánto vale la vacuna de la rabia?" }

    Response (JSON):
        { "response": "💊 Productos encontrados:...", "quick_replies": [...] }
    """
    # ── Rate limit (session-based) ──
    chat_history = request.session.get('_chat_timestamps', [])
    now = time.time()
    chat_history = [ts for ts in chat_history if now - ts < _CHAT_WINDOW_SECONDS]
    if len(chat_history) >= _MAX_CHAT_REQUESTS:
        return JsonResponse({
            'response': 'Has enviado muchos mensajes. Espera un momento e intenta de nuevo. ⏳',
            'quick_replies': ['📅 Citas', '💊 Productos', '📍 Ubicación', '🚨 Urgencias'],
        }, status=429)
    chat_history.append(now)
    request.session['_chat_timestamps'] = chat_history

    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({
            'response': STATIC_RESPONSES['fallback'],
            'quick_replies': ['📅 Citas', '💊 Productos', '📍 Ubicación', '🚨 Urgencias'],
        })

    if not message:
        return JsonResponse({
            'response': STATIC_RESPONSES['bienvenida'],
            'quick_replies': ['📅 Citas', '💊 Productos', '📍 Ubicación', '🚨 Urgencias'],
        })

    intent = _detect_intent(message)

    # ── AI conversation state: if the user was talking to the AI,
    #     keep routing to NIM unless they explicitly ask for something
    #     transactional (schedule, location, emergency, appointment).
    _ai_active = request.session.get('_ai_conversation_active', False)
    _transactional_intents = {'urgencia', 'ubicacion', 'horario', 'cita'}

    if _ai_active and intent not in _transactional_intents:
        intent = 'fallback'

    # Authenticated user personalization
    is_authenticated = request.user.is_authenticated
    user_name = ''
    user_mascotas = []
    user_citas_count = 0

    if is_authenticated:
        user_name = request.user.first_name or request.user.username
        user_mascotas = list(
            request.user.mascotas.values_list('nombre', flat=True)[:3]
        )
        user_citas_count = Cita.objects.filter(
            mascota__propietario=request.user,
            estado='Programada',
        ).count()

    # Build response based on intent
    quick_replies = ['📅 Citas', '💊 Productos', '📍 Ubicación', '🚨 Urgencias']
    response = ''
    clinic_info = _get_clinic_info()

    if intent == 'urgencia':
        response = STATIC_RESPONSES['urgencia']
        quick_replies = ['📍 Ubicación', '📅 Citas']

    elif intent == 'ubicacion':
        response = STATIC_RESPONSES['ubicacion'](clinic_info)
        quick_replies = ['📅 Citas', '💊 Productos', '🚨 Urgencias']

    elif intent == 'horario':
        response = STATIC_RESPONSES['horario'](clinic_info)
        quick_replies = ['📅 Citas', '📍 Ubicación']

    elif intent == 'bienvenida':
        if is_authenticated and user_name:
            greeting = f'¡Hola, {user_name}! 👋'
            if user_mascotas:
                mascotas_str = ', '.join(user_mascotas)
                greeting += f' ¿Cómo están {mascotas_str}?'
            if user_citas_count > 0:
                greeting += f' Tienes {user_citas_count} cita{"s" if user_citas_count > 1 else ""} programada{"s" if user_citas_count > 1 else ""}.'
            response = greeting + '\n\n' + STATIC_RESPONSES['bienvenida']
        else:
            response = STATIC_RESPONSES['bienvenida']

    elif intent == 'producto':
        # Three-tier product flow:
        # 1. No search terms → show categories with product counts (no prices)
        # 2. Category name → list product names (no prices)
        # 3. Product name / "precio de X" → show price and stock details
        stop_words = {'precio', 'precios', 'vale', 'cuesta', 'costo', 'cuanto',
                       'valor', 'lista', 'catalogo', 'tienda', 'comprar', 'del', 'de',
                       'la', 'el', 'las', 'los', 'un', 'una', 'por', 'favor',
                       'necesito', 'quiero', 'busco', 'tienen', 'hay', 'producto',
                       'productos', 'medicamento', 'medicamentos'}
        words = _normalize_message(message).split()
        search_terms = [w for w in words if w not in stop_words and len(w) > 2]

        # Map normalized terms to category keys for direct category search
        cat_key_map = {val: val for val, _ in CATEGORIAS}
        cat_label_map = {_normalize_message(label): val for val, label in CATEGORIAS}
        emoji_map = {
            'vacunas': '💉', 'medicamentos': '💊', 'alimentos': '🍖',
            'insumos': '🩺', 'higiene': '🛁', 'servicios': '🏥', 'otros': '🔧',
        }

        # Set defaults — each branch overrides as needed
        quick_replies = ['📅 Citas', '📍 Ubicación', '🚨 Urgencias']

        if search_terms:
            # STEP 2 or 3: user typed something specific
            # Check if the term matches a category → list product names (no prices)
            category_match = None
            for term in search_terms:
                if term in cat_key_map:
                    category_match = cat_key_map[term]
                    break
                if term in cat_label_map:
                    category_match = cat_label_map[term]
                    break

            if category_match:
                # STEP 2: Show product names in that category (no prices)
                cat_products = list(
                    Producto.objects.filter(
                        esta_activo=True, cantidad_stock__gt=0, categoria=category_match
                    ).order_by('nombre')
                )
                cat_name = dict(CATEGORIAS).get(category_match, category_match)
                if cat_products:
                    emoji = emoji_map.get(category_match, '📦')
                    product_lines = '\n'.join(
                        f'  • {p.nombre}'
                        for p in cat_products
                    )
                    # Quick replies with first few product names for price lookup
                    quick_replies = [f'💰 {p.nombre}' for p in cat_products[:4]]
                    response = (
                        f'{emoji} **{cat_name}** ({len(cat_products)} producto{"s" if len(cat_products) > 1 else ""}):\n\n'
                        f'{product_lines}\n\n'
                        f'Toca un producto para ver su precio, o escribe "precio de" seguido del nombre. 😊'
                    )
                else:
                    response = f'No tenemos productos en **{cat_name}** en este momento.'
            else:
                # STEP 3: General keyword search — show price and stock details
                products = []
                for term in search_terms:
                    products = _search_products(term)
                    if products:
                        break
                response = _format_product(products)
        else:
            # STEP 1: No specific search term — show categories with counts (no prices)
            cat_labels = dict(CATEGORIAS)
            categories_with_stock = (
                Producto.objects
                .filter(esta_activo=True, cantidad_stock__gt=0)
                .values_list('categoria', flat=True)
                .distinct()
                .order_by('categoria')
            )
            if categories_with_stock:
                lines = ['💊 **Categorías de nuestra tienda:**\n']
                category_replies = []
                for cat_key in categories_with_stock:
                    cat_name = cat_labels.get(cat_key, cat_key)
                    count = Producto.objects.filter(
                        esta_activo=True, cantidad_stock__gt=0, categoria=cat_key
                    ).count()
                    emoji = emoji_map.get(cat_key, '📦')
                    lines.append(f'{emoji} **{cat_name}** — {count} producto{"s" if count != 1 else ""}')
                    category_replies.append(f'{emoji} {cat_name}')
                lines.append('')
                lines.append('Toca una categoría o escribe su nombre para ver los productos.')
                response = '\n'.join(lines)
                quick_replies = category_replies[:6]  # Max 6 quick replies for UI
            else:
                response = STATIC_RESPONSES['no_productos']

    elif intent == 'cita':
        slots = _get_available_slots(limit=5)
        if is_authenticated:
            header = f'📅 {user_name}, estos son los próximos turnos disponibles:\n\n'
        else:
            header = '📅 Próximos turnos disponibles:\n\n'
        response = header + _format_slots(slots)
        quick_replies = ['💊 Productos', '📍 Ubicación', '🚨 Urgencias']

    # ── Rule engine responded → exit AI conversation mode
    if intent != 'fallback':
        request.session['_ai_conversation_active'] = False

    else:
        # ── Hybrid dispatch: try NIM, fall back to static fallback ──
        try:
            nim_client = NimClient(
                api_key=settings.NVIDIA_NIM_API_KEY,
                base_url=settings.NVIDIA_NIM_BASE_URL,
                model=settings.NVIDIA_NIM_MODEL,
                timeout=settings.NVIDIA_NIM_TIMEOUT,
            )
            system_prompt = (
                "Eres el asistente virtual de la clínica veterinaria Huellitas Alegres. "
                "Responde en español de forma amable, concisa y profesional. "
                "Usa EXCLUSIVAMENTE la información proporcionada en el contexto del sistema. "
                "Si te preguntan algo que no aparece en el contexto, di que no tienes esa "
                "información y sugiere consultar directamente en la clínica. "
                "NUNCA inventes productos, servicios, precios ni especialidades. "
                "Siempre responde en formato JSON con la estructura "
                '{"response": "tu respuesta aquí", "quick_replies": ["sugerencia1", "sugerencia2"]}. '
                "No incluyas texto fuera del JSON."
            )
            context = _build_nim_context()
            raw_text = nim_client.send(message, system_prompt, context=context)
            formatted = NimResponseFormatter.parse(raw_text)
            response = formatted['response']
            quick_replies = formatted['quick_replies']
            # Conversation is now with AI — mark session
            request.session['_ai_conversation_active'] = True
        except requests.exceptions.Timeout as e:
            print(f'[NIM TIMEOUT] {e}')
            response = 'Lo siento, estoy teniendo problemas para conectar con mi cerebro principal. ¿Podrías intentar de nuevo en unos segundos?'
            quick_replies = ['🔄 Intentar de nuevo']
        except requests.exceptions.ConnectionError as e:
            print(f'[NIM CONNECTION] {e}')
            response = 'Lo siento, no puedo contactar con el servicio de IA en este momento. Intenta de nuevo más tarde.'
            quick_replies = ['🔄 Reintentar', '📍 Ubicación', '🕐 Horarios']
        except Exception as e:
            print(f'[NIM ERROR] {type(e).__name__}: {e}')
            response = STATIC_RESPONSES['fallback']
            quick_replies = ['📅 Citas', '💊 Productos', '📍 Ubicación', '🚨 Urgencias']

    return JsonResponse({
        'response': response,
        'quick_replies': quick_replies,
    })