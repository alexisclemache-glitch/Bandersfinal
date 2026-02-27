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
    first_name = forms.CharField(
        max_length=30,
        label=_('Nombre'),
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Apellido'),
        widget=forms.TextInput(attrs={'placeholder': 'Tu apellido'})
    )
    # Nuevo campo de Rol
    rol = forms.ChoiceField(
        choices=ROLES_CHOICES,
        label=_('Especialidad / Rol'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    def save(self, request):
        # Allauth crea el usuario base
        user = super(UsuarioRegistroForm, self).save(request)

        # Guardamos los campos extra en el modelo UsuarioCustom
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.rol = self.cleaned_data['rol']  # Asegúrate de tener este campo en tu modelo
        user.save()
        return user


class UsuarioLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(UsuarioLoginForm, self).__init__(*args, **kwargs)

        # Estilos para Allauth v6
        if 'login' in self.fields:
            self.fields['login'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
            })

        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Contraseña'
            })

        # Forzamos el "Recuérdame" para que la sesión de 30 días sea efectiva
        if 'remember' in self.fields:
            self.fields['remember'].initial = True
            self.fields['remember'].widget = forms.HiddenInput()