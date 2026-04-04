from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps


class UsuarioCustom(AbstractUser):
    # Identificador principal
    email = models.EmailField(_('dirección de correo'), unique=True)

    # El username debe ser opcional en BD porque lo llenamos automáticamente
    username = models.CharField(
        _('nombre de usuario'),
        max_length=150,
        unique=True,
        null=True,
        blank=True
    )

    ROL_CHOICES = [
        ('abogado', 'Abogado'),
        ('contador', 'Contador'),
        ('psicologo', 'Psicólogo'),
        ('administrador', 'Administrador'),
        ('marketing', 'Marketing'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='abogado',
        verbose_name="Rol en el Consorcio"
    )

    foto = models.ImageField(
        upload_to='perfiles/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Foto de Perfil"
    )

    # CAMPO CLAVE PARA EL MIDDLEWARE Y ADAPTER
    esta_aprobado = models.BooleanField(
        default=False,
        verbose_name="¿Usuario Aprobado?"
    )

    # CONFIGURACIÓN PARA LOGIN POR EMAIL (Requerido para Allauth v6)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'rol']

    class Meta:
        app_label = 'usuarios'
        verbose_name = "Usuario del Consorcio"
        verbose_name_plural = "Usuarios del Consorcio"
        ordering = ['-date_joined']

    def save(self, *args, **kwargs):
        # NORMALIZACIÓN: Forzamos que el username sea siempre el email
        # Esto previene errores de integridad en el login de Allauth
        if self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        nombre = self.get_full_name()
        return f"{nombre if nombre else self.email} - {self.get_rol_display()}"


# --- SEÑALES DE SISTEMA ---

@receiver(post_save, sender=UsuarioCustom)
def manejar_registro_completo_usuario(sender, instance, created, **kwargs):
    """
    Crea el perfil profesional automáticamente tras el registro exitoso.
    Esto ocurre justo antes de que el middleware lance el MFA.
    """
    if created:
        # Definimos roles que requieren perfil en la app 'abogados'
        roles_con_perfil = ['abogado', 'administrador']

        if instance.rol in roles_con_perfil:
            try:
                # Carga dinámica del modelo para evitar importación circular
                Perfil = apps.get_model('abogados', 'Perfil')

                # Asignamos especialidad por defecto según el rol
                especialidad_default = 'Dirección' if instance.rol == 'administrador' else 'Derecho General'

                Perfil.objects.get_or_create(
                    user=instance,
                    defaults={
                        'especialidad': especialidad_default,
                        'bio': 'Miembro del equipo Banders.'
                    }
                )
            except (LookupError, ImportError):
                # La app abogados no está cargada o el modelo Perfil no existe aún
                pass
            except Exception as e:
                # Log del error pero permitimos que el registro continúe
                print(f"⚠️ Error al crear perfil automático para {instance.email}: {e}")