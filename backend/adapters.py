# logic for switching between OpenRouter,perplexity,gemini,etc.

from typing import Dict, Any, AsyncGenerator

class ProviderAdapter:
    
    def __init__(self, api_key: str, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url
