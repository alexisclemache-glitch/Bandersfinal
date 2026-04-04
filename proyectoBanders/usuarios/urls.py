from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Registro personalizado
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro'),

    # Login: Usamos la de Allauth por defecto para que el MFA funcione al 100%
    # Si tienes una lógica visual especial, Allauth usará tu template 'account/login.html'
    path('login/', views.LoginUsuarioView.as_view(), name='login'),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='account_login'), name='logout'),

    # Estado de espera para aprobación de Admin
    path('espera-aprobacion/', views.espera_aprobacion, name='espera_aprobacion'),

    # Perfil y Archivos
    path('mi-perfil/', views.mi_perfil_view, name='mi_perfil'),
    path('ver-archivo/<path:ruta_archivo>/', views.servir_archivo_protegido, name='media_protegido'),
]