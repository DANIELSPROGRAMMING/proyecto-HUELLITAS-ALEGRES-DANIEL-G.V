"""Tests for the notification system — model, helpers, views, context processor."""

import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from notificaciones.models import Notificacion
from notificaciones.helpers import notify, notify_role
from usuarios.models import Rol

Usuario = get_user_model()


class NotificacionModelTest(TestCase):
    """Test the Notificacion model."""

    def setUp(self):
        self.rol = Rol.objects.get(nombre='Administrador')
        self.user = Usuario.objects.create_user(
            username='testuser', email='testuser@test.com', password='testpass123*',
            first_name='Test', last_name='User', rol=self.rol,
        )

    def test_create_notification(self):
        n = Notificacion.objects.create(
            usuario=self.user, tipo='cita', mensaje='Test notification', url='/agenda/citas/'
        )
        self.assertEqual(n.usuario, self.user)
        self.assertEqual(n.tipo, 'cita')
        self.assertFalse(n.leido)
        self.assertIsNotNone(n.fecha_creacion)

    def test_str_representation_unread(self):
        n = Notificacion.objects.create(usuario=self.user, tipo='sistema', mensaje='A' * 100)
        self.assertIn('●', str(n))

    def test_str_representation_read(self):
        n = Notificacion.objects.create(usuario=self.user, tipo='sistema', mensaje='Read notif', leido=True)
        self.assertIn('✓', str(n))

    def test_ordering_newest_first(self):
        """Notifications with same timestamp still maintain creation order."""
        Notificacion.objects.create(usuario=self.user, tipo='sistema', mensaje='First')
        Notificacion.objects.create(usuario=self.user, tipo='cita', mensaje='Second')
        qs = self.user.notificaciones.all()
        self.assertEqual(qs[0].mensaje, 'Second')
        self.assertEqual(qs[1].mensaje, 'First')


class HelpersTest(TestCase):
    """Test notify() and notify_role() helpers."""

    def setUp(self):
        self.rol_admin = Rol.objects.get(nombre='Administrador')
        self.rol_vet = Rol.objects.get(nombre='Veterinario')
        self.user = Usuario.objects.create_user(
            username='vet1', email='vet1@test.com', password='testpass123*',
            first_name='Dr.', last_name='House', rol=self.rol_vet,
        )
        self.admin = Usuario.objects.create_user(
            username='admin1', email='admin1@test.com', password='testpass123*',
            first_name='Admin', last_name='One', rol=self.rol_admin,
        )

    def test_notify_creates_one(self):
        n = notify(self.user, 'Test message', tipo='cita', url='/test/')
        self.assertEqual(n.usuario, self.user)
        self.assertEqual(n.mensaje, 'Test message')
        self.assertEqual(n.tipo, 'cita')
        self.assertEqual(n.url, '/test/')

    def test_notify_default_values(self):
        n = notify(self.user, 'Simple')
        self.assertEqual(n.tipo, 'sistema')
        self.assertEqual(n.url, '')

    def test_notify_role_creates_for_all(self):
        results = notify_role('Administrador', 'Admin broadcast', tipo='stock')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].mensaje, 'Admin broadcast')

    def test_notify_role_empty_role(self):
        results = notify_role('NonExistent', 'Test')
        self.assertEqual(len(results), 0)


class ContextProcessorTest(TestCase):
    """Test the notificaciones_context processor."""

    def setUp(self):
        self.rol = Rol.objects.get(nombre='Cliente')
        self.user = Usuario.objects.create_user(
            username='cliente1', email='cp1@test.com', password='testpass123*',
            first_name='Juan', rol=self.rol,
        )

    def test_unauthenticated_returns_empty(self):
        from notificaciones.context_processors import notificaciones_context
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/')
        request.user = type('FakeUser', (), {'is_authenticated': False})()
        ctx = notificaciones_context(request)
        self.assertEqual(ctx['notificaciones_count'], 0)
        self.assertEqual(ctx['notificaciones_no_leidas'], [])

    def test_authenticated_with_notifications(self):
        from notificaciones.context_processors import notificaciones_context
        from django.test import RequestFactory

        Notificacion.objects.create(usuario=self.user, tipo='cita', mensaje='Unread 1')
        Notificacion.objects.create(usuario=self.user, tipo='pedido', mensaje='Unread 2')
        Notificacion.objects.create(usuario=self.user, tipo='sistema', mensaje='Read', leido=True)

        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        ctx = notificaciones_context(request)
        self.assertEqual(ctx['notificaciones_count'], 2)


class NotificacionesViewTest(TestCase):
    """Test notification views (mark as read, etc.)."""

    def setUp(self):
        self.rol = Rol.objects.get(nombre='Cliente')
        self.user = Usuario.objects.create_user(
            username='vw1', email='vw1@test.com', password='testpass123*', rol=self.rol,
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_marcar_leido(self):
        n = Notificacion.objects.create(usuario=self.user, tipo='cita', mensaje='Test')
        self.assertFalse(n.leido)
        response = self.client.post(f'/notificaciones/marcar-leido/{n.pk}/')
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.leido)

    def test_marcar_leido_other_user_forbidden(self):
        other = Usuario.objects.create_user(
            username='other', email='other@test.com', password='testpass123*', rol=self.rol,
        )
        n = Notificacion.objects.create(usuario=other, tipo='cita', mensaje='Someone else')
        response = self.client.post(f'/notificaciones/marcar-leido/{n.pk}/')
        self.assertEqual(response.status_code, 404)

    def test_marcar_todos_leido(self):
        Notificacion.objects.create(usuario=self.user, tipo='cita', mensaje='A')
        Notificacion.objects.create(usuario=self.user, tipo='pedido', mensaje='B')
        response = self.client.post('/notificaciones/marcar-todos-leido/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notificacion.objects.filter(usuario=self.user, leido=False).count(), 0)

    def test_listar_notificaciones(self):
        Notificacion.objects.create(usuario=self.user, tipo='cita', mensaje='Test')
        response = self.client.get('/notificaciones/listar/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['notificaciones']), 1)