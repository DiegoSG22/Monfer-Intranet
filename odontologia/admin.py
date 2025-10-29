from django.contrib import admin
from .models import Doctor, Paciente, Tratamiento, Examen, Atencion, DetalleAtencion, ExamenAtencion, Boleta

# Clases para mostrar detalles "inline" (dentro de la misma página)
class DetalleAtencionInline(admin.TabularInline):
    model = DetalleAtencion
    extra = 1 # Muestra un campo vacío para añadir un tratamiento

class ExamenAtencionInline(admin.TabularInline):
    model = ExamenAtencion
    extra = 1 # Muestra un campo vacío para añadir un examen

# --- CORRECCIÓN EN AtencionAdmin ---
@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    # Reemplazamos 'paciente' por un método que muestra nombre y apellido
    list_display = ('fecha', 'doctor', 'get_paciente_completo', 'motivo_visita') # Añadido motivo_visita como ejemplo
    list_filter = ('fecha', 'doctor')
    # Actualizamos los campos de búsqueda para usar los nuevos campos del paciente
    search_fields = ('paciente_nombre', 'paciente_apellido', 'paciente_rut', 'doctor__user__first_name', 'doctor__user__last_name')
    inlines = [DetalleAtencionInline, ExamenAtencionInline]

    # NUEVO MÉTODO: Para mostrar nombre y apellido juntos en la lista del admin
    @admin.display(description='Paciente') # Texto que aparecerá como cabecera de columna
    def get_paciente_completo(self, obj):
        # obj es la instancia de Atencion que se está mostrando
        return f"{obj.paciente_nombre} {obj.paciente_apellido}"
# --- FIN CORRECCIÓN ---

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'rut')
    search_fields = ('user__first_name', 'user__last_name', 'rut')

@admin.register(Paciente) # Mantenemos PacienteAdmin por si acaso, aunque Atencion no lo use
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut')
    search_fields = ('nombre', 'rut')

@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo_base', 'duracion_aproximada') # Añadido duracion_aproximada

@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo')

@admin.register(Boleta)
class BoletaAdmin(admin.ModelAdmin):
    list_display = ('id', 'atencion', 'total_tratamientos', 'total_examenes', 'ganancia_neta_doctor', 'fecha_emision') # Añadido total_examenes
    readonly_fields = ('total_tratamientos', 'total_examenes', 'ganancia_neta_doctor', 'fecha_emision') # Añadidos campos calculados/auto

# (Opcional) Registrar los otros modelos si quieres verlos en el admin individualmente
# admin.site.register(DetalleAtencion)
# admin.site.register(ExamenAtencion)