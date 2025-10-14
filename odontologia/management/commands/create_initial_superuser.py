# odontologia/management/commands/create_initial_superuser.py

import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Crea un superusuario si no existe ninguno'

    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('Un superusuario ya existe. Saltando.'))
            return

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stderr.write(self.style.ERROR(
                'Faltan las variables de entorno DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL o DJANGO_SUPERUSER_PASSWORD'
            ))
            return

        self.stdout.write(f"Creando superusuario '{username}'...")
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS('Superusuario creado exitosamente.'))