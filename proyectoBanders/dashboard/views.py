import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Importación de modelos desde sus respectivas apps
from proyectoBanders.pagos.models import Pago, Abono
from proyectoBanders.clientes.models import Cliente
from proyectoBanders.expedientes.models import Expediente
from proyectoBanders.audiencias.models import Audiencia

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del Dashboard.
    Filtra la información según el rol del usuario (Admin vs Abogado).
    """
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        hoy = timezone.now()
        hace_30_dias = hoy - timedelta(days=30)

        # 1. SEGURIDAD DE FILTRADO (Lógica de Roles)
        # Verificamos si es superuser o tiene el rol de administrador en el modelo Custom
        es_admin = user.is_superuser or getattr(user, 'rol', '') == 'administrador'

        if es_admin:
            exp_qs = Expediente.objects.all().select_related('cliente')
            cli_qs = Cliente.objects.all()
            pago_qs = Pago.objects.all()
            abono_qs = Abono.objects.all()
        else:
            # El abogado solo ve lo que él creó o lo que está asignado a él
            exp_qs = Expediente.objects.filter(
                Q(creado_por=user) | Q(cliente__creado_por=user)
            ).select_related('cliente').distinct()
            cli_qs = Cliente.objects.filter(creado_por=user)
            pago_qs = Pago.objects.filter(expediente__in=exp_qs)
            abono_qs = Abono.objects.filter(pago_asociado__expediente__in=exp_qs)

        # 2. MÉTRICAS GENERALES
        total_casos = exp_qs.count()
        casos_nuevos_mes = exp_qs.filter(fecha_inicio__gte=hace_30_dias).count()
        total_clientes = cli_qs.count()

        # 3. CÁLCULOS FINANCIEROS (Para la Tarjeta Visa Infinite)
        # Sumamos el total pactado en expedientes
        data_pactado = pago_qs.aggregate(total=Sum('total_deuda'))
        total_pactado = data_pactado['total'] or Decimal('0.00')

        # Sumamos todos los abonos realizados
        data_recaudado = abono_qs.aggregate(total=Sum('monto'))
        total_recaudado = data_recaudado['total'] or Decimal('0.00')

        # El saldo pendiente nunca debe ser negativo
        total_por_cobrar = max(total_pactado - total_recaudado, Decimal('0.00'))

        # 4. PRÓXIMAS AUDIENCIAS (Agenda Lateral)
        audiencias_proximas = Audiencia.objects.filter(
            expediente__in=exp_qs,
            fecha_inicio__gte=hoy
        ).select_related('expediente__cliente').order_by('fecha_inicio')[:4]

        # 5. PREPARACIÓN DE FULLCALENDAR (JSON)
        eventos_lista = []
        # Traemos todas las audiencias para el calendario del Offcanvas
        calendar_qs = Audiencia.objects.filter(expediente__in=exp_qs).select_related('expediente__cliente')

        for aud in calendar_qs:
            eventos_lista.append({
                'id': str(aud.id),
                'title': f"{aud.expediente.cliente.nombre[:10]} - {aud.titulo}",
                'start': aud.fecha_inicio.isoformat(),
                'end': aud.fecha_fin.isoformat() if aud.fecha_fin else None,
                # Color azul si es futura, gris si ya pasó
                'backgroundColor': '#0061ff' if aud.fecha_inicio >= hoy else '#64748b',
                'borderColor': 'transparent',
                'allDay': False
            })

        # 6. ENTREGA DE CONTEXTO AL TEMPLATE
        # Usamos nombres claros que coincidan con tus etiquetas {{ }} en el HTML
        context.update({
            'nombre_abogado': f"{user.first_name} {user.last_name}".strip() or user.username,
            'rol_usuario': user.get_rol_display() if hasattr(user, 'get_rol_display') else "Profesional",
            'total_casos': total_casos,
            'casos_nuevos_mes': casos_nuevos_mes,
            'total_clientes': total_clientes,
            'total_recaudado': total_recaudado,
            'total_por_cobrar': total_por_cobrar,
            'casos_recientes': exp_qs.order_by('-id')[:6],
            'audiencias_proximas': audiencias_proximas,
            'eventos_json': json.dumps(eventos_lista),
        })

        return context