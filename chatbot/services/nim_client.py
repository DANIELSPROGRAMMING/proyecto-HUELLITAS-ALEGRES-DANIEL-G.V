"""NVIDIA NIM HTTP client for chatbot AI fallback."""

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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if context:
            messages.append({"role": "system", "content": str(context)})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 1,
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        # OpenAI-compatible chat completions: choices[0].message.content
        choices = data.get('choices', [])
        if choices:
            return choices[0]['message']['content']
        return ''
