# odontologia/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import decimal

# --- Modelos Principales ---

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario del Sistema")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT")
    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Paciente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT")
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
    def __str__(self):
        return self.nombre

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre del Tratamiento")
    costo_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Costo Base", default=0)
    # NUEVO CAMPO:
    duracion_aproximada = models.PositiveIntegerField(default=30, help_text="Duración en minutos", verbose_name="Duración Aproximada (min)")
    class Meta:
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"
    def __str__(self):
        return self.nombre

class Examen(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre del Examen")
    costo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Costo")
    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"
    def __str__(self):
        return self.nombre

# --- Modelos de Transacciones ---

class Atencion(models.Model):
    METODOS_PAGO = [
        ('EF', 'Efectivo'),
        ('TC', 'Tarjeta de Crédito'),
        ('TD', 'Tarjeta de Débito'),
        ('TR', 'Transferencia'),
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, verbose_name="Doctor")
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, verbose_name="Paciente")
    fecha = models.DateField(verbose_name="Fecha de Atención")
    # NUEVOS CAMPOS:
    motivo_visita = models.CharField(max_length=200, verbose_name="Motivo de la Visita", default='')
    metodo_pago = models.CharField(max_length=2, choices=METODOS_PAGO, verbose_name="Método de Pago", default='EF')
    class Meta:
        verbose_name = "Atención"
        verbose_name_plural = "Atenciones"
        unique_together = ('doctor', 'paciente', 'fecha')
    def __str__(self):
        return f"Atención de {self.doctor} a {self.paciente} el {self.fecha}"

class DetalleAtencion(models.Model):
    atencion = models.ForeignKey(Atencion, related_name='detalles', on_delete=models.CASCADE, verbose_name="Atención")
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.PROTECT, verbose_name="Tratamiento")
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Valor del Tratamiento")
    class Meta:
        verbose_name = "Detalle de Atención"
        verbose_name_plural = "Detalles de Atenciones"
    def __str__(self):
        return f"{self.tratamiento.nombre} en {self.atencion}"

class ExamenAtencion(models.Model):
    atencion = models.ForeignKey(Atencion, related_name='examenes', on_delete=models.CASCADE, verbose_name="Atención")
    examen = models.ForeignKey(Examen, on_delete=models.PROTECT, verbose_name="Examen")
    costo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Costo del Examen")
    class Meta:
        verbose_name = "Examen de Atención"
        verbose_name_plural = "Exámenes de Atenciones"
    def __str__(self):
        return f"{self.examen.nombre} en {self.atencion}"

class Boleta(models.Model):
    atencion = models.OneToOneField(Atencion, on_delete=models.CASCADE, verbose_name="Atención Asociada")
    total_tratamientos = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Tratamientos")
    total_examenes = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Exámenes")
    ganancia_neta_doctor = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Ganancia Neta Doctor")
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    class Meta:
        verbose_name = "Boleta"
        verbose_name_plural = "Boletas"
    def __str__(self):
        return f"Boleta para la atención del {self.atencion.fecha} (ID: {self.id})"