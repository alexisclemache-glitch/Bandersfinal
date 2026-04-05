import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages

# ==========================================
# 1. RUTAS BÁSICAS Y CARGA DE ENTORNO
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Vital para que Django encuentre los módulos en la estructura de Contabo
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'proyectoBanders'))

load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==========================================
# 2. SEGURIDAD DE PRODUCCIÓN
# ==========================================
SECRET_KEY = os.getenv('SECRET_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# MODO PRODUCCIÓN ACTIVADO
DEBUG = False

# Hosts autorizados (Dominio y IP de tu Contabo)
ALLOWED_HOSTS = [
    'app.abgbanders.com',
    'www.app.abgbanders.com',
    '217.216.92.156',
    'localhost',
    '127.0.0.1'
]

# ==========================================
# 3. APLICACIONES (MFA NATIVO ALLAUTH V6)
# ==========================================
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    # Allauth Core & MFA Nativo
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.mfa',

    # UI & Herramientas
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'simple_history',

    # Apps del Proyecto
    'proyectoBanders.usuarios',
    'proyectoBanders.dashboard',
    'proyectoBanders.abogados',
    'proyectoBanders.clientes',
    'proyectoBanders.expedientes',
    'proyectoBanders.audiencias',
    'proyectoBanders.pages',
    'proyectoBanders.pagos',
    'proyectoBanders.busqueda',
    'proyectoBanders.asistente_ia',
]

SITE_ID = 1

# ==========================================
# 4. MIDDLEWARE (ORDEN CRÍTICO)
# ==========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Manejo de estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'proyectoBanders.usuarios.middleware.ProtegerMFAMiddleware', # Tu bloqueo de QR
]

ROOT_URLCONF = 'proyectoBanders.config.urls'

# ==========================================
# 5. TEMPLATES
# ==========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'proyectoBanders.audiencias.context_processors.notificaciones_audiencias',
            ],
        },
    },
]

WSGI_APPLICATION = 'proyectoBanders.config.wsgi.application'

# ==========================================
# 6. BASE DE DATOS (POSTGRESQL)
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'config',
        'USER': 'postgres',
        'PASSWORD': '1910',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ==========================================
# 7. AUTENTICACIÓN
# ==========================================
AUTH_USER_MODEL = 'usuarios.UsuarioCustom'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ==========================================
# 8. ALLAUTH v6 CONFIG (SIN WARNINGS)
# ==========================================
ACCOUNT_ADAPTER = 'proyectoBanders.usuarios.adapter.AprobacionAdminAdapter'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_FORMS = {
    'signup': 'proyectoBanders.usuarios.forms.UsuarioRegistroForm',
    'login': 'proyectoBanders.usuarios.forms.UsuarioLoginForm',
}

ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_SIGNUP = True

# ==========================================
# 9. MFA (MULTI-FACTOR AUTHENTICATION)
# ==========================================
MFA_SUPPORTED_TYPES = ['totp']
MFA_TOTP_ISSUER = 'Consorcio Banders'
MFA_PASSWORDS_REQUIRED = True
MFA_REAUTHENTICATE_TIMEOUT = 1800

MFA_TOTP_ACTIVATION_REDIRECT_URL = 'dashboard:index'
MFA_LOGIN_REDIRECT_URL = 'dashboard:index'

# ==========================================
# 10. ESTÁTICOS Y MULTIMEDIA
# ==========================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_production')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'proyectoBanders', 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==========================================
# 11. REDIRECCIONES Y MENSAJES
# ==========================================
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'account_login'

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
# ==========================================
# 12. CORREO ELECTRÓNICO (SMTP GMAIL)
# ==========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'

# CAMBIO AQUÍ: Del 587 al 465
EMAIL_PORT = 465

# CAMBIO AQUÍ: TLS en False y SSL en True
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

EMAIL_HOST_USER = 'consorciojuridicobanders@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'consorciojuridicobanders@gmail.com'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Banders Law] '

# ==========================================
# 13. SEGURIDAD DE RED Y SSL (PRO)
# ==========================================
if not DEBUG:
    # Confianza en el proxy de Nginx
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Forzar HTTPS en todo el sitio
    SECURE_SSL_REDIRECT = True

    # Protección de Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Cabeceras de seguridad extra
    SECURE_HSTS_SECONDS = 31536000 # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Orígenes de confianza para CSRF
    CSRF_TRUSTED_ORIGINS = [
        'https://app.abgbanders.com',
        'https://www.app.abgbanders.com',
    ]

# Configuración UI
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
