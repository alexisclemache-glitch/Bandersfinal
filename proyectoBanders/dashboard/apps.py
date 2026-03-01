from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # ACTUALIZADO: Debe llevar el prefijo del proyecto
    name = 'proyectoBanders.dashboard'
    verbose_name = 'Panel de Control Banders'