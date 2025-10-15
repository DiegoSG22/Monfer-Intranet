from django.contrib import admin
from .models import Doctor, Paciente, Tratamiento, Examen, Atencion, DetalleAtencion, ExamenAtencion, Boleta

# Clases para mostrar detalles "inline" (dentro de la misma página)
class DetalleAtencionInline(admin.TabularInline):
    model = DetalleAtencion
    extra = 1 # Muestra un campo vacío para añadir un tratamiento

class ExamenAtencionInline(admin.TabularInline):
    model = ExamenAtencion
    extra = 1 # Muestra un campo vacío para añadir un examen

@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'doctor', 'paciente')
    list_filter = ('fecha', 'doctor')
    search_fields = ('paciente__nombre', 'doctor__user__first_name', 'doctor__user__last_name')
    inlines = [DetalleAtencionInline, ExamenAtencionInline]

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'rut')
    search_fields = ('user__first_name', 'user__last_name', 'rut')

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut')
    search_fields = ('nombre', 'rut')

@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo_base')

@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo')

@admin.register(Boleta)
class BoletaAdmin(admin.ModelAdmin):
    list_display = ('id', 'atencion', 'total_tratamientos', 'ganancia_neta_doctor', 'fecha_emision')
    readonly_fields = ('total_tratamientos', 'total_examenes', 'ganancia_neta_doctor')