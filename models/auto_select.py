"""
Auto-selects the best available free model.
Priority: Llama (Groq) → Gemini → Claude
Llama is always first because it has a generous free tier with no daily quota.
"""

import os
from typing import Callable


def _get_caller(name: str) -> Callable[[str], str] | None:
    if name == "Llama" and os.environ.get("GROQ_API_KEY"):
        from models.llama_client import call_llama
        return call_llama
    if name == "Gemini" and os.environ.get("GEMINI_API_KEY"):
        from models.gemini_client import call_gemini
        return call_gemini
    if name == "Claude" and os.environ.get("ANTHROPIC_API_KEY"):
        from models.claude_client import call_claude
        return call_claude
    return None


# Priority order: free-first
FREE_PRIORITY = ["Llama", "Gemini", "Claude"]


def get_best_model() -> tuple[str, Callable[[str], str]]:
    """Returns (model_display_name, caller_fn) for the best available model."""
    for name in FREE_PRIORITY:
        caller = _get_caller(name)
        if caller:
            labels = {
                "Llama":  "Llama 3.3 · Groq (Free)",
                "Gemini": "Gemini 2.0 Flash · Google (Free tier)",
                "Claude": "Claude Sonnet · Anthropic",
            }
            return labels[name], caller
    raise RuntimeError(
        "No API keys found. Add GROQ_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY to your .env file."
    )


def list_available() -> list[dict]:
    """Returns all configured models with their status."""
    results = []
    labels = {
        "Llama":  ("Llama 3.3", "Groq", "Free — no quota limits"),
        "Gemini": ("Gemini 2.0 Flash", "Google", "Free tier — 1,500 req/day"),
        "Claude": ("Claude Sonnet", "Anthropic", "Paid — requires credits"),
    }
    keys = {"Llama": "GROQ_API_KEY", "Gemini": "GEMINI_API_KEY", "Claude": "ANTHROPIC_API_KEY"}
    for name in FREE_PRIORITY:
        model, provider, note = labels[name]
        has_key = bool(os.environ.get(keys[name]))
        results.append({
            "name": name,
            "model": model,
            "provider": provider,
            "note": note,
            "available": has_key,
        })
    return results
