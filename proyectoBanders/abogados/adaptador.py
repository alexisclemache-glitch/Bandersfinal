from django.shortcuts import redirect
from django.contrib.auth import logout
from django.apps import apps
from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse


class PerfilAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        """
        Se ejecuta tras validar la contraseña y el código MFA.
        """
        user = request.user

        try:
            # Referencia correcta al modelo Perfil
            PerfilModel = apps.get_model('abogados', 'Perfil')

            # Buscamos el perfil o lo creamos si no existe
            perfil, created = PerfilModel.objects.get_or_create(user=user)

            # LÓGICA DE BLOQUEO:
            # Si NO es superusuario y NO está aprobado por ti...
            if not user.is_superuser and not perfil.esta_aprobado:
                # 1. Cerramos la sesión para invalidar el acceso al dashboard
                logout(request)

                # 2. Redirigimos a la página de aviso (GET limpio)
                # Usamos el name 'abogados:espera_aprobacion'
                raise ImmediateHttpResponse(redirect('abogados:espera_aprobacion'))

            # Si es Dr. Cristian o un abogado ya aprobado:
            print(f"✅ Acceso concedido al perfil: {user.email}")
            return "/dashboard/"

        except Exception as e:
            print(f"⚠️ Error en el adaptador de perfil: {e}")
            logout(request)
            return "/accounts/login/"