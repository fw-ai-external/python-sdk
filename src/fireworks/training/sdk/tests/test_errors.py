"""Tests for fireworks.training.sdk.errors — error formatting, parsing, and retry logic."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import httpx
import pytest
import requests

from fireworks.training.sdk.errors import (
    DISCORD_URL,
    HTTP_STATUS_HINTS,
    AGENT_DEBUG_INSTRUCTIONS,
    parse_api_error,
    format_sdk_error,
    parse_retry_after,
    request_with_retries,
    _is_retryable_status_code,
    async_request_with_retries,
    format_checkpoint_promotion_error,
    format_session_checkpoint_promotion_error,
)

_URL = "https://api.example.com/inference/v1/completions"

# ---------------------------------------------------------------------------
# format_sdk_error
# ---------------------------------------------------------------------------


class TestFormatSdkError:
    def test_basic_output(self):
        result = format_sdk_error("Job failed", "bad model", "Fix the model name")
        assert "ERROR: Job failed" in result
        assert "Cause: bad model" in result
        assert "Solution: Fix the model name" in result
        assert f"Agent debug: {AGENT_DEBUG_INSTRUCTIONS}" in result

    def test_with_docs_url(self):
        result = format_sdk_error(
            "Job failed", "bad model", "Fix it", docs_url="https://docs.example.com"
        )
        assert "Docs: https://docs.example.com" in result

    def test_without_docs_url(self):
        result = format_sdk_error("Job failed", "bad model", "Fix it")
        assert "Docs:" not in result

    def test_multiline_solution(self):
        solution = "Step 1: Do this\n  Step 2: Do that"
        result = format_sdk_error("Oops", "reason", solution)
        assert "Step 1: Do this" in result
        assert "Step 2: Do that" in result

    def test_output_line_order(self):
        result = format_sdk_error("W", "C", "S", docs_url="D")
        lines = result.split("\n")
        assert lines[0].startswith("ERROR:")
        assert lines[1].strip().startswith("Cause:")
        assert lines[2].strip().startswith("Solution:")
        assert lines[3].strip().startswith("Agent debug:")
        assert lines[4].strip().startswith("Docs:")

    def test_show_support_includes_discord(self):
        result = format_sdk_error("Oops", "reason", "Try again", show_support=True)
        assert f"Support: {DISCORD_URL}" in result

    def test_show_support_false_no_discord(self):
        result = format_sdk_error("Oops", "reason", "Try again", show_support=False)
        assert "Support:" not in result

    def test_show_support_with_docs(self):
        result = format_sdk_error("W", "C", "S", docs_url="D", show_support=True)
        lines = result.split("\n")
        assert lines[3].strip().startswith("Agent debug:")
        assert lines[4].strip().startswith("Docs:")
        assert lines[5].strip().startswith("Support:")


class TestHttpStatusHints:
    def test_401_mentions_training_scoped_keys(self):
        hint = HTTP_STATUS_HINTS[401]
        assert "training-scoped" in hint
        assert "inference-only" in hint

    def test_403_mentions_valid_key_but_wrong_resource_scope(self):
        hint = HTTP_STATUS_HINTS[403]
        assert "key is valid" in hint
        assert "resource" in hint

    def test_502_mentions_retry(self):
        hint = HTTP_STATUS_HINTS[502]
        assert "Retry" in hint


class TestFormatCheckpointPromotionError:
    def test_502_includes_status_and_retry_guidance(self):
        resp = MagicMock()
        resp.status_code = 502
        resp.json.return_value = {"error": {"message": "bad gateway"}}

        result = format_checkpoint_promotion_error(
            resp,
            checkpoint_id="cp-1",
        )

        assert "Failed to promote checkpoint 'cp-1' (HTTP 502)" in result
        assert "bad gateway" in result
        assert "Retry checkpoint promotion" in result
        assert "Use a checkpoint name returned by list_checkpoints" not in result
        assert f"Support: {DISCORD_URL}" in result

    def test_400_uses_client_error_solution(self):
        resp = MagicMock()
        resp.status_code = 400
        resp.json.return_value = {"error": {"message": "invalid base_model"}}

        result = format_checkpoint_promotion_error(
            resp,
            checkpoint_id="cp-1",
        )

        assert "invalid base_model" in result
        assert "Use a checkpoint name returned by list_checkpoints" in result
        assert "Support:" not in result

    def test_session_404_uses_session_checkpoint_hint(self):
        resp = MagicMock()
        resp.status_code = 404
        resp.json.return_value = {"error": {"message": "session checkpoint not found"}}

        result = format_session_checkpoint_promotion_error(
            resp,
            checkpoint_id="cp-1",
        )

        assert "session checkpoint not found" in result
        assert "Use a checkpoint name returned by list_training_session_checkpoints" in result
        assert "Use a checkpoint name returned by list_checkpoints" not in result


# ---------------------------------------------------------------------------
# parse_api_error
# ---------------------------------------------------------------------------


class TestParseApiError:
    def _resp(self, *, json_body=None, text="", raises=False, status_code=None):
        r = MagicMock()
        r.status_code = status_code
        r.text = text
        if raises:
            r.json.side_effect = ValueError("not json")
        else:
            r.json.return_value = json_body
        return r

    def test_error_string(self):
        resp = self._resp(json_body={"error": "something went wrong"})
        assert parse_api_error(resp) == "something went wrong"

    def test_error_dict_with_message(self):
        resp = self._resp(json_body={"error": {"message": "bad request", "code": 400}})
        assert parse_api_error(resp) == "bad request"

    def test_error_dict_without_message(self):
        resp = self._resp(json_body={"error": {"code": 500}})
        result = parse_api_error(resp)
        assert "code" in result

    def test_plain_text_body(self):
        resp = self._resp(text="  plain text error  ", raises=True)
        assert parse_api_error(resp) == "plain text error"

    def test_non_json_response_returns_response_text(self):
        resp = self._resp(text="<html>error</html>", raises=True)
        assert parse_api_error(resp) == "<html>error</html>"

    def test_empty_body(self):
        resp = self._resp(text="", raises=True)
        assert parse_api_error(resp) == ""

    def test_long_text_truncated_to_200(self):
        resp = self._resp(text="x" * 500, raises=True)
        result = parse_api_error(resp)
        assert len(result) == 200

    def test_no_error_key_returns_whole_body(self):
        resp = self._resp(json_body={"detail": "not found"})
        result = parse_api_error(resp)
        assert "detail" in result


# ---------------------------------------------------------------------------
# _is_retryable_status_code
# ---------------------------------------------------------------------------


class TestIsRetryableStatusCode:
    @pytest.mark.parametrize("code", [408, 429, 500, 502, 503, 504])
    def test_retryable(self, code):
        assert _is_retryable_status_code(code) is True

    @pytest.mark.parametrize("code", [200, 201, 400, 401, 403, 404, 409, 425])
    def test_not_retryable(self, code):
        assert _is_retryable_status_code(code) is False


# ---------------------------------------------------------------------------
# request_with_retries
# ---------------------------------------------------------------------------


class TestRequestWithRetries:
    def _ok_response(self, status=200):
        r = MagicMock(spec=requests.Response)
        r.status_code = status
        return r

    def test_successful_request(self):
        resp = self._ok_response()
        func = MagicMock(return_value=resp)
        result = request_with_retries(func, "http://example.com")
        assert result is resp
        func.assert_called_once()

    @patch("fireworks.training.sdk.errors.time.sleep")
    def test_retry_on_connection_error(self, mock_sleep):
        ok = self._ok_response()
        func = MagicMock(side_effect=[requests.ConnectionError("conn refused"), ok])
        result = request_with_retries(func, "http://example.com")
        assert result is ok
        assert func.call_count == 2
        mock_sleep.assert_called_once()

    @patch("fireworks.training.sdk.errors.time.sleep")
    def test_retry_on_503(self, mock_sleep):
        bad = self._ok_response(503)
        ok = self._ok_response(200)
        func = MagicMock(side_effect=[bad, ok])
        result = request_with_retries(func, "http://example.com")
        assert result.status_code == 200
        mock_sleep.assert_called_once()

    @patch("fireworks.training.sdk.errors.time.sleep")
    @patch("fireworks.training.sdk.errors.time.time")
    def test_exhaust_max_wait_time(self, mock_time, mock_sleep):
        mock_time.side_effect = [0, 0, 100, 100]
        bad = self._ok_response(503)
        func = MagicMock(return_value=bad)
        result = request_with_retries(func, "http://example.com", max_wait_time=5)
        assert result.status_code == 503

    def test_non_retryable_status_returned_immediately(self):
        bad = self._ok_response(400)
        func = MagicMock(return_value=bad)
        result = request_with_retries(func, "http://example.com")
        assert result.status_code == 400
        func.assert_called_once()

    @patch("fireworks.training.sdk.errors.time.sleep")
    @patch("fireworks.training.sdk.errors.time.time")
    def test_connection_error_exhausts_raises(self, mock_time, mock_sleep):
        mock_time.side_effect = [0, 0, 1, 200, 200]
        func = MagicMock(side_effect=requests.ConnectionError("down"))
        with pytest.raises(requests.ConnectionError):
            request_with_retries(func, "http://example.com", max_wait_time=5)

    @patch("fireworks.training.sdk.errors.time.sleep")
    def test_retry_on_timeout_exception(self, mock_sleep):
        ok = self._ok_response()
        func = MagicMock(side_effect=[requests.Timeout("timed out"), ok])
        result = request_with_retries(func, "http://example.com")
        assert result is ok
        assert func.call_count == 2

    def test_425_not_retried(self):
        resp = self._ok_response(425)
        func = MagicMock(return_value=resp)
        result = request_with_retries(func, "http://example.com")
        assert result.status_code == 425
        func.assert_called_once()

    def test_args_and_kwargs_forwarded(self):
        ok = self._ok_response()
        func = MagicMock(return_value=ok)
        request_with_retries(func, "http://example.com", json={"a": 1}, timeout=10)
        func.assert_called_once_with("http://example.com", json={"a": 1}, timeout=10)


# ---------------------------------------------------------------------------
# async_request_with_retries — default retries + per-call opt-out
# ---------------------------------------------------------------------------


class TestAsyncRequestWithRetries:
    @staticmethod
    def _resp(status):
        return httpx.Response(status, request=httpx.Request("POST", _URL))

    @patch("fireworks.training.sdk.errors.asyncio.sleep")
    def test_default_retries_status(self, mock_sleep):
        async def _sleep(_s):
            return None

        mock_sleep.side_effect = _sleep
        seq = [self._resp(503), self._resp(200)]
        calls = {"n": 0}

        async def _func(*a, **k):
            r = seq[min(calls["n"], len(seq) - 1)]
            calls["n"] += 1
            return r

        resp = asyncio.run(async_request_with_retries(_func))
        assert resp.status_code == 200
        assert calls["n"] == 2

    def test_opt_out_makes_single_call(self):
        calls = {"n": 0}

        async def _func(*a, **k):
            calls["n"] += 1
            return self._resp(503)

        resp = asyncio.run(
            async_request_with_retries(_func, retry_status_codes=(), retry_exceptions=())
        )
        assert resp.status_code == 503
        assert calls["n"] == 1  # no transport-level retry (sampling opts out here)

    def test_opt_out_does_not_retry_exceptions(self):
        async def _func(*a, **k):
            raise httpx.ConnectError("down")

        with pytest.raises(httpx.ConnectError):
            asyncio.run(
                async_request_with_retries(_func, retry_status_codes=(), retry_exceptions=())
            )


class TestParseRetryAfter:
    @staticmethod
    def _resp(headers):
        return httpx.Response(429, headers=headers, request=httpx.Request("POST", _URL))

    def test_seconds(self):
        assert parse_retry_after(self._resp({"retry-after": "5"})) == 5.0

    def test_missing(self):
        assert parse_retry_after(self._resp({})) is None

    def test_garbage_is_none(self):
        assert parse_retry_after(self._resp({"retry-after": "soon"})) is None

    def test_http_date_far_past_clamped_to_zero(self):
        assert parse_retry_after(self._resp({"retry-after": "Wed, 21 Oct 2015 07:28:00 GMT"})) == 0.0
