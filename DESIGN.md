# 🎨 Huellitas Alegres — Design System

**Sistema de diseño visual y de experiencia de usuario para la plataforma.**
Basado en Material Design 3, implementado con Tailwind CSS CDN + Alpine.js + Material Symbols.

---

## 📐 Índice

- [Paleta de Colores](#-paleta-de-colores)
- [Tipografía](#-tipografía)
- [Espaciado y Layout](#-espaciado-y-layout)
- [Íconos](#-íconos)
- [Componentes Base](#-componentes-base)
- [Sidebar por Rol](#-sidebar-por-rol)
- [Dashboards por Rol](#-dashboards-por-rol)
- [Landing Page](#-landing-page)
- [Formularios](#-formularios)
- [Tablas](#-tablas)
- [Estados y Badges](#-estados-y-badges)
- [Chatbot Widget](#-chatbot-widget)
- [Notificaciones](#-notificaciones)
- [Responsive Design](#-responsive-design)

---

## 🎨 Paleta de Colores

Inspirada en tonos verdes naturales para transmitir salud, confianza y calidez. Esquema **light-only** adaptado a Material Design 3.

| Token | Hex | Uso |
|-------|-----|-----|
| `primary` | `#37563b` | Botones principales, links activos, acentos |
| `primary-container` | `#4f6f52` | Fondos de acento, cards activas |
| `on-primary` | `#ffffff` | Texto sobre primary |
| `surface` | `#f8f9fa` | Fondo principal de página |
| `surface-container-lowest` | `#ffffff` | Cards y contenedores elevados |
| `surface-container` | `#edeeef` | Fondos de secciones |
| `surface-container-high` | `#e7e8e9` | Hover states, headers de tabla |
| `background` | `#f8f9fa` | Fondo raíz del body |
| `on-surface` | `#191c1d` | Texto principal |
| `on-surface-variant` | `#424841` | Texto secundario, placeholders, captions |
| `outline-variant` | `#c2c8bf` | Bordes de cards, inputs, tablas |
| `tertiary` | `#47541d` | Color de acento terciario (gráficos, métricas) |
| `tertiary-container` | `#5e6d33` | Fondos terciarios, botón "Iniciar Entrega" |
| `error` | `#ba1a1a` | Errores, cancelaciones, alertas críticas |
| `error-container` | `#ffdad6` | Fondos de error |
| `secondary` | `#625e56` | Texto de sidebar, iconos inactivos |
| `secondary-container` | `#e6dfd5` | Fondos de sidebar, avatares |

### Reglas de uso

- **Texto**: `on-surface` (principal), `on-surface-variant` (secundario), `text-secondary` (sidebar)
- **Fondos**: Siempre usar tokens de surface (nunca colores directos)
- **Bordes**: `border-outline-variant` con opacidad 10-30%
- **Sombras**: `shadow-[0_4px_20px_rgba(0,0,0,0.03)]` para elevación sutil

---

## 🔤 Tipografía

Fuentes cargadas desde Google Fonts CDN. No requieren instalación local.

| Token | Font | Size | Weight | Line Height | Uso |
|-------|------|------|--------|-------------|-----|
| `display-lg` | Plus Jakarta Sans | 48px | 700 | 1.2 | Hero de landing page |
| `headline-lg` | Plus Jakarta Sans | 32px | 600 | 1.3 | Títulos de sección |
| `headline-md` | Plus Jakarta Sans | 24px | 600 | 1.4 | Títulos de card, sidebar brand |
| `body-lg` | Manrope | 18px | 400 | 1.6 | Párrafos largos |
| `body-md` | Manrope | 16px | 400 | 1.6 | Cuerpo general, tablas |
| `label-md` | Manrope | 14px | 600 | 1.2 | Botones, labels, sidebar, métricas |
| `caption` | Manrope | 12px | 500 | 1.2 | Timestamps, badges, notas al pie |

Clases CSS: `font-{token} text-{token}` (ej: `font-headline-md text-headline-md`).

---

## 📏 Espaciado y Layout

Sistema de spacing basado en Tailwind extendido con tokens semánticos:

| Token | Valor | Uso |
|-------|-------|-----|
| `xs` | 4px | Badges, gap mínimo |
| `sm` | 12px | Gap entre botones, padding interno compacto |
| `base` | 8px | Unidad mínima de espaciado |
| `md` | 24px | Padding de cards, gap entre secciones |
| `gutter` | 24px | Gap de grid (cards en bento) |
| `lg` | 48px | Margen entre secciones grandes |
| `margin-mobile` | 16px | Padding lateral en móvil |
| `margin-desktop` | 40px | Padding lateral en desktop |
| `xl` | 80px | Separación de secciones principales |

Layout máximo: `max-w-[1440px] mx-auto` centrado con márgenes automáticos.

---

## 🏷️ Íconos

**Material Symbols Outlined** (Google Fonts CDN), con soporte de variante FILL:

```html
<!-- Ícono estándar -->
<span class="material-symbols-outlined">pets</span>

<!-- Ícono relleno (activo/seleccionado) -->
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">dashboard</span>
```

Tamaños por contexto:
- `text-[18px]` — botones, sidebar, badges
- `text-[20px]` — métricas, cards, formularios
- `text-[24px]` — modales, alertas
- `text-[48px]` — estados finales (success, error)

---

## 🧩 Componentes Base

### Cards

```html
<div class="bg-surface-container-lowest rounded-xl border border-outline-variant/10
            shadow-[0_4px_20px_rgba(0,0,0,0.03)] overflow-hidden">
    <!-- Header con fondo de color -->
    <div class="px-6 py-4 bg-primary-container/20">
        <h3 class="font-headline-md text-headline-md">Título</h3>
    </div>
    <!-- Contenido -->
    <div class="p-6">...</div>
</div>
```

**Variantes**:
- **Colored header**: `bg-[#e8edd4]` (pendiente), `bg-primary-container/20` (en camino), `bg-primary/10` (entregado), `bg-error-container/20` (cancelado)
- **Border top accent**: `border-t-4 border-t-primary` — indica estado del pedido
- **Danger card**: `bg-error-container/20 border border-error/20`
- **Success card**: `bg-tertiary-container/20 border border-tertiary/20`

### Botones

```html
<!-- Primario -->
<button class="bg-primary text-on-primary font-label-md text-label-md
               px-8 py-3.5 rounded-lg hover:opacity-90 shadow-sm">
    Acción Principal
</button>

<!-- Secundario -->
<button class="border border-outline-variant/30 text-on-surface-variant
               font-label-md text-label-md px-6 py-2.5 rounded-lg
               hover:bg-surface-container-high">
    Cancelar
</button>

<!-- Danger -->
<button class="bg-error text-on-error font-label-md text-label-md
               px-4 py-2.5 rounded-lg hover:opacity-90">
    Eliminar
</button>
```

### Status Pills / Badges

```html
<!-- Activo/Entregado -->
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full
             bg-[#E6F4EA] text-[#1E8E3E] font-caption text-caption">
    <span class="w-1.5 h-1.5 rounded-full bg-[#1E8E3E]"></span> Entregado
</span>

<!-- Pendiente / En progreso -->
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full
             bg-[#FEF7E0] text-[#B06000] font-caption text-caption">
    <span class="w-1.5 h-1.5 rounded-full bg-[#B06000]"></span> Pendiente
</span>

<!-- Cancelado / Error -->
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full
             bg-error-container/50 text-error font-caption text-caption">
    Cancelado
</span>
```

### Modales (Alpine.js)

```html
<div x-show="open" x-cloak @click.outside="open = false"
     class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
    <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/20
                shadow-xl max-w-md w-full" @click.stop>
        <div class="bg-error px-5 py-4 rounded-t-xl">
            <h3 class="font-headline-md text-headline-md text-on-error">Título</h3>
        </div>
        <form>...</form>
    </div>
</div>
```

### Progress Ring SVG (Métricas)

Anillo animado para tasa de cumplimiento con umbrales de color:
- `>90%`: `stroke="currentColor" text-primary`
- `70-89%`: `text-tertiary`
- `<70%`: `text-orange-500`

---

## 🧭 Sidebar por Rol

Sidebar fijo a la izquierda (`w-[280px]`), condicional por rol. Colapsa en móvil.

### Estructura base

```html
<nav class="bg-surface-container-low border-r border-outline-variant/20
            h-screen w-[280px] fixed left-0 top-0 flex flex-col p-md gap-base z-40">
    <!-- Brand -->
    <div class="mb-lg px-sm">
        <h1 class="font-headline-md text-headline-md text-primary">Huellitas Alegres</h1>
        <p class="font-caption text-caption text-secondary">Portal {{ rol }}</p>
    </div>
    <!-- Nav links -->
    <ul class="flex flex-col gap-xs flex-1">...</ul>
    <!-- Footer -->
    <ul class="mt-auto pt-md border-t border-outline-variant/20">...</ul>
</nav>
```

### Links por rol

| Rol | Enlaces del sidebar |
|-----|---------------------|
| **Administrador** | Dashboard, Citas, Pacientes, Productos, Servicios, Proveedores, Usuarios, Reportes, Torre de Control, Configuración |
| **Veterinario** | Dashboard, Citas, Disponibilidades, Pacientes, Historial, Tienda, Reportes |
| **Cliente** | Dashboard, Mis Mascotas, Tienda, Servicios, Mis Pedidos, Mi Perfil |
| **Domiciliario** | Dashboard, Mis Pedidos (simplificado), Mi Perfil |

### Estilo de link

- **Activo**: `bg-primary-container text-on-primary-container rounded-lg font-bold`
- **Inactivo**: `text-secondary hover:bg-surface-container-high`
- **Ícono**: `font-variation-settings: 'FILL' 1` solo en el link activo

---

## 📊 Dashboards por Rol

### Administrador
- **Metrics grid** (4 cards): Ingresos del mes, Ocupación, Staff activo, Alertas críticas
- **Top 5 Productos**: tabla con nombre, categoría, unidades vendidas, ingresos
- **Productividad de Staff**: tabla con citas del mes y totales por veterinario
- **Tasa de cumplimiento**: progress ring SVG animado

### Veterinario
- Citas del día (lista con filtro por estado)
- Pacientes recientes
- Disponibilidades de la semana
- Acceso rápido a crear cita y registrar historial

### Cliente
- Mascotas registradas con acceso rápido a historial
- Próximas citas
- Pedidos activos
- Catálogo de servicios y tienda

### Domiciliario
- Pedidos asignados con acciones inline
- Toggle de disponibilidad personal
- Resumen diario de entregas

---

## 🏠 Landing Page

Página pública (`/`, standalone, no extiende `base.html`):

1. **Navbar fija**: Logo, links de navegación, botones "Acceso Staff" y "Registrar Mascota"
2. **Hero section**: Headline + descripción + CTA + imagen de fondo
3. **Bento grid de servicios** (3 cards + CTA card en layout de revista):
   - Bienestar General (1 col)
   - Cirugía Avanzada (2 cols, con elemento decorativo)
   - Cuidado Dental (1 col)
   - Consulta Urgente CTA (2 cols, fondo primary)
4. **Footer**: Logo, links legales, copyright

Redirige al dashboard del rol si el usuario ya está autenticado.

---

## 📝 Formularios

### Input base

```html
<input type="text"
       class="w-full px-4 py-2.5 bg-surface-container-low border border-outline-variant/30
              rounded-lg font-body-md text-body-md text-on-surface
              placeholder-on-surface-variant focus:outline-none focus:border-primary
              focus:ring-1 focus:ring-primary transition-colors">
```

### File input (imagen)

```html
<input type="file" accept="image/*"
       class="w-full px-4 py-2.5 bg-surface-container-low border border-outline-variant/30
              rounded-lg file:mr-4 file:py-1.5 file:px-3 file:rounded-lg file:border-0
              file:bg-primary-container file:text-primary file:font-label-md file:cursor-pointer">
```

### Select

```html
<select class="w-full px-4 py-2.5 bg-surface-container-low border border-outline-variant/30
               rounded-lg font-body-md text-body-md">
```

### Textarea

```html
<textarea rows="4"
          class="w-full px-4 py-2.5 bg-surface-container-low border border-outline-variant/30
                 rounded-lg font-body-md resize-vertical"></textarea>
```

### Reglas de formularios

- **CSRF token**: `{% csrf_token %}` obligatorio en todos los POST
- **Validación**: Mensajes de error en `text-error font-caption` debajo del campo
- **Éxito**: `messages.success` con fondo `bg-tertiary-container/20`
- **Error**: `messages.error` con fondo `bg-error-container/20`

---

## 📋 Tablas

```html
<div class="bg-surface-container-low rounded-xl border border-outline-variant/10 overflow-hidden">
    <table class="w-full text-left font-body-md text-body-md">
        <thead class="bg-surface-container-high text-on-surface-variant font-label-md text-label-md">
            <tr>
                <th class="py-2.5 px-4 font-semibold">Columna</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-outline-variant/10">
            <tr class="hover:bg-surface transition-colors">
                <td class="py-2.5 px-4">Dato</td>
            </tr>
        </tbody>
    </table>
</div>
```

---

## 🚦 Estados y Badges

### Pedidos

| Estado | Color header | Badge |
|--------|-------------|-------|
| Pendiente | `bg-[#e8edd4]` / `border-t-[#5e6d33]` | `bg-[#2b3a1a] text-white` |
| En Camino | `bg-primary-container/20` / `border-t-primary` | `bg-primary-container text-on-primary-container` |
| Entregado | `bg-primary/10` / `border-t-primary` | `bg-primary text-on-primary` |
| Cancelado | `bg-error-container/20` / `border-t-error` | `bg-error text-on-error` |

### Productos (stock)

| Stock | Badge |
|-------|-------|
| > 10 | `🟢 Disponible` (sin badge, texto verde) |
| 1-10 | `🟠 ¡Últimas unidades!` (badge warning) |
| 0 | `🔴 Agotado` (botón deshabilitado) |

### Citas

| Estado | Badge |
|--------|-------|
| Programada | `bg-primary-container/20 text-on-primary-container` |
| Confirmada | `bg-tertiary-container/20 text-on-tertiary-container` |
| Atendida | `bg-[#E6F4EA] text-[#1E8E3E]` |
| Cancelada | `bg-error-container/30 text-error` |

---

## 💬 Chatbot Widget

Widget flotante en esquina inferior derecha, Alpine.js + Tailwind.

### Comportamiento

- Botón FAB (`bg-primary rounded-full`) abre/cierra el panel
- Panel de chat con scroll automático al último mensaje
- Quick replies como chips debajo de cada respuesta
- Input de texto + botón 📷 para imágenes (validación 4MB client-side)
- Preview de imagen antes de enviar
- Indicador de "escribiendo..." durante llamada a NIM

### Colores del chat

- **Usuario**: `bg-primary text-on-primary` (burbuja derecha)
- **Bot**: `bg-surface-container-high text-on-surface` (burbuja izquierda)
- **Quick replies**: `border border-outline-variant/30 hover:bg-primary-container/20`
- **Error**: `bg-error-container/20 text-error`

---

## 🔔 Notificaciones

### Campana en Navbar

```html
<button class="relative">
    <span class="material-symbols-outlined">notifications</span>
    <span class="absolute -top-1 -right-1 bg-error text-on-error
                 rounded-full w-5 h-5 flex items-center justify-center
                 font-caption text-[10px] font-bold"
          x-show="count > 0" x-text="count"></span>
</button>
```

### Dropdown

Lista de las 10 más recientes no leídas con:
- Ícono según tipo (`📅` cita, `📦` pedido, `🚨` stock, `ℹ️` sistema)
- Mensaje truncado a 50 caracteres
- Link directo a la URL de la notificación
- Botón "Marcar todas como leídas"

---

## 📱 Responsive Design

| Breakpoint | Comportamiento |
|------------|---------------|
| Mobile (`<768px`) | Sidebar oculto (hamburguesa), padding `margin-mobile`, cards full-width |
| Tablet (`768px-1024px`) | Sidebar colapsado, grid de 2 columnas |
| Desktop (`>1024px`) | Sidebar fijo 280px, grid de 3-4 columnas, padding `margin-desktop` |

Sidebar usa `hidden md:flex` y se muestra en mobile con overlay al hacer toggle.

---

## 🎯 Principios de Diseño

1. **Coherencia**: Misma paleta, misma tipografía, mismos tokens en TODO el sistema
2. **Jerarquía visual**: Headlines → body → captions → labels, en ese orden de importancia
3. **Feedback inmediato**: Alpine.js para interactividad sin recarga (modales, toggles, badges)
4. **Accesibilidad**: Contraste mínimo 4.5:1 en texto, focus rings visibles, labels en formularios
5. **Progressive enhancement**: Funciona sin JS (degradación graceful a full-page reload)
6. **Mobile-first**: Tailwind breakpoints empiezan en mobile, escalan hacia desktop

---

## 📦 Dependencias de Diseño

| Recurso | Tipo | CDN |
|---------|------|-----|
| Tailwind CSS | Framework | `cdn.tailwindcss.com` con plugins forms + container-queries |
| Alpine.js | Reactividad | `cdn.jsdelivr.net/npm/alpinejs` (v3.x) |
| Material Symbols | Íconos | `fonts.googleapis.com/css2?family=Material+Symbols+Outlined` |
| Plus Jakarta Sans | Tipografía | `fonts.googleapis.com/css2?family=Plus+Jakarta+Sans` |
| Manrope | Tipografía | `fonts.googleapis.com/css2?family=Manrope` |

**Cero dependencias de build**: Todo se carga desde CDN. No requiere npm, webpack, ni postcss.
