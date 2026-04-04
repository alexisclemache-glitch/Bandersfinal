from django.apps import AppConfig


class ExpedientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    # Nombre completo del paquete
    name = 'proyectoBanders.expedientes'

    # Etiqueta corta (CRUCIAL para resolver el RuntimeError)
    label = 'expedientes'

    verbose_name = 'Gestión de Expedientes'