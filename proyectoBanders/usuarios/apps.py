from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    # Ruta completa al paquete de la aplicación
    name = 'proyectoBanders.usuarios'

    # Etiqueta corta para referencias internas
    label = 'usuarios'

    verbose_name = 'Gestión de Usuarios Banders'

    def ready(self):
        """
        Este método se ejecuta UNA SOLA VEZ cuando Django arranca.
        Importamos las señales aquí para evitar importaciones circulares.
        """
        try:
            # Importación absoluta para evitar ambigüedades en el refactor
            import proyectoBanders.usuarios.signals
            print("✅ SISTEMA: Señales de Usuario y MFA vinculadas correctamente.")
        except ImportError as e:
            logger.error(f"❌ ERROR crítico al cargar señales en UsuariosConfig: {e}")
            # No lanzamos excepción para que el servidor no se caiga,
            # pero lo marcamos en consola.
            print(f"Falló la carga de señales: {e}")