# odontologia/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView # <--- 1. Importa RedirectView
from . import views

urlpatterns = [
    # 2. Añade esta nueva línea AL PRINCIPIO de la lista
    #    Redirige la página principal ('') a la página de login ('/login/')
    path('', RedirectView.as_view(url='login/', permanent=False), name='index'),

    path('login/', auth_views.LoginView.as_view(template_name='odontologia/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar-atencion/', views.registrar_atencion, name='registrar_atencion'),
]