# odontologia/forms.py
from django import forms
from .models import Atencion, DetalleAtencion, Doctor
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re 
from itertools import cycle

class AtencionForm(forms.ModelForm):
    class Meta:
        model = Atencion
        fields = [
            'paciente_nombre', 'paciente_apellido', 'paciente_rut', 'paciente_edad',
            'paciente_sexo', 'paciente_email', 'paciente_celular',
            'fecha', 'hora_atencion', 'motivo_visita', 'metodo_pago'
        ]
        widgets = {
            'paciente_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'paciente_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'paciente_rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'}),
            'paciente_edad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '120'}),
            'paciente_sexo': forms.Select(attrs={'class': 'form-select'}),
            'paciente_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ejemplo.com'}),
            'paciente_celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+569...'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_atencion': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo_visita': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe el motivo...'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        """Validaciones cruzadas (Duplicidad e Identidad)."""
        cleaned_data = super().clean()
        rut = cleaned_data.get('paciente_rut')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora_atencion')
        nombre_nuevo = cleaned_data.get('paciente_nombre', '').strip()
        apellido_nuevo = cleaned_data.get('paciente_apellido', '').strip()

        # 1. VALIDACIÓN DE DUPLICIDAD DE HORARIO
        if rut and fecha and hora:
            coincidencias = Atencion.objects.filter(
                paciente_rut=rut,
                fecha=fecha,
                hora_atencion=hora
            ).exclude(pk=self.instance.pk)

            if coincidencias.exists():
                raise ValidationError(
                    f"Error: El paciente con RUT {rut} ya tiene una atención agendada "
                    f"exactamente el {fecha} a las {hora}."
                )

        # 2. VALIDACIÓN DE IDENTIDAD ÚNICA (TU PEDIDO)
        if rut and nombre_nuevo and apellido_nuevo:
            # Buscamos si este RUT ya existe en la base de datos (excluyendo la ficha actual si se está editando)
            paciente_previo = Atencion.objects.filter(paciente_rut=rut).exclude(pk=self.instance.pk).first()

            if paciente_previo:
                # Comparamos nombres (ignorando mayúsculas/minúsculas)
                nombre_registrado = paciente_previo.paciente_nombre.strip()
                apellido_registrado = paciente_previo.paciente_apellido.strip()

                if (nombre_nuevo.lower() != nombre_registrado.lower()) or \
                   (apellido_nuevo.lower() != apellido_registrado.lower()):
                    
                    # Si los nombres no coinciden, lanzamos error
                    raise ValidationError({
                        'paciente_rut': f"Este RUT ya pertenece a {nombre_registrado} {apellido_registrado}. "
                                        f"No puedes registrarlo como {nombre_nuevo} {apellido_nuevo}."
                    })

        return cleaned_data

    def clean_paciente_rut(self):
        """Valida el RUT chileno (Formato, Rango y Matemática)."""
        rut = self.cleaned_data.get('paciente_rut')
        
        if not rut:
            return rut

        # Limpieza
        rut = rut.strip().upper().replace('.', '').replace(' ', '')

        # Formato
        if not re.match(r'^\d{1,8}-[\dK]$', rut):
            raise ValidationError("Formato inválido. Use el formato: 12345678-9")

        cuerpo, dv_ingresado = rut.split('-')

        # Rango Numérico
        try:
            cuerpo_num = int(cuerpo)
        except ValueError:
            raise ValidationError("El cuerpo del RUT debe ser numérico.")

        if cuerpo_num < 1000000:
            raise ValidationError("RUT inválido (número demasiado bajo).")
        
        if cuerpo_num >= 30000000:
            raise ValidationError("RUT inválido (fuera del rango de personas naturales).")

        # Algoritmo Módulo 11
        reversed_digits = map(int, reversed(cuerpo))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        res = (-s) % 11

        if res == 10: dv_esperado = 'K'
        else: dv_esperado = str(res)

        if dv_ingresado != dv_esperado:
            raise ValidationError("RUT inválido. El dígito verificador no corresponde.")

        return rut

# --- OTROS FORMULARIOS ---

class DetalleAtencionForm(forms.ModelForm):
    class Meta:
        model = DetalleAtencion
        fields = ['especialidad', 'descripcion', 'valor']
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Detalle del procedimiento'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '$ 0'}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Apellido", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['rut', 'fecha_nacimiento', 'foto_perfil']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }