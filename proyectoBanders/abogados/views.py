from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import Http404, HttpResponse
from decimal import Decimal

# Librerías para MFA (Google Authenticator)
import pyotp
import qrcode
from io import BytesIO

# Importación de modelos y formularios locales
from .models import Perfil, DocumentoAdjunto, NotaKeep
from .forms import PerfilForm, NotaKeepForm, DocumentoForm

# Importación de modelos externos
from proyectoBanders.expedientes.models import Expediente
from proyectoBanders.pagos.models import Pago, Abono
from proyectoBanders.clientes.models import Cliente


# ==============================================================================
# VISTAS DE SEGURIDAD MFA (GOOGLE AUTHENTICATOR)
# ==============================================================================

@login_required
def qr_code_image(request):
    """Genera dinámicamente la imagen PNG del código QR para el perfil"""
    perfil = request.user.perfil
    uri = perfil.get_totp_uri()

    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type="image/png")


@login_required
def verificar_mfa(request):
    """Pantalla de validación del código de 6 dígitos"""
    perfil = request.user.perfil

    if request.method == "POST":
        codigo = request.POST.get("otp_token")
        totp = pyotp.totp.TOTP(perfil.otp_secret)

        if totp.verify(codigo):
            request.session['mfa_verificado'] = True
            if not perfil.mfa_configurado:
                perfil.mfa_configurado = True
                perfil.save()

            messages.success(request, "¡Acceso concedido! Bienvenido al sistema.")
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Código incorrecto. Verifique su aplicación.")

    return render(request, "abogados/mfa_verificar.html", {
        "mfa_configurado": perfil.mfa_configurado
    })


# ==============================================================================
# VISTAS DE GESTIÓN DE COLABORADORES (DIRECTORIO Y PERFIL)
# ==============================================================================

class ColaboradoresListView(LoginRequiredMixin, ListView):
    model = Perfil
    template_name = 'abogados/colaboradores_list.html'
    context_object_name = 'colaboradores'

    def get_queryset(self):
        return Perfil.objects.select_related('user').all()


class PerfilDetailView(LoginRequiredMixin, DetailView):
    model = Perfil
    template_name = 'abogados/perfil_detail.html'
    context_object_name = 'colaborador'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        try:
            return get_object_or_404(Perfil, pk=pk)
        except Http404:
            perfil, created = Perfil.objects.get_or_create(user=self.request.user)
            return perfil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil_visitado = self.object
        user_asociado = perfil_visitado.user

        # 1. QUERYSET DE EXPEDIENTES (Filtro de seguridad)
        # Solo expedientes vinculados directamente al abogado o a sus clientes creados
        exp_qs = Expediente.objects.filter(
            Q(creado_por=user_asociado) | Q(cliente__creado_por=user_asociado)
        ).distinct()

        # 2. MÉTRICAS CUANTITATIVAS (Exactitud de Clientes y Casos)
        context['total_clientes'] = Cliente.objects.filter(creado_por=user_asociado).count()
        context['casos_activos'] = exp_qs.count()

        # 3. FINANZAS OPTIMIZADAS (Uso de Aggregate para rendimiento)
        # Calculamos recaudado y total pactado en consultas separadas pero directas
        recaudado_data = Abono.objects.filter(
            pago_asociado__expediente__in=exp_qs
        ).aggregate(total=Sum('monto'))

        total_pactado_data = Pago.objects.filter(
            expediente__in=exp_qs
        ).aggregate(total=Sum('total_deuda'))

        total_recaudado = recaudado_data['total'] or Decimal('0.00')
        total_pactado = total_pactado_data['total'] or Decimal('0.00')

        # 4. PASO DE DATOS AL CONTEXTO (Sincronizado con Tarjeta Banders Infinite)
        context['total_recaudado'] = total_recaudado
        context['total_por_cobrar'] = max(total_pactado - total_recaudado, Decimal('0.00'))

        # Datos de UI y Formularios
        context['es_dueno'] = (self.request.user == user_asociado)
        context['doc_form'] = DocumentoForm()
        context['nota_form'] = NotaKeepForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Seguridad: Solo el dueño puede editar su propia "Bóveda" o "Notas"
        if self.request.user != self.object.user:
            messages.error(request, "Acceso denegado. No puede modificar este perfil.")
            return redirect('abogados:perfil_detail', pk=self.object.pk)

        # Acción: Subir Documento a la Bóveda
        if 'subir_archivo' in request.POST:
            form = DocumentoForm(request.POST, request.FILES)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.perfil = self.object
                doc.save()
                messages.success(request, "Documento guardado en su bOveda.")

        # Acción: Crear Nota Personal (Keep)
        elif 'crear_nota' in request.POST:
            form = NotaKeepForm(request.POST)
            if form.is_valid():
                nota = form.save(commit=False)
                nota.perfil = self.object
                nota.save()
                messages.success(request, "Nota personal guardada.")

        # Acción: Eliminar Documento
        elif 'eliminar_archivo' in request.POST:
            doc_id = request.POST.get('doc_id')
            get_object_or_404(DocumentoAdjunto, id=doc_id, perfil=self.object).delete()
            messages.warning(request, "Documento eliminado.")

        # Acción: Eliminar Nota
        elif 'eliminar_nota' in request.POST:
            nota_id = request.POST.get('nota_id')
            get_object_or_404(NotaKeep, id=nota_id, perfil=self.object).delete()
            messages.warning(request, "Nota eliminada.")

        return redirect('abogados:perfil_detail', pk=self.object.pk)


# ==============================================================================
# ACCIONES ADMINISTRATIVAS Y EDICIÓN
# ==============================================================================

@user_passes_test(lambda u: u.is_superuser)
def colaborador_toggle_active(request, pk):
    perfil = get_object_or_404(Perfil, pk=pk)
    user_to_toggle = perfil.user

    if user_to_toggle == request.user:
        messages.error(request, "No puedes desactivar tu propia cuenta.")
    else:
        user_to_toggle.is_active = not user_to_toggle.is_active
        user_to_toggle.save()
        status = "activado" if user_to_toggle.is_active else "desactivado"
        messages.info(request, f"Usuario {user_to_toggle.email} {status}.")

    return redirect('abogados:colaboradores_list')


@user_passes_test(lambda u: u.is_superuser)
def colaborador_delete(request, pk):
    perfil = get_object_or_404(Perfil, pk=pk)
    perfil.user.delete()
    messages.success(request, "Colaborador eliminado permanentemente.")
    return redirect('abogados:colaboradores_list')


class AbogadoUpdateView(LoginRequiredMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = 'abogados/abogado_form.html'

    def get_object(self, queryset=None):
        # Asegura que el usuario edite su propio perfil
        perfil, created = Perfil.objects.get_or_create(user=self.request.user)
        return perfil

    def get_success_url(self):
        return reverse_lazy('abogados:perfil_detail', kwargs={'pk': self.object.pk})