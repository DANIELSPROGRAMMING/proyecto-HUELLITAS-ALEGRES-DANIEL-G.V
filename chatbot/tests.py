"""Tests for chatbot rule-based engine."""

import json

from unittest.mock import patch, MagicMock
import requests

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
        # Prevent real NIM API calls during existing view tests.
        # Mock NimClient to always raise so the hybrid dispatch falls back
        # to STATIC_RESPONSES['fallback'] — preserving pre-NIM test expectations.
        nim_patcher = patch('chatbot.views.NimClient')
        self.MockNimClient = nim_patcher.start()
        mock_instance = MagicMock()
        mock_instance.send.side_effect = Exception("Mocked NIM unavailable")
        self.MockNimClient.return_value = mock_instance
        self.addCleanup(nim_patcher.stop)

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


# ──────────────────────────────────────────────
# Phase 4 Tests — NVIDIA NIM Hybrid Integration
# ──────────────────────────────────────────────


class NimClientTests(TestCase):
    """Test NimClient HTTP wrapper."""

    def setUp(self):
        from chatbot.services.nim_client import NimClient
        self.client = NimClient(
            api_key='test-key',
            base_url='https://api.nvidia.com',
            model='test-model',
            timeout=5,
        )
        self.system_prompt = "You are a helpful assistant."
        self.user_message = "Hello"

    @patch('chatbot.services.nim_client.requests.post')
    def test_send_success_returns_raw_text(self, mock_post):
        """NimClient.send() returns text on successful API response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': "Sure! Here is the answer.\n"}}]
        }
        mock_post.return_value = mock_response

        result = self.client.send(self.user_message, self.system_prompt)
        self.assertIsInstance(result, str)
        self.assertIn("Sure!", result)

    @patch('chatbot.services.nim_client.requests.post')
    def test_send_payload_format(self, mock_post):
        """NimClient.send() formats OpenAI-compatible chat completions payload."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response

        self.client.send("¿Tienen comida para gatos?", "Eres un asistente.")

        # Verify payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        messages = payload['messages']
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[0]['content'], 'Eres un asistente.')
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[1]['content'], '¿Tienen comida para gatos?')
        # Verify headers
        headers = call_args[1]['headers']
        self.assertIn('Authorization', headers)
        self.assertIn('test-key', headers['Authorization'])

    @patch('chatbot.services.nim_client.requests.post')
    def test_send_timeout_raises_request_exception(self, mock_post):
        """NimClient.send() raises RequestException on timeout."""
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")
        with self.assertRaises(requests.RequestException):
            self.client.send(self.user_message, self.system_prompt)

    @patch('chatbot.services.nim_client.requests.post')
    def test_send_http_error_raises_request_exception(self, mock_post):
        """NimClient.send() raises RequestException on HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_post.return_value = mock_response

        with self.assertRaises(requests.RequestException):
            self.client.send(self.user_message, self.system_prompt)

    @patch('chatbot.services.nim_client.requests.post')
    def test_send_invalid_api_key_401(self, mock_post):
        """NimClient.send() raises RequestException on 401 Unauthorized."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response

        with self.assertRaises(requests.RequestException):
            self.client.send(self.user_message, self.system_prompt)

    @patch('chatbot.services.nim_client.requests.post')
    def test_send_invalid_api_key_403(self, mock_post):
        """NimClient.send() raises RequestException on 403 Forbidden."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
        mock_post.return_value = mock_response

        with self.assertRaises(requests.RequestException):
            self.client.send(self.user_message, self.system_prompt)


class NimFormatterTests(TestCase):
    """Test NimResponseFormatter parsing."""

    def test_parse_valid_json(self):
        """Valid JSON → correct dict with response and quick_replies."""
        from chatbot.services.nim_formatter import NimResponseFormatter
        raw = '{"response": "Hola, ¿en qué te ayudo?", "quick_replies": ["Precios", "Citas"]}'
        result = NimResponseFormatter.parse(raw)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['response'], 'Hola, ¿en qué te ayudo?')
        self.assertEqual(result['quick_replies'], ['Precios', 'Citas'])

    def test_parse_plain_text_fallback(self):
        """Plain text (not JSON) → text becomes response, quick_replies=defaults."""
        from chatbot.services.nim_formatter import NimResponseFormatter
        raw = "Hola, soy el asistente de la clínica."
        result = NimResponseFormatter.parse(raw)
        self.assertIsInstance(result, dict)
        self.assertIn('response', result)
        self.assertIn('quick_replies', result)
        self.assertIn('clínica', result['response'])
        self.assertEqual(result['quick_replies'], NimResponseFormatter.DEFAULT_QUICK_REPLIES)

    def test_parse_malformed_json(self):
        """Malformed JSON → graceful fallback, never raises."""
        from chatbot.services.nim_formatter import NimResponseFormatter
        raw = '{"response": "broken json", "quick_replies": ['
        result = NimResponseFormatter.parse(raw)
        self.assertIsInstance(result, dict)
        self.assertIn('response', result)
        self.assertIsInstance(result['quick_replies'], list)

    def test_parse_strips_nemotron_special_tokens(self):
        """Nemotron special tokens are stripped BEFORE JSON parsing."""
        from chatbot.services.nim_formatter import NimResponseFormatter
        raw = (
            '<extra_id_0>Assistant\n'
            '{"response": "Claro", "quick_replies": ["Sí", "No"]}\n'
            '<|endoftext|>'
        )
        result = NimResponseFormatter.parse(raw)
        self.assertEqual(result['response'], 'Claro')
        self.assertEqual(result['quick_replies'], ['Sí', 'No'])

    def test_parse_strips_all_special_tokens(self):
        """All Nemotron tokens stripped: extra_id, endoftext, assistant, user, system."""
        from chatbot.services.nim_formatter import NimResponseFormatter
        raw = (
            '<extra_id_0>System\nSystem prompt\n'
            '<extra_id_1>User\nUser message\n'
            '<extra_id_0>Assistant\n'
            '<|user|><|system|><|assistant|>'
            '{"response": "Test", "quick_replies": ["A", "B"]}'
            '<|endoftext|>'
        )
        result = NimResponseFormatter.parse(raw)
        self.assertEqual(result['response'], 'Test')
        self.assertEqual(result['quick_replies'], ['A', 'B'])

    def test_parse_empty_input(self):
        """Empty input → safe defaults, never raises."""
        from chatbot.services.nim_formatter import NimResponseFormatter
        result = NimResponseFormatter.parse('')
        self.assertIsInstance(result, dict)
        self.assertIn('response', result)
        self.assertIsInstance(result['quick_replies'], list)
        self.assertTrue(len(result['quick_replies']) > 0)


class NimIntegrationTests(TestCase):
    """Integration tests via Django Client — NIM path in procesar_chat."""

    def setUp(self):
        self.client = Client()

    def _post(self, message):
        """Helper to POST a chat message and return (response, parsed JSON)."""
        response = self.client.post(
            '/chatbot/procesar/',
            data=json.dumps({'message': message}),
            content_type='application/json',
        )
        return response, json.loads(response.content)

    @patch('chatbot.views.NimClient')
    def test_fallback_triggers_nim_path(self, MockNimClient):
        """Unrecognized message triggers NIM dispatch path."""
        from chatbot.services.nim_formatter import NimResponseFormatter

        mock_instance = MagicMock()
        mock_instance.send.return_value = '{"response": "Respuesta IA", "quick_replies": ["A", "B"]}'
        MockNimClient.return_value = mock_instance

        response, data = self._post('consulta_inexistente_xyz_123')
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', data)
        self.assertIn('quick_replies', data)
        # NIM path should have been called
        mock_instance.send.assert_called_once()
        # Response should NOT be the static fallback
        self.assertNotIn('No estoy seguro', data['response'])

    @patch('chatbot.views.NimClient')
    def test_nim_error_falls_back_to_static(self, MockNimClient):
        """Generic/unexpected NIM error → graceful fallback to STATIC_RESPONSES['fallback']."""
        mock_instance = MagicMock()
        mock_instance.send.side_effect = Exception("Unexpected error")
        MockNimClient.return_value = mock_instance

        response, data = self._post('consulta_inexistente_error_test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('No estoy seguro', data['response'])

    @patch('chatbot.views.NimClient')
    def test_nim_timeout_shows_technical_message(self, MockNimClient):
        """NIM timeout → user-friendly technical error, NOT static fallback menu."""
        mock_instance = MagicMock()
        mock_instance.send.side_effect = requests.exceptions.Timeout("Timeout")
        MockNimClient.return_value = mock_instance

        response, data = self._post('consulta_timeout_test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('problemas para conectar', data['response'])
        self.assertNotIn('No estoy seguro', data['response'])

    @patch('chatbot.views.NimClient')
    def test_nim_401_falls_back_to_static(self, MockNimClient):
        """Invalid API key (401) → fallback to static response, NO error logging."""
        mock_instance = MagicMock()
        mock_instance.send.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        MockNimClient.return_value = mock_instance

        response, data = self._post('test_nim_401_fallback')
        self.assertEqual(response.status_code, 200)
        self.assertIn('No estoy seguro', data['response'])

    def test_existing_intents_still_work(self):
        """Existing intents work unchanged (not affected by NIM integration)."""
        response, data = self._post('hola')
        self.assertEqual(response.status_code, 200)
        self.assertIn('👋', data['response'])


class AIConversationStateTests(TestCase):
    """Test the _ai_conversation_active session flag for AI conversation mode."""

    def setUp(self):
        self.client = Client()

    def _post(self, message):
        response = self.client.post(
            '/chatbot/procesar/',
            data=json.dumps({'message': message}),
            content_type='application/json',
        )
        return response, json.loads(response.content)

    @patch('chatbot.views.NimClient')
    def test_ai_active_forces_nim_on_non_transactional(self, MockNimClient):
        """When _ai_conversation_active=True, non-transactional messages go to NIM,
        even if they contain keywords that would normally match rule-based intents."""
        session = self.client.session
        session['_ai_conversation_active'] = True
        session.save()

        mock_instance = MagicMock()
        mock_instance.send.return_value = (
            '{"response": "Hola desde la IA", "quick_replies": ["Sí", "No"]}'
        )
        MockNimClient.return_value = mock_instance

        # 'pollo' would normally match 'producto' intent, but AI mode forces NIM
        response, data = self._post('pollo')
        self.assertIn('Hola desde la IA', data['response'])
        mock_instance.send.assert_called_once()

    @patch('chatbot.views.NimClient')
    def test_ai_active_allows_transactional_intents(self, MockNimClient):
        """When _ai_conversation_active=True, transactional intents
        (horario, ubicacion, urgencia, cita) still use the rule engine."""
        session = self.client.session
        session['_ai_conversation_active'] = True
        session.save()

        response, data = self._post('horario')
        # Rule engine should handle it, not NIM
        MockNimClient.assert_not_called()

    @patch('chatbot.views.NimClient')
    def test_nim_success_sets_ai_active_flag(self, MockNimClient):
        """After NIM responds successfully, _ai_conversation_active is set to True."""
        mock_instance = MagicMock()
        mock_instance.send.return_value = (
            '{"response": "Respuesta IA", "quick_replies": ["A"]}'
        )
        MockNimClient.return_value = mock_instance

        self._post('mensaje_desconocido_para_nim')
        # Session flag must be True after NIM success
        self.assertTrue(self.client.session['_ai_conversation_active'])

    @patch('chatbot.views.NimClient')
    def test_rule_engine_resets_ai_active_flag(self, MockNimClient):
        """After rule engine responds, _ai_conversation_active is set to False."""
        session = self.client.session
        session['_ai_conversation_active'] = True
        session.save()

        self._post('ubicacion')
        # Flag must be reset after rule engine takes over
        self.assertFalse(self.client.session['_ai_conversation_active'])


class RAGContextTests(TestCase):
    """Test that NIM receives real DB context to prevent hallucinations."""

    def test_build_context_returns_string_with_clinic_info(self):
        """_build_nim_context() returns non-empty string with clinic data."""
        from chatbot.views import _build_nim_context
        ctx = _build_nim_context()
        self.assertIsInstance(ctx, str)
        self.assertGreater(len(ctx), 50)
        self.assertIn('Huellitas', ctx)

    def test_build_context_includes_product_categories(self):
        """_build_nim_context() includes real product category names."""
        from chatbot.views import _build_nim_context
        ctx = _build_nim_context()
        self.assertIn('Productos por categoría', ctx)

    @patch('chatbot.views.NimClient')
    def test_nim_receives_context_parameter(self, MockNimClient):
        """NimClient.send() is called with context= containing real DB data."""
        mock_instance = MagicMock()
        mock_instance.send.return_value = (
            '{"response": "OK", "quick_replies": ["ok"]}'
        )
        MockNimClient.return_value = mock_instance

        self.client = Client()
        self.client.post(
            '/chatbot/procesar/',
            data=json.dumps({'message': 'que_servicios_tienen'}),
            content_type='application/json',
        )

        # Verify send() was called with context parameter
        call_kwargs = mock_instance.send.call_args
        self.assertIn('context', call_kwargs[1])
        context = call_kwargs[1]['context']
        self.assertIsInstance(context, str)
        self.assertGreater(len(context), 50)

    @patch('chatbot.views.NimClient')
    def test_system_prompt_forces_context_only_no_invention(self, MockNimClient):
        """System prompt instructs model to use ONLY provided context, never invent."""
        mock_instance = MagicMock()
        mock_instance.send.return_value = (
            '{"response": "OK", "quick_replies": ["ok"]}'
        )
        MockNimClient.return_value = mock_instance

        self.client = Client()
        self.client.post(
            '/chatbot/procesar/',
            data=json.dumps({'message': 'que_ofrecen'}),
            content_type='application/json',
        )

        call_kwargs = mock_instance.send.call_args
        system_prompt = call_kwargs[0][1]  # second positional arg
        self.assertIn('EXCLUSIVAMENTE', system_prompt)
        self.assertIn('NUNCA inventes', system_prompt)