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
            # --- SECCIÓN PACIENTE ---
            'paciente_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'paciente_apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'paciente_rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 11111111-K',
                'required': True,
                'pattern': r'^\d{7,8}-[\dkK]$',
                'title': 'Formato RUT inválido. Debe tener 7 u 8 dígitos, sin puntos y con guion (Ej: 11111111-K).',
                'minlength': '9',
                'maxlength': '10'
            }),
            'paciente_edad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '120',
                'title': 'La edad debe estar entre 1 y 120.'
            }),
            'paciente_sexo': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'paciente_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'paciente@email.com',
                'required': True,
                'type': 'email'
            }),
            'paciente_celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+569...'}),

            # --- SECCIÓN ATENCIÓN ---
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'hora_atencion': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': True}),
            'motivo_visita': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
        labels = {
            'paciente_nombre': 'Nombre(s) Paciente',
            'paciente_apellido': 'Apellido(s) Paciente',
            'paciente_rut': 'RUT Paciente (sin puntos, con guion)',
            'paciente_edad': 'Edad Paciente (1-120 años)',
            'paciente_sexo': 'Sexo',
            'paciente_email': 'Email',
            'paciente_celular': 'Celular (9 dígitos, ej: 912345678)',
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

    # Validación de RUT (mínimo 7-8 dígitos + verificador)
    def clean_paciente_rut(self):
        rut = self.cleaned_data.get('paciente_rut', '').strip().upper().replace('.', '')
        if not re.fullmatch(r'^\d{7,8}-[\dkK]$', rut):
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
        if not email:
            raise forms.ValidationError("El correo electrónico es requerido.")
        if '@' not in email:
            raise forms.ValidationError("El correo electrónico debe contener un '@'.")
        return email

    # Validación de Celular (opcional, pero si existe debe ser válido)
    def clean_paciente_celular(self):
        celular = self.cleaned_data.get('paciente_celular')
        if not celular: # Si está vacío, es válido (campo opcional)
            return celular 
        celular = celular.strip()
        if not celular.isdigit():
            raise forms.ValidationError("El celular debe contener solo números.")
        if not celular.startswith('9'):
            raise forms.ValidationError("El celular debe comenzar con 9.")
        if len(celular) != 9:
            raise forms.ValidationError("El celular debe tener exactamente 9 dígitos.")
        return celular

class DetalleAtencionForm(forms.ModelForm):
    class Meta:
        model = DetalleAtencion
        fields = ['especialidad', 'descripcion', 'valor']
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles del tratamiento realizado...'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'CLP', 'required': True}),
        }
        labels = {
            'valor': 'Valor (CLP)',
        }

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
            'rut': 'RUT (sin puntos, con guion)',
            'fecha_nacimiento': 'Fecha de Nacimiento (18-90 años)',
            'foto_perfil': 'Foto de Perfil',
        }
        widgets = {
            # --- WIDGET RUT CORREGIDO ---
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 11111111-K',
                'pattern': r'^\d{7,8}-[\dkK]$', # Regex para 7-8 dígitos + guion + digit/K
                'title': 'Formato RUT inválido. Debe tener 7 u 8 dígitos, sin puntos y con guion (Ej: 11111111-K).',
                'minlength': '9', # 1111111-K (9 chars)
                'maxlength': '10' # 11111111-K (10 chars)
            }),
            # --- FIN CORRECCIÓN RUT ---
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # --- VALIDACIÓN DE FECHA DE NACIMIENTO CORREGIDA (18-90 AÑOS) ---
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if not fecha_nacimiento:
            return fecha_nacimiento # Es opcional (null=True, blank=True en el modelo)

        today = datetime.date.today()
        # Fecha límite más tardía (para tener 18 años)
        latest_bday = today.replace(year=today.year - 18)
        # Fecha límite más temprana (para tener 90 años)
        earliest_bday = today.replace(year=today.year - 90)

        if fecha_nacimiento > latest_bday:
            raise forms.ValidationError("El doctor debe tener al menos 18 años de edad.")
        if fecha_nacimiento < earliest_bday:
            raise forms.ValidationError("La edad máxima permitida es de 90 años.")
        
        return fecha_nacimiento
    # --- FIN CORRECCIÓN FECHA ---

    # --- VALIDACIÓN DE RUT AÑADIDA (IDÉNTICA A LA DE PACIENTE) ---
    def clean_rut(self):
        rut = self.cleaned_data.get('rut', '').strip().upper().replace('.', '')
        if not rut: # El RUT es obligatorio en el modelo Doctor, así que validamos
            raise forms.ValidationError("El RUT es requerido.")
        
        if not re.fullmatch(r'^\d{7,8}-[\dkK]$', rut):
             raise forms.ValidationError("Formato de RUT inválido. Use XXXXXXXX-X (sin puntos).")
        # Aquí podrías añadir una validación completa del dígito verificador
        return rut
    # --- FIN VALIDACIÓN RUT ---