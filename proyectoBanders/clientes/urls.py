from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # --- GESTIÓN DE CLIENTES ---
    path('', views.ClienteListView.as_view(), name='list'),
    path('crear/', views.ClienteCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='delete'),

    # --- EXPEDIENTES ---
    path('expediente/crear/', views.ExpedienteCreateView.as_view(), name='expediente_create'),
    path('expediente/<int:expediente_id>/subir-archivo/', views.upload_expediente_document, name='upload_expediente_document'),

    # --- BÓVEDA ---
    path('<int:pk>/subir-documento/', views.upload_document, name='upload_document'),
    path('documento/<int:pk>/eliminar/', views.delete_document, name='delete_document'),
    path('escrito/eliminar/<int:pk>/', views.delete_escrito, name='delete_escrito'),
    path('<int:pk>/toggle-status/', views.toggle_cliente_status, name='toggle_status'),
]