from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. SEGURIDAD Y MFA (Prioridad máxima)
    # Esta línea permite que Allauth gestione el flujo de los 6 dígitos
    path('accounts/mfa/', include('allauth.mfa.urls')),

    # Rutas base de Allauth (Login, Registro, Confirmación de Email)
    path('accounts/', include('allauth.urls')),

    # 2. TUS RUTAS PERSONALIZADAS DE USUARIOS
    # Mantenemos tu namespace pero asegúrate de que tus vistas hereden de Allauth
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),

    # 3. APLICACIONES DE CORE (Negocio)
    path('', include('dashboard.urls', namespace='dashboard')),
    path('abogados/', include('abogados.urls', namespace='abogados')),
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('expedientes/', include('expedientes.urls', namespace='expedientes')),
    path('audiencias/', include('audiencias.urls', namespace='audiencias')),

    # 4. APLICACIONES DE SOPORTE Y HERRAMIENTAS
    path('busqueda/', include('busqueda.urls', namespace='busqueda')),
    path('pagos/', include('pagos.urls', namespace='pagos')),

    # 5. INTELIGENCIA ARTIFICIAL (Gemini)
    path('asistente-ia/', include('asistente_ia.urls', namespace='asistente_ia')),
]

# Servir archivos multimedia y estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)