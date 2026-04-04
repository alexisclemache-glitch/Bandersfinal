from django.apps import AppConfig


class PagosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    # Nombre completo del paquete
    name = 'proyectoBanders.pagos'

    # Etiqueta corta para que Django sepa que es la app 'pagos'
    label = 'pagos'

    verbose_name = 'Gestión de Pagos'