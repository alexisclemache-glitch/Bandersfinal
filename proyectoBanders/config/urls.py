from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
# Importación limpia
from proyectoBanders.abogados.views import media_protegido, espera_aprobacion_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- SEGURIDAD MFA NATIVA ---
    path('accounts/', include('allauth.urls')),

    # --- MÓDULOS DEL SISTEMA ---
    path('dashboard/', include('proyectoBanders.dashboard.urls', namespace='dashboard')),
    path('usuarios/', include('proyectoBanders.usuarios.urls', namespace='usuarios')),
    path('abogados/', include('proyectoBanders.abogados.urls', namespace='abogados')),
    path('clientes/', include('proyectoBanders.clientes.urls', namespace='clientes')),
    path('expedientes/', include('proyectoBanders.expedientes.urls', namespace='expedientes')),
    path('audiencias/', include('proyectoBanders.audiencias.urls', namespace='audiencias')),
    path('busqueda/', include('proyectoBanders.busqueda.urls', namespace='busqueda')),
    path('pagos/', include('proyectoBanders.pagos.urls', namespace='pagos')),
    path('asistente-ia/', include('proyectoBanders.asistente_ia.urls', namespace='asistente_ia')),

    # --- RUTA DE ATERRIZAJE PARA NO APROBADOS ---
    path('espera-aprobacion/', espera_aprobacion_view, name='espera_aprobacion'),

    # --- ARCHIVOS Y REDIRECCIÓN ---
    path('ver-archivo/<path:ruta_archivo>/', media_protegido, name='media_protegido'),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
]

# Servir estáticos en desarrollo
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Importante: No servimos MEDIA directamente si queremos que media_protegido funcione
    # Pero para desarrollo, se suele dejar así:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)