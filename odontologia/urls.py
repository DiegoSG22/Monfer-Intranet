from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='odontologia/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # ✅ ASEGÚRATE DE QUE ESTA LÍNEA EXISTA Y ESTÉ BIEN ESCRITA
    path('registrar-atencion/', views.registrar_atencion, name='registrar_atencion'),
]