import requests
from typing import List, Dict

class OllamaClient:
    """Minimal client for Ollama chat API."""
    def __init__(self, host: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.host = host.rstrip("/")
        self.model = model

    def chat(self, messages: List[Dict], temperature: float = 0.3) -> str:
        """Send messages to /api/chat and return assistant text."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        r = requests.post(f"{self.host}/api/chat", json=payload, timeout=300)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
