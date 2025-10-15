# mi_web/urls.py

from django.contrib import admin
from django.urls import path, include # Importa 'include'

urlpatterns = [
    # La ruta para el panel de administración sigue igual
    path('admin/', admin.site.urls),

    # Conecta todas las URLs de tu app 'odontologia' a la raíz del sitio
    path('', include('odontologia.urls')),
]