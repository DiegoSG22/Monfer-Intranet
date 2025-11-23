"""
Django settings for mi_web project.
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configuración Inteligente ---
if 'DATABASE_URL' in os.environ:
    # --- Configuración para Producción (Render) ---
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    ALLOWED_HOSTS = ['https://monfer-intranet.onrender.com', '.onrender.com']
    CSRF_TRUSTED_ORIGINS = ['https://monfer-intranet.onrender.com']
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # --- Configuración para Desarrollo Local (Tu PC) ---
    SECRET_KEY = 'django-insecure-zunad+1--#c)p9emx-!#qma5!0*0+*wrqu9@!-w#30ifm!md#d'
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mi_sitio_db',
            'USER': 'postgres',
            'PASSWORD': 'perlita',
            'HOST': 'localhost',
            'PORT': '5433', # Asegúrate de que este puerto sea correcto
        }
    }
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# --- Resto de la configuración (común para ambos entornos) ---

INSTALLED_APPS = [
    'jazzmin', # Jazzmin debe ir ANTES de admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'odontologia',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mi_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mi_web.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'odontologia', 'static'), # Asegúrate que Django también encuentre los static de odontologia
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirección después del login
LOGIN_REDIRECT_URL = '/dashboard/'

# --- CONFIGURACIÓN DE JAZZMIN MEJORADA ---
JAZZMIN_SETTINGS = {
    # Títulos
    "site_title": "Intranet Monfer",
    "site_header": "Monfer SPA",
    "welcome_sign": "Bienvenido a la Intranet de Monfer SPA",

    # Logo (asegúrate que 'dental_v_logo.png' esté en 'static/images/')
    "site_logo": "images/dental_v_logo.png",
    "login_logo_size": "200px",

    # Tema
    "theme": "pulse", # Un tema limpio y moderno (alternativas: litera, lux, minty)

    # Copyright
    "copyright": "Monfer SPA Ltd.",

    # CSS Personalizado (el que ya tenías)
    "custom_css": "css/admin_custom.css",

    # --- Organización del Menú Lateral ---
    "order_with_respect_to": [
        # Primero la app Odontologia, con este orden:
        "odontologia.Atencion",
        "odontologia.Doctor",
        "odontologia.Tratamiento",
        "odontologia.Examen",
        "odontologia.Boleta",
        # Luego la app de Autenticación
        "auth.User",
        "auth.Group",
    ],

    # Cambiar nombres de las apps
    "apps": {
        "odontologia": "Gestión Clínica",
        "auth": "Administración de Usuarios",
    },

    # Ocultar modelos que no usamos
    "hide_models": [
        "odontologia.Paciente", # Oculta el modelo Paciente (ya que usamos campos en Atencion)
        "odontologia.DetalleAtencion", # Se maneja dentro de Atencion
        "odontologia.ExamenAtencion",  # Se maneja dentro de Atencion
    ],

    # Iconos para los modelos (usando Font Awesome)
    "icons": {
        "auth.User": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "odontologia.Atencion": "fas fa-calendar-check",
        "odontologia.Doctor": "fas fa-user-md",
        "odontologia.Tratamiento": "fas fa-tooth",
        "odontologia.Examen": "fas fa-vial",
        "odontologia.Boleta": "fas fa-file-invoice-dollar",
    },
}