import os

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import dj_database_url
# Configuracion de la ruta base del proyecto
#Esto es necesario para que Django pueda encontrar los archivos 
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
# SECURITY: secret key from env, hardcoded fallback for local dev only
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-#6866yvo@54pp!c*3#p9gup1lud_##bx$*%*#eg#zto%+$w1d6')

# SECURITY: debug off in production, on by default for local dev
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Railway injects the public domain automatically
_railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
if _railway_domain:
    ALLOWED_HOSTS.append(_railway_domain)
    ALLOWED_HOSTS.append(f'.{_railway_domain}')

# CSRF: required for HTTPS POST on Railway (Django 4.0+)
CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']
if _railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_railway_domain}')
    CSRF_TRUSTED_ORIGINS.append(f'https://*.{_railway_domain}')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'productos', # aplicacion personalizada para manejar productos de la tienda
    'usuarios', # aplicacion personalizada para manejar autenticacion de usuarios
    'mascotas', # aplicacion para manejar mascotas (pacientes) de la clinica
    'agenda', # aplicacion para gestion de disponibilidades y citas
    'historial',
    'reportes',  # aplicacion para reportes PDF y Excel
    'servicios',  # aplicacion para gestion de servicios veterinarios
    'entregas',  # aplicacion para gestion de pedidos y entregas domiciliarias
    'tienda',  # aplicacion para catalogo y carrito de compras del Cliente
    'proveedores',  # aplicacion para gestion de proveedores
    'chatbot',  # chatbot de reglas para atencion al cliente
    'notificaciones',  # sistema de notificaciones por rol
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'huellitas_alegres.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],  # carpeta global donde está base.html
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notificaciones.context_processors.notificaciones_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'huellitas_alegres.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# PostgreSQL en Railway (DATABASE_URL), SQLite en desarrollo local

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'usuarios.validators.ComplexityPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Email configuration
# In production, configure a real SMTP backend (Gmail, SendGrid, etc.)
# For development and demonstration, emails are printed to the console.
# When a real SMTP server is configured, change to 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Huellitas Alegres <no-reply@huellitasalegres.com>'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración del modelo de usuario personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'

# URL de inicio de sesión (usada por @login_required y autenticación)
LOGIN_URL = '/usuarios/login/'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────────
# NVIDIA NIM — Chatbot AI fallback
# ──────────────────────────────────────────────

NVIDIA_NIM_API_KEY = os.getenv('NVIDIA_NIM_API_KEY', '')
NVIDIA_NIM_BASE_URL = 'https://integrate.api.nvidia.com'
NVIDIA_NIM_MODEL = 'nvidia/nemotron-mini-4b-instruct'
NVIDIA_NIM_VISION_MODEL = 'meta/llama-3.2-11b-vision-instruct'
NVIDIA_NIM_TIMEOUT = 15
NVIDIA_NIM_IMAGE_TIMEOUT = 30
# Max image size accepted from frontend (bytes). Enforced in JS + server.
NIM_MAX_IMAGE_BYTES = 4 * 1024 * 1024  # 4 MB
