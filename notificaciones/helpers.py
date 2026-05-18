"""Helper para crear notificaciones desde cualquier vista del sistema.

Uso:
    from notificaciones.helpers import notify

    notify(usuario_destino, 'mensaje', tipo='cita', url='/agenda/citas/1/')
"""


def notify(usuario, mensaje, tipo='sistema', url=''):
    """Crear una notificación para un usuario.

    Args:
        usuario: User instance — destino de la notificación.
        mensaje: str — texto visible de la notificación.
        tipo: str — uno de 'cita', 'pedido', 'stock', 'sistema'.
        url: str — enlace interno al que lleva al hacer clic.

    Returns:
        Notificacion instance.
    """
    from .models import Notificacion

    return Notificacion.objects.create(
        usuario=usuario,
        tipo=tipo,
        mensaje=mensaje,
        url=url,
    )


def notify_role(rol_nombre, mensaje, tipo='sistema', url=''):
    """Crear notificaciones para TODOS los usuarios con un rol dado.

    Args:
        rol_nombre: str — nombre del rol (ej. 'Administrador', 'Veterinario').
        mensaje: str — texto visible.
        tipo: str — tipo de notificación.
        url: str — enlace interno.

    Returns:
        list of Notificacion instances created.
    """
    from usuarios.models import Usuario

    usuarios = Usuario.objects.filter(rol__nombre=rol_nombre, is_active=True)
    return [notify(u, mensaje, tipo, url) for u in usuarios]