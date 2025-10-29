# odontologia/views.py
import json # Para formatear los eventos del calendario
from django.http import JsonResponse # Para la vista de API
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Doctor, Atencion, DetalleAtencion, ExamenAtencion # Importa todos los modelos necesarios
from .forms import AtencionForm, DetalleAtencionForm, ExamenAtencionForm # Importa forms actualizados
from .forms import UserUpdateForm, DoctorProfileForm # Importa forms de perfil
from django.templatetags.static import static # Para obtener URL estática del placeholder
import datetime # Importa datetime para get_saludo

# --- Funciones Auxiliares ---

def get_saludo():
    """Determina el saludo según la hora."""
    now = timezone.localtime(timezone.now())
    hora_actual = now.hour
    if 5 <= hora_actual < 12: return "Buenos días"
    elif 12 <= hora_actual < 20: return "Buenas tardes"
    else: return "Buenas noches"

def get_doctor_data(user):
    """Obtiene el nombre y la URL de la foto del doctor asociado al usuario."""
    nombre_doctor = user.first_name or user.username # Nombre por defecto
    # URL del placeholder por defecto (asegúrate que exista en static/images/)
    doctor_profile_pic_url = static('images/doctor_placeholder.png')
    try:
        doctor = user.doctor # Accede a la relación inversa OneToOneField
        # Actualiza nombre si existe perfil
        nombre_doctor = doctor.user.first_name or doctor.user.username
        # Usa la foto real si existe
        if doctor.foto_perfil and hasattr(doctor.foto_perfil, 'url'):
            doctor_profile_pic_url = doctor.foto_perfil.url
    except Doctor.DoesNotExist:
        pass # Si no hay perfil de Doctor, usa los valores por defecto
    return nombre_doctor, doctor_profile_pic_url

# --- Vistas Principales ---

@login_required
def dashboard(request):
    """
    Muestra el panel principal del doctor.
    """
    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)
    atenciones_recientes = []

    try:
        # Intenta obtener el perfil Doctor para buscar sus atenciones
        # Usamos request.user.doctor que es la forma estándar de acceder a la relación inversa
        doctor = request.user.doctor
        atenciones_recientes = Atencion.objects.filter(doctor=doctor).order_by('-fecha')[:5]
    except Doctor.DoesNotExist:
        # Si el usuario logueado no tiene un perfil de Doctor asociado
        pass # Muestra la lista vacía

    context = {
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'atenciones': atenciones_recientes,
        'doctor_profile_pic': doctor_profile_pic,
    }
    return render(request, 'odontologia/dashboard.html', context)


@login_required
def registrar_atencion(request):
    """
    Maneja el registro de una nueva atención con detalles y exámenes.
    """
    try:
        # Asegura que el usuario tenga perfil de doctor para registrar
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, 'Error: Tu usuario no está asociado a un perfil de Doctor.')
        return redirect('dashboard')

    DetalleFormSet = inlineformset_factory(
        Atencion, DetalleAtencion, form=DetalleAtencionForm, extra=1, can_delete=False
    )
    ExamenFormSet = inlineformset_factory(
        Atencion, ExamenAtencion, form=ExamenAtencionForm, extra=1, can_delete=False
    )

    if request.method == 'POST':
        form = AtencionForm(request.POST)
        detalle_formset = DetalleFormSet(request.POST, prefix='detalles')
        examen_formset = ExamenFormSet(request.POST, prefix='examenes')

        if form.is_valid() and detalle_formset.is_valid() and examen_formset.is_valid():
            atencion = form.save(commit=False)
            atencion.doctor = doctor
            atencion.save()

            detalle_formset.instance = atencion
            detalle_formset.save()

            examen_formset.instance = atencion
            examen_formset.save()

            messages.success(request, '¡Atención guardada con éxito!')
            return redirect('dashboard')
        else:
             messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AtencionForm()
        detalle_formset = DetalleFormSet(prefix='detalles')
        examen_formset = ExamenFormSet(prefix='examenes')

    # Necesitamos pasar datos para la plantilla base (reloj, tema, etc.)
    nombre_doctor_display, doctor_profile_pic_display = get_doctor_data(request.user)
    saludo_display = get_saludo()

    context = {
        'form': form,
        'detalle_formset': detalle_formset,
        'examen_formset': examen_formset,
        # Añadimos datos para consistencia (aunque no se usen si no hereda)
        'nombre_doctor': nombre_doctor_display,
        'doctor_profile_pic': doctor_profile_pic_display,
        'saludo': saludo_display,
    }
    return render(request, 'odontologia/registrar_atencion.html', context)


# --- Vistas de Perfil ---

@login_required
def ver_perfil(request):
    """Muestra la información del perfil del doctor logueado."""
    try:
        # Usa la relación inversa para obtener el doctor
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.warning(request, 'No se encontró un perfil de doctor asociado a tu cuenta.')
        return redirect('dashboard')

    # Obtener datos necesarios para la plantilla base (dashboard.html)
    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    # Prepara los formularios con los datos actuales
    user_form = UserUpdateForm(instance=request.user)
    doctor_form = DoctorProfileForm(instance=doctor)

    context = {
        'user_form': user_form,
        'doctor_form': doctor_form,
        # Pasa las variables requeridas por la plantilla base
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
    }
    # Renderiza la plantilla de perfil (que extiende dashboard.html)
    return render(request, 'odontologia/perfil.html', context)


@login_required
def editar_perfil(request):
    """Procesa el formulario para editar el perfil."""
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, 'Perfil de doctor no encontrado.')
        return redirect('dashboard')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        # Importante: request.FILES para manejar la subida de la foto
        doctor_form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)

        if user_form.is_valid() and doctor_form.is_valid():
            user_form.save()
            doctor_form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('ver_perfil') # Redirige de vuelta a ver el perfil
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            # Si hay errores, necesitamos volver a renderizar la plantilla 'perfil.html'
            # con los formularios inválidos Y el contexto de la plantilla base

            # Obtener datos necesarios para la plantilla base
            saludo = get_saludo()
            nombre_doctor, doctor_profile_pic = get_doctor_data(request.user) # Recalcula por si cambió nombre

            context = {
                'user_form': user_form,     # Pasa el formulario inválido para mostrar errores
                'doctor_form': doctor_form, # Pasa el formulario inválido para mostrar errores
                # Pasa las variables requeridas por la plantilla base
                'saludo': saludo,
                'nombre_doctor': nombre_doctor,
                'doctor_profile_pic': doctor_profile_pic,
            }
            # Renderiza la misma plantilla, pero ahora mostrará los errores
            return render(request, 'odontologia/perfil.html', context)

    else: # Si el método no es POST (es GET), no debería llegar aquí directamente
        return redirect('ver_perfil')

# --- Vistas de Calendario y Detalles ---

@login_required
def detalle_atencion(request, pk):
    """Muestra los detalles de una atención específica."""
    # Busca la atención por su ID (pk) Y asegura que pertenezca al doctor logueado
    try:
        doctor = request.user.doctor
        atencion = get_object_or_404(Atencion, pk=pk, doctor=doctor)
    except Doctor.DoesNotExist:
        messages.error(request, 'Error: Tu usuario no está asociado a un perfil de Doctor.')
        return redirect('dashboard')
    except Atencion.DoesNotExist: # Si el ID no existe o no pertenece a este doctor
        messages.error(request, 'La atención solicitada no existe o no tienes permiso para verla.')
        return redirect('dashboard')

    # Obtiene los detalles y exámenes relacionados
    detalles_tratamiento = atencion.detalles.all() # Usa el related_name='detalles'
    examenes_solicitados = atencion.examenes.all() # Usa el related_name='examenes'

    # Datos para la plantilla base (saludo, nombre, foto)
    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    context = {
        'atencion': atencion,
        'detalles': detalles_tratamiento,
        'examenes': examenes_solicitados,
        # Datos para la plantilla base
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
    }
    return render(request, 'odontologia/detalle_atencion.html', context)

@login_required
def ver_calendario(request):
    """Muestra la página del calendario y le pasa los eventos."""

    # Obtener datos para la plantilla base (saludo, nombre, foto)
    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    eventos_calendario = []
    try:
        # Obtener el doctor y sus atenciones
        doctor = request.user.doctor
        atenciones = Atencion.objects.filter(doctor=doctor)

        # Formatear las atenciones para que FullCalendar las entienda
        for atencion in atenciones:
            eventos_calendario.append({
                'id': atencion.pk, # El ID de la atención
                'title': f"{atencion.paciente_nombre} {atencion.paciente_apellido}", # Título del evento
                'start': atencion.fecha.isoformat(), # Fecha (FullCalendar entiende 'YYYY-MM-DD')
                'allDay': True, # Marca el evento como de día completo
                'color': '#e83e8c' # Color rosa
            })

    except Doctor.DoesNotExist:
        messages.warning(request, 'No se encontró un perfil de doctor asociado.')

    context = {
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
        # Convertimos la lista de eventos a una cadena JSON segura
        'atenciones_json': json.dumps(eventos_calendario),
    }
    return render(request, 'odontologia/calendario.html', context)


@login_required
def atencion_json(request, pk):
    """Devuelve los detalles de una atención específica en formato JSON."""
    try:
        # Busca la atención por PK y se asegura que pertenezca al doctor logueado
        atencion = get_object_or_404(Atencion, pk=pk, doctor=request.user.doctor)

        # Prepara los datos de los detalles y exámenes
        detalles = list(atencion.detalles.all().values('especialidad', 'descripcion', 'valor'))
        examenes = list(atencion.examenes.all().values('examen__nombre', 'costo'))
        
        # Formatear valores como strings (para JSON)
        for d in detalles:
            d['valor'] = str(d['valor'])
        for e in examenes:
            e['costo'] = str(e['costo'])

        # Prepara el diccionario de datos para enviar
        data = {
            'paciente': f"{atencion.paciente_nombre} {atencion.paciente_apellido}",
            'rut': atencion.paciente_rut,
            'fecha': atencion.fecha.strftime("%d/%m/%Y"),
            'motivo': atencion.motivo_visita or "No especificado",
            'pago': atencion.get_metodo_pago_display(),
            'detalles': detalles,
            'examenes': examenes,
        }
        return JsonResponse(data)

    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Perfil de doctor no encontrado'}, status=403)
    except Atencion.DoesNotExist:
        return JsonResponse({'error': 'Atención no encontrada o no autorizada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def editar_atencion(request, pk):
    """Muestra el formulario para editar una atención existente."""
    try:
        doctor = request.user.doctor
        atencion = get_object_or_404(Atencion, pk=pk, doctor=doctor)
    except Doctor.DoesNotExist:
        messages.error(request, 'Error: Tu usuario no está asociado a un perfil de Doctor.')
        return redirect('dashboard')
    except Atencion.DoesNotExist:
        messages.error(request, 'No tienes permiso para editar esta atención.')
        return redirect('dashboard')

    # Definimos los Formsets (igual que en registrar_atencion)
    DetalleFormSet = inlineformset_factory(
        Atencion, DetalleAtencion, form=DetalleAtencionForm, extra=1, can_delete=True # Permitir borrar
    )
    ExamenFormSet = inlineformset_factory(
        Atencion, ExamenAtencion, form=ExamenAtencionForm, extra=1, can_delete=True # Permitir borrar
    )

    if request.method == 'POST':
        # Llenamos los formularios con los datos enviados (request.POST) Y la instancia existente
        form = AtencionForm(request.POST, instance=atencion)
        detalle_formset = DetalleFormSet(request.POST, instance=atencion, prefix='detalles')
        examen_formset = ExamenFormSet(request.POST, instance=atencion, prefix='examenes')

        if form.is_valid() and detalle_formset.is_valid() and examen_formset.is_valid():
            form.save()
            detalle_formset.save()
            examen_formset.save()
            messages.success(request, '¡Atención actualizada exitosamente!')
            return redirect('detalle_atencion', pk=atencion.pk) # Volver a la vista de detalle
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        # Llenamos los formularios con los datos de la instancia existente
        form = AtencionForm(instance=atencion)
        detalle_formset = DetalleFormSet(instance=atencion, prefix='detalles')
        examen_formset = ExamenFormSet(instance=atencion, prefix='examenes')

    # Datos para la plantilla base
    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    context = {
        'form': form,
        'detalle_formset': detalle_formset,
        'examen_formset': examen_formset,
        'is_edit': True, # Bandera para indicar a la plantilla que estamos editando
        # Datos para la plantilla base
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
    }
    # Reutilizamos la misma plantilla de 'registrar_atencion.html'
    return render(request, 'odontologia/registrar_atencion.html', context)


@login_required
def eliminar_atencion(request, pk):
    """Muestra la confirmación y maneja la eliminación de una atención."""
    try:
        doctor = request.user.doctor
        atencion = get_object_or_404(Atencion, pk=pk, doctor=doctor)
    except Doctor.DoesNotExist:
        messages.error(request, 'Error: Tu usuario no está asociado a un perfil de Doctor.')
        return redirect('dashboard')
    except Atencion.DoesNotExist:
        messages.error(request, 'No tienes permiso para eliminar esta atención.')
        return redirect('dashboard')

    if request.method == 'POST':
        # Si el formulario se envió (confirmación)
        atencion_paciente_nombre = atencion.paciente_nombre # Guardamos el nombre antes de borrar
        atencion.delete() # Elimina la atención (y sus detalles/exámenes en cascada)
        messages.success(request, f"La atención de {atencion_paciente_nombre} ha sido eliminada.")
        return redirect('dashboard') # Redirige al panel principal

    # Si es GET, muestra la página de confirmación
    # Datos para la plantilla base
    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    context = {
        'atencion': atencion,
        # Datos para la plantilla base
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
    }
    return render(request, 'odontologia/eliminar_atencion_confirm.html', context)