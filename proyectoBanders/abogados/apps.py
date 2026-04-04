from django.apps import AppConfig


class AbogadosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proyectoBanders.abogados'

    def ready(self):
        # IMPORTANTE: La importación debe ir AQUÍ ADENTRO
        try:
            import proyectoBanders.abogados.signals
            # Si necesitas usar el modelo aquí por alguna razón (raro),
            # también se importa aquí adentro:
            # from .models import Abogado

            print("✅ SISTEMA: Señales de Perfil vinculadas correctamente.")
        except ImportError:
            pass