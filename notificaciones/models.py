"""Modelo de Notificaciones — Huellitas Alegres

Sistema de notificaciones basado en base de datos (polling).
Cada notificación va dirigida a un usuario específico con tipo, mensaje y enlace.
"""

from django.db import models
from django.conf import settings


class Notificacion(models.Model):
    """Notificación individual dirigida a un usuario del sistema."""

    TIPO_CHOICES = [
        ('cita', '📅 Cita'),
        ('pedido', '📦 Pedido'),
        ('stock', '🚨 Inventario'),
        ('sistema', 'ℹ️ Sistema'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Usuario destino',
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='sistema',
        verbose_name='Tipo de notificación',
    )
    mensaje = models.TextField(
        verbose_name='Mensaje',
        help_text='Texto de la notificación visible por el usuario.',
    )
    url = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='URL de destino',
        help_text='Enlace interno al que lleva al hacer clic. Dejar vacío si no aplica.',
    )
    leido = models.BooleanField(
        default=False,
        verbose_name='Leído',
        db_index=True,
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        db_table = 'notificaciones_notificacion'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leido', '-fecha_creacion'], name='notif_user_leido_date'),
        ]

    def clean(self):
        """Validate that url is an internal path (starts with /) if provided."""
        from django.core.exceptions import ValidationError
        if self.url and not self.url.startswith('/'):
            raise ValidationError({'url': 'La URL debe ser una ruta interna que empiece con /'})

    def save(self, *args, **kwargs):
        """Ensure clean() validation runs on every save."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        estado = '✓' if self.leido else '●'
        return f'{estado} [{self.get_tipo_display()}] {self.mensaje[:50]}'