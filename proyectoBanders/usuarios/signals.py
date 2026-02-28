from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from allauth.mfa.models import Authenticator
import logging

# Configuramos un logger para ver errores en la consola de Django
logger = logging.getLogger(__name__)

@receiver(email_confirmed)
def activar_mfa_automatico(request, email_address, **kwargs):
    """
    Activa automáticamente el MFA por correo al confirmar el email.
    Optimizado para Allauth v6.0+, Django 6 y PostgreSQL.
    """
    user = email_address.user

    # Usamos constantes de Allauth para evitar errores de escritura ('email' vs 'EMAIL')
    # Allauth v6 usa Authenticator.Type.EMAIL
    mfa_type = Authenticator.Type.EMAIL

    # Verificamos si ya tiene este tipo de MFA activo
    if not Authenticator.objects.filter(user=user, type=mfa_type).exists():
        try:
            Authenticator.objects.create(
                user=user,
                type=mfa_type,
                data={}  # CRÍTICO para PostgreSQL: Evita el IntegrityError (campo JSON no nulo)
            )
            print(f"✅ SEGURIDAD: MFA (Email) activado automáticamente para {user.email}")
        except Exception as e:
            logger.error(f"❌ ERROR al activar MFA para {user.email}: {e}")
            print(f"Error al activar MFA: {e}")