from django.urls import path
from .views import DashboardView

# El app_name debe coincidir con el namespace que pusiste en el urls.py principal
app_name = 'dashboard'

urlpatterns = [
    # Al dejar el string vacío '', esta es la ruta raíz de la app
    path('', DashboardView.as_view(), name='dashboard'),
]