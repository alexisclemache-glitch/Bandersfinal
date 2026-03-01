from django.apps import AppConfig

class PagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # El nombre debe incluir la carpeta contenedora proyectoBanders
    name = 'proyectoBanders.pages'
    verbose_name = 'Gestión de Páginas'