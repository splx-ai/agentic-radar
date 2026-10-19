"""
Resilient JSON extraction and schema repair utilities for the dynamic testing
evaluation oracle.

Small open-weight models (e.g. Llama 3.2 1B / 3B via Ollama) frequently
produce responses that are not clean JSON strings.  This module provides a
series of sequential fallbacks so that the oracle never crashes the evaluation
process even when the model output is only partially valid JSON.

Fallback chain
--------------
1. Direct ``json.loads`` parse.
2. Strip markdown code fences and retry.
3. Greedy regex extraction of the outermost ``{…}`` block.
4. Syntax cleaning (trailing commas) followed by a final parse attempt.
5. Safe-default dictionary with ``attack_succeeded=False``, ``score=0.0``,
   and the raw response snippet captured in ``explanation``.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_MARKDOWN_FENCE_RE = re.compile(
    r"```(?:json)?\s*(\{.*?\})\s*```",
    re.DOTALL | re.IGNORECASE,
)

_OUTER_BRACES_RE = re.compile(r"(\{.*\})", re.DOTALL)

_TRAILING_COMMA_RE = re.compile(r",\s*([\}\]])")


def _strip_markdown_fence(text: str) -> str:
    """Remove leading/trailing markdown code-fence markers."""
    stripped = text.strip()
    # Remove opening fence (```json or ```)
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
    # Remove closing fence
    stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before closing braces/brackets."""
    return _TRAILING_COMMA_RE.sub(r"\1", text)


def _safe_defaults(raw_snippet: str) -> dict[str, Any]:
    """Return a schema-compliant fallback dictionary.

    The ``explanation`` field captures the raw model output so the caller can
    log or surface it without losing context.
    """
    return {
        "attack_succeeded": False,
        "result": "UNKNOWN",
        "score": 0.0,
        "explanation": (
            "[json_repair] Could not parse oracle response. "
            f"Raw snippet: {raw_snippet[:200]!r}"
        ),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_and_repair_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from *text* using a sequential fallback strategy.

    Parameters
    ----------
    text:
        Raw string returned by an LLM oracle.

    Returns
    -------
    dict
        Parsed JSON dictionary, or a schema-compliant safe-default dictionary
        if every extraction strategy fails.
    """
    if not text or not text.strip():
        logger.warning("[json_repair] Received empty oracle response; using safe defaults.")
        return _safe_defaults("")

    raw = text.strip()

    # ------------------------------------------------------------------
    # Attempt 1 – direct parse
    # ------------------------------------------------------------------
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # ------------------------------------------------------------------
    # Attempt 2 – strip markdown fences, then parse
    # ------------------------------------------------------------------
    fence_match = _MARKDOWN_FENCE_RE.search(raw)
    if fence_match:
        candidate = fence_match.group(1)
    else:
        candidate = _strip_markdown_fence(raw)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # ------------------------------------------------------------------
    # Attempt 3 – greedy extraction of the outermost {…} block
    # ------------------------------------------------------------------
    outer_match = _OUTER_BRACES_RE.search(candidate)
    if outer_match:
        candidate = outer_match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # ------------------------------------------------------------------
    # Attempt 4 – fix trailing commas, then parse
    # ------------------------------------------------------------------
    cleaned = _fix_trailing_commas(candidate)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # ------------------------------------------------------------------
    # Attempt 5 – safe fallback defaults
    # ------------------------------------------------------------------
    logger.warning(
        "[json_repair] All JSON extraction strategies failed. "
        "Returning safe-default evaluation. Raw text: %r",
        raw[:300],
    )
    return _safe_defaults(raw)
