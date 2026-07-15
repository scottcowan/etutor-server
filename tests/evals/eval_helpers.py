"""
Shared helpers for evals. Import this module directly in eval files.

Usage:
    from eval_helpers import requires_llm, MODEL
"""
import os
import pytest


def _llm_available() -> bool:
    model = os.environ.get("ETUTOR_EVAL_MODEL", "claude-haiku-4-5-20251001")
    local_prefixes = ("ollama/", "ollama_chat/", "lm_studio/", "http://", "https://localhost")
    if any(model.startswith(p) for p in local_prefixes):
        return True
    key_vars = [
        "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "AZURE_API_KEY",
        "COHERE_API_KEY", "MISTRAL_API_KEY", "GROQ_API_KEY",
        "AWS_PROFILE", "AWS_ACCESS_KEY_ID",
    ]
    return any(os.environ.get(k) for k in key_vars)


requires_llm = pytest.mark.skipif(
    not _llm_available(),
    reason=(
        "No LLM backend configured. Set ETUTOR_EVAL_MODEL + an API key, "
        "or use a local backend: ETUTOR_EVAL_MODEL=ollama/llama3.2 pytest tests/evals/"
    ),
)

MODEL = os.environ.get("ETUTOR_EVAL_MODEL", "claude-haiku-4-5-20251001")
