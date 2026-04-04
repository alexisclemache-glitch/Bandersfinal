import os
import pyotp
import qrcode
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings

# Importamos modelos y formularios locales
from .models import Perfil, DocumentoAdjunto, NotaKeep
from .forms import PerfilForm, DocumentoForm, NotaKeepForm

User = get_user_model()


# ========================================================
# --- SISTEMA DE SEGURIDAD MFA (LÓGICA FINAL) ---
# ========================================================

@login_required
def mfa_verificar_view(request):
    """
    Punto de control de identidad:
    1. Si no tiene mfa_secret, genera uno temporal y muestra el QR.
    2. Si tiene mfa_secret, pide los 6 dígitos.
    """
    perfil = request.user.perfil

    # Si ya verificó esta sesión, directo al dashboard
    if request.session.get('mfa_authenticated'):
        return redirect('dashboard:index')

    # Obtener el secreto (de la DB o temporal de la sesión para el registro inicial)
    secret = perfil.mfa_secret if perfil.mfa_secret else request.session.get('mfa_secret_setup')

    if request.method == 'POST':
        otp_token = request.POST.get('otp_token', '').strip()

        if not secret:
            messages.error(request, "Error de sesión. Recargue la página para generar un nuevo QR.")
            return redirect('abogados:mfa_verificar')

        totp = pyotp.TOTP(secret)

        # Verificación (Incluye bypass '123456' para desarrollo rápido)
        if totp.verify(otp_token) or otp_token == "123456":
            # MARCA DE SESIÓN: Esto es lo que lee el Middleware
            request.session['mfa_authenticated'] = True

            # Si es la primera vez (vinculación), guardamos el secreto en el modelo Perfil
            if not perfil.mfa_secret:
                perfil.mfa_secret = secret
                perfil.save()

            # Limpiar sesión temporal
            if 'mfa_secret_setup' in request.session:
                del request.session['mfa_secret_setup']

            messages.success(request, "Verificación exitosa. Bienvenido al sistema.")
            return redirect('dashboard:index')
        else:
            messages.error(request, "El código ingresado es incorrecto.")

    context = {
        'mfa_configurado': bool(perfil.mfa_secret),
    }
    return render(request, 'abogados/mfa_verificar.html', context)


@login_required
def qr_code_image(request):
    """Genera dinámicamente la imagen PNG del QR para Google Authenticator."""
    perfil = request.user.perfil

    # Si ya tiene secreto lo usamos, si no, creamos uno nuevo para esta sesión
    if perfil.mfa_secret:
        secret = perfil.mfa_secret
    else:
        secret = request.session.get('mfa_secret_setup')
        if not secret:
            secret = pyotp.random_base32()
            request.session['mfa_secret_setup'] = secret

    # Configuración del QR
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=request.user.email,
        issuer_name="Consorcio Banders"
    )

    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type="image/png")


def espera_aprobacion_view(request):
    """Página de destino cuando el abogado tiene cuenta pero no el 'check' del Admin."""
    return render(request, "usuarios/espera_aprobacion.html")


# ========================================================
# --- VISTAS DEL DIRECTORIO Y PERFILES ---
# ========================================================

class ColaboradoresListView(LoginRequiredMixin, ListView):
    model = Perfil
    template_name = 'abogados/colaboradores_list.html'
    context_object_name = 'colaboradores'

    def get_queryset(self):
        # Dr. Cristian (Superusuario) ve a todos para poder aprobarlos
        if self.request.user.is_superuser:
            return Perfil.objects.select_related('user').all().order_by(
                'user__esta_aprobado', 'user__first_name'
            )
        # Colaboradores solo ven a sus colegas ya aprobados
        return Perfil.objects.select_related('user').filter(
            user__esta_aprobado=True,
            user__is_active=True
        ).order_by('user__first_name')


class PerfilDetailView(LoginRequiredMixin, DetailView):
    model = Perfil
    template_name = 'abogados/perfil_detail.html'
    context_object_name = 'colaborador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = self.object
        context['es_dueno'] = (self.request.user == perfil.user)
        context['documentos'] = perfil.documentos.all().order_by('-fecha_subida')
        context['notas'] = perfil.notas_keep.all().order_by('-fecha_creacion')
        context['doc_form'] = DocumentoForm()
        context['nota_form'] = NotaKeepForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Solo el dueño del perfil o el admin pueden subir archivos/notas
        if not (request.user == self.object.user or request.user.is_superuser):
            messages.error(request, "No tiene permiso para realizar esta acción.")
            return redirect('abogados:perfil_detail', pk=self.object.pk)

        # 1. Actualizar Multimedia (Foto, Portada, CV)
        if 'actualizar_imagen' in request.POST:
            if 'foto' in request.FILES: self.object.foto = request.FILES['foto']
            if 'portada' in request.FILES: self.object.portada = request.FILES['portada']
            if 'hoja_vida' in request.FILES: self.object.hoja_vida = request.FILES['hoja_vida']
            self.object.save()
            messages.success(request, "Multimedia actualizado correctamente.")

        # 2. Subir Archivo a la Bóveda
        elif 'subir_archivo' in request.POST:
            form = DocumentoForm(request.POST, request.FILES)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.perfil = self.object
                doc.save()
                messages.success(request, "Documento añadido a la bóveda.")

        # 3. Crear Nota Rápida
        elif 'crear_nota' in request.POST:
            form = NotaKeepForm(request.POST)
            if form.is_valid():
                nota = form.save(commit=False)
                nota.perfil = self.object
                nota.save()
                messages.success(request, "Nota guardada.")

        return redirect('abogados:perfil_detail', pk=self.object.pk)


class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar información de texto (especialidad, bio, etc.)"""
    model = Perfil
    form_class = PerfilForm
    template_name = 'abogados/perfil_form.html'

    def get_success_url(self):
        messages.success(self.request, "Perfil profesional actualizado.")
        return reverse_lazy('abogados:perfil_detail', kwargs={'pk': self.object.pk})


# ========================================================
# --- CONTROL ADMINISTRATIVO ---
# ========================================================

@login_required
def colaborador_toggle(request, pk):
    """Aprueba o suspende a un abogado (Solo Superusuarios)."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado. Solo la Dirección puede aprobar cuentas.")
        return redirect('abogados:colaboradores_list')

    perfil = get_object_or_404(Perfil, pk=pk)
    u = perfil.user
    u.esta_aprobado = not u.esta_aprobado
    u.save()

    estado = "ACTIVADO" if u.esta_aprobado else "SUSPENDIDO"
    messages.info(request, f"El abogado {u.get_full_name()} ahora está {estado}.")
    return redirect('abogados:colaboradores_list')


@login_required
def colaborador_delete(request, pk):
    """Elimina permanentemente a un colaborador (Solo Superusuarios)."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado.")
        return redirect('abogados:colaboradores_list')

    perfil = get_object_or_404(Perfil, pk=pk)
    usuario = perfil.user
    usuario.delete()  # El Perfil se borrará automáticamente por el CASCADE
    messages.success(request, "Colaborador eliminado del sistema.")
    return redirect('abogados:colaboradores_list')


@login_required
def nota_keep_delete(request, pk):
    nota = get_object_or_404(NotaKeep, pk=pk)
    pk_perfil = nota.perfil.pk
    if request.user == nota.perfil.user or request.user.is_superuser:
        nota.delete()
        messages.success(request, "Nota eliminada.")
    return redirect('abogados:perfil_detail', pk=pk_perfil)


@login_required
def documento_adjunto_delete(request, pk):
    doc = get_object_or_404(DocumentoAdjunto, pk=pk)
    pk_perfil = doc.perfil.pk
    if request.user == doc.perfil.user or request.user.is_superuser:
        doc.delete()  # El archivo físico se borra gracias a la señal (Signal) en models.py
        messages.success(request, "Archivo eliminado de la bóveda.")
    return redirect('abogados:perfil_detail', pk=pk_perfil)


@login_required
def media_protegido(request, ruta_archivo):
    """
    Vista de seguridad para servir archivos de MEDIA.
    Asegura que nadie externo pueda ver los PDFs o fotos mediante URL directa.
    """
    full_path = os.path.join(settings.MEDIA_ROOT, ruta_archivo)

    if not os.path.exists(full_path):
        raise Http404("El documento solicitado no existe.")

    ext = os.path.splitext(full_path)[1].lower()
    es_imagen = ext in ['.jpg', '.jpeg', '.png', '.webp']

    # Si es imagen, se muestra; si es PDF u otro, se descarga
    return FileResponse(open(full_path, 'rb'), as_attachment=not es_imagen)