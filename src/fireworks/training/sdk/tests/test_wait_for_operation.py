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
            patch("fireworks.training.sdk.fireworks_client.time.monotonic", side_effect=[0, 1, 2, 3]),
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


class TestPromoteCheckpointAsyncOptIn:
    def test_promote_checkpoint_sends_async_promotion_field(self, client: FireworksClient):
        resp = MagicMock()
        resp.is_success = True
        resp.json.return_value = {
            "model": {
                "name": "accounts/acct/models/out",
                "state": "READY",
                "kind": "HF_BASE_MODEL",
            },
        }

        with patch.object(client, "_post", return_value=resp) as mock_post:
            model = client.promote_checkpoint(
                name="accounts/acct/rlorTrainerJobs/job-1/checkpoints/cp-1",
                output_model_id="out",
                base_model="accounts/fireworks/models/base",
            )

        assert model["name"] == "accounts/acct/models/out"
        body = mock_post.call_args.kwargs["json"]
        assert body["async_promotion"] is True

    def test_promote_checkpoint_retries_without_async_field_for_old_server(self, client: FireworksClient):
        old_server_resp = MagicMock()
        old_server_resp.is_success = False
        old_server_resp.status_code = 400
        old_server_resp.json.return_value = {
            "error": {"message": "unknown field \"async_promotion\""}
        }

        sync_resp = MagicMock()
        sync_resp.is_success = True
        sync_resp.json.return_value = {
            "model": {
                "name": "accounts/acct/models/out",
                "state": "READY",
                "kind": "HF_BASE_MODEL",
            },
        }

        with patch.object(client, "_post", side_effect=[old_server_resp, sync_resp]) as mock_post:
            model = client.promote_checkpoint(
                name="accounts/acct/rlorTrainerJobs/job-1/checkpoints/cp-1",
                output_model_id="out",
                base_model="accounts/fireworks/models/base",
            )

        assert model["name"] == "accounts/acct/models/out"
        assert mock_post.call_count == 2
        assert mock_post.call_args_list[0].kwargs["json"]["async_promotion"] is True
        assert "async_promotion" not in mock_post.call_args_list[1].kwargs["json"]
