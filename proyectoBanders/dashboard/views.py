import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Importación de tus modelos
from proyectoBanders.pagos.models import Pago, Abono
from proyectoBanders.clientes.models import Cliente
from proyectoBanders.expedientes.models import Expediente
from proyectoBanders.audiencias.models import Audiencia


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        hoy = timezone.now()
        hace_30_dias = hoy - timedelta(days=30)

        # 1. FILTRADO DE SEGURIDAD (Adaptado a Roles de Banders)
        # Si es superusuario o tiene rol 'administrador', ve todo el consorcio
        if user.is_superuser or getattr(user, 'rol', '') == 'administrador':
            exp_qs = Expediente.objects.all().select_related('cliente')
            cli_qs = Cliente.objects.all()
            pago_qs = Pago.objects.all()
            abono_qs = Abono.objects.all()
        else:
            # Filtro estricto: Lo que el abogado creó o sus expedientes asignados
            exp_qs = Expediente.objects.filter(
                Q(creado_por=user) | Q(cliente__creado_por=user)
            ).select_related('cliente').distinct()
            cli_qs = Cliente.objects.filter(creado_por=user)
            pago_qs = Pago.objects.filter(expediente__in=exp_qs)
            abono_qs = Abono.objects.filter(pago_asociado__expediente__in=exp_qs)

        # 2. MÉTRICAS CORE
        total_casos = exp_qs.count()
        casos_nuevos_mes = exp_qs.filter(fecha_inicio__gte=hace_30_dias).count()

        # 3. FINANZAS (Cálculos precisos para la Visa Card)
        pago_data = pago_qs.aggregate(total=Sum('total_deuda'))
        total_pactado = pago_data['total'] or Decimal('0.00')

        abono_data = abono_qs.aggregate(total=Sum('monto'))
        total_recaudado = abono_data['total'] or Decimal('0.00')

        # Pendiente = Pactado - Recaudado (Evitamos negativos)
        total_por_cobrar = total_pactado - total_recaudado
        if total_por_cobrar < 0:
            total_por_cobrar = Decimal('0.00')

        # 4. PRÓXIMAS AUDIENCIAS (Barra Lateral Agenda)
        # Usamos select_related para traer los datos del cliente en una sola consulta
        audiencias_proximas = Audiencia.objects.filter(
            expediente__in=exp_qs,
            fecha_inicio__gte=hoy
        ).select_related('expediente__cliente').order_by('fecha_inicio')[:4]

        # 5. FULLCALENDAR JSON (Para el Offcanvas derecho)
        eventos_lista = []
        # Traemos todas las audiencias relacionadas para mapearlas al calendario
        calendar_qs = Audiencia.objects.filter(expediente__in=exp_qs).select_related('expediente__cliente')

        for aud in calendar_qs:
            eventos_lista.append({
                'id': str(aud.id),
                'title': f"{aud.expediente.cliente.nombre[:10]} | {aud.titulo}",
                'start': aud.fecha_inicio.isoformat(),
                'end': aud.fecha_fin.isoformat() if aud.fecha_fin else None,
                # Usamos colores elegantes de la paleta Banders
                'backgroundColor': '#0061ff' if aud.fecha_inicio >= hoy else '#64748b',
                'borderColor': 'transparent',
                'extendedProps': {
                    'cliente': f"{aud.expediente.cliente.nombre} {aud.expediente.cliente.apellido}"
                }
            })

        # 6. ACTUALIZACIÓN DEL CONTEXTO
        context.update({
            'nombre_abogado': user.get_full_name() or user.username,
            'total_casos': total_casos,
            'casos_nuevos_mes': casos_nuevos_mes,
            'total_clientes': cli_qs.count(),
            'total_recaudado': total_recaudado,
            'total_por_cobrar': total_por_cobrar,
            'casos_recientes': exp_qs.order_by('-id')[:6],
            'audiencias_proximas': audiencias_proximas,
            'eventos_json': json.dumps(eventos_lista),
        })

        return context