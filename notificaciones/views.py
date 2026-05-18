"""Vistas de Notificaciones — Huellitas Alegres

Marcar como leído (individual y masivo) y listar notificaciones.
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from .models import Notificacion


@login_required
@require_POST
def marcar_leido(request, pk):
    """Marcar una notificación como leída. Devuelve JSON."""
    notif = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notif.leido = True
    notif.save(update_fields=['leido'])
    count = request.user.notificaciones.filter(leido=False).count()
    return JsonResponse({'status': 'ok', 'count': count})


@login_required
@require_POST
def marcar_todos_leido(request):
    """Marcar todas las notificaciones del usuario como leídas."""
    updated = request.user.notificaciones.filter(leido=False).update(leido=True)
    return JsonResponse({'status': 'ok', 'updated': updated, 'count': 0})


@login_required
def listar_notificaciones(request):
    """Devolver las últimas 20 notificaciones del usuario como JSON (para AJAX)."""
    notifs = request.user.notificaciones.all()[:20]
    data = [
        {
            'id': n.pk,
            'tipo': n.tipo,
            'mensaje': n.mensaje,
            'url': n.url,
            'leido': n.leido,
            'fecha': n.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
        }
        for n in notifs
    ]
    return JsonResponse({'notificaciones': data})