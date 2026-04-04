from django.urls import path
from . import views

app_name = 'abogados'

urlpatterns = [
    # ==========================================
    # 1. SEGURIDAD Y FLUJO MFA (¡CRÍTICO PARA EL MIDDLEWARE!)
    # ==========================================
    # Esta es la ruta donde el usuario pone los 6 dígitos
    path('mfa/verificar/', views.mfa_verificar_view, name='mfa_verificar'),

    # Esta ruta genera la imagen del código QR para vincular la App
    path('mfa/qr-code/', views.qr_code_image, name='qr_code_image'),

    # Ruta de aterrizaje para quienes pasan el MFA pero no están aprobados aún
    path('espera-aprobacion/', views.espera_aprobacion_view, name='espera_aprobacion'),

    # ==========================================
    # 2. DIRECTORIO Y PERFILES PROFESIONALES
    # ==========================================
    # Muestra la lista de abogados aprobados
    path('directorio/', views.ColaboradoresListView.as_view(), name='colaboradores_list'),

    # Detalle completo de un abogado (Expedientes, Notas, Bóveda)
    path('perfil/<int:pk>/', views.PerfilDetailView.as_view(), name='perfil_detail'),

    # Formulario de edición de perfil (Solo dueño o superusuario)
    path('perfil/editar/<int:pk>/', views.PerfilUpdateView.as_view(), name='abogado_update'),

    # ==========================================
    # 3. ACCIONES ADMINISTRATIVAS (EXCLUSIVO DR. CRISTIAN)
    # ==========================================
    path('colaborador/toggle/<int:pk>/', views.colaborador_toggle, name='colaborador_toggle'),
    path('colaborador/eliminar/<int:pk>/', views.colaborador_delete, name='colaborador_delete'),

    # ==========================================
    # 4. GESTIÓN DE CONTENIDO (ELIMINACIÓN)
    # ==========================================
    path('nota/borrar/<int:pk>/', views.nota_keep_delete, name='nota_delete'),
    path('archivo/borrar/<int:pk>/', views.documento_adjunto_delete, name='documento_delete'),
    
]