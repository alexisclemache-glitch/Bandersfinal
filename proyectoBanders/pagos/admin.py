from django.contrib import admin
from .models import Pago, Abono

class AbonoInline(admin.TabularInline):
    model = Abono
    extra = 1
    readonly_fields = ('fecha_abono',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    # Quitamos 'transaccion_id' porque no existe en el modelo
    # Usamos 'id' o el 'expediente' como referencia
    list_display = ('id', 'expediente', 'get_cliente', 'total_deuda', 'estado')
    list_filter = ('estado', 'expediente__tipo_expediente')
    search_fields = ('expediente__titulo', 'expediente__cliente__nombre', 'expediente__cliente__apellido')
    inlines = [AbonoInline]

    @admin.display(description='Cliente')
    def get_cliente(self, obj):
        return f"{obj.expediente.cliente.nombre} {obj.expediente.cliente.apellido}"

    # Eliminamos get_tipo porque causaría error si el campo en Expediente
    # no tiene "choices" definidas con etiquetas legibles (display).