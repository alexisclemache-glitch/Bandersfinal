from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Perfil

# IMPORTANTE: Importar el modelo de autenticación de Allauth
from allauth.mfa.models import Authenticator

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manejar_perfil_y_mfa_usuario(sender, instance, created, **kwargs):
    """
    1. Garantiza la existencia del Perfil.
    2. Activa automáticamente el MFA por Email para nuevos usuarios.
    """
    # --- PARTE 1: GESTIÓN DEL PERFIL ---
    if created:
        Perfil.objects.get_or_create(user=instance)
    else:
        # Aseguramos que el perfil exista y lo guardamos
        perfil, _ = Perfil.objects.get_or_create(user=instance)
        perfil.save()

    # --- PARTE 2: ACTIVACIÓN AUTOMÁTICA DE MFA (v6.0) ---
    # Solo intentamos activar MFA si el usuario acaba de ser creado
    if created:
        try:
            # En v6.0+, el tipo se define simplemente como el string 'email'
            if not Authenticator.objects.filter(user=instance, type='email').exists():
                Authenticator.objects.create(
                    user=instance,
                    type='email',
                    data={'email': instance.email}
                )
                print(f"✅ MFA (6 dígitos) activado automáticamente para: {instance.email}")
        except Exception as e:
            # Capturamos el error para que el registro del usuario no falle si el MFA falla
            print(f"⚠️ Error al activar MFA en Signal: {str(e)}")