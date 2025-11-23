#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Recolectar archivos estáticos (CSS, JS, Imágenes del sistema)
python manage.py collectstatic --no-input

# Aplicar migraciones a la base de datos de la nube
python manage.py migrate