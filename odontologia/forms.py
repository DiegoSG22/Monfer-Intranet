# odontologia/forms.py
from django import forms
from .models import Atencion, DetalleAtencion, Doctor
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re 
from itertools import cycle
from datetime import date 

class AtencionForm(forms.ModelForm):
    # Validación explícita del campo numérico de edad
    paciente_edad = forms.IntegerField(
        label="Edad",
        min_value=0,
        max_value=65, # <--- AQUI: Si pone 66 o más, Django lo bloquea
        error_messages={
            'max_value': 'La edad máxima permitida para la atención es de 65 años.',
            'min_value': 'La edad no puede ser negativa.'
        },
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

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
            'paciente_sexo': forms.Select(attrs={'class': 'form-select'}),
            'paciente_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ejemplo.com'}),
            'paciente_celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+569...'}),
            
            # CORRECCIÓN FECHA: Forzamos el formato YYYY-MM-DD para que no salga error en el navegador
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'hora_atencion': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            
            'motivo_visita': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        rut = cleaned_data.get('paciente_rut')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora_atencion')
        nombre_nuevo = cleaned_data.get('paciente_nombre', '').strip()
        apellido_nuevo = cleaned_data.get('paciente_apellido', '').strip()

        # Validación 1: Duplicidad de Horario
        if rut and fecha and hora:
            coincidencias = Atencion.objects.filter(
                paciente_rut=rut, fecha=fecha, hora_atencion=hora
            ).exclude(pk=self.instance.pk)
            if coincidencias.exists():
                raise ValidationError(f"El paciente con RUT {rut} ya tiene hora ese día a esa misma hora.")

        # Validación 2: Identidad Única
        if rut and nombre_nuevo and apellido_nuevo:
            paciente_previo = Atencion.objects.filter(paciente_rut=rut).exclude(pk=self.instance.pk).first()
            if paciente_previo:
                nombre_reg = paciente_previo.paciente_nombre.strip()
                apellido_reg = paciente_previo.paciente_apellido.strip()
                if (nombre_nuevo.lower() != nombre_reg.lower()) or (apellido_nuevo.lower() != apellido_reg.lower()):
                    raise ValidationError({
                        'paciente_rut': f"Conflicto: El RUT {rut} pertenece a {nombre_reg} {apellido_reg}."
                    })
        return cleaned_data

    def clean_paciente_rut(self):
        rut = self.cleaned_data.get('paciente_rut')
        if not rut: return rut
        rut = rut.strip().upper().replace('.', '').replace(' ', '')
        
        if not re.match(r'^\d{1,8}-[\dK]$', rut):
            raise ValidationError("Formato inválido. Use: 12345678-9")
        
        cuerpo, dv_ingresado = rut.split('-')
        try:
            cuerpo_num = int(cuerpo)
        except ValueError:
            raise ValidationError("El cuerpo del RUT debe ser numérico.")
        
        if cuerpo_num < 1000000: raise ValidationError("RUT inválido (muy bajo).")
        if cuerpo_num >= 30000000: raise ValidationError("RUT inválido (fuera de rango).")
        
        reversed_digits = map(int, reversed(cuerpo))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        res = (-s) % 11
        if res == 10: dv_esperado = 'K'
        else: dv_esperado = str(res)
        
        if dv_ingresado != dv_esperado:
            raise ValidationError("RUT inválido. Dígito verificador incorrecto.")
        return rut

# --- OTROS FORMULARIOS ---

class DetalleAtencionForm(forms.ModelForm):
    class Meta:
        model = DetalleAtencion
        fields = ['especialidad', 'descripcion', 'valor']
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '$ 0'}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
        error_messages={'invalid': 'Ingresa una dirección de correo válida.'}
    )
    first_name = forms.CharField(
        label="Nombre", max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50'})
    )
    last_name = forms.CharField(
        label="Apellido", max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50'})
    )
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['rut', 'fecha_nacimiento', 'foto_perfil']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            # CORRECCIÓN FECHA AQUÍ TAMBIÉN
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_fecha_nacimiento(self):
        """Validar edad del doctor (Entre 18 y 65 años)."""
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        
        if fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            
            if edad < 18:
                raise ValidationError("Debes ser mayor de 18 años.")
            
            # AQUÍ ESTÁ EL BLOQUEO DE 1955 (Si tiene más de 65, error)
            if edad > 65:
                raise ValidationError(f"La edad máxima permitida es 65 años. (Calculada: {edad} años).")
                
        return fecha_nacimiento