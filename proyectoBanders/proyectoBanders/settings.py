import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from django.contrib.messages import constants as messages

# 1. RUTAS BÁSICAS (Ajustado para manage.py en C:\django-banders)
# settings.py está en proyectoBanders/proyectoBanders/settings.py
# Subimos 3 niveles para llegar a la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. VARIABLES DE ENTORNO
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 3. SEGURIDAD
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-banders-2026-security-key')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

# 4. APLICACIONES
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    # Aplicaciones de Terceros
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.mfa',  # Necesario para el QR (Google Authenticator)
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'simple_history',
    'whitenoise.runserver_nostatic',

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

# 5. MIDDLEWARE
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
    'proyectoBanders.abogados.middleware.ProtegerMFAMiddleware',
]

ROOT_URLCONF = 'proyectoBanders.proyectoBanders.urls'

# 6. TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'proyectoBanders', 'templates'),
        ],
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

# 7. INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# 8. BASE DE DATOS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'proyectoBanders',
        'USER': 'postgres',
        'PASSWORD': '1910',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 9. MODELO DE USUARIO PERSONALIZADO
AUTH_USER_MODEL = 'usuarios.UsuarioCustom'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# 10. CONFIGURACIÓN ALLAUTH (SINCRO DJANGO 6.0+ - SIN CONFLICTOS)
# Al definir 'email', Django ya sabe que es obligatorio.
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_VERIFICATION = "none"

# ELIMINADO EL CONFLICTO W001: No menciones 'email' aquí.
ACCOUNT_SIGNUP_FIELDS = ['first_name', 'last_name']

ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

ACCOUNT_FORMS = {
    'login': 'proyectoBanders.usuarios.forms.UsuarioLoginForm',
    'signup': 'proyectoBanders.usuarios.forms.UsuarioRegistroForm',
}

# 11. CONFIGURACIÓN QR (MFA / TOTP)
MFA_SUPPORTED_TYPES = ['totp']  # 'totp' activa el QR compatible con tus carpetas
MFA_TOTP_ISSUER = 'Consorcio Banders'
MFA_REQUIRED_FOR_LOGIN = False
MFA_ADAPTER = 'allauth.mfa.adapter.DefaultMFAAdapter'

# 12. CONFIGURACIÓN CRISPY FORMS
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# 13. ARCHIVOS ESTÁTICOS
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_production')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'proyectoBanders', 'static'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 14. CORREO
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Consorcio Jurídico Banders <consorciojuridicobanders@gmail.com>'

# 15. SESIÓN
SESSION_COOKIE_AGE = 2592000
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
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