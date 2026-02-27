from django.urls import path
from . import views

app_name = 'abogados'

urlpatterns = [
    # --- GESTIÓN DE DIRECTORIO Y COLABORADORES ---
    path('directorio/', views.ColaboradoresListView.as_view(), name='colaboradores_list'),
    path('activar-colaborador/<int:pk>/', views.colaborador_toggle_active, name='activar_colaborador'),
    path('colaborador/<int:pk>/delete/', views.colaborador_delete, name='colaborador_delete'),

    # --- PERFIL DEL ABOGADO ---
    path('perfil/<int:pk>/', views.PerfilDetailView.as_view(), name='perfil_detail'),
    path('perfil/editar/<int:pk>/', views.AbogadoUpdateView.as_view(), name='abogado_edit'),

    # --- SEGURIDAD MFA (GOOGLE AUTHENTICATOR) ---
    # Esta es la ruta donde el abogado pone los 6 dígitos
    path('mfa/verificar/', views.verificar_mfa, name='verificar_mfa'),

    # Esta ruta genera la imagen del código QR para ser escaneada
    path('mfa/qr-image/', views.qr_code_image, name='qr_code_image'),
]