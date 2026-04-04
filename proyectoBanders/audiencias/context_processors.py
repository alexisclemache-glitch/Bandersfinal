from django.utils import timezone
from .models import Audiencia


def notificaciones_audiencias(request):
    if request.user.is_authenticated:
        # --- CORRECCIÓN AQUÍ ---
        # Usamos .replace para que busque desde el primer segundo de HOY
        ahora_mismo = timezone.now()
        inicio_hoy = ahora_mismo.replace(hour=0, minute=0, second=0, microsecond=0)

        # Mantenemos el límite de 3 días
        limite_3_dias = ahora_mismo + timezone.timedelta(days=3)

        proximas = Audiencia.objects.filter(
            fecha_inicio__gte=inicio_hoy,  # Ahora sí incluye las de hace unos minutos
            fecha_inicio__lte=limite_3_dias
        ).select_related(
            'expediente',
            'expediente__cliente'
        ).prefetch_related(
            'usuarios_asignados'
        ).order_by('fecha_inicio')

        return {
            'notificaciones_audiencias': proximas,
            'total_notificaciones_audiencias': proximas.count()
        }

    return {
        'notificaciones_audiencias': [],
        'total_notificaciones_audiencias': 0
    }