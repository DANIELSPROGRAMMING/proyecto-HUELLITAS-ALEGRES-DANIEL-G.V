"""NVIDIA NIM HTTP client for chatbot AI fallback."""

import json

import requests


class NimClient:
    """HTTP client for NVIDIA NIM API.

    Usage:
        client = NimClient(
            api_key='nvapi-...',
            base_url='https://api.nvidia.com',
            model='nvidia/nemotron-mini-4b-instruct',
            timeout=5,
        )
        text = client.send("¿Tienen comida para gatos?", system_prompt)
    """

    def __init__(self, api_key, base_url, model, timeout=5):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout

    def send(self, user_message, system_prompt, context=None):
        """Send message to NIM and return raw text response.

        Uses OpenAI-compatible chat completions format with messages array.
        Raises requests.RequestException on HTTP errors or timeout.
        """
        url = f"{self.base_url}/v1/chat/completions"
        messages = self._build_messages(system_prompt, user_message, context)
        data = self._call_api(url, messages)
        choices = data.get('choices', [])
        if choices:
            return choices[0]['message']['content']
        return ''

    def send_with_tools(self, user_message, system_prompt, tools, context=None,
                        tool_executor=None, max_rounds=3):
        """Full tool-calling conversation loop.

        1. Send user message + tools → NIM responds with text or tool_calls
        2. If tool_calls: execute via tool_executor(name, args) → send results back
        3. Repeat until NIM returns final text (max max_rounds iterations)

        Args:
            tool_executor: callable(name: str, args: dict) -> str result
            max_rounds: max API calls before forced stop

        Returns: final text response string
        """
        url = f"{self.base_url}/v1/chat/completions"
        messages = self._build_messages(system_prompt, user_message, context)

        def _execute_and_append(msg):
            """Execute tool calls and append results to messages."""
            messages.append(msg)
            for tc in msg.get('tool_calls', []):
                func_name = tc['function']['name']
                try:
                    func_args = json.loads(tc['function']['arguments'])
                except (json.JSONDecodeError, TypeError, KeyError):
                    func_args = {}
                result = tool_executor(func_name, func_args) if tool_executor else (
                    f"Error: herramienta '{func_name}' no disponible."
                )
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get('id', 'unknown'),
                    "content": str(result),
                })

        for _ in range(max_rounds):
            data = self._call_api(url, messages, tools=tools)
            msg = data.get('choices', [{}])[0].get('message', {})

            if msg.get('tool_calls'):
                _execute_and_append(msg)
                continue

            return msg.get('content', '')

        return (
            'Lo siento, el proceso de análisis tomó demasiados pasos. '
            '¿Podrías ser más específico con tu consulta?'
        )

    def send_image(self, user_message, image_base64, system_prompt,
                   context=None, vision_model=None, image_timeout=30,
                   image_mime='image/jpeg'):
        """Send text + image to multimodal NIM model.

        Uses OpenAI-compatible vision format with image_url in content array.
        Image is sent as base64 data URI (not stored on disk).

        Args:
            image_base64: raw base64 string WITHOUT the data:image prefix
            vision_model: model override for vision (default: self.model)
            image_timeout: separate timeout for image inference (default: 30s)
            image_mime: MIME type for the image (default: image/jpeg).
                        Auto-detected from frontend when available.

        Returns: raw text response string
        """
        url = f"{self.base_url}/v1/chat/completions"
        model = vision_model or self.model

        # Auto-detect image format from base64 header
        if image_base64.startswith('iVBOR'):
            image_mime = 'image/png'
        elif image_base64.startswith('/9j/'):
            image_mime = 'image/jpeg'
        elif image_base64.startswith('R0lGOD'):
            image_mime = 'image/gif'
        elif image_base64.startswith('UklGR'):
            image_mime = 'image/webp'

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if context:
            messages.append({"role": "system", "content": str(context)})

        # Multimodal user message: text + image
        content = []
        if user_message:
            content.append({"type": "text", "text": user_message})
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{image_mime};base64,{image_base64}"},
        })
        messages.append({"role": "user", "content": content})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 1,
        }

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=image_timeout,
        )
        response.raise_for_status()

        data = response.json()
        choices = data.get('choices', [])
        if choices:
            return choices[0]['message']['content']
        return ''

    def _build_messages(self, system_prompt, user_message, context):
        """Build the messages array for a chat completion request."""
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if context:
            messages.append({"role": "system", "content": str(context)})
        messages.append({"role": "user", "content": user_message})
        return messages

    def _call_api(self, url, messages, tools=None):
        """Make a single chat completions API call. Returns parsed JSON dict."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 1,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
