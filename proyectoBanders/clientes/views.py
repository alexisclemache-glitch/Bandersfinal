from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Importación de modelos
from .models import Cliente, DocumentoCliente
from proyectoBanders.expedientes.models import Expediente, NotaExpediente, DocumentoExpediente

# --- VISTAS DE CLIENTE ---

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'clientes'

    def get_queryset(self):
        return Cliente.objects.all().order_by('-fecha_registro')

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    fields = ['nombre', 'apellido', 'rut', 'email', 'telefono', 'foto',
              'estado_civil', 'provincia', 'canton', 'direccion', 'estado_operativo']
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:list')

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, "✅ Cliente registrado con éxito.")
        return super().form_valid(form)

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expedientes'] = self.object.expedientes_juridicos.all().prefetch_related(
            'notas_seguimiento', 'archivos_expediente'
        ).order_by('-fecha_inicio')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'btn_nota_expediente' in request.POST:
            expediente_id = request.POST.get('expediente_id')
            contenido = request.POST.get('contenido')
            expediente = get_object_or_404(Expediente, id=expediente_id, cliente=self.object)
            if contenido:
                NotaExpediente.objects.create(expediente=expediente, contenido=contenido, autor=request.user)
                messages.success(request, "✅ Seguimiento guardado.")
        return redirect('clientes:detail', pk=self.object.pk)

class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    fields = ['nombre', 'apellido', 'rut', 'email', 'telefono', 'foto',
              'estado_civil', 'provincia', 'canton', 'direccion', 'estado_operativo']
    template_name = 'clientes/cliente_form.html'

    def get_success_url(self):
        return reverse_lazy('clientes:detail', kwargs={'pk': self.object.pk})

class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    success_url = reverse_lazy('clientes:list')

# --- VISTAS DE EXPEDIENTES ---

class ExpedienteCreateView(LoginRequiredMixin, CreateView):
    model = Expediente
    fields = ['titulo', 'numero_proceso', 'tipo_expediente', 'estado', 'provincia_judicial', 'juzgado_unidad', 'descripcion']
    template_name = 'expedientes/expediente_form.html'

    def form_valid(self, form):
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            form.instance.cliente = get_object_or_404(Cliente, id=cliente_id)
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clientes:detail', kwargs={'pk': self.object.cliente.pk})

# --- GESTIÓN DE DOCUMENTOS (FUNCIONES) ---

@login_required
def upload_document(request, pk):
    """Sube archivos a la bóveda personal del cliente (DocumentoCliente)"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        nombre_form = request.POST.get('nombre')
        categoria_form = request.POST.get('categoria', 'otros')
        descripcion_form = request.POST.get('descripcion', '')

        if archivo:
            DocumentoCliente.objects.create(
                cliente=cliente,
                archivo=archivo,
                titulo=nombre_form,      # Usamos 'titulo' según tu modelo
                categoria=categoria_form,
                descripcion=descripcion_form
            )
            messages.success(request, "📁 Documento guardado en la bóveda.")
    return redirect('clientes:detail', pk=pk)

@login_required
def upload_expediente_document(request, expediente_id):
    """Sube archivos a un expediente específico (DocumentoExpediente)"""
    expediente = get_object_or_404(Expediente, pk=expediente_id)
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        nombre = request.POST.get('nombre')
        if archivo:
            DocumentoExpediente.objects.create(expediente=expediente, archivo=archivo, nombre=nombre)
            messages.success(request, "📄 Escrito adjuntado al expediente.")
    return redirect('clientes:detail', pk=expediente.cliente.pk)

@login_required
def delete_document(request, pk):
    doc = get_object_or_404(DocumentoCliente, pk=pk)
    cliente_id = doc.cliente.id
    doc.delete()
    return redirect('clientes:detail', pk=cliente_id)

@login_required
def delete_escrito(request, pk):
    doc = get_object_or_404(DocumentoExpediente, pk=pk)
    cliente_id = doc.expediente.cliente.id
    doc.delete()
    return redirect('clientes:detail', pk=cliente_id)


@login_required
def toggle_cliente_status(request, pk):
    """Cambia el estado de activo a inactivo y viceversa"""
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.esta_activo = not cliente.esta_activo
    cliente.save()

    estado = "Activado" if cliente.esta_activo else "Desactivado"
    messages.info(request, f"Cliente {cliente.nombre} ha sido {estado}.")

    return redirect('clientes:list')