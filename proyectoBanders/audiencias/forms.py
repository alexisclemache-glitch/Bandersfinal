from django import forms
from .models import Audiencia
from proyectoBanders.expedientes.models import Expediente

class AudienciaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Hacemos que el expediente NO sea obligatorio para permitir Asesorías
        self.fields['expediente'].required = False

        # Cambiamos el "--------- " por algo más profesional para cuando sea cita libre
        self.fields['expediente'].empty_label = "SIN EXPEDIENTE (ASESORÍA DIRECTA)"

        # 2. Carga RUT + Nombre en el selector
        self.fields['expediente'].queryset = Expediente.objects.all().select_related('cliente')

        self.fields['expediente'].label_from_instance = lambda \
                obj: f"{obj.cliente.nombre} ({obj.cliente.rut}){f' - {obj.numero_proceso}' if obj.numero_proceso else ''}"

        # 3. Asegura que Prioridad tenga un label limpio
        self.fields['color_categoria'].empty_label = "-- Seleccionar Prioridad --"

    class Meta:
        model = Audiencia
        fields = [
            'expediente',
            'titulo',
            'fecha_inicio',
            'fecha_fin',
            'color_categoria',
            'descripcion',
            'usuarios_asignados'
        ]
        widgets = {
            'expediente': forms.Select(attrs={'class': 'form-select select2-single'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente o asunto'}),
            'fecha_inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'fecha_fin': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'color_categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales...'}),
            'usuarios_asignados': forms.SelectMultiple(attrs={'class': 'form-select select2-multiple'}),
        }