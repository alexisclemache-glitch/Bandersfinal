from django.db import models
from proyectoBanders.expedientes.models import Expediente
from django.db.models import Sum
from decimal import Decimal
from django.core.exceptions import ValidationError

# Opciones para métodos de pago y conceptos
METODOS_PAGO_CHOICES = [
    ('transferencia', 'Transferencia Bancaria'),
    ('efectivo', 'Efectivo'),
    ('deposito', 'Depósito'),
    ('tarjeta', 'Tarjeta de Crédito/Débito'),
]

CONCEPTO_CHOICES = [
    ('honorarios', 'Honorarios Profesionales'),
    ('gastos_judiciales', 'Gastos Judiciales / Tasas'),
    ('peritaje', 'Servicios de Peritaje'),
    ('otros', 'Otros Conceptos'),
]


def path_comprobante_pago(instance, filename):
    """Genera la ruta dinámica para guardar los comprobantes por RUT de cliente."""
    rut = instance.pago_asociado.expediente.cliente.rut
    return f'clientes/{rut}/pagos/comprobante_{filename}'


class Pago(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('parcial', 'Pago Parcial')
    ]

    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='pagos_registrados')
    concepto = models.CharField(max_length=50, choices=CONCEPTO_CHOICES, default='honorarios')
    total_deuda = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    transaccion_id = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    notas_pago = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.transaccion_id} - {self.expediente.cliente.nombre}"

    @property
    def total_abonado(self):
        """Suma todos los abonos relacionados."""
        return self.abonos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    @property
    def saldo_pendiente(self):
        """Calcula lo que falta por pagar."""
        return max(self.total_deuda - self.total_abonado, Decimal('0.00'))

    @property
    def porcentaje_pagado(self):
        """Retorna el entero para la barra de progreso de la tarjeta."""
        if self.total_deuda > 0:
            porcentaje = (self.total_abonado * 100) / self.total_deuda
            return int(min(porcentaje, 100))
        return 0

    def actualizar_estado(self):
        """Cambia el estado automáticamente según el total abonado."""
        total = self.total_abonado
        if total >= self.total_deuda:
            nuevo_estado = 'completado'
        elif total > 0:
            nuevo_estado = 'parcial'
        else:
            nuevo_estado = 'pendiente'

        if self.estado != nuevo_estado:
            self.estado = nuevo_estado
            self.save(update_fields=['estado'])


class Abono(models.Model):
    pago_asociado = models.ForeignKey(Pago, related_name='abonos', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_abono = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, choices=METODOS_PAGO_CHOICES, default='transferencia')
    comprobante_file = models.FileField(upload_to=path_comprobante_pago, null=True, blank=True)
    referencia_bancaria = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        """Validación de seguridad: No permite abonar más de la deuda pendiente."""
        if not self.pago_asociado_id:
            return

        if not self.pk:  # Nuevo abono
            if self.monto > self.pago_asociado.saldo_pendiente:
                raise ValidationError(f"El monto excede el saldo pendiente (${self.pago_asociado.saldo_pendiente})")
        else:  # Editando abono existente
            original = Abono.objects.get(pk=self.pk)
            # El máximo permitido es el saldo actual + lo que ya valía este abono
            max_permitido = self.pago_asociado.saldo_pendiente + original.monto
            if self.monto > max_permitido:
                raise ValidationError(f"Monto inválido. El máximo permitido es: ${max_permitido}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Al guardar, disparamos la actualización de estado del Pago padre
        self.pago_asociado.actualizar_estado()

    def delete(self, *args, **kwargs):
        pago = self.pago_asociado
        super().delete(*args, **kwargs)
        # Al eliminar, recalculamos el estado del Pago padre
        pago.actualizar_estado()