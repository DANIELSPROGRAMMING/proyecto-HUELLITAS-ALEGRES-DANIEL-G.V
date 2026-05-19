# 🐾 Huellitas Alegres

**Sistema Integral de Gestión para Clínicas Veterinarias**

Plataforma web desarrollada con Django que permite administrar de forma completa una clínica veterinaria: gestión de pacientes (mascotas), citas médicas, historial clínico, inventario de productos, tienda en línea con domicilio, catálogo de servicios para clientes, chatbot de reglas con datos reales, y un panel administrativo con métricas de negocio.

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Roles del Sistema](#-roles-del-sistema)
- [Funcionalidades por Rol](#-funcionalidades-por-rol)
- [Chatbot de Reglas](#-chatbot-de-reglas)
- [Sistema de Notificaciones](#-sistema-de-notificaciones)
- [Catálogo de Servicios para Clientes](#-catálogo-de-servicios-para-clientes)
- [Diseño Visual](#-diseño-visual)
- [Características Técnicas Destacadas](#-características-técnicas-destacadas)
- [Tecnologías](#-tecnologías)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Creación del Superusuario](#-creación-del-superusuario)
- [Ejecución](#-ejecución)
- [Pruebas](#-pruebas)
- [Autor](#-autor)
- [Licencia](#-licencia)
- [Futuras Implementaciones / Roadmap de Innovación](#-futuras-implementaciones--roadmap-de-innovación)

---

## 🏥 Descripción General

**Huellitas Alegres** es un sistema de información diseñado para cubrir todas las necesidades operativas de una clínica veterinaria. Desde el registro de mascotas y la programación de citas, hasta la venta de productos con entrega a domicilio, el catálogo de servicios con agendamiento guiado, y la generación de reportes financieros en PDF y Excel.

El sistema implementa un modelo de **roles diferenciados** donde cada tipo de usuario accede únicamente a las funcionalidades correspondientes a su perfil, garantizando seguridad y fluidez en la operación diaria.

La interfaz sigue un **sistema de diseño Material Design 3** con paleta personalizada (documentada en `DESIGN.md`), tipografía Plus Jakarta Sans para encabezados y Manrope para cuerpo, e iconos Material Symbols Outlined con variante FILL para estados activos. La Landing Page pública recibe al visitante y redirige automáticamente al dashboard del rol correspondiente tras autenticación.

---

## 👥 Roles del Sistema

| Rol | Descripción |
|-----|-------------|
| 🩺 **Veterinario** | Gestiona citas, atiende pacientes, registra historial clínico y genera reportes |
| 🚗 **Domiciliario** | Gestiona pedidos asignados, cambia estados de entrega, sube evidencia fotográfica |
| 👤 **Cliente** | Registra mascotas, solicita citas, compra en la tienda, consulta servicios y agenda desde el catálogo |
| 👑 **Administrador** | Control total: usuarios, métricas, configuración, torre de control y disponibilidad |

---

## ⚙️ Funcionalidades por Rol

### 🩺 Veterinario
- Dashboard con citas del día y pacientes recientes
- CRUD de disponibilidades (bloques horarios)
- Gestión de citas (crear, confirmar, cancelar)
- Historial clínico completo con adjuntos (hasta 5 MB)
- Atención de citas con registro directo al historial
- Catálogo de servicios veterinarios con tarifas en pesos colombianos
- Reportes en PDF/Excel de citas, historial, inventario y servicios

### 🚗 Domiciliario
- Dashboard con pedidos asignados y acciones inline (Iniciar Entrega, Confirmar, Cancelar)
- Cambio de estado con transiciones validadas (pendiente → en camino → entregado)
- Evidencia obligatoria: foto y firma para confirmar entrega
- Deducción automática de inventario al entregar pedidos
- Registro de incidentes con motivo obligatorio al cancelar
- Resumen diario de entregas con totales
- Comprobante PDF con datos dinámicos de la clínica (NIT, dirección, teléfono)

### 👤 Cliente
- Landing Page pública con información de la clínica y chatbot integrado
- Registro de cuenta propia con auto-asignación de rol
- Dashboard personalizado con sus mascotas y citas
- CRUD completo de sus mascotas
- Solicitud y cancelación de citas
- **Catálogo de Servicios**: tarjetas con imagen, nombre, duración y tarifa; botón "Agendar Servicio" que pre-selecciona el servicio en el formulario de cita
- **Tienda en línea**: catálogo con imágenes de productos, filtros por categoría, badges de disponibilidad, carrito en sesión, checkout con asignación automática de domiciliario
- Consulta de pedidos realizados con seguimiento
- Historial clínico de sus mascotas (solo lectura)
- Mi Perfil: edición de datos, foto y cambio de contraseña

### 👑 Administrador
- Dashboard con métricas: usuarios, mascotas, citas, ingresos del mes
- **Gestión de Usuarios**: crear, editar, activar/desactivar, asignar contraseña temporal
- **Torre de Control**: vista global de pedidos con reasignación inline de domiciliario, tabla de domiciliarios con estado de disponibilidad y botones Reincorporar/Desactivar
- **Métricas de Negocio**: Top 5 Productos, Productividad de Staff, Tasa de Cumplimiento (anillo de progreso SVG animado)
- **Exportación de Métricas**: PDF y Excel con datos dinámicos de ConfiguraciónClínica
- **Configuración Clínica**: modelo singleton (NIT, dirección, teléfono, email) reflejado en todos los PDF
- **Gestión de Proveedores**: CRUD completo con vinculación al inventario
- **Gestión de Productos**: CRUD con categorías correctas (Vacunas, Medicamentos, Alimentos, Insumos médicos, Higiene y cuidado, Otros), formato pesos colombianos y subida de imágenes con redimensionamiento automático
- **Gestión de Servicios**: CRUD con imagen, categoría, tarifa y duración
- Reportes PDF/Excel de citas, historial, inventario y servicios

---

## 🤖 Chatbot de Reglas

El sistema cuenta con un **Chatbot de Reglas** (Rule-based Chatbot) que opera de forma local, sin dependencias externas ni costos de infraestructura.

### Funcionamiento

El chatbot utiliza **detección de palabras clave** con normalización de texto (eliminación de acentos, emojis y caracteres especiales) para identificar la intención del usuario. Los datos consultados provienen **directamente de la base de datos**, garantizando información siempre actualizada.

### Intenciones soportadas

| Intención | Palabras clave | Respuesta |
|-----------|---------------|-----------|
| 📍 **Ubicación** | "ubicación", "dirección", "dónde queda" | Dirección, teléfono y horarios desde `ConfiguraciónClínica` |
| 📅 **Horario** | "horario", "a qué hora", "atienden" | Horarios de atención (L-V, Sábados, Domingos) |
| 🚨 **Urgencia** | "urgencia", "no respira", "convulsión" | Línea de emergencia 24/7 con síntomas críticos |
| 💊 **Productos** | "precio", "vacuna", "shampoo", nombre de producto | Flujo de 3 niveles (ver abajo) |
| 📅 **Citas** | "cita", "agendar", "turno", "disponibilidad" | Próximos turnos disponibles con nombre del veterinario |
| 👋 **Bienvenida** | "hola", "buenas", "hey" | Saludo personalizado si el usuario está autenticado |

### Flujo de 3 niveles para productos

El chatbot implementa una **divulgación progresiva** para no saturar al usuario con información:

1. **Nivel 1 — Categorías**: Al tocar "💊 Productos" sin término de búsqueda, muestra las categorías disponibles con cantidad de productos, **sin precios**.
2. **Nivel 2 — Nombres**: Al escribir una categoría (ej: "alimentos"), lista los nombres de productos, **sin precios**. Invita a preguntar por precio.
3. **Nivel 3 — Detalle**: Al escribir un nombre específico o "precio de X", muestra **nombre, categoría, precio y stock disponible**.

### Características técnicas

- **Rate limiting**: 30 mensajes por minuto por sesión (protección contra abuso)
- **Normalización**: `_normalize_message()` elimina emojis, acentos y caracteres especiales antes del matching
- **Prioridad de intenciones**: `urgencia > cita > producto > ubicación/horario > bienvenida > fallback`
- **Datos reales**: Ubicación y teléfono desde `ConfiguracionClinica.get_config()`, productos desde `Producto.objects`, citas desde `Disponibilidad` no ocupadas
- **Personalización**: Usuarios autenticados ven su nombre, mascotas y citas programadas en el saludo
- **Widget**: Alpine.js con burbuja flotante, funcionando tanto en `base.html` como en `landing.html`

---

## 🔔 Sistema de Notificaciones

El sistema implementa notificaciones **en tiempo real** mediante un context processor que inyecta el conteo de notificaciones no leídas en todas las plantillas, con campana visible en la navbar.

### 13 disparadores de notificación por rol

| Rol | Evento | Ícono |
|-----|--------|-------|
| Veterinario | Cita agendada por cliente | 📅 |
| Veterinario | Cita cancelada por cliente | 🚫 |
| Cliente | Cita confirmada por veterinario | ✅ |
| Domiciliario | Pedido asignado | 📦 |
| Todos | Cita recordatorio (24h antes) | ⏰ |
| Administrador | Nueva orden registrada | 💰 |
| Administrador | Stock bajo de producto | ⚠️ |
| Administrador | Nuevo usuario registrado | 👤 |
| Administrador | Pedido cancelado con incidente | 🛑 |
| Cliente | Pedido en camino | 🚚 |
| Cliente | Pedido entregado | ✅ |
| Cliente | Cita próxima (24h) | 📅 |
| Cliente | Resultado de historial disponible | 📋 |

### Características

- **Modelo `Notificacion`**: campos `mensaje`, `tipo`, `url`, `leido`, `fecha_creacion`, índice compuesto `(usuario, leido, -fecha_creacion)` para consulta rápida
- **Validación de URL**: `clean()` verifica que `url` comience con `/` (previene XSS)
- **Helpers**: `notify(usuario, mensaje)` y `notify_role(nombre_rol, mensaje)` para disparar notificaciones en masa
- **Vistas**: marcar como leída individual, marcar todas como leídas, listar notificaciones
- **Campana**: badge con conteo de no leídas en navbar, desplegable con lista y enlaces directos

---

## 🏥 Catálogo de Servicios para Clientes

Los **servicios** (Peluquería, Consulta, Vacunación, etc.) son un modelo independiente de los productos de la tienda. Esto evita el error de arquitectura de mostrar servicios como categoría de productos.

### Flujo de agendamiento guiado

```
Sidebar Cliente → Servicios → Tarjetas con imagen, nombre, duración y tarifa
                              ↓
                        [Agendar Servicio]
                              ↓
                solicitar_cita?servicio_id=X
                              ↓
                Motivo pre-llenado: "Peluquería"
                Elige mascota, fecha, veterinario → Confirmar
```

### Características

- **6 categorías de servicio**: Consulta, Cirugía, Estética y peluquería, Vacunación, Laboratorio, Imágenes diagnósticas, Hospitalización, Otro
- **Tarjetas con fallback de iconos**: Si no hay imagen, se muestra un ícono Material Symbol según la categoría
- **Imagen de servicio**: Campo `imagen` en el modelo con upload a `servicios/`, el Admin puede cargar fotos desde el formulario de edición
- **Filtro y búsqueda**: Barra de búsqueda y selector de categoría en el catálogo del cliente
- **Sidebar**: Enlace "Servicios" entre "Tienda" y "Mis Mascotas" en el sidebar del Cliente

---

## 🎨 Diseño Visual

El sistema cuenta con un **sistema de diseño cohesivo** basado en Material Design 3, implementado con Tailwind CSS CDN y documentado en `DESIGN.md`:

- **Paleta**: Primary=#37563b, Primary Container=#4f6f52, Surface=#f8f9fa, Error=#ba1a1a, con variantes para containers, outlines y estados
- **Tipografía**: Plus Jakarta Sans (encabezados) + Manrope (cuerpo y etiquetas)
- **Iconografía**: Material Symbols Outlined con variante FILL para estados activos
- **Componentes**: Cards con colored-header, status pills, danger/confirmation cards, progress rings SVG, formularios con `.tw-form`
- **Sidebar**: Navegación condicional por rol, con indicador activo y colapso en móvil
- **Navbar**: Slim con avatar del usuario, campana de notificaciones, dropdown Alpine.js y enlace de inicio de sesión

La **Landing Page** (`/`) es standalone (no extiende `base.html`) y presenta la clínica al visitante con secciones de servicios, testimonios y CTA. Al autenticarse, redirige automáticamente al dashboard del rol correspondiente.

---

## 🚀 Características Técnicas Destacadas

### 🔄 Asignación Round-Robin de Domiciliarios
El sistema asigna automáticamente pedidos al domiciliario **disponible con menor carga** (pedidos activos: pendiente + en camino). Si un domiciliario cancela por incidente, se marca como no disponible y el Admin puede reincorporarlo desde la Torre de Control.

### 📊 Anillo de Progreso SVG Animado
Las métricas de negocio muestran la tasa de cumplimiento como un **anillo de progreso SVG animado** con umbrales de color: >90% verde, 70-89% esmeralda, <70% naranja.

### 🛒 Tienda con Categorías y Estados de Disponibilidad
Los productos se organizan en **6 categorías correctas** (Vacunas, Medicamentos, Alimentos, Insumos médicos, Higiene y cuidado, Otros — los Servicios son un módulo separado). El catálogo muestra badges inteligentes según el stock:
- 🟢 **Disponible** (stock > 10)
- 🟠 **¡Últimas unidades!** (stock 1-10)
- 🔴 **Agotado** (stock = 0, botón deshabilitado)

### 🖼️ Imágenes con Optimización Automática
Productos y servicios pueden tener fotos de referencia subidas por el Admin. El sistema **redimensiona automáticamente** a 800×800px con compresión JPEG calidad 85%, reduciendo fotos de celular de 5MB a ~150KB. Los elementos sin imagen muestran placeholders elegantes.

### 💵 Formato Pesos Colombianos
Las tarifas y precios se muestran con **puntos de miles** ($85.000 en vez de $85000) mediante filtros de template personalizados. Los formularios aceptan entrada con o sin puntos (85.000 o 85000).

### 🔐 Control de Acceso por Roles
Cada vista está protegida por decoradores de rol (`@role_required`, `@admin_required`, `@veterinario_required`) que verifican autenticación y permisos. Las vistas que manejan datos sensibles (métricas de negocio, exportación PDF/Excel) están restringidas exclusivamente a Administradores.

### 📝 Evidencia Obligatoria de Entrega
Para confirmar una entrega, el domiciliario **debe** subir foto de evidencia y firma del cliente. Ambos campos son obligatorios en modelo, formulario y vista. Un pedido no puede pasar a "entregado" sin ellos.

### 🔒 Soft Delete y Integridad Referencial
Los productos y servicios usan **soft delete** (`esta_activo=False`) en lugar de eliminación física. Producto usa `base_manager_name = 'all_objects'` para que los `PedidoItem` y `CarritoItem` puedan acceder a productos desactivados vía FK sin romper las consultas del carrito.

---

## 🛠️ Tecnologías

| Componente | Tecnología |
|------------|-----------|
| **Backend** | Django 5.2 (Python 3.12+) |
| **Base de Datos** | SQLite (desarrollo) / PostgreSQL (producción) |
| **Frontend** | Tailwind CSS CDN + Alpine.js + Material Symbols Outlined |
| **Plantillas** | Django Templates con herencia y bloques |
| **PDF** | xhtml2pdf |
| **Excel** | openpyxl |
| **Imágenes** | Pillow (redimensionamiento automático) |
| **Autenticación** | Django AUTH_USER_MODEL personalizado (email como USERNAME_FIELD) |
| **Autorización** | Modelo Rol personalizado + decoradores por rol |
| **Sesiones** | Django Sessions (carrito de compras + rate limiting del chatbot) |
| **Chatbot** | Rule-based con normalización de texto y consultas DB en tiempo real |
| **Notificaciones** | Modelado con helpers `notify()`/`notify_role()` e inyección vía context processor |
| **Zona Horaria** | America/Bogota (timezone.localdate()) |

---

## 📁 Estructura del Proyecto

```
huellitas_alegres/
├── agenda/                  # Disponibilidades y Citas
│   ├── models.py            # Disponibilidad, Cita (estados: Programada, Atendida, Cancelada)
│   ├── forms.py             # DisponibilidadForm, CitaForm, SolicitarCitaForm, ReprogramarCitaForm
│   └── views.py             # Dashboard vet, CRUD citas, solicitar_cita (acepta ?servicio_id=)
├── chatbot/                 # Chatbot de Reglas
│   ├── views.py             # procesar_chat(), _detect_intent(), _normalize_message(), _search_products()
│   └── tests.py             # 21 tests: detección de intenciones, flujo 3 niveles, rate limiting
├── entregas/                # Pedidos y Domicilio
│   ├── models.py            # Pedido (estados), PedidoItem, asignación round-robin
│   └── views.py             # Dashboard, detalle, torre de control, comprobante PDF
├── historial/                # Historial Clínico y Adjuntos
├── huellitas_alegres/       # Configuración del proyecto Django
│   ├── settings.py          # TIME_ZONE = 'America/Bogota', AUTH_USER_MODEL
│   └── urls.py              # URLs principales con namespaces por app
├── mascotas/                # Mascotas (pacientes)
├── notificaciones/          # Sistema de Notificaciones
│   ├── models.py            # Notificacion (con validación URL, índice compuesto)
│   ├── helpers.py           # notify(), notify_role()
│   └── context_processors.py # Inyección de conteo no leídas en templates
├── productos/               # Inventario y Kardex
│   ├── models.py            # Producto (6 categorías + soft delete + auto-resize), MovimientoInventario
│   └── forms.py             # ProductoForm (imagen, tarifa con puntos)
├── proveedores/             # Proveedores (CRUD)
├── reportes/                # Reportes PDF/Excel y Métricas Admin
├── servicios/                # Catálogo de Servicios Veterinarios
│   ├── models.py            # Servicio (con imagen, categoría, tarifa, duración)
│   ├── forms.py             # ServicioForm (tarifa CharField, campo imagen)
│   └── views.py             # CRUD admin + catalogo_servicios (vista tarjeta para Cliente)
├── tienda/                  # Catálogo, Carrito y Checkout
│   └── views.py             # Checkout con asignación round-robin de domiciliario
├── usuarios/                # Usuarios, Roles, Perfil, Configuración Clínica
│   ├── models.py            # Usuario (con is_disponible), Rol, Perfil, ConfiguracionClinica
│   ├── decorators.py        # role_required, admin_required, veterinario_required
│   └── views.py             # Auth, dashboards, gestión de usuarios
├── templates/                # Plantillas con diseño Material Design 3
│   ├── base.html            # Layout unificado: navbar + campana notif + sidebar + contenido
│   ├── landing.html          # Landing Page pública (standalone, con chatbot)
│   ├── inicio.html          # Dashboard fallback con cards por rol
│   ├── includes/            # Sidebars por rol, back_button, chatbot_widget
│   ├── agenda/              # Solicitar cita (con banner servicio pre-seleccionado)
│   ├── chatbot/             # chatbot_widget.html (Alpine.js)
│   ├── servicios/           # catalogo_servicios.html (tarjetas + agendar)
│   ├── tienda/              # Catálogo, carrito, checkout
│   └── ...
└── DESIGN.md                 # Sistema de diseño (paleta, tipografía, componentes)
```

---

## 🚀 Instalación

1. **Clonar el repositorio:**

```bash
git clone https://github.com/DANIELSPROGRAMMING/proyecto-HUELLITAS-ALEGRES-DANIEL-G.V.git
cd proyecto-HUELLITAS-ALEGRES-DANIEL-G.V
```

2. **Crear y activar entorno virtual:**

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

4. **Aplicar migraciones:**

```bash
python manage.py migrate
```

5. **Cargar datos iniciales (roles):**

```bash
python manage.py shell < seed_roles.py
```

---

## 👑 Creación del Superusuario

Como el modelo `Usuario` tiene un campo `rol` obligatorio (ForeignKey), no se puede usar `createsuperuser` directamente. Usá el shell de Django:

```bash
python manage.py shell
```

Dentro del shell:

```python
from usuarios.models import Usuario, Rol

rol_admin = Rol.objects.get(nombre='Administrador')

usuario = Usuario.objects.create_superuser(
    username='admin',
    email='admin@huellitasalegres.com',
    password='TU_CONTRASEÑA_SEGURA',
    rol=rol_admin,
)

print(f"✅ Superusuario creado: {usuario.email}")
```

Escribí `exit()` para salir del shell.

---

## ▶️ Ejecución

```bash
python manage.py runserver
```

El servidor se inicia en `http://127.0.0.1:8000/`

- `/` — Landing Page (pública, redirige al dashboard si ya estás autenticado)
- `/usuarios/auth/` — Login / Registro
- `/inicio/` — Dashboard genérico (fallback)
- `/servicios/catalogo/` — Catálogo de Servicios para Clientes
- `/chatbot/procesar/` — Endpoint del Chatbot (POST)

---

## 🧪 Pruebas

Ejecutar todas las pruebas:

```bash
python manage.py test
```

Ejecutar pruebas de una app específica:

```bash
python manage.py test chatbot
python manage.py test servicios.tests.ServicioModelTest
python manage.py test tienda
python manage.py test notificaciones
```

El proyecto cuenta con **más de 50 pruebas** cubriendo:
- Chatbot: detección de intenciones, flujo de 3 niveles de productos, rate limiting, respuestas por intención
- Tienda: catálogo, carrito, checkout, asignación de domiciliario
- Notificaciones: creación, marcado como leída, conteo por rol
- Servicios: modelo, formulario, categorías
- Agenda: formulario de cita, disponibilidades, validaciones
- Y más

---

## 👨‍💻 Autor

**Daniel G.V.** — Proyecto formativo SENA (ADSO)

---

## 📄 Licencia

Este proyecto es de uso educativo como parte del programa de formación del SENA.

---

## 🚀 Futuras Implementaciones / Roadmap de Innovación

### 🤖 Evolución del Chatbot: de Reglas a Inteligencia Artificial

En la fase actual de evaluación, el sistema cuenta con un **Chatbot basado en Reglas** (Rule-based Chatbot) que opera localmente de manera eficiente, sin costos de infraestructura y con consulta directa a la base de datos. Este enfoque garantiza respuestas rápidas, predecibles y 100% trazables, ideales para el entorno de producción actual.

Como **visión de escalabilidad tecnológica**, se tiene planificada la migración hacia un **Asistente Virtual con Inteligencia Artificial Avanzada**. La arquitectura objetivo integra:

- **NVIDIA NIM** (NVIDIA Inference Microservices): infraestructura de inferencia optimizada para despliegue de modelos de lenguaje en producción.
- **Modelos de última generación**: integración con modelos de razonamiento avanzado (como `deepseek-v4-pro` o equivalentes) a través de los endpoints de desarrollo de NVIDIA NIM, consumidos mediante la librería de OpenAI como interfaz de comunicación.
- **Procesamiento de lenguaje natural complejo**: el asistente podrá interpretar consultas ambiguas, mantener contexto conversacional y resolver dudas que el sistema basado en reglas no cubre, como preguntas abiertas, comparaciones de productos o recomendaciones personalizadas basadas en el historial del cliente.
- **Conexión por APIs seguras**: el asistente se integrará al ecosistema del software mediante endpoints protegidos (autenticación, rate limiting, validación de entrada), manteniendo la trazabilidad y seguridad del sistema actual.

Esta evolución elevará la experiencia de usuario (UX) a un nivel de **producción comercial**, posicionando a Huellitas Alegres como una clínica veterinaria con atención digital inteligente de última generación.

### 📧 Notificaciones por Email (Parcialmente Implementadas)

El sistema ya cuenta con la lógica para envío de correos electrónicos mediante `django.core.mail` con `console.EmailBackend`. Las siguientes funcionalidades están preparadas a nivel de código y solo requieren credenciales SMTP para activar el envío real:

| Funcionalidad | Estado | Qué falta |
|--------------|--------|-----------|
| Confirmación de registro | Lógica de creación de usuario ✅, envío de email ❌ | Credenciales SMTP |
| Recordatorio de cita (24h antes) | Trigger programado ✅, email no enviado | Credenciales SMTP |
| Notificación al domiciliario | Asignación de pedido ✅, push/email ❌ | SMTP o WebSocket |
| Recuperación de contraseña | Vista de cambio ✅, enlace por email ❌ | Credenciales SMTP |

### 💳 Pasarela de Pago

La integración con una pasarela de pago (Wompi, PayU, Stripe u otra) se contempla como implementación futura. Esto requiere:

- Cuenta de comerciante aprobada por el proveedor
- API key y credenciales de integración
- Implementación del flujo de checkout con redirección a la pasarela
- Webhook para confirmación de transacción
- Validación de firma y encriptación de datos sensibles (manejado por la pasarela)
- Flujo de devolución y reembolso (dependiente de la pasarela seleccionada)

Actualmente el sistema opera con el modelo declarado **"Pago Contra Entrega"**, reflejado de forma honesta en la interfaz de checkout y las notificaciones.