# usuarios/context_processors.py
from audiencias.models import Audiencia
from django.utils import timezone
from datetime import timedelta


def notificaciones_audiencias(request):
    if request.user.is_authenticated:
        ahora = timezone.now()
        limite = ahora + timedelta(days=2)

        # Agregamos .distinct() para evitar duplicados por la relación ManyToMany
        audiencias_proximas = Audiencia.objects.filter(
            usuarios_asignados=request.user,
            fecha_inicio__gte=ahora,
            fecha_inicio__lte=limite
        ).distinct()

        return {
            'audiencias_notificaciones': audiencias_proximas,
            'conteo_audiencias': audiencias_proximas.count()
        }
    return {}