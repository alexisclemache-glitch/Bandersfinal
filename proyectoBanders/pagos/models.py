import os
from django.db import models
from django.conf import settings
from django.db.models import Sum
from decimal import Decimal
from django.core.exceptions import ValidationError

# --- OPCIONES ---
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


# --- FUNCIONES DE AYUDA ---
def path_comprobante_pago(instance, filename):
    """Genera la ruta dinámica usando el RUT del cliente."""
    # Accedemos a través de la relación sin importar el modelo arriba
    rut = instance.pago_asociado.expediente.cliente.rut
    return f'clientes/{rut}/pagos/comprobante_{filename}'


# --- MODELO PAGO ---
class Pago(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('parcial', 'Pago Parcial')
    ]

    # CAMBIO CRITICO: Usar string 'expedientes.Expediente' para evitar errores de carga
    expediente = models.ForeignKey(
        'expedientes.Expediente',
        on_delete=models.CASCADE,
        related_name='pagos_registrados'
    )
    concepto = models.CharField(max_length=50, choices=CONCEPTO_CHOICES, default='honorarios')
    total_deuda = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    transaccion_id = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    notas_pago = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'pagos'  # Ayuda a Django a identificar la app
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.transaccion_id} - {self.expediente.cliente.nombre}"

    @property
    def total_abonado(self):
        return self.abonos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    @property
    def saldo_pendiente(self):
        return max(self.total_deuda - self.total_abonado, Decimal('0.00'))

    def actualizar_estado(self):
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


# --- MODELO ABONO ---
class Abono(models.Model):
    pago_asociado = models.ForeignKey(Pago, related_name='abonos', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_abono = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, choices=METODOS_PAGO_CHOICES, default='efectivo')

    # Relación con Usuario (MFA compatible)
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='abonos_realizados'
    )

    comprobante_file = models.FileField(upload_to=path_comprobante_pago, null=True, blank=True)
    referencia_bancaria = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'pagos'

    def clean(self):
        # Evitamos errores si el pago aún no está asignado en memoria
        if not hasattr(self, 'pago_asociado'):
            return

        saldo = self.pago_asociado.saldo_pendiente

        if not self.pk:  # Es un abono nuevo
            if self.monto > saldo:
                raise ValidationError(f"El monto (${self.monto}) excede el saldo pendiente (${saldo})")
        else:  # Es una edición
            original = Abono.objects.get(pk=self.pk)
            if self.monto > (saldo + original.monto):
                raise ValidationError("El monto editado supera la deuda total.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.pago_asociado.actualizar_estado()

    def delete(self, *args, **kwargs):
        pago = self.pago_asociado
        super().delete(*args, **kwargs)
        pago.actualizar_estado()