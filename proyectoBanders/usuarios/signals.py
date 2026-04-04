from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manejar_usuario_banders(sender, instance, created, **kwargs):
    """
    Crea el perfil profesional automáticamente al registrarse.
    """
    if created:
        try:
            # Según tu archivo de modelos de la app abogados:
            # App: 'abogados', Modelo: 'Perfil'
            ModeloPerfil = apps.get_model('abogados', 'Perfil')

            if getattr(instance, 'rol', None) == 'abogado':
                # El campo en tu modelo Perfil es 'user', no 'usuario'
                ModeloPerfil.objects.get_or_create(user=instance)
                print(f"✅ SISTEMA: Perfil (Colaborador) creado para {instance.email}")

        except Exception as e:
            # Si falla el perfil, NO detenemos el proceso para que llegue al QR
            print(f"⚠️ SISTEMA: Error al crear perfil profesional: {e}")