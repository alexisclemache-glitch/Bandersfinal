from django.shortcuts import redirect
from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages

class AprobacionAdminAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        """
        Determina a dónde va el usuario tras loguearse y pasar el MFA.
        """
        user = request.user

        # 1. ACCESO TOTAL: Superusuario (Dr. Cristian)
        if user.is_superuser:
            return reverse('dashboard:index')

        # 2. VERIFICACIÓN DE APROBACIÓN:
        # NO usamos logout(request) aquí para que el usuario pueda ver
        # la página de "Espera de aprobación" estando logueado.
        if not getattr(user, 'esta_aprobado', False):
            # Redirigimos a la vista que definimos en la app 'abogados'
            return reverse('abogados:espera_aprobacion')

        # 3. COLABORADORES APROBADOS
        return reverse('dashboard:index')

    def is_open_for_signup(self, request):
        """
        Permite o bloquea registros nuevos.
        """
        return True