# odontologia/forms.py
from django import forms
from .models import Atencion, DetalleAtencion, ExamenAtencion

class AtencionForm(forms.ModelForm):
    """Formulario para la información principal de la atención."""
    class Meta:
        model = Atencion
        # El doctor se asigna automáticamente, por eso no está aquí
        fields = ['paciente', 'fecha']
        widgets = {
            'fecha': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'paciente': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }

class DetalleAtencionForm(forms.ModelForm):
    """Formulario para añadir un tratamiento a la atención."""
    class Meta:
        model = DetalleAtencion
        # La atención se asigna automáticamente
        fields = ['tratamiento', 'valor']
        widgets = {
            'tratamiento': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ExamenAtencionForm(forms.ModelForm):
    """Formulario para añadir un examen a la atención."""
    class Meta:
        model = ExamenAtencion
        # La atención se asigna automáticamente
        fields = ['examen', 'costo']
        widgets = {
            'examen': forms.Select(attrs={'class': 'form-control'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
        }