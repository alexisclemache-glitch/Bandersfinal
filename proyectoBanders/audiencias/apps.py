from django.apps import AppConfig

class AudienciasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audiencias'
    verbose_name = 'Gestión de Audiencias y Calendario'

    def ready(self):
        # Aquí importarás las señales si decides automatizar recordatorios
        # import audiencias.signals
        pass