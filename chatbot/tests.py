"""Tests for chatbot rule-based engine."""

import json

from django.test import TestCase, Client


class DetectIntentTests(TestCase):
    """Test keyword-based intent detection."""

    def test_greeting(self):
        from chatbot.views import _detect_intent
        self.assertEqual(_detect_intent('hola'), 'bienvenida')
        self.assertEqual(_detect_intent('buenas tardes'), 'bienvenida')
        self.assertEqual(_detect_intent('hey'), 'bienvenida')

    def test_location(self):
        from chatbot.views import _detect_intent
        self.assertEqual(_detect_intent('donde queda la clinica'), 'ubicacion')
        self.assertEqual(_detect_intent('direccion'), 'ubicacion')

    def test_schedule(self):
        from chatbot.views import _detect_intent
        self.assertEqual(_detect_intent('horario'), 'horario')
        self.assertEqual(_detect_intent('que horas atienden'), 'horario')

    def test_emergency(self):
        from chatbot.views import _detect_intent
        self.assertEqual(_detect_intent('urgencia'), 'urgencia')
        self.assertEqual(_detect_intent('mi perro no respira'), 'urgencia')

    def test_product(self):
        from chatbot.views import _detect_intent
        self.assertEqual(_detect_intent('precio de vacuna'), 'producto')
        self.assertEqual(_detect_intent('cuanto vale el alimento'), 'producto')
        self.assertEqual(_detect_intent('medicamento para mi gato'), 'producto')

    def test_appointment(self):
        from chatbot.views import _detect_intent
        self.assertEqual(_detect_intent('cita'), 'cita')
        self.assertEqual(_detect_intent('agendar cita'), 'cita')
        self.assertEqual(_detect_intent('disponibilidad'), 'cita')

    def test_emergency_priority_over_others(self):
        """Urgency has highest priority — 'urgencia' wins even with other keywords."""
        from chatbot.views import _detect_intent
        self.assertEqual(_detect_intent('urgencia cita'), 'urgencia')

    def test_fallback(self):
        from chatbot.views import _detect_intent
        self.assertEqual(_detect_intent('xyz abc random'), 'fallback')
        self.assertEqual(_detect_intent(''), 'fallback')


class ChatbotViewTests(TestCase):
    """Test the procesar_chat view endpoint using Django Client (includes auth middleware)."""

    def setUp(self):
        self.client = Client()

    def _post(self, message):
        """Helper to POST a chat message and return parsed JSON."""
        response = self.client.post(
            '/chatbot/procesar/',
            data=json.dumps({'message': message}),
            content_type='application/json',
        )
        return response, json.loads(response.content)

    def test_post_greeting(self):
        response, data = self._post('hola')
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', data)
        self.assertIn('quick_replies', data)
        self.assertIn('👋', data['response'])

    def test_post_location(self):
        response, data = self._post('ubicacion')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Calle 30', data['response'])

    def test_post_emergency(self):
        response, data = self._post('urgencia')
        self.assertEqual(response.status_code, 200)
        self.assertIn('24/7', data['response'])

    def test_post_fallback(self):
        response, data = self._post('xyzrandom123')
        self.assertEqual(response.status_code, 200)
        self.assertIn('No estoy seguro', data['response'])

    def test_empty_message(self):
        response, data = self._post('')
        self.assertEqual(response.status_code, 200)
        self.assertIn('👋', data['response'])

    def test_invalid_json(self):
        response = self.client.post(
            '/chatbot/procesar/',
            data='invalid json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('response', data)

    def test_get_not_allowed(self):
        """GET requests should return 405 (require_POST)."""
        response = self.client.get('/chatbot/procesar/')
        self.assertEqual(response.status_code, 405)

    def test_product_query(self):
        response, data = self._post('precio vacuna')
        self.assertEqual(response.status_code, 200)
        self.assertIn('quick_replies', data)

    def test_appointment_query(self):
        response, data = self._post('cita')
        self.assertEqual(response.status_code, 200)
        self.assertIn('quick_replies', data)

    def test_quick_replies_structure(self):
        """Every response must include quick_replies as a list."""
        response, data = self._post('horario')
        self.assertIsInstance(data['quick_replies'], list)
        self.assertTrue(len(data['quick_replies']) > 0)