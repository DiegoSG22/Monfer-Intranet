# odontologia/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.utils import timezone
import datetime # Necesario para la validación de fecha y hora
import decimal # Para el default de DecimalField

# --- Modelos Principales ---
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario del Sistema")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT")
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True, verbose_name="Foto de Perfil")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    class Meta: verbose_name = "Doctor"; verbose_name_plural = "Doctores"
    def __str__(self): return f"{self.user.first_name} {self.user.last_name}"

class Paciente(models.Model): # Mantenemos por si acaso
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT")
    class Meta: verbose_name = "Paciente"; verbose_name_plural = "Pacientes"
    def __str__(self): return self.nombre

class Tratamiento(models.Model): # Catálogo general
    nombre = models.CharField(max_length=50, verbose_name="Nombre del Tratamiento")
    costo_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Costo Base", default=0)
    duracion_aproximada = models.PositiveIntegerField(default=30, help_text="Duración en minutos", verbose_name="Duración Aproximada (min)")
    class Meta: verbose_name = "Tratamiento"; verbose_name_plural = "Tratamientos"
    def __str__(self): return self.nombre

class Examen(models.Model): # Catálogo general de Exámenes (si quieres usarlo en el futuro)
    nombre = models.CharField(max_length=50, verbose_name="Nombre del Examen")
    costo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Costo", default=0)
    class Meta: verbose_name = "Examen"; verbose_name_plural = "Exámenes"
    def __str__(self): return self.nombre

# --- Modelos de Transacciones ---

class Atencion(models.Model):
    METODOS_PAGO = [('EF', 'Efectivo'), ('TC', 'Tarjeta de Crédito'), ('TD', 'Tarjeta de Débito'), ('TR', 'Transferencia')]
    PACIENTE_SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]

    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, verbose_name="Doctor")
    fecha = models.DateField(verbose_name="Fecha de Atención", default=datetime.date.today)
    hora_atencion = models.TimeField(verbose_name="Hora de Atención", default=datetime.time(9, 0))
    motivo_visita = models.CharField(max_length=200, verbose_name="Motivo de la Visita", default='')
    metodo_pago = models.CharField(max_length=2, choices=METODOS_PAGO, verbose_name="Método de Pago", default='EF')
    paciente_nombre = models.CharField(max_length=50, verbose_name="Nombre del Paciente", default='')
    paciente_apellido = models.CharField(max_length=50, verbose_name="Apellido del Paciente", default='')
    paciente_rut = models.CharField(max_length=15, verbose_name="RUT del Paciente", default='')
    paciente_edad = models.PositiveIntegerField(verbose_name="Edad del Paciente", null=True, blank=True)
    paciente_sexo = models.CharField(max_length=1, choices=PACIENTE_SEXO_CHOICES, verbose_name="Sexo del Paciente", default='O')
    paciente_email = models.EmailField(verbose_name="Email del Paciente", blank=True, null=True) # Lo hacemos opcional de nuevo para que coincida con el form
    paciente_celular = models.CharField(max_length=15, verbose_name="Celular del Paciente", blank=True, null=True)

    class Meta:
        verbose_name = "Atención"
        verbose_name_plural = "Atenciones"
    def __str__(self):
        return f"Atención de {self.doctor} a {self.paciente_nombre} {self.paciente_apellido} el {self.fecha}"

class DetalleAtencion(models.Model):
    ESPECIALIDADES = [
        ('OPER', 'Operatoria'), ('ENDO', 'Endodoncia'), ('ORTO', 'Ortodoncia'),
        ('CIRU', 'Cirugía'), ('IMPL', 'Implantes'), ('PEDIA', 'Odontopediatría'),
        ('HIGI', 'Higiene Oral'), ('OTRO', 'Otro'),
    ]
    atencion = models.ForeignKey(Atencion, related_name='detalles', on_delete=models.CASCADE, verbose_name="Atención")
    especialidad = models.CharField(max_length=5, choices=ESPECIALIDADES, verbose_name="Especialidad", default='OTRO')
    descripcion = models.TextField(max_length=1000, validators=[MaxLengthValidator(1000)], verbose_name="Descripción del Tratamiento", default='')
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Valor", default=decimal.Decimal('0.00'))

    class Meta:
        verbose_name = "Detalle de Atención"
        verbose_name_plural = "Detalles de Atenciones"
    def __str__(self):
        return f"{self.get_especialidad_display()} en {self.atencion}"

# --- NUEVO MODELO DE EXÁMENES (RE-AÑADIDO Y MODIFICADO) ---
class ExamenAtencion(models.Model):
    atencion = models.ForeignKey(Atencion, related_name='examenes_solicitados', on_delete=models.CASCADE, verbose_name="Atención")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción del Examen", default='')
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad", default=1)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Costo Total", default=decimal.Decimal('0.00'))
    
    class Meta:
        verbose_name = "Examen Solicitado"
        verbose_name_plural = "Exámenes Solicitados"
    def __str__(self): 
        return f"{self.cantidad}x {self.descripcion} para {self.atencion}"
# ----------------------------------------------------

class Boleta(models.Model):
    atencion = models.OneToOneField(Atencion, on_delete=models.CASCADE, verbose_name="Atención Asociada")
    total_tratamientos = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Tratamientos")
    # --- RE-AÑADIDO ---
    total_examenes = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Exámenes")
    # ------------------
    ganancia_neta_doctor = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Ganancia Neta Doctor")
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    class Meta: verbose_name = "Boleta"; verbose_name_plural = "Boletas"
    def __str__(self): return f"Boleta para la atención del {self.atencion.fecha} (ID: {self.id})"