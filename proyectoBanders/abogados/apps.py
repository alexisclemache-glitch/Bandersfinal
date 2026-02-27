from django.apps import AppConfig

class AbogadosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'abogados'

    def ready(self):
        # Al importar las señales aquí, Django las activa
        # en cuanto el servidor se pone en marcha
        import abogados.signals