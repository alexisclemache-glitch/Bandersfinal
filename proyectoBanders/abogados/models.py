import os
import pyotp
import qrcode
from io import BytesIO
from PIL import Image

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile


# --- MODELO DE PERFIL PRINCIPAL ---
class Perfil(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    # Campos de imagen con compresión
    foto = models.ImageField(
        upload_to='perfiles/fotos/',
        null=True,
        blank=True,
        help_text="Tamaño recomendado: 400x400px"
    )
    portada = models.ImageField(
        upload_to='perfiles/portadas/',
        null=True,
        blank=True
    )

    # Información profesional
    especialidad = models.CharField(
        max_length=100,
        default="Abogado Jurídico"
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name="Biografía Profesional"
    )
    hoja_vida = models.FileField(
        upload_to='perfiles/hcv/',
        null=True,
        blank=True
    )

    # --- CAMPOS PARA SEGURIDAD MFA (GOOGLE AUTHENTICATOR) ---
    otp_secret = models.CharField(
        max_length=32,
        default=pyotp.random_base32,
        editable=False
    )
    mfa_configurado = models.BooleanField(
        default=False,
        help_text="Indica si el usuario ya vinculó su Google Authenticator"
    )

    class Meta:
        verbose_name = "Perfil de Abogado"
        verbose_name_plural = "Perfiles de Abogados"

    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"

    # Genera la URL necesaria para el código QR
    def get_totp_uri(self):
        return pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
            name=self.user.email,
            issuer_name="Consorcio Jurídico Banders"
        )

    # --- MÉTODO PARA COMPRIMIR IMÁGENES AL GUARDAR ---
    def save(self, *args, **kwargs):
        if self.foto:
            self.foto = self.comprimir_imagen(self.foto, (400, 400))
        if self.portada:
            self.portada = self.comprimir_imagen(self.portada, (1200, 400))
        super().save(*args, **kwargs)

    def comprimir_imagen(self, campo_imagen, tamano):
        try:
            extension = os.path.splitext(campo_imagen.name)[1].lower()
            if extension not in ['.jpg', '.jpeg', '.png', '.webp']:
                return campo_imagen

            img = Image.open(campo_imagen)
            if img.width <= tamano[0] and img.height <= tamano[1]:
                return campo_imagen

            img.thumbnail(tamano, Image.Resampling.LANCZOS)
            output = BytesIO()
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.save(output, format='JPEG', quality=70, optimize=True)
            output.seek(0)
            return ContentFile(output.read(), name=os.path.basename(campo_imagen.name))
        except Exception as e:
            print(f"⚠️ Error procesando imagen {campo_imagen.name}: {e}")
            return campo_imagen


# --- MODELOS ADICIONALES ---

class DocumentoAdjunto(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='documentos')
    archivo = models.FileField(upload_to='perfiles/documentos/')
    nombre = models.CharField(max_length=255, default="Archivo sin nombre")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.perfil.user.username})"

    def extension(self):
        ext = os.path.splitext(self.archivo.name)[1].lower()
        iconos = {
            '.pdf': 'ri-file-pdf-fill text-danger',
            '.doc': 'ri-file-word-fill text-primary',
            '.docx': 'ri-file-word-fill text-primary',
            '.xls': 'ri-file-excel-fill text-success',
            '.xlsx': 'ri-file-excel-fill text-success',
            '.jpg': 'ri-image-fill text-info',
            '.png': 'ri-image-fill text-info',
        }
        return iconos.get(ext, 'ri-file-text-fill text-secondary')


class NotaKeep(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='notas_keep')
    titulo = models.CharField(max_length=100, default="Nueva Nota")
    contenido = models.TextField()
    color = models.CharField(max_length=20, default='#ffffff')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota Rápida"
        verbose_name_plural = "Notas Rápidas"
        ordering = ['-fecha_creacion']


# --- SIGNALS ---
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manejar_perfil_automatico(sender, instance, created, **kwargs):
    if created:
        # Crea el perfil automáticamente al registrar un nuevo usuario
        Perfil.objects.get_or_create(user=instance)

        # Bloqueo inicial para nuevos abogados (requieren activación manual)
        if not instance.is_superuser:
            instance.is_active = False
            instance.save()
    else:
        # Asegura que perfiles antiguos tengan su objeto Perfil
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(user=instance)