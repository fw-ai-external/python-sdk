"""Tests for long-running operation polling in FireworksClient."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from fireworks.training.sdk.fireworks_client import (
    FireworksClient,
    _TransientOperationPollError,
)


@pytest.fixture
def client() -> FireworksClient:
    return FireworksClient(api_key="test-key", base_url="https://api.test")


class TestGetOperation:
    def test_success(self, client: FireworksClient):
        resp = MagicMock()
        resp.is_success = True
        resp.json.return_value = {"name": "accounts/x/operations/op-1", "done": False}
        with patch.object(client, "_get", return_value=resp) as mock_get:
            result = client._get_operation("accounts/x/operations/op-1")
        assert result["done"] is False
        mock_get.assert_called_once_with("/v1/accounts/x/operations/op-1", timeout=30)

    def test_transient_503(self, client: FireworksClient):
        resp = MagicMock()
        resp.is_success = False
        resp.status_code = 503
        with patch.object(client, "_get", return_value=resp):
            with pytest.raises(_TransientOperationPollError):
                client._get_operation("accounts/x/operations/op-1")

    def test_permanent_404(self, client: FireworksClient):
        resp = MagicMock()
        resp.is_success = False
        resp.status_code = 404
        with patch.object(client, "_get", return_value=resp):
            with pytest.raises(RuntimeError, match="Failed to poll operation"):
                client._get_operation("accounts/x/operations/op-1")

    def test_transient_connect_error(self, client: FireworksClient):
        with patch.object(
            client,
            "_get",
            side_effect=httpx.ConnectError("connection reset"),
        ):
            with pytest.raises(_TransientOperationPollError):
                client._get_operation("accounts/x/operations/op-1")


class TestWaitForOperation:
    def test_completes_after_transient_poll_error(self, client: FireworksClient):
        operation = {
            "name": "accounts/x/operations/op-1",
            "done": False,
        }
        done_operation = {
            "name": "accounts/x/operations/op-1",
            "done": True,
            "response": {"name": "accounts/x/models/out"},
        }
        side_effects = [
            _TransientOperationPollError("HTTP 503"),
            done_operation,
        ]

        with (
            patch.object(client, "_get_operation", side_effect=side_effects) as mock_get,
            patch("fireworks.training.sdk.fireworks_client.time.sleep"),
            patch("fireworks.training.sdk.fireworks_client.time.monotonic", side_effect=[0, 1, 2]),
        ):
            result = client._wait_for_operation(
                operation,
                timeout_s=7200,
                poll_interval_s=0,
            )

        assert result["done"] is True
        assert mock_get.call_count == 2

    def test_non_retryable_poll_error_fails_immediately(self, client: FireworksClient):
        operation = {"name": "accounts/x/operations/op-1", "done": False}
        with (
            patch.object(
                client,
                "_get_operation",
                side_effect=RuntimeError("Failed to poll operation"),
            ),
            patch("fireworks.training.sdk.fireworks_client.time.sleep"),
            patch("fireworks.training.sdk.fireworks_client.time.monotonic", return_value=0),
        ):
            with pytest.raises(RuntimeError, match="Failed to poll operation"):
                client._wait_for_operation(operation, poll_interval_s=0)

    def test_operation_error_after_done(self, client: FireworksClient):
        operation = {
            "name": "accounts/x/operations/op-1",
            "done": True,
            "error": {"message": "promotion failed"},
        }
        with pytest.raises(RuntimeError, match="promotion failed"):
            client._wait_for_operation(operation, poll_interval_s=0)
