import os
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from allauth.account.views import LoginView, SignupView

# --- IMPORTACIONES DE MODELOS Y FORMULARIOS ---
try:
    from proyectoBanders.abogados.models import Perfil
except ImportError:
    from abogados.models import Perfil

from .forms import UsuarioRegistroForm, UsuarioLoginForm


# ==========================================
# 1. AUTENTICACIÓN: LOGIN Y REGISTRO
# ==========================================

class LoginUsuarioView(LoginView):
    """Vista de acceso personalizada para Banders."""
    form_class = UsuarioLoginForm
    template_name = 'account/login.html'

    def get_success_url(self):
        # El middleware ProtegerMFAMiddleware interceptará esto si no está aprobado
        return reverse_lazy('dashboard:dashboard')


class RegistroUsuarioView(SignupView):
    """Registro de profesionales con bloqueo preventivo de seguridad."""
    form_class = UsuarioRegistroForm
    template_name = 'account/signup.html'

    def form_valid(self, form):
        # Allauth realiza el guardado inicial (crea el usuario y hashes)
        response = super().form_valid(form)

        # Obtenemos al usuario recién creado
        user = self.user

        # Forzamos el estado de 'no aprobado' para la revisión de Dirección Jurídica
        user.esta_aprobado = False
        # Mantenemos is_active=True para que pueda loguearse y ver la pantalla de 'Espera'
        user.is_active = True
        user.save()

        messages.success(
            self.request,
            "Registro enviado con éxito. Su cuenta está en proceso de validación por la Dirección Jurídica."
        )
        # Redirigimos explícitamente al login para que el mensaje de éxito sea visible
        return redirect('account_login')


# ==========================================
# 2. SEGURIDAD DE ARCHIVOS (PROTECCIÓN VPS)
# ==========================================

@login_required
def servir_archivo_protegido(request, ruta_archivo):
    """
    Sirve documentos sensibles (PDFs, Poderes, Contratos) validando aprobación.
    """
    # 1. Validación de Jerarquía
    es_admin = request.user.is_superuser
    esta_aprobado = getattr(request.user, 'esta_aprobado', False)

    if not es_admin and not esta_aprobado:
        return HttpResponseForbidden("Acceso denegado: Su perfil no cuenta con aprobación jerárquica activa.")

    # 2. Seguridad de Ruta (evita Directory Traversal)
    ruta_archivo = os.path.normpath(ruta_archivo).lstrip('/')
    ruta_completa = os.path.join(settings.MEDIA_ROOT, ruta_archivo)

    # 3. Verificación de existencia física en el VPS
    if not os.path.exists(ruta_completa) or os.path.isdir(ruta_completa):
        raise Http404("El documento solicitado no se encuentra en el servidor.")

    # 4. Entrega segura del archivo
    return FileResponse(open(ruta_completa, 'rb'), content_type='application/pdf')


# ==========================================
# 3. PANTALLA DE BLOQUEO Y PERFIL PROFESIONAL
# ==========================================

def espera_aprobacion(request):
    """Vista de aterrizaje para usuarios registrados no validados."""
    if request.user.is_authenticated:
        # Si el usuario ya fue aprobado mientras tenía la sesión abierta, lo liberamos
        if request.user.is_superuser or getattr(request.user, 'esta_aprobado', False):
            return redirect('dashboard:dashboard')

    return render(request, 'usuarios/espera_aprobacion.html', {
        'contacto_admin': 'soporte@consorciobanders.com',
        'titulo': 'Validación de Credenciales | Banders'
    })


@login_required
def mi_perfil_view(request):
    """Redirección dinámica al detalle del perfil del abogado."""
    if request.user.is_superuser:
        messages.info(request, "Los administradores gestionan perfiles desde el panel de control.")
        return redirect('dashboard:dashboard')

    try:
        # Buscamos el perfil en la app abogados vinculado al User actual
        perfil = Perfil.objects.get(user=request.user)
        return redirect('abogados:perfil_detail', pk=perfil.pk)
    except Perfil.DoesNotExist:
        messages.warning(request, "Su ficha profesional está siendo generada por el sistema.")
        return redirect('dashboard:dashboard')