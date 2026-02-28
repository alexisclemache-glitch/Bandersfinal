from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proyectoBanders.usuarios'

    def ready(self):
        # Importación relativa para evitar errores de rutas
        from . import signals