import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from django.contrib.messages import constants as messages

# 1. RUTAS BÁSICAS
BASE_DIR = Path(__file__).resolve().parent.parent

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
    'allauth.mfa',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'simple_history',
    'whitenoise.runserver_nostatic',

    # Aplicaciones Locales
    'usuarios.apps.UsuariosConfig',
    'dashboard.apps.DashboardConfig',
    'abogados.apps.AbogadosConfig',
    'clientes.apps.ClientesConfig',
    'expedientes.apps.ExpedientesConfig',
    'audiencias.apps.AudienciasConfig',
    'pages.apps.PagesConfig',
    'pagos.apps.PagosConfig',
    'busqueda.apps.BusquedaConfig',
    'asistente_ia',
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

    # --- MIDDLEWARE DE SEGURIDAD PERSONALIZADO (BANDERS 2FA) ---
    'abogados.middleware.ProtegerMFAMiddleware',
]

ROOT_URLCONF = 'proyectoBanders.urls'

# 6. TEMPLATES
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
                'audiencias.context_processors.notificaciones_audiencias',
            ],
        },
    },
]

# 7. INTERNACIONALIZACIÓN (ECUADOR)
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_L10N = True
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

# ==============================================================================
# 10. CONFIGURACIÓN ALLAUTH (ACTUALIZADO v6.0)
# ==============================================================================
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7

# IMPORTANTE: Mantenemos False para que el Middleware tome el control tras el login
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False

ACCOUNT_FORMS = {
    'login': 'usuarios.forms.UsuarioLoginForm',
    'signup': 'usuarios.forms.UsuarioRegistroForm',
}

# ==============================================================================
# 11. CONFIGURACIÓN MFA (TOTALMENTE PERSONALIZADO PARA GOOGLE AUTHENTICATOR)
# ==============================================================================
# NOTA: Al usar nuestro propio ProtegerMFAMiddleware y pyotp,
# desactivamos los requerimientos automáticos de allauth.mfa para evitar conflictos.
MFA_REQUIRED_FOR_LOGIN = False

# ==============================================================================
# 12. CONFIGURACIÓN CRISPY FORMS
# ==============================================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ==============================================================================
# 13. ARCHIVOS ESTÁTICOS Y MULTIMEDIA
# ==============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'staticfiles'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'assets_production')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

FILE_UPLOAD_MAX_MEMORY_SIZE = 15728640
DATA_UPLOAD_MAX_MEMORY_SIZE = 15728640

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

# ==============================================================================
# 14. CORREO (CONSOLA PARA DESARROLLO)
# ==============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Consorcio Jurídico Banders <consorciojuridicobanders@gmail.com>'

# 15. SESIÓN Y MENSAJES
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