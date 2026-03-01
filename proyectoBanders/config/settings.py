import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from django.contrib.messages import constants as messages

# 1. RUTAS BÁSICAS
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. VARIABLES DE ENTORNO
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 3. SEGURIDAD
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-banders-2026-security-key')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

# 4. APLICACIONES (Orden corregido para Allauth v6 y Estáticos)
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',  # Maneja estáticos en desarrollo eficientemente
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    # Allauth v6 + MFA (Configuración que no rompe F2A)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.mfa',

    # UI y Utilidades
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'simple_history',

    # Aplicaciones Locales
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

# 5. MIDDLEWARE (WhiteNoise debe ir justo debajo de SecurityMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'proyectoBanders.abogados.middleware.ProtegerMFAMiddleware',  # Tu protección 2FA
]

ROOT_URLCONF = 'proyectoBanders.config.urls'
WSGI_APPLICATION = 'proyectoBanders.config.wsgi.application'

# 6. TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'proyectoBanders', 'templates')],
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

# 8. BASE DE DATOS
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

# 9. MODELO DE USUARIO
AUTH_USER_MODEL = 'usuarios.UsuarioCustom'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# 10. CONFIGURACIÓN ALLAUTH v6.0+ (Sintaxis moderna sin Warnings)
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# Esto reemplaza ACCOUNT_EMAIL_REQUIRED y ACCOUNT_USERNAME_REQUIRED
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*', 'first_name', 'last_name']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

ACCOUNT_FORMS = {
    'login': 'proyectoBanders.usuarios.forms.UsuarioLoginForm',
    'signup': 'proyectoBanders.usuarios.forms.UsuarioRegistroForm',
}

# 11. CONFIGURACIÓN MFA / TOTP (Indispensable para F2A)
MFA_SUPPORTED_TYPES = ['totp']
MFA_TOTP_ISSUER = 'Consorcio Banders'
MFA_REQUIRED_FOR_LOGIN = False

# 12. CRISPY FORMS
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# 13. ARCHIVOS ESTÁTICOS (CORRECCIÓN CRÍTICA DE DISEÑO)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_production')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'proyectoBanders', 'static'),
]

# Esta lógica evita que el menú se encime por falta de CSS en desarrollo
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 14. CORREO
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Consorcio Jurídico Banders <consorciojuridicobanders@gmail.com>'

# 15. SESIÓN Y MENSAJES
SESSION_COOKIE_AGE = 2592000
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
MESSAGE_TAGS = {messages.ERROR: 'danger'}


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return str(obj)
        return super().default(obj)


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# 16. REDIRECCIONES
LOGIN_REDIRECT_URL = 'dashboard:dashboard'
LOGOUT_REDIRECT_URL = 'account_login'