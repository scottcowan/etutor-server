"""
Shared eval configuration.

Evals run against any litellm-compatible model — Anthropic, OpenAI, Ollama,
AWS Bedrock, etc. Set ETUTOR_EVAL_MODEL to point at whichever backend you have:

    # Anthropic (default)
    ETUTOR_EVAL_MODEL=claude-haiku-4-5-20251001 pytest tests/evals/

    # OpenAI
    OPENAI_API_KEY=sk-... ETUTOR_EVAL_MODEL=gpt-4o-mini pytest tests/evals/

    # Ollama (no key needed)
    ETUTOR_EVAL_MODEL=ollama/llama3.2 pytest tests/evals/

The evals skip if no usable LLM is configured — detected by checking whether
any known API key is set OR whether ETUTOR_EVAL_MODEL points at a local endpoint.
"""

import os
import pytest

# ---------------------------------------------------------------------------
# Detect whether a usable LLM backend is configured
# ---------------------------------------------------------------------------

def _llm_available() -> bool:
    model = os.environ.get("ETUTOR_EVAL_MODEL", "claude-haiku-4-5-20251001")

    # Local/self-hosted backends — never need a key
    local_prefixes = ("ollama/", "ollama_chat/", "lm_studio/", "together/local", "http://", "https://localhost")
    if any(model.startswith(p) for p in local_prefixes):
        return True

    # Cloud backends — check for known keys
    key_vars = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "AZURE_API_KEY",
        "COHERE_API_KEY",
        "MISTRAL_API_KEY",
        "GROQ_API_KEY",
        "AWS_PROFILE",          # Bedrock via profile
        "AWS_ACCESS_KEY_ID",    # Bedrock via keys
    ]
    return any(os.environ.get(k) for k in key_vars)


LLM_AVAILABLE = _llm_available()

# ---------------------------------------------------------------------------
# Shared skip marker — use in every eval test
# ---------------------------------------------------------------------------

requires_llm = pytest.mark.skipif(
    not LLM_AVAILABLE,
    reason=(
        "No LLM backend configured. Set ETUTOR_EVAL_MODEL + an API key, "
        "or point at a local Ollama endpoint: "
        "ETUTOR_EVAL_MODEL=ollama/llama3.2 pytest tests/evals/"
    ),
)
