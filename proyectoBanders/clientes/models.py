from django.db import models
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum


# --- FUNCIONES DE RUTA PARA ARCHIVOS ---
def path_cliente_foto(instance, filename):
    return f'clientes/{instance.rut}/foto/{filename}'


def path_documentos_cliente(instance, filename):
    # Organiza archivos por cliente y categoría en el servidor
    return f'clientes/{instance.cliente.rut}/documentos/{instance.categoria}/{filename}'


# --- OPCIONES DE SELECCIÓN ---
ESTADO_CIVIL_CHOICES = [
    ('soltero', 'Soltero/a'), ('casado', 'Casado/a'),
    ('divorciado', 'Divorciado/a'), ('viudo', 'Viudo/a'), ('otro', 'Otro'),
]

ESTADO_OPERATIVO_CHOICES = [
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
    ('pendiente', 'Pendiente'),
]

# Categorías aumentadas para los documentos
CATEGORIA_DOC_CHOICES = [
    ('identidad', 'Cédula / Pasaporte'),
    ('contrato', 'Contratos / Convenios'),
    ('poder', 'Poderes Judiciales'),
    ('evidencia', 'Evidencias / Pruebas'),
    ('pago', 'Comprobantes de Pago'),
    ('otros', 'Otros Documentos'),
]

PROVINCIA_CHOICES = [
    ('azuay', 'Azuay'), ('bolivar', 'Bolívar'), ('cañar', 'Cañar'), ('carchi', 'Carchi'),
    ('chimborazo', 'Chimborazo'), ('cotopaxi', 'Cotopaxi'), ('el_oro', 'El Oro'),
    ('esmeraldas', 'Esmeraldas'), ('galapagos', 'Galápagos'), ('guayas', 'Guayas'),
    ('imbabura', 'Imbabura'), ('loja', 'Loja'), ('los_rios', 'Los Ríos'),
    ('manabi', 'Manabí'), ('morona_santiago', 'Morona Santiago'), ('napo', 'Napo'),
    ('orellana', 'Orellana'), ('pastaza', 'Pastaza'), ('pichincha', 'Pichincha'),
    ('santa_elena', 'Santa Elena'), ('santo_domingo', 'Santo Domingo'),
    ('sucumbios', 'Sucumbíos'), ('tungurahua', 'Tungurahua'), ('zamora_chinchipe', 'Zamora Chinchipe'),
]


# --- MODELO PRINCIPAL: CLIENTE ---
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=20, unique=True, verbose_name="Cédula/ID")
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to=path_cliente_foto, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección Domiciliaria")

    estado_operativo = models.CharField(
        max_length=20,
        choices=ESTADO_OPERATIVO_CHOICES,
        default='activo',
        verbose_name="Estado Operativo"
    )

    esta_activo = models.BooleanField(default=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, default='soltero', null=True,
                                    blank=True)
    provincia = models.CharField(max_length=50, choices=PROVINCIA_CHOICES, null=True, blank=True)
    canton = models.CharField(max_length=100, null=True, blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_creados_usuario'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def honorarios_totales(self):
        from django.apps import apps
        try:
            Pago = apps.get_model('pagos', 'Pago')
            total = Pago.objects.filter(expediente__cliente=self).aggregate(total=Sum('total_deuda'))['total']
            return total or Decimal('0.00')
        except:
            return Decimal('0.00')

    @property
    def total_pagado(self):
        from django.apps import apps
        try:
            Abono = apps.get_model('pagos', 'Abono')
            total = Abono.objects.filter(pago_asociado__expediente__cliente=self).aggregate(total=Sum('monto'))['total']
            return total or Decimal('0.00')
        except:
            return Decimal('0.00')

    @property
    def saldo_pendiente(self):
        return self.honorarios_totales - self.total_pagado


# --- MODELO SECUNDARIO: DOCUMENTOS (AUMENTADO) ---
class DocumentoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='documentos')

    # Campo clave (unificado con la vista)
    titulo = models.CharField(max_length=150, verbose_name="Nombre del Documento")

    # Aumentos
    categoria = models.CharField(max_length=30, choices=CATEGORIA_DOC_CHOICES, default='otros')
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción opcional")

    archivo = models.FileField(upload_to=path_documentos_cliente)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento de Cliente"
        verbose_name_plural = "Documentos de Clientes"
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nombre}"