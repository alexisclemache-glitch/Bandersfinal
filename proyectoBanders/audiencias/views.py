import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from .models import Audiencia
from .forms import AudienciaForm

class CalendarioAudienciasView(TemplateView):
    template_name = 'audiencias/pages-calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Audiencia.objects.all().select_related('expediente__cliente').prefetch_related('usuarios_asignados')

        eventos = []
        for a in qs:
            if a.expediente:
                titulo = f"{a.expediente.cliente.nombre} | {a.titulo}"
                exp_id = a.expediente_id
            else:
                titulo = f"CIT: {a.titulo}"
                exp_id = None

            eventos.append({
                'id': a.id,
                'title': titulo,
                'start': a.fecha_inicio.isoformat(),
                'end': a.fecha_fin.isoformat() if a.fecha_fin else None,
                'className': [a.color_categoria],
                'extendedProps': {
                    'expediente_id': exp_id,
                    'prioridad': a.color_categoria,
                    'descripcion': a.descripcion or "",
                    'abogados': list(a.usuarios_asignados.values_list('id', flat=True))
                }
            })
        context['eventos_json'] = json.dumps(eventos)
        context['form'] = AudienciaForm()
        return context

class AudienciaActionView(View):
    def post(self, request, id=None):
        instancia = get_object_or_404(Audiencia, id=id) if id else None
        form = AudienciaForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

class AudienciaEliminarView(View):
    def post(self, request, id):
        get_object_or_404(Audiencia, id=id).delete()
        return JsonResponse({'status': 'ok'})