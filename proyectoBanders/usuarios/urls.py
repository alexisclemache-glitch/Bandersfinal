from django.urls import path
from allauth.account.views import LoginView, SignupView, LogoutView

app_name = 'usuarios'

urlpatterns = [
    # Usamos las vistas de Allauth pero en tus rutas de 'usuarios/'
    path('registro/', SignupView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]