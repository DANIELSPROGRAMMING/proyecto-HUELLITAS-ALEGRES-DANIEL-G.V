"""Custom template filters for historial app."""

import os
from django import template

register = template.Library()


@register.filter(name='last_path')
def last_path(value):
    """Return the last component of a file path.

    Usage: {{ adjunto.archivo.name|last_path }}
    Returns: 'documento.pdf' from 'evidencias/1/documento.pdf'
    """
    if not value:
        return ''
    return os.path.basename(str(value))