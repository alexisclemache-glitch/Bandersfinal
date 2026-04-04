from django.urls import path
from . import views

app_name = 'expedientes'

urlpatterns = [
    # Vista principal y creación
    path('', views.lista_expedientes, name='lista_expedientes'),
    path('nuevo/', views.lista_expedientes, name='create'),

    # --- CAMBIO DE ESTADO (ABIERTO / CERRADO) ---
    # Esta ruta es la que usa el botón dinámico del calendario y la lista
    path('estado/<int:pk>/', views.actualizar_estado_expediente, name='actualizar_estado'),

    # Gestión de archivos y borrado
    path('eliminar/<int:pk>/', views.eliminar_expediente, name='eliminar_expediente'),
    path('subir-documento/<int:expediente_id>/', views.upload_expediente_document, name='upload_expediente_document'),
]