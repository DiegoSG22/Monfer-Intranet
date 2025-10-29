# odontologia/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
# Las importaciones de settings y static no son necesarias aquí
from django.views.generic import RedirectView 
from . import views

# La lista no debe estar indentada
urlpatterns = [
    # Redirige la página principal ('') a la página de login ('/login/')
    path('', RedirectView.as_view(url='login/', permanent=False), name='index'),

    # Rutas de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='odontologia/login.html'), name='login'),
    # Esta ruta de logout funciona con el formulario (botón) que usa POST
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'), 
    
    # Rutas de la aplicación
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar-atencion/', views.registrar_atencion, name='registrar_atencion'),
    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('atencion/<int:pk>/', views.detalle_atencion, name='detalle_atencion'),

    # Rutas del calendario
    path('calendario/', views.ver_calendario, name='ver_calendario'),
    path('api/atencion/<int:pk>/', views.atencion_json, name='atencion_json'),
    
    path('atencion/<int:pk>/editar/', views.editar_atencion, name='editar_atencion'),
    path('atencion/<int:pk>/eliminar/', views.eliminar_atencion, name='eliminar_atencion'),
]