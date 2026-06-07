"""Management command to ensure the admin user has Django Admin access."""
from django.core.management.base import BaseCommand
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Garantiza que el admin tenga is_staff e is_superuser'

    def handle(self, *args, **options):
        admin = Usuario.objects.filter(
            email='admin.huellitas@gmail.com',
            rol__nombre='Administrador',
        ).first()

        if admin:
            updated = False
            if not admin.is_staff:
                admin.is_staff = True
                updated = True
            if not admin.is_superuser:
                admin.is_superuser = True
                updated = True
            if updated:
                admin.save()
                self.stdout.write(self.style.SUCCESS('✅ Admin ahora tiene acceso al Django Admin'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ Admin ya tenía acceso'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ No se encontró admin.huellitas@gmail.com'))
