from unittest.mock import MagicMock

import httpx
import pytest

from fireworks.training.sdk.client import FiretitanServiceClient
from fireworks.training.sdk.fireworks_client import FireworksClient


def _response(status_code: int, payload: dict) -> httpx.Response:
    return httpx.Response(
        status_code,
        json=payload,
        request=httpx.Request("POST", "https://api.test/v1/accounts/acme/supportTickets"),
    )


def test_create_support_ticket_requires_confirmation() -> None:
    client = FireworksClient(api_key="test-key", base_url="https://api.test")
    client._post = MagicMock()

    with pytest.raises(ValueError, match="user_confirmed=True is required"):
        client.create_support_ticket(
            question_type="job_failure",
            subject="Training failed",
            description="Reviewed description",
        )

    client._post.assert_not_called()
    client.close()


def test_create_support_ticket_submits_reviewed_fields() -> None:
    client = FireworksClient(api_key="test-key", base_url="https://api.test")
    client._post = MagicMock(
        return_value=_response(
            200,
            {
                "submissionStatus": "SUBMISSION_STATUS_SUBMITTED",
                "ticketId": "issue_123",
            },
        )
    )

    result = client.create_support_ticket(
        question_type="job-failure",
        subject="Training failed",
        description="Reviewed description",
        resource_name="accounts/acme/trainingSessions/session-1/trainingRuns/run-1",
        error_reason="BACKEND_ERROR",
        request_id="req-123",
        user_confirmed=True,
    )

    client._post.assert_called_once_with(
        "/v1/accounts/acme/supportTickets",
        json={
            "parent": "accounts/acme",
            "questionType": "SUPPORT_QUESTION_TYPE_JOB_FAILURE",
            "subject": "Training failed",
            "description": "Reviewed description",
            "resourceName": "accounts/acme/trainingSessions/session-1/trainingRuns/run-1",
            "errorReason": "BACKEND_ERROR",
            "requestId": "req-123",
            "userConfirmed": True,
        },
    )
    assert result["ticketId"] == "issue_123"
    client.close()


def test_create_support_ticket_rejects_unknown_question_type() -> None:
    client = FireworksClient(api_key="test-key", base_url="https://api.test")
    client._post = MagicMock()

    with pytest.raises(ValueError, match="invalid question_type"):
        client.create_support_ticket(
            question_type="unknown",
            subject="Training failed",
            description="Reviewed description",
            user_confirmed=True,
        )

    client._post.assert_not_called()
    client.close()


def test_create_support_ticket_reports_api_failure() -> None:
    client = FireworksClient(api_key="test-key", base_url="https://api.test")
    client._post = MagicMock(return_value=_response(400, {"error": {"message": "resource is not accessible"}}))

    with pytest.raises(RuntimeError, match="resource is not accessible"):
        client.create_support_ticket(
            question_type="job_failure",
            subject="Training failed",
            description="Reviewed description",
            account_id="acme",
            user_confirmed=True,
        )

    client.close()


def test_training_api_service_client_delegates_to_control_plane(monkeypatch) -> None:
    seen: dict = {}

    def fake_create_support_ticket(self, **kwargs):
        seen["base_url"] = self.base_url
        seen["kwargs"] = kwargs
        return {"ticketId": "issue_789"}

    monkeypatch.setattr(FireworksClient, "create_support_ticket", fake_create_support_ticket)
    service = object.__new__(FiretitanServiceClient)
    service._fireworks_api_key = "test-key"
    service._managed_base_url = "https://api.test/training/v1/serverless"

    result = service.create_support_ticket(
        question_type="job_failure",
        subject="Training run failed",
        description="Reviewed description",
        resource_name="accounts/acme/trainingSessions/session-1/trainingRuns/run-1",
        error_reason="BACKEND_ERROR",
        request_id="req-789",
        user_confirmed=True,
    )

    assert result["ticketId"] == "issue_789"
    assert seen["base_url"] == "https://api.test"
    assert seen["kwargs"]["error_reason"] == "BACKEND_ERROR"
    assert seen["kwargs"]["user_confirmed"] is True
