import os
from django.db import models
from django.conf import settings

# --- FUNCIONES DE AYUDA ---

def path_documentos_expediente(instance, filename):
    """Organiza archivos por el ID del expediente."""
    exp_id = instance.expediente.pk if instance.expediente.pk else "nuevo"
    return f'expedientes/ID_{exp_id}/docs/{filename}'


# --- MODELO PRINCIPAL ---

class Expediente(models.Model):
    MATERIA_CHOICES = [
        ('penal', '⚖️ Penal'),
        ('civil', '📜 Civil'),
        ('laboral', '👷 Laboral'),
        ('familia', '🏠 Familia'),
        ('administrativo', '📂 Administrativo'),  # <-- COMA AGREGADA AQUÍ
        ('migratorio', '✈️ Migratorio'),
    ]
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Proceso'),
        ('finalizado', 'Finalizado'),
        ('suspendido', 'Suspendido')
    ]
    PRIORIDAD_CHOICES = [
        ('baja', '🟢 Baja'),
        ('media', '🟡 Media'),
        ('alta', '🔴 Alta')
    ]

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.CASCADE,
        related_name='expedientes_juridicos',
        verbose_name="Cliente"
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    titulo = models.CharField(max_length=255, verbose_name="Título del Caso")
    numero_proceso = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="N° Proceso / Causa"
    )
    tipo_expediente = models.CharField(max_length=50, choices=MATERIA_CHOICES, default='civil')
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='abierto')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    honorarios_totales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Resumen")
    fecha_inicio = models.DateField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Expediente"
        verbose_name_plural = "Expedientes"
        ordering = ['-actualizado_en']

    def __str__(self):
        return f"{self.numero_proceso or 'S/N'} - {self.titulo}"


# --- MODELOS RELACIONADOS (AÑADIDOS PARA EL ADMIN) ---

class NotaExpediente(models.Model):  # <-- MODELO RE-INSTALADO
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='notas_seguimiento')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    contenido = models.TextField(verbose_name="Actuación / Comentario")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota de Seguimiento"
        verbose_name_plural = "Notas de Seguimiento"
        ordering = ['-fecha_creacion']


class DocumentoExpediente(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='archivos_expediente')
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Documento", blank=True)
    archivo = models.FileField(upload_to=path_documentos_expediente)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.nombre:
            self.nombre = os.path.basename(self.archivo.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"