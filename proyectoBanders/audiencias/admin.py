from django.contrib import admin
from .models import Audiencia


@admin.register(Audiencia)
class AudienciaAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista principal del admin
    list_display = ('titulo', 'get_cliente', 'expediente', 'fecha_inicio', 'color_categoria')

    # Filtros laterales para buscar más rápido
    list_filter = ('color_categoria', 'fecha_inicio', 'expediente__tipo_expediente')

    # Buscador por título, nombre del cliente o título del expediente
    search_fields = ('titulo', 'expediente__titulo', 'expediente__cliente__nombre')

    # Orden predeterminado (más recientes primero)
    ordering = ('-fecha_inicio',)

    # Método para mostrar el nombre del cliente en la lista
    def get_cliente(self, obj):
        return obj.expediente.cliente.nombre if obj.expediente.cliente else "Sin Cliente"

    get_cliente.short_description = 'Cliente'