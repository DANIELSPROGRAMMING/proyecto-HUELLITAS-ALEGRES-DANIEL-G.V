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

    def test_category_name_not_false_positive(self):
        """Category names like 'higiene' must not match keywords like 'hi' inside them."""
        from chatbot.views import _detect_intent
        # 'hi' is a bienvenida keyword, but 'higiene' is a product category
        self.assertEqual(_detect_intent('higiene'), 'producto')
        self.assertEqual(_detect_intent('higiene y cuidado'), 'producto')
        # 'hi' alone should still be bienvenida
        self.assertEqual(_detect_intent('hi'), 'bienvenida')

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
        # Response comes from ConfiguracionClinica (real data) or fallback —
        # both include "Dirección:" so we assert structural content, not hardcoded addresses.
        self.assertIn('Dirección:', data['response'])

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

    # ── Three-tier product flow tests ──

    def test_product_tier1_categories_only(self):
        """Step 1: 'productos' with no search terms shows categories with counts, no prices."""
        from productos.models import Producto
        # Seed test products so categories have stock
        Producto.objects.create(nombre='Test Alimento', categoria='alimentos', precio=10000, cantidad_stock=50)
        Producto.objects.create(nombre='Test Higiene', categoria='higiene', precio=15000, cantidad_stock=30)
        response, data = self._post('productos')
        self.assertEqual(response.status_code, 200)
        # Should show category listing
        self.assertIn('Categor', data['response'])
        # Should NOT contain price format at this tier
        self.assertNotIn('$', data['response'])
        # Clean up
        Producto.objects.filter(nombre__in=['Test Alimento', 'Test Higiene']).delete()

    def test_product_tier2_category_names_no_prices(self):
        """Step 2: Typing a category name lists product names without prices."""
        from productos.models import Producto
        Producto.objects.create(nombre='Concentrado Test', categoria='alimentos', precio=75000, cantidad_stock=20)
        response, data = self._post('alimentos')
        self.assertEqual(response.status_code, 200)
        # Should show the product name
        self.assertIn('Concentrado Test', data['response'])
        # Should invite user to ask for price
        self.assertIn('precio', data['response'].lower())
        # Should NOT show $ at this tier
        self.assertNotIn('$', data['response'])
        # Clean up
        Producto.objects.filter(nombre='Concentrado Test').delete()

    def test_product_tier3_search_shows_prices(self):
        """Step 3: Specific product search shows price details."""
        from productos.models import Producto
        Producto.objects.create(nombre='Shampoo Test Precio', categoria='higiene', precio=32000, cantidad_stock=10)
        response, data = self._post('precio de shampoo')
        self.assertEqual(response.status_code, 200)
        # Price search should show $ symbol
        self.assertIn('$', data['response'])
        # Clean up
        Producto.objects.filter(nombre='Shampoo Test Precio').delete()