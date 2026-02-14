"""
LLM Client - Abstraction layer with local/cloud fallback.
Tries local LM Studio first, falls back to Gemini API if unavailable.
"""
import os
import time
import requests
from typing import List, Dict, Any, Optional

# Local LLM (LM Studio / Ollama)
LOCAL_API_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:8080/v1")
LOCAL_MODEL = os.getenv("LOCAL_LLM_MODEL", "Marlon81/Phi-3-mini-4k-instruct-Q5_K_M-GGUF:Q5_K_M")

# Cloud LLM (Gemini) - Using new google.genai library
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAlcu5wrSj_L1b2y2c2Nm7iHqHBPqaR5SY")
GEMINI_MODEL = "gemini-1.5-flash"  # Standard free tier model


class LLMClient:
    """
    Unified LLM client with automatic fallback.
    Usage:
        client = LLMClient()
        response = client.chat([{"role": "user", "content": "Hello"}])
    """
    
    def __init__(self, prefer_local: bool = True):
        self.prefer_local = prefer_local
        self._local_available = None
        self._gemini_client = None
        self._openai_client = None
        
    def _check_local(self) -> bool:
        """Check if local LLM is running."""
        if self._local_available is not None:
            return self._local_available
        
        try:
            r = requests.get(f"{LOCAL_API_URL}/models", timeout=2)
            self._local_available = r.status_code == 200
        except:
            self._local_available = False
        
        return self._local_available
    
    def _get_local_client(self):
        """Lazy-load OpenAI-compatible client for local LLM."""
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI(base_url=LOCAL_API_URL, api_key="lm-studio")
        return self._openai_client
    
    def _get_gemini_client(self):
        """Lazy-load Gemini client using new google.genai library."""
        if self._gemini_client is None:
            from google import genai
            self._gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        return self._gemini_client
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Send chat completion request.
        
        Args:
            messages: List of {"role": "user/system/assistant", "content": "..."}
            temperature: Sampling temperature.
            
        Returns:
            Response text.
        """
        # Try local first
        if self.prefer_local and self._check_local():
            return self._chat_local(messages, temperature)
        
        # Fallback to Gemini
        return self._chat_gemini(messages, temperature)
    
    def _chat_local(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Chat using local LM Studio."""
        client = self._get_local_client()
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _chat_gemini(self, messages: List[Dict[str, str]], temperature: float, retries: int = 3) -> str:
        """Chat using Gemini API with retry logic."""
        client = self._get_gemini_client()
        
        # Convert OpenAI-style messages to single prompt
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"[System Instructions]\n{content}\n")
            else:
                prompt_parts.append(content)
        
        full_prompt = "\n".join(prompt_parts)
        
        for attempt in range(retries):
            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=full_prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": 2048
                    }
                )
                return response.text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    wait_time = 45 * (attempt + 1)  # Exponential backoff
                    print(f"[LLM] Rate limit hit. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
        
        raise Exception("Gemini API failed after retries")
    
    @property
    def mode(self) -> str:
        """Return which backend is active."""
        if self.prefer_local and self._check_local():
            return "local"
        return "gemini"


# Singleton for convenience
_default_client: Optional[LLMClient] = None

def get_client(prefer_local: bool = True) -> LLMClient:
    """Get or create the default LLM client."""
    global _default_client
    if _default_client is None:
        _default_client = LLMClient(prefer_local)
    return _default_client
