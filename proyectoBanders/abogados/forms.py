from django import forms
from .models import Perfil, DocumentoAdjunto, NotaKeep

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto', 'portada', 'especialidad', 'telefono', 'bio', 'hoja_vida']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 4, 'placeholder': 'Cuéntanos sobre tu trayectoria...'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Ej. Derecho Civil'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': '+593...'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'portada': forms.FileInput(attrs={'class': 'form-control'}),
            'hoja_vida': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = DocumentoAdjunto
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'form-control rounded-pill',
                'accept': '.pdf,.doc,.docx,.jpg,.png'
            }),
        }

class NotaKeepForm(forms.ModelForm):
    class Meta:
        model = NotaKeep
        fields = ['titulo', 'contenido', 'color']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control fw-bold border-0 bg-light',
                'placeholder': 'Título de la nota...'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control border-0 bg-light',
                'rows': 3,
                'placeholder': 'Escribe los detalles aquí...',
                'style': 'resize: none;'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color border-0 w-100 shadow-sm',
                'style': 'height: 45px; border-radius: 12px;'
            }),
        }