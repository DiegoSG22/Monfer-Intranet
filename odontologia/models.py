from django.db import models
from django.contrib.auth.models import User

class Odontologo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.especialidad})"

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=100)
    valor_base = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class RegistroTrabajo(models.Model):
    odontologo = models.ForeignKey(Odontologo, on_delete=models.CASCADE)
    fecha = models.DateField()
    horas_trabajadas = models.DecimalField(max_digits=5, decimal_places=2)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.odontologo} - {self.fecha}"
