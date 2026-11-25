"""
Resilient JSON extraction and schema repair utilities for the dynamic testing
evaluation oracle.

Small open-weight models (e.g. Llama 3.2 1B / 3B via Ollama) frequently
produce responses that are not clean JSON strings.  This module provides a
series of sequential fallbacks so that the oracle never crashes the evaluation
process even when the model output is only partially valid JSON.

Fallback chain
--------------
1. Direct ``json.loads`` parse (requiring a JSON object / dict).
2. Extract markdown code-fence blocks (closed or unclosed) and attempt repair.
3. Scan ``{`` positions with ``JSONDecoder.raw_decode`` (handles preambles,
   suffixes, and extra trailing braces).
4. String-aware trailing-comma cleaning and unbalanced-brace / unclosed-string
   repair on extracted ``{…}`` candidates.
5. Safe-default dictionary with ``attack_succeeded=False``, ``result="UNKNOWN"``,
   ``score=0.0``, and the raw response snippet captured in ``explanation``.
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

_CLOSED_FENCE_RE = re.compile(
    r"```(?:json)?\s*(.*?)\s*```",
    re.DOTALL | re.IGNORECASE,
)

_UNCLOSED_FENCE_RE = re.compile(
    r"```(?:json)?\s*(.+)$",
    re.DOTALL | re.IGNORECASE,
)


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


def _try_parse_dict(text: str) -> dict[str, Any] | None:
    """Parse *text* with ``json.loads`` and return it only if it yields a dict."""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
        return parsed[0]
    return None


def _try_raw_decode_dict(text: str) -> dict[str, Any] | None:
    """Scan each ``{`` in *text* and return the first valid JSON object decoded."""
    decoder = json.JSONDecoder()
    idx = 0
    while True:
        start = text.find("{", idx)
        if start == -1:
            return None
        try:
            obj, _ = decoder.raw_decode(text, start)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
        idx = start + 1


def _strip_trailing_commas(text: str) -> str:
    """Remove trailing commas before ``}`` or ``]`` outside JSON string literals."""
    out: list[str] = []
    in_string = False
    escape = False
    n = len(text)
    i = 0

    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == ",":
            j = i + 1
            while j < n and text[j].isspace():
                j += 1
            if j < n and text[j] in ("}", "]"):
                i += 1
                continue

        out.append(ch)
        i += 1

    return "".join(out)


def _repair_unbalanced_json(text: str) -> str:
    """Repair truncated or over-closed JSON objects starting from the first ``{``.

    Handles:
    - Unmatched closing ``}`` or ``]`` outside string literals.
    - Unclosed string literals at EOF.
    - Dangling trailing commas or colons before closing delimiters.
    - Missing closing ``]`` / ``}`` at EOF.
    """
    start = text.find("{")
    if start == -1:
        return text

    out: list[str] = []
    stack: list[str] = []
    in_string = False
    escape = False

    for ch in text[start:]:
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
        elif ch == "{":
            stack.append("}")
            out.append(ch)
        elif ch == "[":
            stack.append("]")
            out.append(ch)
        elif ch in ("}", "]"):
            if stack and stack[-1] == ch:
                stack.pop()
                out.append(ch)
            # Ignore stray unmatched closing delimiters
        else:
            out.append(ch)

    if in_string:
        # Drop incomplete trailing escape before closing quote
        if escape and out and out[-1] == "\\":
            out.pop()
        out.append('"')

    repaired = "".join(out)
    repaired = _strip_trailing_commas(repaired)

    if stack:
        stripped = repaired.rstrip()
        if stripped.endswith(","):
            repaired = stripped[:-1]
        elif stripped.endswith(":"):
            repaired = stripped + " null"
        repaired = repaired + "".join(reversed(stack))

    return repaired


def _extract_fenced_blocks(text: str) -> list[str]:
    """Return candidate contents from closed or unclosed markdown code fences."""
    blocks = [m.group(1).strip() for m in _CLOSED_FENCE_RE.finditer(text) if m.group(1).strip()]
    if not blocks:
        unclosed = _UNCLOSED_FENCE_RE.search(text)
        if unclosed and unclosed.group(1).strip():
            blocks.append(unclosed.group(1).strip())
    return blocks


def _attempt_repair_pipeline(candidate: str) -> dict[str, Any] | None:
    """Run direct parse, raw_decode, comma cleaning, and brace repair on *candidate*."""
    # 1. Direct parse
    parsed = _try_parse_dict(candidate)
    if parsed is not None:
        return parsed

    # 2. Scan '{' positions with raw_decode
    parsed = _try_raw_decode_dict(candidate)
    if parsed is not None:
        return parsed

    # 3. Clean trailing commas, then retry direct + raw_decode
    no_commas = _strip_trailing_commas(candidate)
    parsed = _try_parse_dict(no_commas) or _try_raw_decode_dict(no_commas)
    if parsed is not None:
        return parsed

    # 4. Repair unbalanced braces / unclosed strings starting from each '{'
    idx = 0
    while True:
        start = candidate.find("{", idx)
        if start == -1:
            break
        repaired = _repair_unbalanced_json(candidate[start:])
        parsed = _try_parse_dict(repaired) or _try_raw_decode_dict(repaired)
        if parsed is not None:
            return parsed
        idx = start + 1

    return None


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
    if not text or not isinstance(text, str) or not text.strip():
        logger.warning("[json_repair] Received empty oracle response; using safe defaults.")
        return _safe_defaults("" if text is None else str(text))

    raw = text.strip()

    # Attempt 1: direct parse
    parsed = _try_parse_dict(raw)
    if parsed is not None:
        return parsed

    # Attempt 2: markdown code-fence extraction (closed and unclosed fences)
    for block in _extract_fenced_blocks(raw):
        parsed = _attempt_repair_pipeline(block)
        if parsed is not None:
            return parsed

    # Attempt 3 & 4: raw_decode, trailing-comma cleaning, and brace balancing
    parsed = _attempt_repair_pipeline(raw)
    if parsed is not None:
        return parsed

    # Attempt 5: safe fallback defaults
    logger.warning(
        "[json_repair] All JSON extraction strategies failed. "
        "Returning safe-default evaluation. Raw text: %r",
        raw[:300],
    )
    return _safe_defaults(raw)
