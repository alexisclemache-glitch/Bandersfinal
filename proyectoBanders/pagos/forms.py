from django import forms
from .models import Pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['expediente', 'total_deuda', 'transaccion_id', 'estado', 'concepto']
        widgets = {
            'expediente': forms.Select(attrs={'class': 'form-select'}),
            'total_deuda': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'transaccion_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'concepto': forms.Select(attrs={'class': 'form-select'}),
        }