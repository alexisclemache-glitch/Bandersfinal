from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from allauth.mfa.models import Authenticator

@receiver(email_confirmed)
def activar_mfa_automatico(request, email_address, **kwargs):
    """
    Activa automáticamente el MFA por correo al confirmar el email.
    Obligatorio para Allauth v6.0+ y PostgreSQL (campo data={} no nulo).
    """
    user = email_address.user

    # Verificamos si ya tiene MFA activo para no duplicar
    if not Authenticator.objects.filter(user=user, type='email').exists():
        try:
            Authenticator.objects.create(
                user=user,
                type='email',
                data={}  # CRÍTICO: Evita el IntegrityError en Postgres
            )
            print(f"MFA activado exitosamente para: {user.email}")
        except Exception as e:
            print(f"Error al activar MFA: {e}")