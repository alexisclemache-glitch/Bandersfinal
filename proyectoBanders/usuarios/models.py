from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from allauth.account.signals import email_confirmed


class UsuarioCustom(AbstractUser):
    email = models.EmailField(_('dirección de correo'), unique=True)

    # IMPORTANTE: Para que Allauth no busque un 'username' si no lo usas,
    # puedes dejarlo pero el email es el principal.

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

    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "Usuario del Consorcio"
        verbose_name_plural = "Usuarios del Consorcio"
        ordering = ['-date_joined']

    def __str__(self):
        nombre_completo = self.get_full_name()
        return f"{nombre_completo if nombre_completo else self.username} - {self.get_rol_display()}"


# ==========================================
# SIGNAL: ACTIVACIÓN AUTOMÁTICA DE 6 DÍGITOS
# ==========================================
@receiver(email_confirmed)
def activar_mfa_automatico(request, email_address, **kwargs):
    """
    Cuando el usuario confirma su correo, activamos el MFA por Email
    automáticamente para que el sistema le pida el código de 6 dígitos.
    """
    try:
        from allauth.mfa.models import Authenticator

        # El campo 'data' DEBE ser un dict vacío para evitar el Internal Server Error
        Authenticator.objects.get_or_create(
            user=email_address.user,
            type=Authenticator.Type.EMAIL,
            defaults={'data': {}}
        )
        print(f"DEBUG: MFA activado exitosamente para {email_address.user.email}")
    except Exception as e:
        print(f"DEBUG ERROR en Signal MFA: {e}")