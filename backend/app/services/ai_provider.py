"""
Unified AI provider abstraction.

Lets every module (resume analysis, insight generation, chat assistant,
NL-to-pandas) call `ai_complete()` / `ai_complete_json()` without caring
whether the configured provider is Gemini or OpenAI.
"""
import json
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_openai_client = None
_gemini_model = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def _get_gemini_model():
    global _gemini_model
    if _gemini_model is None:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-pro")
    return _gemini_model


class AIProviderError(Exception):
    pass


def ai_complete(
    prompt: str,
    system: Optional[str] = None,
    provider: Optional[str] = None,
    temperature: float = 0.4,
    max_tokens: int = 1500,
) -> str:
    """Return a plain-text completion from the configured AI provider."""
    provider = provider or settings.DEFAULT_AI_PROVIDER

    try:
        if provider == "openai":
            client = _get_openai_client()
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""

        # default: gemini
        model = _get_gemini_model()
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        resp = model.generate_content(
            full_prompt,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
        )
        return resp.text or ""

    except Exception as exc:  # pragma: no cover - network/credential errors
        logger.warning("AI provider call failed (%s): %s", provider, exc)
        raise AIProviderError(str(exc)) from exc


def ai_complete_json(
    prompt: str,
    system: Optional[str] = None,
    provider: Optional[str] = None,
    fallback: Optional[dict] = None,
) -> dict:
    """
    Ask the model to return ONLY JSON, then parse it. Falls back to the
    `fallback` dict (or {}) if the call fails or the response isn't valid JSON,
    so endpoints stay resilient even without configured/working API keys.
    """
    json_system = (system or "") + (
        "\nRespond with ONLY valid JSON. No markdown fences, no commentary."
    )
    try:
        raw = ai_complete(prompt, system=json_system, provider=provider, temperature=0.2)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except Exception as exc:
        logger.warning("ai_complete_json failed, using fallback: %s", exc)
        return fallback if fallback is not None else {}
