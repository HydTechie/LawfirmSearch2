
import os
import httpx
from typing import Optional

class LLMResponse:
    def __init__(self, text: str, provider: str):
        self.text = text
        self.provider = provider

class OllamaLLM:
    """
    Minimal Ollama client for local SLM.
    Set OLLAMA_HOST (default http://localhost:11434)
    """
    def __init__(self, model: str = "phi3:mini",
                 host: Optional[str] = None):
        self.model = model
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float = 0.2) -> LLMResponse:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return LLMResponse(data.get("response", "").strip(),
                               f"ollama:{self.model}")

class FallbackExtractiveLLM:
    """Fallback: returns snippets if LLM unavailable"""
    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float = 0.0) -> LLMResponse:
        return LLMResponse(
            "LLM unavailable. Returning top retrieved snippets:\n\n" + prompt[:max_tokens],
            "fallback:extractive"
        )
