# odontologia/views.py
import json # Para formatear los eventos del calendario
from django.http import JsonResponse # Para la vista de API
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.forms import inlineformset_factory
from django.contrib import messages
# Importamos los modelos correctos (sin ExamenAtencion)
from .models import Doctor, Atencion, DetalleAtencion, Examen
# Importamos los forms correctos (sin ExamenAtencionForm)
from .forms import AtencionForm, DetalleAtencionForm
from .forms import UserUpdateForm, DoctorProfileForm # Importa forms de perfil
from django.templatetags.static import static # Para obtener URL estática del placeholder
import datetime # Importa datetime

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
        doctor = request.user.doctor
        # CORREGIDO: Ordenado por fecha Y hora
        atenciones_recientes = Atencion.objects.filter(doctor=doctor).order_by('-fecha', '-hora_atencion')[:5]
    except Doctor.DoesNotExist:
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
    Maneja el registro de una nueva atención con detalles.
    """
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, 'Error: Tu usuario no está asociado a un perfil de Doctor.')
        return redirect('dashboard')

    DetalleFormSet = inlineformset_factory(
        Atencion, DetalleAtencion, form=DetalleAtencionForm, extra=1, can_delete=False
    )
    # --- ExamenFormSet ELIMINADO ---

    if request.method == 'POST':
        form = AtencionForm(request.POST)
        detalle_formset = DetalleFormSet(request.POST, prefix='detalles')
        # --- examen_formset ELIMINADO ---

        # CORREGIDO: Eliminada validación de examen_formset
        if form.is_valid() and detalle_formset.is_valid():
            atencion = form.save(commit=False)
            atencion.doctor = doctor
            atencion.save()

            detalle_formset.instance = atencion
            detalle_formset.save()
            
            # --- guardado de examen_formset ELIMINADO ---

            messages.success(request, '¡Atención guardada con éxito!')
            return redirect('dashboard')
        else:
             messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AtencionForm()
        detalle_formset = DetalleFormSet(prefix='detalles')
        # --- examen_formset ELIMINADO ---

    nombre_doctor_display, doctor_profile_pic_display = get_doctor_data(request.user)
    saludo_display = get_saludo()

    context = {
        'form': form,
        'detalle_formset': detalle_formset,
        # --- examen_formset ELIMINADO ---
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
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.warning(request, 'No se encontró un perfil de doctor asociado a tu cuenta.')
        return redirect('dashboard')

    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    user_form = UserUpdateForm(instance=request.user)
    doctor_form = DoctorProfileForm(instance=doctor)

    context = {
        'user_form': user_form,
        'doctor_form': doctor_form,
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
    }
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
        doctor_form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)

        if user_form.is_valid() and doctor_form.is_valid():
            user_form.save()
            doctor_form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('ver_perfil')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            
            saludo = get_saludo()
            nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

            context = {
                'user_form': user_form,
                'doctor_form': doctor_form,
                'saludo': saludo,
                'nombre_doctor': nombre_doctor,
                'doctor_profile_pic': doctor_profile_pic,
            }
            return render(request, 'odontologia/perfil.html', context)

    else:
        return redirect('ver_perfil')

# --- Vistas de Calendario y Detalles ---

@login_required
def detalle_atencion(request, pk):
    """Muestra los detalles de una atención específica."""
    try:
        doctor = request.user.doctor
        atencion = get_object_or_404(Atencion, pk=pk, doctor=doctor)
    except Doctor.DoesNotExist:
        messages.error(request, 'Error: Tu usuario no está asociado a un perfil de Doctor.')
        return redirect('dashboard')
    except Atencion.DoesNotExist:
        messages.error(request, 'La atención solicitada no existe o no tienes permiso para verla.')
        return redirect('dashboard')

    detalles_tratamiento = atencion.detalles.all()
    # --- examenes_solicitados ELIMINADO ---

    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    context = {
        'atencion': atencion,
        'detalles': detalles_tratamiento,
        # --- examenes ELIMINADO ---
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
    }
    return render(request, 'odontologia/detalle_atencion.html', context)

@login_required
def ver_calendario(request):
    """Muestra la página del calendario y le pasa los eventos."""
    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    eventos_calendario = []
    try:
        doctor = request.user.doctor
        atenciones = Atencion.objects.filter(doctor=doctor)

        for atencion in atenciones:
            # CORREGIDO: Combinar fecha y hora
            start_datetime = datetime.datetime.combine(atencion.fecha, atencion.hora_atencion)
            eventos_calendario.append({
                'id': atencion.pk,
                'title': f"{atencion.paciente_nombre} {atencion.paciente_apellido}",
                'start': start_datetime.isoformat(), # Formato ISO 8601
                'allDay': False # Ya no es un evento de día completo
            })
    except Doctor.DoesNotExist:
        messages.warning(request, 'No se encontró un perfil de doctor asociado.')

    context = {
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
        'atenciones_json': json.dumps(eventos_calendario),
    }
    return render(request, 'odontologia/calendario.html', context)


@login_required
def atencion_json(request, pk):
    """Devuelve los detalles de una atención específica en formato JSON."""
    try:
        atencion = get_object_or_404(Atencion, pk=pk, doctor=request.user.doctor)

        detalles = list(atencion.detalles.all().values('especialidad', 'descripcion', 'valor'))
        # --- examenes ELIMINADO ---
        
        for d in detalles: d['valor'] = str(d['valor'])
        # --- bucle for para examenes ELIMINADO ---

        data = {
            'paciente': f"{atencion.paciente_nombre} {atencion.paciente_apellido}",
            'rut': atencion.paciente_rut,
            'fecha': atencion.fecha.strftime("%d/%m/%Y"),
            'hora': atencion.hora_atencion.strftime("%H:%M"), # Añadir hora
            'motivo': atencion.motivo_visita or "No especificado",
            'pago': atencion.get_metodo_pago_display(),
            'detalles': detalles,
            # --- examenes ELIMINADO ---
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

    DetalleFormSet = inlineformset_factory(
        Atencion, DetalleAtencion, form=DetalleAtencionForm, extra=1, can_delete=True
    )
    # --- ExamenFormSet ELIMINADO ---

    if request.method == 'POST':
        form = AtencionForm(request.POST, instance=atencion)
        detalle_formset = DetalleFormSet(request.POST, instance=atencion, prefix='detalles')
        # --- examen_formset ELIMINADO ---

        # CORREGIDO: Eliminada validación de examen_formset
        if form.is_valid() and detalle_formset.is_valid():
            form.save()
            detalle_formset.save()
            # --- examen_formset.save() ELIMINADO ---
            messages.success(request, '¡Atención actualizada exitosamente!')
            return redirect('detalle_atencion', pk=atencion.pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AtencionForm(instance=atencion)
        detalle_formset = DetalleFormSet(instance=atencion, prefix='detalles')
        # --- examen_formset ELIMINADO ---

    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    context = {
        'form': form,
        'detalle_formset': detalle_formset,
        # --- examen_formset ELIMINADO ---
        'is_edit': True,
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
    }
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
        atencion_paciente_nombre = atencion.paciente_nombre
        atencion.delete()
        messages.success(request, f"La atención de {atencion_paciente_nombre} ha sido eliminada.")
        return redirect('dashboard')

    saludo = get_saludo()
    nombre_doctor, doctor_profile_pic = get_doctor_data(request.user)

    context = {
        'atencion': atencion,
        'saludo': saludo,
        'nombre_doctor': nombre_doctor,
        'doctor_profile_pic': doctor_profile_pic,
    }
    return render(request, 'odontologia/eliminar_atencion_confirm.html', context)