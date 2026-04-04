from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manejar_usuario_banders(sender, instance, created, **kwargs):
    if created:
        try:
            # IMPORTANTE: Usamos el nombre de la app tal cual está en INSTALLED_APPS
            # o el label definido en el AppConfig
            Perfil = apps.get_model('abogados', 'Perfil')

            # Usamos get_or_create para evitar errores si el perfil ya existe por alguna razón
            perfil, created_profile = Perfil.objects.get_or_create(user=instance)

            if created_profile:
                print(f"✅ SISTEMA: Perfil de Abogado creado automáticamente para {instance.email}")
        except LookupError:
            print("⚠️ Error: No se encontró el modelo 'Perfil' en la app 'abogados'.")
        except Exception as e:
            print(f"⚠️ Error inesperado en señal: {e}")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Asegura que el perfil se guarde cuando se guarda el usuario"""
    try:
        # Verificamos si el usuario tiene el atributo 'perfil' (related_name en el modelo)
        if hasattr(instance, 'perfil'):
            instance.perfil.save()
    except Exception:
        pass