from django.utils import timezone
from .models import Audiencia

def notificaciones_audiencias(request):
    """
    Muestra las audiencias de todo el consorcio para los próximos 3 días.
    Útil para el dropdown de notificaciones en el navbar.
    """
    if request.user.is_authenticated:
        ahora = timezone.now()
        # Ampliamos el rango a 3 días
        limite_3_dias = ahora + timezone.timedelta(days=3)

        # 🛠️ CORRECCIÓN: 'caso' cambiado por 'expediente'
        # 🚀 OPTIMIZACIÓN: Traemos cliente para evitar múltiples consultas SQL
        proximas = Audiencia.objects.filter(
            fecha_inicio__gte=ahora,
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