"""
File path: backend/modules/explainability/llm_client.py
Purpose: Grok API client wrapper for LLM-generated analyst narratives.
         Uses xAI Grok API (OpenAI-compatible endpoint).
         Key: GROK_API_KEY from config/environment.
         
Called by ExplainabilityEngine to generate 3-5 sentence analyst narratives.
On failure: raises LLMClientError so engine falls back to FallbackBuilder.
Per SPEC Section 14.
"""
import logging
import requests
from core.exceptions import LLMClientError

logger = logging.getLogger("app")

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-beta"
MAX_TOKENS = 512


class LLMClient:
    """
    Thin wrapper around the xAI Grok API.
    Implements retry logic (3 attempts, exponential backoff).
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def generate_narrative(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Grok API with the given system + user prompt.
        
        Returns:
            Generated narrative text string (up to 2000 chars).
        
        Raises:
            LLMClientError: on API failure, timeout, or invalid response.
        
        TODO: Implement with requests + retry logic
        Steps:
          1. Build request payload with model, messages, max_tokens
          2. POST to GROK_API_URL with auth header
          3. Parse response.choices[0].message.content
          4. Validate response is non-empty
          5. Return narrative string
        """
        raise NotImplementedError("LLMClient.generate_narrative() not yet implemented")
