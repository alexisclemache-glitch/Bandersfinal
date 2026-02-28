from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q
from proyectoBanders.expedientes.models import Expediente
from proyectoBanders.pagos.models import Pago

def realizar_busqueda(request):
    query = request.GET.get('q', '').strip()

    # 1. SI ES UN TXN: Redirección directa a la lista de pagos para abrir la Tarjeta Visa
    if query.upper().startswith('TXN-'):
        pago_existe = Pago.objects.filter(transaccion_id__icontains=query).first()
        if pago_existe:
            return redirect(f"{reverse('pagos:lista_pagos')}?q={pago_existe.transaccion_id}")

    resultados_expedientes = []
    resultados_pagos = []

    if query:
        # 2. BÚSQUEDA EN EXPEDIENTES (Usamos 'rut' que es tu campo de cédula)
        resultados_expedientes = Expediente.objects.filter(
            Q(titulo__icontains=query) |
            Q(numero_proceso__icontains=query) |
            Q(cliente__nombre__icontains=query) |
            Q(cliente__apellido__icontains=query) |
            Q(cliente__rut__icontains=query)  # <-- Cambiado de 'cedula' a 'rut'
        ).select_related('cliente').distinct()

        # 3. BÚSQUEDA EN PAGOS (Usamos 'rut' para vincular con la deuda)
        resultados_pagos = Pago.objects.filter(
            Q(transaccion_id__icontains=query) |
            Q(expediente__cliente__nombre__icontains=query) |
            Q(expediente__cliente__apellido__icontains=query) |
            Q(expediente__cliente__rut__icontains=query)  # <-- Cambiado de 'cedula' a 'rut'
        ).select_related('expediente__cliente').distinct()

        # --- LÓGICA DE REDIRECCIÓN AUTOMÁTICA ---

        # Si la búsqueda por cédula (o nombre) arroja exactamente UN PAGO y ningún expediente suelto
        if resultados_pagos.count() == 1 and resultados_expedientes.count() == 0:
            return redirect(f"{reverse('pagos:lista_pagos')}?q={resultados_pagos.first().transaccion_id}")

        # Si solo se encuentra un expediente (y el cliente no tiene pagos registrados aún)
        if resultados_expedientes.count() == 1 and resultados_pagos.count() == 0:
            return redirect('clientes:detail', pk=resultados_expedientes.first().cliente.pk)

    total_global = (resultados_expedientes.count() if resultados_expedientes else 0) + \
                   (resultados_pagos.count() if resultados_pagos else 0)

    return render(request, 'busqueda/resultados.html', {
        'query': query,
        'resultados_expedientes': resultados_expedientes,
        'resultados_pagos': resultados_pagos,
        'total_global': total_global
    })