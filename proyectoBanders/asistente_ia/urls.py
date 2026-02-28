from django.urls import path
from . import views

app_name = 'asistente_ia'

urlpatterns = [
    path('inbox/', views.inbox_ia, name='inbox_ia'),
    path('generar-escrito/', views.generar_escrito_gemini, name='generar_escrito_gemini'),
    path('guardar-escrito/', views.guardar_en_notebook, name='guardar_en_notebook'),
    path('eliminar-escrito/<int:pk>/', views.eliminar_cuaderno, name='eliminar_cuaderno'),
]