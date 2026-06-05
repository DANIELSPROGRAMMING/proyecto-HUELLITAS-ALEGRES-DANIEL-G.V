# 🐾 Huellitas Alegres

**Sistema Integral de Gestión para Clínicas Veterinarias**

Plataforma web desarrollada con Django que cubre todas las operaciones de una clínica veterinaria: gestión de pacientes, citas médicas, historial clínico, inventario, tienda en línea con entrega a domicilio, catálogo de servicios, reportes exportables, y un asistente virtual con inteligencia artificial.

---

## 👥 Roles del Sistema

| Rol | Funciones principales |
|-----|----------------------|
| 👑 **Administrador** | Control total: CRUD de usuarios/productos/servicios/proveedores, torre de control de domiciliarios, métricas de negocio con exportación PDF y Excel, configuración de la clínica |
| 🩺 **Veterinario** | Dashboard de citas, gestión de disponibilidades horarias, atención de pacientes con registro automático al historial clínico, adjuntos (hasta 5 MB), reportes |
| 👤 **Cliente** | Landing page pública, tienda en línea con carrito y checkout, catálogo de servicios con agendamiento guiado, registro de mascotas, solicitud de citas, seguimiento de pedidos, perfil |
| 🚗 **Domiciliario** | Dashboard con pedidos asignados, cambio de estado con evidencia obligatoria (foto + firma), deducción automática de inventario, toggle de disponibilidad, resumen diario |

---

## 🤖 Asistente Virtual con IA

El chatbot integra **NVIDIA NIM** en una arquitectura híbrida: motor de reglas local para consultas frecuentes (gratuito, instantáneo) e inteligencia artificial para preguntas abiertas. Si la IA no responde, el sistema degrada automáticamente.

| Componente | Descripción |
|-----------|-------------|
| 🧠 **RAG** | Cada consulta a la IA inyecta datos reales de la base de datos (productos, servicios, horarios). **Cero alucinaciones.** |
| 🔧 **Function Calling** | 4 herramientas: `check_availability`, `list_services`, `list_products_by_category`, `get_clinic_info`. Solo lectura, loop limitado a 3 rondas. |
| 📷 **Análisis visual** | El cliente sube una foto de su mascota y `llama-3.2-11b-vision-instruct` analiza pelaje, piel, parásitos visibles. Incluye disclaimer veterinario. |
| 🛡️ **Rate limiting** | 30 mensajes por minuto por sesión. Sin API key, el bot funciona solo con reglas. |

**Modelos**: `nemotron-mini-4b-instruct` (texto) + `llama-3.2-11b-vision-instruct` (imágenes)

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Django 5.2 · Python 3.12+ |
| Base de datos | PostgreSQL 16 (producción Railway) · SQLite (desarrollo local) |
| Frontend | Tailwind CSS CDN · Alpine.js · Material Symbols Outlined |
| IA / Chatbot | NVIDIA NIM API (OpenAI-compatible) |
| Documentos | xhtml2pdf (PDF) · openpyxl (Excel) |
| Despliegue | Railway · Gunicorn · migraciones automáticas |
| Diseño | Material Design 3 documentado en [`DESIGN.md`](DESIGN.md) |

---

## 📁 Estructura del Proyecto

```
huellitas_alegres/          # Configuración Django (settings, urls, wsgi)
├── agenda/                 # Disponibilidades y Citas (4 estados, notificaciones)
├── chatbot/                # Asistente virtual (reglas + NIM + RAG + tools + imágenes)
│   └── services/           # nim_client, nim_formatter, tools (4 handlers)
├── entregas/               # Pedidos y domicilio (round-robin, evidencia, stepper)
├── historial/              # Historial clínico con adjuntos (upload/descarga)
├── mascotas/               # Pacientes (CRUD, búsqueda por cédula)
├── notificaciones/         # Campana + badge + 19 disparadores (notify/notify_role)
├── productos/              # Inventario con kardex, soft delete, 6 categorías
├── proveedores/            # CRUD de proveedores vinculados a productos
├── reportes/               # PDFs y Excel de citas, historial, inventario, métricas
├── servicios/              # Catálogo con agendamiento guiado (?servicio_id=X)
├── tienda/                 # Catálogo, carrito (sesión), checkout con asignación automática
├── usuarios/               # Auth, perfiles, roles, decorators, configuración clínica
├── templates/              # 68 plantillas con sidebars condicionales por rol
├── static/                 # CSS, JS, imágenes del proyecto
├── DESIGN.md               # Sistema de diseño (paleta, tipografía, componentes)
├── railpack.json           # Dependencias de sistema para Railway
└── Procfile                # migrate → collectstatic → gunicorn
```

---

## 🚀 Instalación y Ejecución

```bash
git clone https://github.com/DANIELSPROGRAMMING/proyecto-HUELLITAS-ALEGRES-DANIEL-G.V.git
cd proyecto-HUELLITAS-ALEGRES-DANIEL-G.V
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🚀 Despliegue en Railway

El proyecto corre en Railway con PostgreSQL 16 y deploy automático en cada push.

**Variables de entorno requeridas:**
```
DATABASE_URL          # PostgreSQL (Railway la genera)
DJANGO_SECRET_KEY     # Clave secreta de Django
NVIDIA_NIM_API_KEY    # API key de build.nvidia.com
```

`Procfile` ejecuta `migrate` → `collectstatic` → `gunicorn`. Las migraciones son automáticas.

---

## 🔒 Seguridad

- API keys en `.env` (gitignored) · Sin secretos en código fuente
- CSRF en todos los formularios · Permisos por rol en cada vista
- 4 auditorías completas: **30+ issues corregidos, 0 restantes**

---

## 🧪 Pruebas

```bash
python manage.py test
```

Más de 90 tests cubriendo chatbot (reglas, NIM, RAG, tools, imágenes), tienda (catálogo, carrito, checkout), notificaciones, entregas, reportes y permisos.

---

## 🚀 Futuras Implementaciones

- 📧 Notificaciones por email (SMTP) — lógica lista, falta configurar credenciales
- 💳 Pasarela de pago — actualmente opera con modelo "Pago Contra Entrega"
- 📱 PWA / aplicación móvil
- 🐳 Docker para despliegue independiente de plataforma

---

## 👨‍💻 Autor

**Daniel G.V.** — Proyecto formativo SENA (ADSO) · INNOVATECH 2026
