"""Context processor para inyectar notificaciones no leídas en todos los templates.

Inyecta:
  - notificaciones_no_leidas: queryset de las 10 notificaciones más recientes no leídas
  - notificaciones_count: cantidad de notificaciones no leídas (para el badge)
"""


def notificaciones_context(request):
    """Inyectar contador y lista de notificaciones no leídas para usuarios autenticados."""
    if not request.user.is_authenticated:
        return {
            'notificaciones_no_leidas': [],
            'notificaciones_count': 0,
        }

    qs = request.user.notificaciones.filter(leido=False)[:10]
    return {
        'notificaciones_no_leidas': qs,
        'notificaciones_count': qs.count() if hasattr(qs, 'count') else len(qs),
    }