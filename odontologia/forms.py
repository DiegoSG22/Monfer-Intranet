# odontologia/forms.py
from django import forms
from .models import Atencion, DetalleAtencion, ExamenAtencion, Doctor # Asegúrate que Doctor esté importado
from django.contrib.auth.models import User # Importa User
from django.utils import timezone
import datetime
# Importa los validadores necesarios
from django.core.validators import MinValueValidator, MaxValueValidator
import re # Para validación básica de RUT

class AtencionForm(forms.ModelForm):
    class Meta:
        model = Atencion
        fields = [
            'paciente_nombre', 'paciente_apellido', 'paciente_rut', 'paciente_edad',
            'fecha', 'motivo_visita', 'metodo_pago'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'paciente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'paciente_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'paciente_rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 11111111-K'}),
            'paciente_edad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '120'}),
            'motivo_visita': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'paciente_nombre': 'Nombre(s) Paciente',
            'paciente_apellido': 'Apellido(s) Paciente',
            'paciente_rut': 'RUT Paciente (sin puntos, con guion)',
            'paciente_edad': 'Edad Paciente (1-120 años)',
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if not fecha:
            return fecha
        hoy = timezone.localdate()
        ayer = hoy - datetime.timedelta(days=1)
        una_semana_despues = hoy + datetime.timedelta(days=7)

        if fecha < ayer:
            raise forms.ValidationError("La fecha no puede ser anterior a ayer.")
        if fecha > una_semana_despues:
            raise forms.ValidationError("La fecha no puede ser más de una semana en el futuro.")
        return fecha

    def clean_paciente_rut(self):
        rut = self.cleaned_data.get('paciente_rut', '').strip().upper().replace('.', '')
        if not re.fullmatch(r'^\d{1,8}-[\dkK]$', rut):
             raise forms.ValidationError("Formato de RUT inválido. Use XXXXXXXX-X (sin puntos).")
        return rut

    def clean_paciente_edad(self):
        edad = self.cleaned_data.get('paciente_edad')
        if edad is not None and (edad < 1 or edad > 120):
             raise forms.ValidationError("La edad debe estar entre 1 y 120 años.")
        return edad

class DetalleAtencionForm(forms.ModelForm):
    class Meta:
        model = DetalleAtencion
        fields = ['especialidad', 'descripcion', 'valor']
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles del tratamiento realizado...'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'CLP'}),
        }
        labels = {
            'valor': 'Valor (CLP)',
        }

class ExamenAtencionForm(forms.ModelForm):
    class Meta:
        model = ExamenAtencion
        fields = ['examen', 'costo']
        widgets = {
            'examen': forms.Select(attrs={'class': 'form-control'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'CLP'}),
        }
        labels = {
            'costo': 'Costo Examen (CLP)',
        }

# --- Formularios de Perfil (Corregidos y movidos al nivel correcto) ---

class UserUpdateForm(forms.ModelForm):
    """Formulario para actualizar datos básicos del usuario."""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'})) # Añadir widget aquí

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre(s)',
            'last_name': 'Apellido(s)',
            'email': 'Correo Electrónico',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            # email widget ya definido arriba
        }

# odontologia/forms.py
# ... (importaciones y otros formularios) ...

class DoctorProfileForm(forms.ModelForm):
    """Formulario para actualizar datos específicos del perfil de Doctor."""

    # --- ASEGÚRATE DE TENER ESTA CLASE META INTERNA ---
    class Meta:
        # --- Y QUE SU CONTENIDO ESTÉ INDENTADO ---
        model = Doctor  # Especifica el modelo
        fields = ['rut', 'fecha_nacimiento', 'foto_perfil'] # Campos a incluir
        labels = {
            'rut': 'RUT',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'foto_perfil': 'Foto de Perfil',
        }
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 11111111-K'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
    # --- FIN DE LA CLASE META ---

    # (La función clean_fecha_nacimiento va aquí, al mismo nivel de indentación que class Meta)
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            if fecha_nacimiento > datetime.date.today():
                raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha_nacimiento