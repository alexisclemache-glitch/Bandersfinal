from django import forms
from .models import Cliente, Expediente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # MODIFICADO: Se agregan 'direccion' y 'estado_operativo'
        fields = [
            'nombre', 'apellido', 'rut', 'email', 'telefono',
            'foto', 'esta_activo', 'estado_civil',
            'provincia', 'canton', 'direccion', 'estado_operativo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control rounded-3 bg-light border-0 px-3'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control rounded-3 bg-light border-0 px-3'}),
            'rut': forms.TextInput(
                attrs={'class': 'form-control rounded-3 bg-light border-0 px-3', 'placeholder': 'Ej: 172345678-9'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-3 bg-light border-0 px-3'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control rounded-3 bg-light border-0 px-3'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select rounded-3 bg-light border-0 px-3'}),
            'provincia': forms.Select(attrs={'class': 'form-select rounded-3 bg-light border-0 px-3'}),
            'canton': forms.TextInput(attrs={'class': 'form-control rounded-3 bg-light border-0 px-3'}),

            # NUEVO: Widget para Dirección (Textarea para que sea más cómodo escribir)
            'direccion': forms.Textarea(attrs={
                'class': 'form-control rounded-3 bg-light border-0 px-3',
                'rows': 2,
                'placeholder': 'Ingrese la dirección domiciliaria completa...'
            }),
            # NUEVO: Widget para Estado Operativo
            'estado_operativo': forms.Select(attrs={'class': 'form-select rounded-3 bg-light border-0 px-3'}),
        }


class ExpedienteForm(forms.ModelForm):
    class Meta:
        model = Expediente
        fields = [
            'cliente', 'titulo', 'numero_proceso',
            'tipo_expediente', 'estado', 'prioridad', 'descripcion'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select rounded-3 bg-light border-0 px-3 shadow-sm'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control rounded-3 bg-light border-0 px-3',
                'placeholder': 'Ej: Demanda de Alimentos - Pérez'
            }),
            'numero_proceso': forms.TextInput(attrs={
                'class': 'form-control rounded-3 bg-light border-0 px-3',
                'placeholder': 'Ej: 17203-2024-00123'
            }),
            'tipo_expediente': forms.Select(attrs={'class': 'form-select rounded-3 bg-light border-0 px-3 shadow-sm'}),
            'estado': forms.Select(attrs={'class': 'form-select rounded-3 bg-light border-0 px-3 shadow-sm'}),
            'prioridad': forms.Select(attrs={'class': 'form-select rounded-3 bg-light border-0 px-3 shadow-sm'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control rounded-3 bg-light border-0 px-3',
                'rows': 3,
                'placeholder': 'Breve resumen de la situación inicial...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].empty_label = "Seleccione un cliente..."
        self.fields['cliente'].queryset = Cliente.objects.filter(esta_activo=True)