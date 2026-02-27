from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Pago, Abono, CONCEPTO_CHOICES, METODOS_PAGO_CHOICES
from expedientes.models import Expediente
from django.db.models import Q
from decimal import Decimal
from django.core.exceptions import ValidationError
import uuid, urllib.parse


# --- LISTADO DE PAGOS ---
def lista_pagos(request):
    query = request.GET.get('q', '').strip()
    # Usamos order_by para que los últimos aparezcan primero
    pagos = Pago.objects.select_related('expediente__cliente').all().order_by('-id')
    expedientes = Expediente.objects.all()

    if query:
        pagos = pagos.filter(
            Q(transaccion_id__icontains=query) |
            Q(expediente__cliente__nombre__icontains=query) |
            Q(expediente__cliente__apellido__icontains=query)
        )

    return render(request, 'pagos/transactions.html', {
        'pagos': pagos,
        'expedientes': expedientes,
        'busqueda': query,
        'conceptos': CONCEPTO_CHOICES,
        'metodos': METODOS_PAGO_CHOICES
    })


# --- CREAR NUEVA OBLIGACIÓN ---
def crear_nuevo_pago(request):
    if request.method == 'POST':
        try:
            exp_id = request.POST.get('expediente')
            monto = request.POST.get('monto_total')
            pago = Pago.objects.create(
                expediente_id=exp_id,
                total_deuda=Decimal(monto),
                transaccion_id=f"TXN-{uuid.uuid4().hex[:8].upper()}"
            )
            messages.success(request, "Transacción creada con éxito.")
        except Exception as e:
            messages.error(request, f"Error al crear transacción: {e}")
    return redirect('pagos:lista_pagos')


# --- REGISTRAR ABONO (UNIFICADO Y CORREGIDO) ---
def registrar_abono(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)

    if request.method == 'POST':
        try:
            monto_abono = request.POST.get('monto')
            # Capturamos el método de pago del select del formulario
            metodo = request.POST.get('metodo_pago') or 'efectivo'

            if monto_abono and Decimal(monto_abono) > 0:
                # Creamos el abono registrando al usuario logueado
                Abono.objects.create(
                    pago_asociado=pago,
                    monto=Decimal(monto_abono),
                    metodo_pago=metodo,
                    usuario_creador=request.user  # <--- Registra quién lo hizo
                )
                messages.success(request, f"¡Éxito! Abono de ${monto_abono} registrado correctamente.")
            else:
                messages.warning(request, "Debe ingresar un monto válido mayor a 0.")

        except ValidationError as e:
            # Esto captura si el monto excede el saldo pendiente (si tienes la lógica en el model)
            messages.error(request, f"Error de validación: {e.messages[0]}")
        except Exception as e:
            messages.error(request, f"Error inesperado: {e}")

    return redirect('pagos:lista_pagos')


# --- DETALLE JSON PARA MODALES ---
def detalle_pago_json(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    cliente = pago.expediente.cliente

    # Incluimos el nombre del usuario que registró cada abono en el JSON
    abonos = [{
        'id': a.id,
        'monto': float(a.monto),
        'fecha': a.fecha_abono.strftime('%d/%m/%Y'),
        'metodo': a.get_metodo_pago_display(),
        'usuario': a.usuario_creador.get_full_name() or a.usuario_creador.username if a.usuario_creador else "N/A"
    } for a in pago.abonos.all().order_by('-fecha_abono')]

    msg = f"Estimado {cliente.nombre}, su saldo pendiente en Banders es ${pago.saldo_pendiente:,.2f}"

    return JsonResponse({
        'id': pago.id,
        'nombre': f"{cliente.nombre} {cliente.apellido}",
        'telefono': cliente.telefono,
        'saldo': float(pago.saldo_pendiente),
        'txn': pago.transaccion_id,
        'abonos': abonos,
        'ws_link': f"https://api.whatsapp.com/send?phone={cliente.telefono}&text={urllib.parse.quote(msg)}"
    })


# --- ELIMINACIÓN Y EXPORTACIÓN ---
def eliminar_abono(request, abono_id):
    abono = get_object_or_404(Abono, id=abono_id)
    abono.delete()
    messages.info(request, "Abono eliminado.")
    return redirect('pagos:lista_pagos')


def eliminar_transaccion(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pago.delete()
    messages.info(request, "Transacción eliminada.")
    return redirect('pagos:lista_pagos')


def exportar_pago_pdf(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    return render(request, 'pagos/pages-invoice.html', {'pago': pago})