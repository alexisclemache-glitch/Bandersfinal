from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch


class ProtegerMFAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. PASO LIBRE: No logueados, Admin, Static, Media y Debug
        # El Dr. Cristian (superuser) también pasa directo para evitar bloqueos accidentales
        if not request.user.is_authenticated or \
                request.user.is_superuser or \
                request.path.startswith('/admin/') or \
                request.path.startswith('/static/') or \
                request.path.startswith('/media/') or \
                request.path.startswith('/__debug__/'):
            return self.get_response(request)

        # 2. DEFINICIÓN DE RUTAS DE ESCAPE
        # Estas rutas SIEMPRE deben estar accesibles para que el usuario no se atrape
        try:
            rutas_permitidas = [
                reverse('abogados:mfa_verificar'),  # Pantalla de 6 dígitos / QR
                reverse('abogados:qr_code_image'),  # La imagen del QR
                reverse('abogados:espera_aprobacion'),  # Pantalla de "Esperando al Admin"
                reverse('account_logout'),  # Para poder cerrar sesión
            ]
        except NoReverseMatch:
            rutas_permitidas = []

        # Si el usuario ya está en una de estas rutas, lo dejamos seguir
        if request.path in rutas_permitidas:
            return self.get_response(request)

        # 3. LÓGICA DE VALIDACIÓN DE MFA
        # Obtenemos el perfil de forma segura
        perfil = getattr(request.user, 'perfil', None)

        # Si por alguna razón el usuario no tiene perfil (error de creación),
        # lo dejamos pasar o podrías manejar el error aquí.
        if not perfil:
            return self.get_response(request)

        # Verificamos si la sesión actual ya pasó el "check" del código de 6 dígitos
        mfa_completado_en_sesion = request.session.get('mfa_authenticated', False)

        # SI NO HA COMPLETADO EL MFA EN ESTA SESIÓN:
        # (No importa si tiene mfa_secret en DB o no, la vista mfa_verificar decide si muestra QR o solo Input)
        if not mfa_completado_en_sesion:
            return redirect('abogados:mfa_verificar')

        # 4. LÓGICA DE APROBACIÓN (DOBLE CANDADO)
        # Si ya pasó el MFA pero el Admin aún no le da el "check" (esta_aprobado=False)
        if not getattr(request.user, 'esta_aprobado', False):
            return redirect('abogados:espera_aprobacion')

        return self.get_response(request)