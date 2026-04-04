from django import forms
from .models import Perfil, DocumentoAdjunto, NotaKeep

class PerfilForm(forms.ModelForm):
    """Formulario para actualizar los datos del abogado, incluyendo fotos."""
    class Meta:
        model = Perfil
        fields = ['especialidad', 'telefono', 'bio', 'foto', 'portada', 'hoja_vida']
        widgets = {
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control rounded-pill',
                'placeholder': 'Ej: Especialista en Derecho Civil'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control rounded-pill',
                'placeholder': '+593 ...'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control rounded-4',
                'rows': 4,
                'placeholder': 'Escribe una breve reseña profesional...'
            }),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'portada': forms.FileInput(attrs={'class': 'form-control'}),
            'hoja_vida': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DocumentoForm(forms.ModelForm):
    """Formulario para subir archivos a la Bóveda."""
    class Meta:
        model = DocumentoAdjunto
        fields = ['nombre', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control rounded-pill',
                'placeholder': 'Nombre del documento (ej: Contrato 2024)'
            }),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class NotaKeepForm(forms.ModelForm):
    """Formulario para las notas rápidas en el perfil."""
    class Meta:
        model = NotaKeep
        fields = ['titulo', 'contenido']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control border-0 fw-bold fs-5 mb-2',
                'placeholder': 'Título de la nota...',
                'style': 'background: transparent; outline: none;'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control border-0',
                'rows': 3,
                'placeholder': 'Escribe algo importante...',
                'style': 'background: transparent; outline: none; resize: none;'
            }),
        }