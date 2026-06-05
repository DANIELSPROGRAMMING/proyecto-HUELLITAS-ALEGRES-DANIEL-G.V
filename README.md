# 🐾 Huellitas Alegres

**Sistema Integral de Gestión para Clínicas Veterinarias** · Django + PostgreSQL + NVIDIA NIM

Plataforma web con 4 roles (Administrador, Veterinario, Cliente, Domiciliario), asistente virtual con IA, tienda en línea con domicilio, reportes PDF/Excel, y notificaciones en tiempo real.

---

## 👥 Roles

| Rol | Funciones principales |
|-----|----------------------|
| 👑 **Admin** | CRUD completo, torre de control, métricas de negocio, reportes exportables |
| 🩺 **Veterinario** | Citas, disponibilidades, historial clínico con adjuntos, atención de pacientes |
| 👤 **Cliente** | Tienda en línea, carrito + checkout, catálogo de servicios, mis mascotas y pedidos |
| 🚗 **Domiciliario** | Dashboard de entregas, evidencia fotográfica, toggle de disponibilidad, resumen diario |

---

## 🤖 Asistente Virtual con IA (NVIDIA NIM)

El chatbot combina un **motor de reglas local** (6 intenciones, instantáneo y gratuito) con **inteligencia artificial en la nube** para preguntas complejas. Si la IA no está disponible, el sistema degrada automáticamente a las reglas.

| Funcionalidad | Descripción |
|--------------|-------------|
| 🧠 **RAG** | Cada consulta a IA inyecta datos reales de la base de datos (productos, servicios, horarios) — **cero alucinaciones** |
| 🔧 **Function Calling** | 4 herramientas nativas: consultar turnos, listar servicios, buscar productos por categoría, info de la clínica |
| 📷 **Análisis de imágenes** | El cliente sube una foto de su mascota y `llama-3.2-11b-vision-instruct` describe lo que observa |
| 🛡️ **Seguridad** | Herramientas de solo lectura, rate limiting (30 req/min), API key externa vía variables de entorno |

**Modelos**: `nemotron-mini-4b-instruct` (texto) + `llama-3.2-11b-vision-instruct` (imágenes)

---

## 🚀 Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Django 5.2 · Python 3.12+ |
| Base de datos | PostgreSQL 16 (producción) · SQLite (desarrollo local) |
| Frontend | Tailwind CSS CDN · Alpine.js · Material Symbols |
| IA / Chatbot | NVIDIA NIM API (OpenAI-compatible) |
| Documentos | xhtml2pdf (PDF) · openpyxl (Excel) |
| Despliegue | Railway · Gunicorn · migraciones automáticas |
| Diseño | Material Design 3 (documentado en [`DESIGN.md`](DESIGN.md)) |

---

## 📦 Instalación

```bash
git clone https://github.com/DANIELSPROGRAMMING/proyecto-HUELLITAS-ALEGRES-DANIEL-G.V.git
cd proyecto-HUELLITAS-ALEGRES-DANIEL-G.V
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🚀 Despliegue (Railway)

El proyecto corre en Railway con deploy automático en cada `git push`.

**Variables de entorno requeridas:**
```
DATABASE_URL          # PostgreSQL (Railway la genera)
DJANGO_DEBUG=False    # True solo para debug
DJANGO_SECRET_KEY     # Clave secreta de Django
NVIDIA_NIM_API_KEY    # API key de build.nvidia.com
```

**Archivos de deploy:** `Procfile` ejecuta `migrate` → `collectstatic` → `gunicorn`. `railpack.json` instala dependencias del sistema para compilar PDFs.

---

## 🔒 Seguridad

- API keys en `.env` (gitignored) · Sin secretos en código
- CSRF en todos los formularios · Permisos por rol en cada vista
- 4 auditorías completas: **30+ issues encontrados, 0 restantes**

---

## 👨‍💻 Autor

**Daniel G.V.** — Proyecto formativo SENA (ADSO) · INNOVATECH 2026
