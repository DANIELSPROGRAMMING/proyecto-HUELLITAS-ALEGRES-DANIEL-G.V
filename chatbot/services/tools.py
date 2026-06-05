"""Function Calling tools for NVIDIA NIM — Huellitas Alegres.

Each tool has:
  - A JSON Schema definition (for the NIM API)
  - A handler function (executes real DB queries)

Design: tools are READ-ONLY. No mutations to the database.
All handlers return strings (success or error message).
"""

import json
from datetime import datetime

# ─────────────────────────────────────────────
# Tool Schema Definitions
# ─────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Consultar los próximos turnos disponibles en la clínica. "
                "Puede filtrarse por fecha."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha": {
                        "type": "string",
                        "description": "Fecha en formato YYYY-MM-DD. Opcional — default: desde hoy.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_services",
            "description": (
                "Listar todos los servicios activos de la clínica con nombre y tarifa. "
                "Usar cuando el usuario pregunta qué servicios ofrecemos."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_products_by_category",
            "description": (
                "Listar los productos de una categoría específica de la tienda. "
                "Usar cuando el usuario pregunta por un tipo de producto."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "description": (
                            "Nombre de la categoría. Valores válidos: Vacunas, Alimentos, "
                            "Medicamentos, Higiene y cuidado, Insumos médicos, Otros."
                        ),
                    },
                },
                "required": ["categoria"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_clinic_info",
            "description": (
                "Obtener información de contacto de la clínica: dirección, "
                "teléfono y horarios de atención."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# ─────────────────────────────────────────────
# Tool Handler Registry
# ─────────────────────────────────────────────

# Maps tool name → handler function.
# Only functions registered here can be executed.
# This is the security boundary: no unregistered code runs.

_HANDLERS = {}


def _register(name):
    """Decorator to register a tool handler."""
    def decorator(func):
        _HANDLERS[name] = func
        return func
    return decorator


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool by name with validated arguments.

    Returns a string result (success message or error).
    NEVER raises — always returns a string.
    """
    handler = _HANDLERS.get(name)
    if handler is None:
        return f"Error: herramienta '{name}' no reconocida."

    try:
        return handler(arguments)
    except Exception as e:
        return f"Error al ejecutar '{name}': {type(e).__name__}"


# ─────────────────────────────────────────────
# Tool Handler Implementations
# ─────────────────────────────────────────────


@_register("check_availability")
def _check_availability(args: dict) -> str:
    """Query Disponibilidad for available slots."""
    from agenda.models import Disponibilidad
    from django.utils import timezone

    fecha_str = args.get("fecha", "").strip()

    queryset = Disponibilidad.objects.filter(
        activa=True,
        fecha__gte=timezone.localdate(),
    ).order_by("fecha", "hora_inicio")

    if fecha_str:
        try:
            target_date = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            queryset = queryset.filter(fecha=target_date)
        except ValueError:
            return f"Error: fecha '{fecha_str}' no es válida. Usa formato YYYY-MM-DD."

    slots = list(queryset[:10])
    if not slots:
        msg = "No hay turnos disponibles"
        if fecha_str:
            msg += f" en la fecha {fecha_str}"
        return msg + "."

    lines = []
    for s in slots:
        vet_name = s.veterinario.get_full_name() or s.veterinario.email
        hora = s.hora_inicio.strftime("%H:%M") if s.hora_inicio else "—"
        lines.append(f"  • {s.fecha.strftime('%d/%m')} — {hora} — Dr/a. {vet_name}")

    return "Turnos disponibles:\n" + "\n".join(lines)


@_register("list_services")
def _list_services(args: dict) -> str:
    """List all active services with names and prices."""
    from servicios.models import Servicio

    servicios = list(Servicio.objects.values("nombre", "tarifa", "duracion_minutos"))
    if not servicios:
        return "No hay servicios disponibles en este momento."

    lines = ["Servicios disponibles:"]
    for s in servicios:
        price = f"${s['tarifa']:,.0f}" if s['tarifa'] else "Consultar"
        lines.append(f"  • {s['nombre']} — {price} ({s['duracion_minutos']} min)")

    return "\n".join(lines)


@_register("list_products_by_category")
def _list_products_by_category(args: dict) -> str:
    """List active products in a given category."""
    from productos.models import Producto
    categoria = args.get("categoria", "").strip()

    if not categoria:
        return "Error: debes especificar una categoría."

    # Map display names (from NIM) to raw DB keys
    CATEGORY_MAP = {
        'vacunas': 'vacunas', 'medicamentos': 'medicamentos',
        'alimentos': 'alimentos', 'insumos médicos': 'insumos',
        'higiene y cuidado': 'higiene', 'higiene': 'higiene',
        'insumos': 'insumos', 'otros': 'otros', 'vacuna': 'vacunas',
    }
    raw_key = CATEGORY_MAP.get(categoria.lower().strip(), categoria)

    products = list(
        Producto.objects.filter(
            esta_activo=True,
            cantidad_stock__gt=0,
            categoria__icontains=raw_key,
        ).values("nombre", "precio", "cantidad_stock")[:10]
    )

    if not products:
        return f"No hay productos en la categoría '{categoria}'."

    lines = [f"Productos en '{categoria}':"]
    for p in products:
        price = f"${p['precio']:,.0f}" if p['precio'] else "Consultar"
        lines.append(f"  • {p['nombre']} — {price} (stock: {p['cantidad_stock']})")

    return "\n".join(lines)


@_register("get_clinic_info")
def _get_clinic_info_handler(args: dict) -> str:
    """Return clinic contact info in a machine-readable format."""
    try:
        from usuarios.models import ConfiguracionClinica
        config = ConfiguracionClinica.get_config()
        return (
            f"Nombre: {config.nombre}\n"
            f"Dirección: {config.direccion}\n"
            f"Teléfono: {config.telefono}\n"
            f"Horario: Lunes a Viernes 7:00 AM — 7:00 PM\n"
            f"Sábados: 8:00 AM — 2:00 PM\n"
            f"Domingo: Cerrado"
        )
    except Exception:
        return (
            "Nombre: Huellitas Alegres\n"
            "Dirección: Consulta nuestra página principal.\n"
            "Teléfono: Contáctanos por nuestro formulario.\n"
            "Horario: Lunes a Viernes 7:00 AM — 7:00 PM"
        )


# ─────────────────────────────────────────────
# Safety: verify all schema names have handlers
# ─────────────────────────────────────────────

_schema_names = {t["function"]["name"] for t in TOOLS}
_unregistered = _schema_names - set(_HANDLERS.keys())
if _unregistered:
    raise RuntimeError(
        f"Tools defined in schema but missing handlers: {_unregistered}"
    )
