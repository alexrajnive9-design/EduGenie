"""Thin wrapper around the Google Gemini SDK, shared by all modules.

Every module calls generate_text(); any failure is raised as GeminiError so
that main.py can turn it into a clean JSON error for the frontend.
"""
from typing import Optional

import config


class GeminiError(Exception):
    """Raised when a Gemini call cannot be completed."""


_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_api_key_here":
            raise GeminiError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key "
                "from https://aistudio.google.com/app/apikey, then restart the server."
            )
        try:
            from google import genai
        except ImportError as exc:  # pragma: no cover
            raise GeminiError(
                "The 'google-genai' package is missing. Run: pip install -r requirements.txt"
            ) from exc
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def generate_text(prompt: str, json_output: bool = False) -> str:
    """Send a prompt to Gemini and return the response text."""
    client = _get_client()
    kwargs = {}
    if json_output:
        from google.genai import types

        kwargs["config"] = types.GenerateContentConfig(response_mime_type="application/json")
    try:
        response = client.models.generate_content(
            model=config.GEMINI_MODEL, contents=prompt, **kwargs
        )
    except Exception as exc:
        raise GeminiError(f"Gemini request failed: {exc}") from exc

    text: Optional[str] = getattr(response, "text", None)
    if not text or not text.strip():
        raise GeminiError("Gemini returned an empty response. Try rephrasing your input.")
    return text.strip()
