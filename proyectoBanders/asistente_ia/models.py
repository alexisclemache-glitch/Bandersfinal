from django.db import models
from django.conf import settings # <--- IMPORTANTE: Importa esto

class NotebookLegal(models.Model):
    # Cambiamos 'User' por settings.AUTH_USER_MODEL
    abogado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    titulo_caso = models.CharField(max_length=255)
    contenido_escrito = models.TextField()
    archivo_adjunto = models.FileField(upload_to='legal_files/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo_caso