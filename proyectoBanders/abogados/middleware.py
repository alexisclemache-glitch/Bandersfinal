from django.shortcuts import redirect
from django.urls import reverse


class ProtegerMFAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            # Rutas que NO deben bloquearse para no causar error de redirección infinita
            exempt_urls = [
                reverse('abogados:verificar_mfa'),
                reverse('abogados:qr_code_image'),
                reverse('account_logout'),
            ]

            # Si el usuario NO ha verificado su 2FA en esta sesión
            if not request.session.get('mfa_verificado', False):
                if request.path not in exempt_urls and not request.path.startswith('/static/'):
                    return redirect('abogados:verificar_mfa')

        return self.get_response(request)