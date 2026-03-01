from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from allauth.mfa.models import Authenticator
import logging

logger = logging.getLogger(__name__)


@receiver(email_confirmed)
def activar_mfa_automatico(request, email_address, **kwargs):
    """
    Se ejecuta al confirmar el email.
    Nota: Allauth MFA soporta TOTP, no EMAIL como tipo de autenticador.
    """
    user = email_address.user

    # El tipo correcto en Allauth es TOTP (para el código QR)
    # Si intentas usar .EMAIL, seguirá saliendo el AttributeError.
    mfa_type = Authenticator.Type.TOTP

    # Verificamos si ya tiene MFA activo
    if not Authenticator.objects.filter(user=user, type=mfa_type).exists():
        try:
            # IMPORTANTE: No podemos "activar" TOTP automáticamente sin que el usuario
            # escanee el QR, por lo que aquí lo ideal es solo LOGUEAR el evento
            # o preparar una configuración básica.

            # Si lo que quieres es forzar a que el usuario use MFA,
            # es mejor redirigirlo a la configuración en lugar de crear un objeto vacío.

            print(f"✅ Email confirmado para {user.email}. Listo para configurar MFA.")

        except Exception as e:
            logger.error(f"❌ ERROR en señal de confirmación para {user.email}: {e}")