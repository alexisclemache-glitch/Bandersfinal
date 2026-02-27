from django.urls import path
from . import views

app_name = 'expedientes'

urlpatterns = [
    path('', views.lista_expedientes, name='lista_expedientes'),
    path('nuevo/', views.lista_expedientes, name='create'),
    path('estado/<int:pk>/', views.actualizar_estado_expediente, name='actualizar_estado'),
    path('eliminar/<int:pk>/', views.eliminar_expediente, name='eliminar_expediente'),
    # Este es el nombre clave que causaba el error:
    path('subir-documento/<int:expediente_id>/', views.upload_expediente_document, name='upload_expediente_document'),
]