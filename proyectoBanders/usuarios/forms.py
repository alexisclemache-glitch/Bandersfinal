from django import forms
from allauth.account.forms import LoginForm, SignupForm
from django.utils.translation import gettext_lazy as _

# Definimos las opciones de roles
ROLES_CHOICES = [
    ('', _('Selecciona tu especialidad...')),
    ('abogado', _('Abogado')),
    ('psicologo', _('Psicólogo')),
    ('contador', _('Contador')),
    ('administrador', _('Administrador')),
    ('marketing', _('Marketing')),
]


class UsuarioRegistroForm(SignupForm):
    # 1. CAMPOS EXTRA (Se renderizan junto a email, password1 y password2)
    first_name = forms.CharField(
        max_length=30,
        label=_('Nombre'),
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre', 'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Apellido'),
        widget=forms.TextInput(attrs={'placeholder': 'Tu apellido', 'class': 'form-control'})
    )
    rol = forms.ChoiceField(
        choices=ROLES_CHOICES,
        label=_('Especialidad / Rol'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        # Llamamos al init del padre para cargar email, password1 y password2 automáticamente
        super(UsuarioRegistroForm, self).__init__(*args, **kwargs)

        # 2. PERSONALIZACIÓN DE ESTILOS (Para que coincida con el CSS de Banders)
        # Como usamos ACCOUNT_LOGIN_METHODS = {'email'}, el campo se llama 'email'
        if 'email' in self.fields:
            self.fields['email'].widget.attrs.update({
                'placeholder': 'correo@banders.com',
                'class': 'form-control'
            })
            self.fields['email'].label = _("Correo Electrónico")

        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'placeholder': 'Crea una contraseña',
                'class': 'form-control'
            })
            self.fields['password1'].label = _("Contraseña")

        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'placeholder': 'Repite tu contraseña',
                'class': 'form-control'
            })
            self.fields['password2'].label = _("Confirmar Contraseña")

    def save(self, request):
        # 3. GUARDADO SEGURO
        # Primero dejamos que Allauth cree el usuario (con email y pass)
        user = super(UsuarioRegistroForm, self).save(request)

        # Luego inyectamos nuestros campos personalizados al UsuarioCustom
        user.first_name = self.cleaned_data.get('first_name', '').strip()
        user.last_name = self.cleaned_data.get('last_name', '').strip()
        user.rol = self.cleaned_data.get('rol')

        # Guardamos definitivamente
        user.save()
        return user


class UsuarioLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(UsuarioLoginForm, self).__init__(*args, **kwargs)

        # Ajuste de estilos para el Login de Banders
        # Allauth usa 'login' como nombre de campo para el email/username
        if 'login' in self.fields:
            self.fields['login'].widget.attrs.update({
                'class': 'form-control py-2',
                'placeholder': 'Correo electrónico'
            })
            self.fields['login'].label = _("Correo Electrónico")

        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({
                'class': 'form-control py-2',
                'placeholder': 'Contraseña'
            })

        # Recordar sesión siempre activo pero oculto
        if 'remember' in self.fields:
            self.fields['remember'].initial = True
            self.fields['remember'].widget = forms.HiddenInput()