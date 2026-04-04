import os
from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver


# ========================================================
# --- MODELO DE PERFIL PROFESIONAL ---
# ========================================================

class Perfil(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    # Información profesional
    especialidad = models.CharField(max_length=100, default="Abogado Jurídico")
    telefono = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    # Multimedia con rutas organizadas
    foto = models.ImageField(upload_to='perfiles/fotos/', null=True, blank=True)
    portada = models.ImageField(upload_to='perfiles/portadas/', null=True, blank=True)
    hoja_vida = models.FileField(upload_to='perfiles/cv/', null=True, blank=True)

    # --- SEGURIDAD MFA ---
    # Almacena el secreto Base32 para generar TOTP (Google Authenticator)
    mfa_secret = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        verbose_name = "Perfil de Abogado"
        verbose_name_plural = "Perfiles de Abogados"
        db_table = 'abogados_perfil'

    def __str__(self):
        return self.user.get_full_name() or self.user.email

    @property
    def get_foto_url(self):
        """Retorna la foto del perfil o el dummy por defecto."""
        if self.foto and hasattr(self.foto, 'url'):
            return self.foto.url
        return f"{settings.STATIC_URL}images/users/user-dummy.jpg"

    @property
    def tiene_mfa(self):
        """
        Verifica si el usuario ya vinculó su dispositivo.
        Usamos bool() para que retorne True si hay un secreto guardado.
        """
        return bool(self.mfa_secret)


# ========================================================
# --- BÓVEDA DE DOCUMENTOS ADJUNTOS ---
# ========================================================

class DocumentoAdjunto(models.Model):
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    archivo = models.FileField(upload_to='perfiles/documentos/')
    nombre = models.CharField(max_length=255, default="Archivo sin nombre")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.perfil.user.email}"

    def extension(self):
        """Retorna el icono de Iconify basado en la extensión del archivo."""
        if not self.archivo:
            return "solar:file-corrupted-bold-duotone"

        ext = os.path.splitext(self.archivo.name)[1].lower()

        iconos = {
            '.pdf': "solar:file-download-bold-duotone",
            '.doc': "solar:document-bold-duotone",
            '.docx': "solar:document-bold-duotone",
            '.jpg': "solar:gallery-bold-duotone",
            '.jpeg': "solar:gallery-bold-duotone",
            '.png': "solar:gallery-bold-duotone",
            '.webp': "solar:gallery-bold-duotone",
            '.xls': "solar:rounded-magnifer-bold-duotone",
            '.xlsx': "solar:rounded-magnifer-bold-duotone",
        }

        return iconos.get(ext, "solar:file-bold-duotone")

    def nombre_archivo_limpio(self):
        """Útil para forzar el nombre original en descargas."""
        return os.path.basename(self.archivo.name)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Bóveda de Documentos"


# ========================================================
# --- NOTAS KEEP (EXPEDIENTE RÁPIDO) ---
# ========================================================

class NotaKeep(models.Model):
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='notas_keep'
    )
    titulo = models.CharField(max_length=100, default="Nueva Nota")
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas Keep"
        db_table = 'abogados_notakeep'

    def __str__(self):
        return f"{self.titulo} - {self.perfil.user.email}"


# ========================================================
# --- SEÑALES (SIGNALS) PARA LIMPIEZA DE DISCO ---
# ========================================================

@receiver(post_delete, sender=DocumentoAdjunto)
def borrar_archivo_fisico(sender, instance, **kwargs):
    """Elimina el archivo del almacenamiento físico al borrar el registro."""
    if instance.archivo:
        if os.path.isfile(instance.archivo.path):
            os.remove(instance.archivo.path)


@receiver(post_delete, sender=Perfil)
def borrar_fotos_perfil(sender, instance, **kwargs):
    """Elimina todos los archivos multimedia asociados al perfil al borrarlo."""
    campos = [instance.foto, instance.portada, instance.hoja_vida]
    for campo in campos:
        if campo and hasattr(campo, 'path'):
            if os.path.isfile(campo.path):
                os.remove(campo.path)