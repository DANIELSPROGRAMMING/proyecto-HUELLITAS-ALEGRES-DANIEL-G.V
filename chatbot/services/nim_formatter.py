"""Response formatter that guarantees {response, quick_replies} contract."""

import json
import re


class NimResponseFormatter:
    """Guarantees structured output from raw NIM text.

    Strategy:
    1. Strip Nemotron special tokens via regex BEFORE JSON parsing
    2. Try JSON parse of the entire cleaned text → extract {response, quick_replies}
    3. If that fails, find JSON object within text via regex → try parse that
    4. If no JSON found → use entire cleaned text as response, generate safe defaults
    5. Never raises — always returns valid dict
    """

    DEFAULT_QUICK_REPLIES = ["¿Necesitas algo más?", "Horarios", "Productos", "Agendar cita"]

    # Nemotron special tokens to strip before parsing
    CLEANUP_PATTERNS = [
        r'<extra_id_\d+>',
        r'<\|endoftext\|>',
        r'<\|assistant\|>',
        r'<\|user\|>',
        r'<\|system\|>',
    ]

    # Pattern to find a JSON object anywhere in text
    JSON_OBJECT_RE = re.compile(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', re.DOTALL)

    @classmethod
    def _clean_text(cls, raw_text):
        """Remove Nemotron special tokens from text."""
        cleaned = raw_text
        for pattern in cls.CLEANUP_PATTERNS:
            cleaned = re.sub(pattern, '', cleaned)
        return cleaned.strip()

    @classmethod
    def _try_parse_json(cls, text):
        """Attempt to parse text as JSON dict. Returns the dict or None."""
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
            return None
        except (json.JSONDecodeError, TypeError, ValueError):
            return None

    @classmethod
    def _extract_and_parse(cls, text):
        """Try JSON parse. If that fails, find JSON object in text and try again."""
        # First: try the whole text as JSON
        data = cls._try_parse_json(text)
        if data is not None:
            return data

        # Second: search for a JSON object within the text
        matches = cls.JSON_OBJECT_RE.findall(text)
        for match in matches:
            data = cls._try_parse_json(match)
            if data is not None:
                return data

        return None

    @classmethod
    def parse(cls, raw_text):
        """Parse raw NIM text into frontend contract.

        Returns: {"response": str, "quick_replies": list[str]}
        Never raises — always returns valid dict.
        """
        cleaned = cls._clean_text(raw_text)

        data = cls._extract_and_parse(cleaned)
        if data is not None:
            response = data.get('response', '')
            quick_replies = data.get('quick_replies', [])
            if isinstance(quick_replies, list) and quick_replies:
                return {
                    'response': str(response) if response else cleaned,
                    'quick_replies': quick_replies,
                }
            return {
                'response': str(response) if response else cleaned,
                'quick_replies': cls.DEFAULT_QUICK_REPLIES,
            }

        # Fallback: plain text → entire cleaned text as response
        if not cleaned:
            return {
                'response': 'Lo siento, no pude procesar tu consulta. ¿Puedes intentar de nuevo?',
                'quick_replies': cls.DEFAULT_QUICK_REPLIES,
            }

        return {
            'response': cleaned,
            'quick_replies': cls.DEFAULT_QUICK_REPLIES,
        }
