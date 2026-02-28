from django.apps import AppConfig

class AbogadosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proyectoBanders.abogados'

    def ready(self):
        # Al importar las señales aquí, Django las activa
        # en cuanto el servidor se pone en marcha
        import proyectoBanders.abogados.signals