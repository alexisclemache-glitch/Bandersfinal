from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from allauth.account.views import LoginView, SignupView
from .forms import UsuarioRegistroForm, UsuarioLoginForm


class LoginUsuarioView(LoginView):
    form_class = UsuarioLoginForm
    template_name = 'account/login.html'

    def get_success_url(self):
        # Redirige al Dashboard. Si tiene MFA, Allauth pedirá el código antes.
        return reverse_lazy('dashboard:dashboard')


class RegistroUsuarioView(SignupView):
    form_class = UsuarioRegistroForm
    template_name = 'account/signup.html'

    def form_valid(self, form):
        # 1. Guardamos el usuario (Esto dispara tu SIGNAL en models.py)
        user = form.save(self.request)

        # 2. BLOQUEO MANUAL: Lo ponemos inactivo para que esperes el "Check" en el directorio
        user.is_active = False
        user.save()

        # 3. Mensaje para el abogado
        messages.info(
            self.request,
            "Tu perfil ha sido creado. Un administrador de Banders revisará tus datos para activar tu acceso."
        )
        return redirect('account_login')