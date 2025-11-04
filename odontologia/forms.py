# odontologia/forms.py
from django import forms
from .models import Atencion, DetalleAtencion, Doctor, Examen # Importa todos los modelos necesarios
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
# Importa los validadores necesarios
from django.core.validators import MinValueValidator, MaxValueValidator
import re # Para validación básica de RUT

class AtencionForm(forms.ModelForm):
    class Meta:
        model = Atencion
        # Campos actualizados
        fields = [
            'paciente_nombre', 'paciente_apellido', 'paciente_rut', 'paciente_edad',
            'paciente_sexo', 'paciente_email', 'paciente_celular',
            'fecha', 'hora_atencion', 'motivo_visita', 'metodo_pago'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_atencion': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'paciente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'paciente_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'paciente_rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 11111111-K'}),
            'paciente_edad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '120'}),
            'paciente_sexo': forms.Select(attrs={'class': 'form-control'}),
            'paciente_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'paciente@email.com'}),
            'paciente_celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+569...'}),
            'motivo_visita': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'paciente_nombre': 'Nombre(s) Paciente',
            'paciente_apellido': 'Apellido(s) Paciente',
            'paciente_rut': 'RUT Paciente (sin puntos, con guion)',
            'paciente_edad': 'Edad Paciente (1-120 años)',
            'paciente_sexo': 'Sexo',
            'paciente_email': 'Email (requerido)',
            'paciente_celular': 'Celular (Opcional)',
        }

    # Validación personalizada para la fecha (ayer hasta +7 días)
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if not fecha:
            return fecha
        hoy = timezone.localdate()
        un_dia_atras = hoy - datetime.timedelta(days=1)
        una_semana_despues = hoy + datetime.timedelta(days=7)

        if fecha < un_dia_atras:
            raise forms.ValidationError("La fecha no puede ser anterior a ayer.")
        if fecha > una_semana_despues:
            raise forms.ValidationError("La fecha no puede ser más de una semana en el futuro.")
        return fecha

    # Validación de RUT (mínimo 8 chars)
    def clean_paciente_rut(self):
        rut = self.cleaned_data.get('paciente_rut', '').strip().upper().replace('.', '')
        if len(rut) < 8:
             raise forms.ValidationError("El RUT debe tener al menos 8 caracteres.")
        if not re.fullmatch(r'^\d{1,8}-[\dkK]$', rut):
             raise forms.ValidationError("Formato de RUT inválido. Use XXXXXXXX-X (sin puntos).")
        return rut

    # Validación de Edad (1-120)
    def clean_paciente_edad(self):
        edad = self.cleaned_data.get('paciente_edad')
        if edad is not None and (edad < 1 or edad > 120):
             raise forms.ValidationError("La edad debe estar entre 1 y 120 años.")
        return edad
    
    # Validación de Email (requerido el @)
    def clean_paciente_email(self):
        email = self.cleaned_data.get('paciente_email')
        # El modelo permite blank=True, null=True, pero tú pediste que sea requerido
        if not email:
            raise forms.ValidationError("El correo electrónico es requerido.")
        if '@' not in email:
            raise forms.ValidationError("El correo electrónico debe contener un '@'.")
        return email

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

# --- FORMULARIO ELIMINADO (ya no se usa ExamenAtencion) ---
# class ExamenAtencionForm(forms.ModelForm):
#     ...

# --- Formularios de Perfil ---

class UserUpdateForm(forms.ModelForm):
    """Formulario para actualizar datos básicos del usuario."""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

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
        }

class DoctorProfileForm(forms.ModelForm):
    """Formulario para actualizar datos específicos del perfil de Doctor."""
    class Meta:
        model = Doctor
        fields = ['rut', 'fecha_nacimiento', 'foto_perfil']
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

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            if fecha_nacimiento > datetime.date.today():
                raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha_nacimiento