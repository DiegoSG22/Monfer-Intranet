#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Recolectar archivos estáticos (CSS, JS, Imágenes del sistema)
python manage.py collectstatic --no-input

# Aplicar migraciones a la base de datos de la nube
python manage.py migrate

python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'Monfer2025') if not User.objects.filter(username='admin').exists() else print('El Superusuario ya existe')"