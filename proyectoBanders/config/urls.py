from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. SEGURIDAD Y MFA (Allauth gestiona sus propias rutas internas)
    path('accounts/mfa/', include('allauth.mfa.urls')),
    path('accounts/', include('allauth.urls')),

    # 2. RUTAS DE USUARIOS (Corregido: proyectoBanders)
    path('usuarios/', include('proyectoBanders.usuarios.urls', namespace='usuarios')),

    # 3. APLICACIONES DE CORE (Corregido: proyectoBanders)
    path('', include('proyectoBanders.dashboard.urls', namespace='dashboard')),
    path('abogados/', include('proyectoBanders.abogados.urls', namespace='abogados')),
    path('clientes/', include('proyectoBanders.clientes.urls', namespace='clientes')),
    path('expedientes/', include('proyectoBanders.expedientes.urls', namespace='expedientes')),
    path('audiencias/', include('proyectoBanders.audiencias.urls', namespace='audiencias')),

    # 4. APLICACIONES DE SOPORTE Y HERRAMIENTAS (Corregido: proyectoBanders)
    path('busqueda/', include('proyectoBanders.busqueda.urls', namespace='busqueda')),
    path('pagos/', include('proyectoBanders.pagos.urls', namespace='pagos')),

    # 5. INTELIGENCIA ARTIFICIAL (Corregido: proyectoBanders)
    path('asistente-ia/', include('proyectoBanders.asistente_ia.urls', namespace='asistente_ia')),
]

# Servir archivos multimedia y estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)