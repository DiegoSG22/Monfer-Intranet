# odontologia/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from .models import Doctor, Atencion, DetalleAtencion, ExamenAtencion
from .forms import AtencionForm # Asegúrate de importar el formulario

@login_required
def dashboard(request):
    """
    Esta es la función que faltaba. Muestra el panel principal.
    """
    context = {
        'nombre_usuario': request.user.first_name
    }
    return render(request, 'odontologia/dashboard.html', context)

@login_required
def registrar_atencion(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    DetalleFormSet = inlineformset_factory(
        Atencion, DetalleAtencion, fields=('tratamiento', 'valor'), extra=1
    )
    ExamenFormSet = inlineformset_factory(
        Atencion, ExamenAtencion, fields=('examen', 'costo'), extra=1
    )

    if request.method == 'POST':
        form = AtencionForm(request.POST)
        detalle_formset = DetalleFormSet(request.POST)
        examen_formset = ExamenFormSet(request.POST)

        if form.is_valid() and detalle_formset.is_valid() and examen_formset.is_valid():
            atencion = form.save(commit=False)
            atencion.doctor = doctor
            atencion.save()

            detalle_formset.instance = atencion
            detalle_formset.save()

            examen_formset.instance = atencion
            examen_formset.save()

            return redirect('dashboard')
    else:
        form = AtencionForm()
        detalle_formset = DetalleFormSet()
        examen_formset = ExamenFormSet()

    context = {
        'form': form,
        'detalle_formset': detalle_formset,
        'examen_formset': examen_formset,
    }
    return render(request, 'odontologia/registrar_atencion.html', context)