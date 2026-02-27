import urllib.parse
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from expedientes.models import Expediente


class Audiencia(models.Model):
    # Permitimos null=True para que existan citas sin expediente
    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name='audiencias',
        null=True,
        blank=True
    )

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)

    PRIORIDAD_CHOICES = [
        ('bg-danger', 'Urgente / Pendiente'),
        ('bg-success', 'Completada / Exitosa'),
        ('bg-primary', 'General / Cita'),
        ('bg-info', 'Informativa'),
    ]
    color_categoria = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='bg-primary'
    )

    usuarios_asignados = models.ManyToManyField(
        settings.AUTH_USER_MODEL,  # Corregido: AUTH_USER_MODEL
        related_name='audiencias_asignadas'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    @property
    def google_calendar_url(self):
        base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
        fmt = "%Y%m%dT%H%M%SZ"
        inicio = self.fecha_inicio.astimezone(timezone.utc).strftime(fmt)
        fin = (self.fecha_fin or (self.fecha_inicio + timedelta(hours=1))).astimezone(timezone.utc).strftime(fmt)

        titulo_url = urllib.parse.quote(self.titulo)

        # Evitamos error si no hay expediente
        if self.expediente:
            desc_txt = f"Expediente: {self.expediente.titulo}\nCliente: {self.expediente.cliente.nombre}\n\n{self.descripcion or ''}"
        else:
            desc_txt = f"Asesoría Directa\n\n{self.descripcion or ''}"

        desc_url = urllib.parse.quote(desc_txt)
        return f"{base_url}&text={titulo_url}&dates={inicio}/{fin}&details={desc_url}"

    def __str__(self):
        if self.expediente:
            return f"{self.titulo} - {self.expediente}"
        return f"CITA: {self.titulo}"