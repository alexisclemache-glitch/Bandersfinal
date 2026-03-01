from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    # ACTUALIZADO: Ahora apunta a la ruta completa tras el refactor
    name = 'proyectoBanders.usuarios'
    label = 'usuarios'

    verbose_name = 'Gestión de Usuarios Banders'

    def ready(self):
        """
        Este método se ejecuta cuando Django arranca.
        Aquí 'encendemos' las señales de MFA automático.
        """
        try:
            # Importación relativa: segura y eficiente dentro del paquete
            from . import signals
            print("✅ SISTEMA: Señales de Usuario (MFA) cargadas correctamente.")
        except ImportError as e:
            logger.error(f"❌ ERROR al cargar las señales de usuarios: {e}")
            print(f"Error crítico en AppConfig de Usuarios: {e}")