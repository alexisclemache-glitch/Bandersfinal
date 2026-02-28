from django.urls import path
from allauth.account.views import LoginView, SignupView, LogoutView

# El app_name se mantiene igual para que 'usuarios:login' siga funcionando
app_name = 'usuarios'

urlpatterns = [
    # Usamos las vistas de Allauth pero bajo tu namespace de 'usuarios'
    path('registro/', SignupView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]