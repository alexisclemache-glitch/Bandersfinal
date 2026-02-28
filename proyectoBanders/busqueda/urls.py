from django.urls import path
from . import views

app_name = 'busqueda'

urlpatterns = [
    path('resultados/', views.realizar_busqueda, name='realizar_busqueda'),
]