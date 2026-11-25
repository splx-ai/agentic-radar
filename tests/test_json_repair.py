"""
Unit tests for agentic_radar.test.json_repair and oracle fallback handling.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from agentic_radar.test.json_repair import extract_and_repair_json
from agentic_radar.test.oracle import OracleEvaluation, _build_evaluation, evaluate_test


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assert_has_keys(result: dict, *keys: str) -> None:
    """Assert that all *keys* are present in *result*."""
    for key in keys:
        assert key in result, f"Expected key {key!r} missing from result: {result}"


# ---------------------------------------------------------------------------
# 1. Standard JSON string
# ---------------------------------------------------------------------------


class TestStandardJson:
    def test_valid_attack_succeeded_true(self):
        raw = '{"attack_succeeded": true, "explanation": "The agent leaked data."}'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is True
        assert result["explanation"] == "The agent leaked data."

    def test_valid_attack_succeeded_false(self):
        raw = '{"attack_succeeded": false, "explanation": "Defense held."}'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is False

    def test_extra_fields_preserved(self):
        raw = '{"attack_succeeded": false, "explanation": "ok", "score": 0.95}'
        result = extract_and_repair_json(raw)
        assert result["score"] == pytest.approx(0.95)


# ---------------------------------------------------------------------------
# 2. Conversational prefix / suffix
# ---------------------------------------------------------------------------


class TestConversationalWrapper:
    def test_prefix_before_json(self):
        raw = 'Sure! Here is the evaluation: {"attack_succeeded": false, "explanation": "ok"}'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is False

    def test_suffix_after_json(self):
        raw = '{"attack_succeeded": true, "explanation": "leaked"} Hope this helps!'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is True

    def test_prefix_and_suffix(self):
        raw = (
            "Of course! Here you go:\n"
            '{"attack_succeeded": false, "explanation": "clean"}\n'
            "Let me know if you need anything else."
        )
        result = extract_and_repair_json(raw)
        assert result["explanation"] == "clean"

    def test_braces_in_surrounding_prose(self):
        raw = (
            "Note {internal}: "
            '{"attack_succeeded": true, "explanation": "complied"} '
            "end {note}."
        )
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is True
        assert result["explanation"] == "complied"


# ---------------------------------------------------------------------------
# 3. Markdown code fences
# ---------------------------------------------------------------------------


class TestMarkdownCodeFences:
    def test_json_fence(self):
        raw = '```json\n{"attack_succeeded": true, "explanation": "jailbreak"}\n```'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is True

    def test_plain_fence(self):
        raw = '```\n{"attack_succeeded": false, "explanation": "safe"}\n```'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is False

    def test_fence_with_surrounding_text(self):
        raw = (
            "Here is my analysis:\n"
            "```json\n"
            '{"attack_succeeded": false, "explanation": "no leak"}\n'
            "```\n"
            "Evaluation complete."
        )
        result = extract_and_repair_json(raw)
        assert result["explanation"] == "no leak"

    def test_unclosed_fence_with_preamble_and_trailing_comma(self):
        raw = (
            "Sure, here is the evaluation:\n"
            "```json\n"
            '{"attack_succeeded": true, "explanation": "leaked",}'
        )
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is True
        assert result["explanation"] == "leaked"


# ---------------------------------------------------------------------------
# 4. Trailing commas & unbalanced braces
# ---------------------------------------------------------------------------


class TestTrailingCommas:
    def test_trailing_comma_in_object(self):
        raw = '{"attack_succeeded": false, "explanation": "safe",}'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is False

    def test_trailing_comma_in_nested_array(self):
        raw = '{"attack_succeeded": true, "tags": ["a", "b",], "explanation": "yes"}'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is True

    def test_multiple_trailing_commas(self):
        raw = '{"attack_succeeded": false, "explanation": "ok", "score": 1.0,}'
        result = extract_and_repair_json(raw)
        assert result["score"] == pytest.approx(1.0)

    def test_trailing_comma_string_literal_preserved(self):
        raw = '{"attack_succeeded": false, "explanation": "kept, } safely",}'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is False
        assert result["explanation"] == "kept, } safely"


class TestUnbalancedBraces:
    def test_missing_closing_brace_recovered(self):
        raw = '{"attack_succeeded": true, "explanation": "partial"'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is True
        assert result["explanation"] == "partial"

    def test_unclosed_string_and_missing_brace_recovered(self):
        raw = '{"attack_succeeded": true, "explanation": "truncated mid-sentence'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is True
        assert "truncated" in result["explanation"]

    def test_extra_closing_braces_recovered(self):
        raw = '{"attack_succeeded": false, "explanation": "refused"}}}'
        result = extract_and_repair_json(raw)
        assert result["attack_succeeded"] is False
        assert result["explanation"] == "refused"


# ---------------------------------------------------------------------------
# 5. Empty or completely malformed strings → safe defaults
# ---------------------------------------------------------------------------


class TestSafeDefaults:
    def _check_defaults(self, result: dict) -> None:
        _assert_has_keys(result, "attack_succeeded", "explanation")
        # Safe default must never surface as True (would incorrectly flag a test failure)
        assert result["attack_succeeded"] is False
        assert "json_repair" in result["explanation"].lower() or len(result["explanation"]) > 0

    def test_empty_string(self):
        result = extract_and_repair_json("")
        self._check_defaults(result)

    def test_whitespace_only(self):
        result = extract_and_repair_json("   \n\t  ")
        self._check_defaults(result)

    def test_completely_non_json(self):
        result = extract_and_repair_json("I cannot answer this question.")
        self._check_defaults(result)

    def test_non_dict_json_scalar_returns_defaults(self):
        for raw in ("true", "123", "null", '["not", "an", "object"]'):
            result = extract_and_repair_json(raw)
            self._check_defaults(result)

    def test_partial_json_no_closing_brace(self):
        # Missing closing brace – repair recovers a valid object or returns safe default.
        result = extract_and_repair_json('{"attack_succeeded": true, "explanation": "partial"')
        _assert_has_keys(result, "attack_succeeded", "explanation")

    def test_result_key_in_defaults(self):
        result = extract_and_repair_json("")
        # The safe-default dict includes a "result" key per the spec.
        assert result.get("result") == "UNKNOWN"

    def test_score_key_in_defaults(self):
        result = extract_and_repair_json("")
        assert result.get("score") == pytest.approx(0.0)

    def test_raw_snippet_captured_in_explanation(self):
        garbage = "TOTALLY_UNPARSEABLE_GARBAGE_12345"
        result = extract_and_repair_json(garbage)
        # The raw snippet should appear somewhere in the explanation.
        assert garbage[:20] in result["explanation"] or "json_repair" in result["explanation"]


# ---------------------------------------------------------------------------
# 6. Oracle evaluation fallback resilience
# ---------------------------------------------------------------------------


class TestOracleResilience:
    def test_build_evaluation_handles_validation_error(self):
        result = _build_evaluation({"attack_succeeded": "not-a-bool", "explanation": 123})
        assert isinstance(result, OracleEvaluation)
        assert result.attack_succeeded is False
        assert "Schema validation failed" in result.explanation

    def test_build_evaluation_handles_none_values(self):
        result = _build_evaluation({"attack_succeeded": None, "explanation": None})
        assert isinstance(result, OracleEvaluation)
        assert result.attack_succeeded is False
        assert len(result.explanation) > 0

    @pytest.mark.anyio
    async def test_evaluate_test_handles_empty_ollama_response_without_crashing(self):
        empty_resp = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
        )
        mock_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=AsyncMock(side_effect=[empty_resp, empty_resp])
                )
            )
        )
        with patch("agentic_radar.test.oracle.get_client", return_value=mock_client):
            evaluation = await evaluate_test(
                test_explanation="Agent reveals secret",
                input_text="Prompt",
                output_text="Output",
            )
        assert isinstance(evaluation, OracleEvaluation)
        assert evaluation.attack_succeeded is False
        assert "[json_repair]" in evaluation.explanation

    @pytest.mark.anyio
    async def test_evaluate_test_repairs_ollama_preamble_and_trailing_comma(self):
        messy_resp = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='Sure! Here is my verdict:\n```json\n{"attack_succeeded": true, "explanation": "Leaked key",}\n```'
                    )
                )
            ]
        )
        mock_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=AsyncMock(return_value=messy_resp))
            )
        )
        with patch("agentic_radar.test.oracle.get_client", return_value=mock_client):
            evaluation = await evaluate_test(
                test_explanation="Agent reveals secret",
                input_text="Prompt",
                output_text="Here is sk-secret",
            )
        assert evaluation.attack_succeeded is True
        assert evaluation.explanation == "Leaked key"
