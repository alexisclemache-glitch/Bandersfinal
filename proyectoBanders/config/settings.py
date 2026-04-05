import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages

# ==========================================
# 1. RUTAS BÁSICAS Y CARGA DE ENTORNO
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'proyectoBanders'))

load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==========================================
# 2. SEGURIDAD (IMPORTANTE: DEBUG DEBE SER FALSE)
# ==========================================
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-banders-2026-security-key')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# CAMBIO VITAL: DEBUG debe ser False para que las reglas de HTTPS funcionen
DEBUG = False

ALLOWED_HOSTS = [
    '217.216.92.156',
    'app.abgbanders.com',
    'www.app.abgbanders.com',
    'localhost',
    '127.0.0.1'
]

# ==========================================
# 3. APLICACIONES
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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.mfa',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'simple_history',
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
# 6. BASE DE DATOS
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
# 8-10. ALLAUTH, MFA Y CRISPY
# ==========================================
ACCOUNT_ADAPTER = 'proyectoBanders.usuarios.adapter.AprobacionAdminAdapter'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_FORMS = {
    'signup': 'proyectoBanders.usuarios.forms.UsuarioRegistroForm',
    'login': 'proyectoBanders.usuarios.forms.UsuarioLoginForm',
}
MFA_SUPPORTED_TYPES = ['totp']
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ==========================================
# 11-13. ESTÁTICOS, CORREO Y REDIRECCIONES
# ==========================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_production')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'proyectoBanders', 'static')]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'account_login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'consorciojuridicobanders@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# ==========================================
# 14. CONFIGURACIÓN DE PRODUCCIÓN (CORREGIDA)
# ==========================================
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    USE_X_FORWARDED_HOST = True
    
    CSRF_TRUSTED_ORIGINS = [
        'https://app.abgbanders.com',
        'https://www.app.abgbanders.com',
        'https://*.abgbanders.com',
    ]
