# mi_web/urls.py

from django.contrib import admin
from django.urls import path, include
# Importaciones necesarias para ver imágenes en desarrollo
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # La ruta para el panel de administración sigue igual
    path('admin/', admin.site.urls),

    # Conecta todas las URLs de tu app 'odontologia' a la raíz del sitio
    path('', include('odontologia.urls')),
]

# Añade esto al final para poder ver las fotos de perfil
# que subas en tu entorno de desarrollo local (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)