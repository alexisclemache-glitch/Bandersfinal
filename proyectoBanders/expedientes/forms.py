from django import forms
from .models import Expediente
from proyectoBanders.clientes.models import Cliente

class ClienteRUTChoiceField(forms.ModelChoiceField):
    """Personaliza el dropdown para mostrar Nombre + RUT en el modal."""
    def label_from_instance(self, obj):
        return f"{obj.nombre} {obj.apellido} | ID: {obj.rut}"

class ExpedienteForm(forms.ModelForm):
    # Campo de cliente con el estilo redondeado del sistema
    cliente = ClienteRUTChoiceField(
        queryset=Cliente.objects.all().order_by('nombre'),
        label="TITULAR DEL CASO",
        widget=forms.Select(attrs={
            'class': 'form-select rounded-pill border-light bg-light px-3 shadow-xs'
        })
    )

    class Meta:
        model = Expediente
        fields = ['cliente', 'titulo', 'numero_proceso', 'tipo_expediente', 'estado', 'prioridad', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control rounded-pill border-light bg-light px-3',
                'placeholder': 'Ej: Demanda de Alimentos'
            }),
            'numero_proceso': forms.TextInput(attrs={
                'class': 'form-control rounded-pill border-light bg-light px-3',
                'placeholder': 'ROL / CAUSA'
            }),
            'tipo_expediente': forms.Select(attrs={
                'class': 'form-select rounded-pill border-light bg-light px-3'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select rounded-pill border-light bg-light px-3'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select rounded-pill border-light bg-light px-3'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control rounded-4 border-light bg-light px-3',
                'rows': 3,
                'placeholder': 'Resumen breve del caso...'
            }),
        }