"""Tests for serverless-only capacity/recovery HTTP 409 retry on future retrieve."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from tinker.lib import api_future_impl

import fireworks.training.sdk.patches  # noqa: F401
from fireworks.training.sdk.errors import _tinker_source_error

_SERVERLESS_URL = "https://api.example.com/training/v1/serverless/api/v1/retrieve_future"
_DEDICATED_URL = "https://api.example.com/training/v1/rlorTrainerJobs/acct/job/api/v1/retrieve_future"


class _FakeAPIStatusError(Exception):
    def __init__(self, *, status: int, body: Any, detail: str, url: str) -> None:
        super().__init__(detail)
        self.request = httpx.Request("POST", url)
        self.response = httpx.Response(status, json=body, request=self.request)
        self.body = body


def _transport(status: int, body: Any, detail: str, *, url: str = _SERVERLESS_URL):
    return api_future_impl._rest_status_error_to_transport_error(
        _FakeAPIStatusError(status=status, body=body, detail=detail, url=url)
    )


def test_serverless_capacity_409_retries() -> None:
    t = _transport(409, {"detail": "model lifecycle is closing"}, "Error code: 409")
    assert t.kind is api_future_impl._TransportErrorKind.RETRY_WITH_BACKOFF


def test_serverless_bare_409_retries() -> None:
    t = _transport(409, {}, "Error code: 409")
    assert t.kind is api_future_impl._TransportErrorKind.RETRY_WITH_BACKOFF


def test_dedicated_trainer_409_stays_fatal() -> None:
    t = _transport(
        409,
        {"detail": "model lifecycle is closing"},
        "Error code: 409",
        url=_DEDICATED_URL,
    )
    assert t.kind is api_future_impl._TransportErrorKind.FATAL


def test_serverless_already_exists_409_stays_fatal() -> None:
    t = _transport(409, {"detail": "model already exists"}, "Error code: 409 - already exists")
    assert t.kind is api_future_impl._TransportErrorKind.FATAL


def test_serverless_durable_state_conflict_stays_fatal() -> None:
    t = _transport(
        409,
        {"detail": "request conflicts with durable model state"},
        "Error code: 409",
    )
    assert t.kind is api_future_impl._TransportErrorKind.FATAL


@pytest.mark.parametrize("state", ["FAILED", "EXPIRED"])
def test_serverless_terminal_run_state_409_stays_fatal(state: str) -> None:
    t = _transport(
        409,
        {"detail": f"cannot resume training run run-example: run state is {state}, not READY or legacy UNSPECIFIED"},
        "Error code: 409",
    )
    assert t.kind is api_future_impl._TransportErrorKind.FATAL


@pytest.mark.parametrize(
    "body",
    [
        {"detail": "unrecognized explicit conflict"},
        {"error_class": "precondition_failed"},
        {"error": {"code": "PRECONDITION_FAILED"}},
        "unrecognized explicit conflict",
    ],
)
def test_serverless_unknown_explicit_409_stays_fatal(body: Any) -> None:
    t = _transport(409, body, "Error code: 409")
    assert t.kind is api_future_impl._TransportErrorKind.FATAL


@pytest.mark.parametrize("body", [None, "", " "])
def test_serverless_empty_body_409_retries(body: Any) -> None:
    t = _transport(409, body, "Error code: 409")
    assert t.kind is api_future_impl._TransportErrorKind.RETRY_WITH_BACKOFF


@pytest.mark.parametrize("error_class", ["capacity_exhausted", "recovery_required"])
def test_serverless_classified_transient_409_retries(error_class: str) -> None:
    t = _transport(409, {"error_class": error_class}, "Error code: 409")
    assert t.kind is api_future_impl._TransportErrorKind.RETRY_WITH_BACKOFF


@pytest.mark.parametrize(
    "response_kwargs",
    [
        {"json": {"detail": "unrecognized explicit conflict"}},
        {"text": "unrecognized explicit conflict"},
    ],
)
def test_serverless_explicit_409_without_parsed_body_stays_fatal(response_kwargs: dict[str, Any]) -> None:
    exc = _FakeAPIStatusError(status=409, body=None, detail="Error code: 409", url=_SERVERLESS_URL)
    exc.response = httpx.Response(409, request=exc.request, **response_kwargs)

    t = api_future_impl._rest_status_error_to_transport_error(exc)

    assert t.kind is api_future_impl._TransportErrorKind.FATAL


def test_serverless_empty_body_with_explicit_source_409_stays_fatal() -> None:
    exc = _FakeAPIStatusError(status=409, body={}, detail="Error code: 409", url=_SERVERLESS_URL)
    source = _tinker_source_error(error=None, category="User", error_class="precondition_failed")
    exc._fireworks_training_error_source = source

    t = api_future_impl._rest_status_error_to_transport_error(exc)

    assert t.kind is api_future_impl._TransportErrorKind.FATAL
