"""Management command to ensure the admin user exists and has Django Admin access.

Runs on every Railway deploy via Procfile. Creates the admin user if missing,
then grants is_staff + is_superuser. Reads DJANGO_ADMIN_EMAIL and
DJANGO_ADMIN_PASSWORD from environment variables.
"""
import os
from django.core.management.base import BaseCommand
from usuarios.models import Usuario, Rol


class Command(BaseCommand):
    help = 'Crea (si no existe) y garantiza acceso al Django Admin para el administrador'

    def handle(self, *args, **options):
        email = os.getenv('DJANGO_ADMIN_EMAIL', 'admin@huellitas.com')
        password = os.getenv('DJANGO_ADMIN_PASSWORD')

        admin = Usuario.objects.filter(email=email).first()

        if admin is None:
            if not password:
                self.stdout.write(self.style.ERROR(
                    f'DJANGO_ADMIN_PASSWORD no está configurada. '
                    f'No se puede crear el admin {email}.'
                ))
                return

            rol_admin = Rol.objects.filter(nombre='Administrador').first()
            if not rol_admin:
                self.stdout.write(self.style.ERROR(
                    'Rol "Administrador" no encontrado en la base de datos.'
                ))
                return

            admin = Usuario.objects.create_user(
                email=email,
                password=password,
                nombre='Admin',
                apellido='Huellitas',
                rol=rol_admin,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS(
                f'✅ Admin {email} creado con acceso al Django Admin'
            ))
            return

        # User exists — ensure permissions
        updated = []
        if not admin.is_staff:
            admin.is_staff = True
            updated.append('is_staff')
        if not admin.is_superuser:
            admin.is_superuser = True
            updated.append('is_superuser')
        if updated:
            admin.save()
            self.stdout.write(self.style.SUCCESS(
                f'✅ Admin {email} ahora tiene: {", ".join(updated)}'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✅ Admin {email} ya tenía acceso completo'
            ))
