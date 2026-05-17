"""Utility functions for sending emails from Huellitas Alegres.

Uses Django's console.EmailBackend for development — emails are printed
to the terminal. In production, switch to SMTP backend in settings.py.
"""

from django.core.mail import send_mail
from django.conf import settings


def send_registration_confirmation(user):
    """Send a welcome email to a newly registered user.

    HU#1 criterion: «El sistema debe enviar un correo electrónico
    de confirmación al nuevo usuario para verificar su dirección de
    correo electrónico.»

    With console.EmailBackend, the email appears in the Django
    development server terminal output.
    """
    subject = 'Registro exitoso — Huellitas Alegres'
    message = (
        f'Hola {user.first_name or user.username},\n\n'
        f'Tu cuenta en Huellitas Alegres ha sido creada exitosamente.\n\n'
        f'Correo registrado: {user.email}\n'
        f'Rol asignado: {user.rol.nombre}\n\n'
        f'Ya puedes iniciar sesión en el sistema.\n\n'
        f'— Equipo Huellitas Alegres'
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        # Don't break registration if email fails
        pass


def send_cita_confirmation(cita, cliente_email):
    """Send a confirmation email when a client books an appointment.

    HU#5 criterion: «El sistema debe enviar una confirmación de la cita
    al cliente, ya sea por correo electrónico o mediante notificación
    en la interfaz del sistema.»

    With console.EmailBackend, the email appears in the Django
    development server terminal output.
    """
    mascota_nombre = cita.mascota.nombre if cita.mascota else 'N/A'
    fecha = cita.disponibilidad.fecha.strftime('%d/%m/%Y') if cita.disponibilidad else 'N/A'
    hora_inicio = cita.disponibilidad.hora_inicio.strftime('%H:%M') if cita.disponibilidad else 'N/A'
    hora_fin = cita.disponibilidad.hora_fin.strftime('%H:%M') if cita.disponibilidad else 'N/A'
    vet = cita.disponibilidad.veterinario.get_full_name() if cita.disponibilidad else 'N/A'
    motivo = cita.motivo or 'No especificado'

    subject = f'Confirmación de cita — {mascota_nombre} — Huellitas Alegres'
    message = (
        f'Estimado/a,\n\n'
        f'Su cita ha sido programada exitosamente.\n\n'
        f'Detalles de la cita:\n'
        f'  Paciente: {mascota_nombre}\n'
        f'  Fecha: {fecha}\n'
        f'  Hora: {hora_inicio} — {hora_fin}\n'
        f'  Veterinario: {vet}\n'
        f'  Motivo: {motivo}\n\n'
        f'Si necesita reprogramar, puede hacerlo desde su panel de usuario.\n\n'
        f'— Equipo Huellitas Alegres'
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente_email],
            fail_silently=True,
        )
    except Exception:
        pass