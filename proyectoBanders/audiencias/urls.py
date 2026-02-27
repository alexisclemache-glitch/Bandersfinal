from django.urls import path
from .views import CalendarioAudienciasView, AudienciaActionView, AudienciaEliminarView

app_name = 'audiencias'

urlpatterns = [
    path('calendario/', CalendarioAudienciasView.as_view(), name='calendario'),
    path('accion/', AudienciaActionView.as_view(), name='crear_audiencia'),
    path('accion/<int:id>/', AudienciaActionView.as_view(), name='editar_audiencia'),
    path('eliminar/<int:id>/', AudienciaEliminarView.as_view(), name='eliminar_audiencia'),
]