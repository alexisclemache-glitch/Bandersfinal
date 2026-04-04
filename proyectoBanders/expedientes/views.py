from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Expediente, NotaExpediente, DocumentoExpediente
from .forms import ExpedienteForm


@login_required
def lista_expedientes(request):
    abrir_modal = False
    if request.method == 'POST':
        # Manejo de Notas Rápidas
        if 'btn_nota_rapida' in request.POST:
            exp_id = request.POST.get('expediente_id')
            contenido = request.POST.get('contenido')
            if exp_id and contenido:
                NotaExpediente.objects.create(
                    expediente_id=exp_id,
                    contenido=contenido,
                    autor=request.user
                )
                messages.success(request, "✅ Nota registrada.")
            return redirect('expedientes:lista_expedientes')

        # Manejo de Nuevo Expediente
        form = ExpedienteForm(request.POST)
        if form.is_valid():
            nuevo = form.save(commit=False)
            nuevo.creado_por = request.user
            nuevo.save()
            messages.success(request, "✅ Expediente creado con éxito.")
            return redirect('expedientes:lista_expedientes')
        else:
            abrir_modal = True
    else:
        form = ExpedienteForm()

    expedientes = Expediente.objects.select_related('cliente').prefetch_related(
        'notas_seguimiento', 'archivos_expediente'
    ).all().order_by('-id')

    return render(request, 'expedientes/expediente_form.html', {
        'expedientes': expedientes,
        'form': form,
        'abrir_modal': abrir_modal
    })


@login_required
def actualizar_estado_expediente(request, pk):
    """
    Cambia el estado de ABIERTO a CERRADO y viceversa.
    Optimizado para responder a la petición AJAX del Calendario.
    """
    expediente = get_object_or_404(Expediente, pk=pk)

    # Normalizamos el string para evitar errores de mayúsculas/minúsculas
    estado_actual = expediente.estado.upper() if expediente.estado else "ABIERTO"

    if estado_actual == 'ABIERTO':
        expediente.estado = 'CERRADO'
        color = 'bg-danger'
        label = 'CERRADO'
    else:
        expediente.estado = 'ABIERTO'
        color = 'bg-success'
        label = 'ABIERTO'

    expediente.save()

    # Respuesta para el AJAX del calendario o botones dinámicos
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({
            'status': 'ok',
            'nuevo_estado': label,
            'nuevo_color': color
        })

    # Respuesta para clicks normales en la lista de expedientes
    messages.info(request, f"El expediente {expediente.titulo} ahora está {label}.")
    return redirect('expedientes:lista_expedientes')


@login_required
def eliminar_expediente(request, pk):
    expediente = get_object_or_404(Expediente, pk=pk)
    if request.method == 'POST':
        expediente.delete()
        messages.warning(request, "Expediente eliminado.")
    return redirect('expedientes:lista_expedientes')


@login_required
def upload_expediente_document(request, expediente_id):
    expediente = get_object_or_404(Expediente, pk=expediente_id)
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        nombre = request.POST.get('nombre')
        if archivo and nombre:
            DocumentoExpediente.objects.create(
                expediente=expediente,
                archivo=archivo,
                nombre=nombre
            )
            messages.success(request, f"📄 Documento '{nombre}' subido correctamente.")
        else:
            messages.error(request, "❌ Error: Debe indicar un nombre y seleccionar un archivo.")
    return redirect('expedientes:lista_expedientes')