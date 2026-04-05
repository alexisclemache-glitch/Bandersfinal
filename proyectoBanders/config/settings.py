import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages

# ==========================================
# 1. RUTAS BÁSICAS Y CARGA DE ENTORNO
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# VITAL PARA CONTABO: Permite que Django encuentre las apps dentro de 'proyectoBanders'
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'proyectoBanders'))

load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==========================================
# 2. SEGURIDAD
# ==========================================
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-banders-2026-security-key')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

# ==========================================
# 3. APLICACIONES (ESTRICTAMENTE MFA NATIVO V6)
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

    # Apps de Banders (Rutas corregidas)
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
# 4. MIDDLEWARE
# ==========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'proyectoBanders.usuarios.middleware.ProtegerMFAMiddleware',
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
# 6. BASE DE DATOS (USUARIO POSTGRES: 1910)
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
# 7. AUTENTICACIÓN Y MODELO CUSTOM
# ==========================================
AUTH_USER_MODEL = 'usuarios.UsuarioCustom'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ==========================================
# 8. CONFIGURACIÓN ALLAUTH v6.0+
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

# ==========================================
# 9. INTEGRACIÓN MFA NATIVA
# ==========================================
MFA_SUPPORTED_TYPES = ['totp']
MFA_TOTP_ISSUER = 'Consorcio Banders'
MFA_PASSWORDS_REQUIRED = True
MFA_REAUTHENTICATE_TIMEOUT = 1800
MFA_REAUTHENTICATION_REQUIRED = False

MFA_TOTP_ACTIVATION_REDIRECT_URL = 'dashboard:index'
MFA_LOGIN_REDIRECT_URL = 'dashboard:index'

# ==========================================
# 10. CRISPY FORMS
# ==========================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ==========================================
# 11. ESTÁTICOS Y MULTIMEDIA (MEDIA)
# ==========================================
# Configuración de Archivos Estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_production')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'proyectoBanders', 'static')]

# CONFIGURACIÓN DE MEDIA (Para clientes/, expedientes/, perfiles/)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==========================================
# 12. REDIRECCIONES Y MENSAJES
# ==========================================
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'account_login'
ACCOUNT_LOGOUT_REDIRECT_URL = 'account_login'

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
# ==========================================
# 13. CONFIGURACIÓN DE CORREO (SMTP)
# ==========================================
# Usamos os.getenv para leer las credenciales de tu archivo .env
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Estas variables deben coincidir con los nombres dentro de tu archivo .env
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'consorciojuridicobanders@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = f'Consorcio Jurídico Banders <{EMAIL_HOST_USER}>'

# Configuración extra para Allauth
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Banders Law] '