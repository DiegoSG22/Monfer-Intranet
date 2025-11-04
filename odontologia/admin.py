from django.contrib import admin
# Importamos los modelos correctos (sin ExamenAtencion)
from .models import Doctor, Paciente, Tratamiento, Examen, Atencion, DetalleAtencion, Boleta

# Clases para mostrar detalles "inline" (dentro de la misma página)
class DetalleAtencionInline(admin.TabularInline):
    model = DetalleAtencion
    extra = 1 # Muestra un campo vacío para añadir un tratamiento

# --- CLASE ELIMINADA ---
# Ya no existe el modelo ExamenAtencion
# class ExamenAtencionInline(admin.TabularInline):
#     model = ExamenAtencion
#     extra = 1
# -----------------------

@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    # CORREGIDO: Reemplazamos 'paciente' por el método 'get_paciente_completo'
    # y añadimos el nuevo campo 'hora_atencion'
    list_display = ('fecha', 'hora_atencion', 'doctor', 'get_paciente_completo', 'motivo_visita')
    list_filter = ('fecha', 'doctor')
    # CORREGIDO: Actualizamos los campos de búsqueda a los nuevos campos directos
    search_fields = ('paciente_nombre', 'paciente_apellido', 'paciente_rut', 'doctor__user__first_name', 'doctor__user__last_name')
    # CORREGIDO: Eliminamos ExamenAtencionInline
    inlines = [DetalleAtencionInline]

    # Método para mostrar nombre y apellido juntos en la lista
    @admin.display(description='Paciente')
    def get_paciente_completo(self, obj):
        # obj es la instancia de Atencion que se está mostrando
        return f"{obj.paciente_nombre} {obj.paciente_apellido}"

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'rut', 'fecha_nacimiento') # Añadido fecha_nacimiento
    search_fields = ('user__first_name', 'user__last_name', 'rut')

@admin.register(Paciente) # Mantenemos PacienteAdmin por si se usa como catálogo
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut')
    search_fields = ('nombre', 'rut')

@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo_base', 'duracion_aproximada')

@admin.register(Examen) # Mantenemos el catálogo de Examenes
class ExamenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo')

@admin.register(Boleta)
class BoletaAdmin(admin.ModelAdmin):
    # CORREGIDO: Eliminamos 'total_examenes'
    list_display = ('id', 'atencion', 'total_tratamientos', 'ganancia_neta_doctor', 'fecha_emision')
    readonly_fields = ('total_tratamientos', 'ganancia_neta_doctor', 'fecha_emision')

# (Opcional) Registrar los otros modelos si quieres verlos en el admin individualmente
# admin.site.register(DetalleAtencion)