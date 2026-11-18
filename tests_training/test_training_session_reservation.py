"""Reservation recovery and ownership checks without live training resources."""

from __future__ import annotations

from unittest.mock import AsyncMock
from collections.abc import Iterator

import httpx
import pytest

from fireworks.training.sdk import FiretitanServiceClient, _rest_client
from fireworks.training.sdk._core.lib import internal_client_holder
from fireworks.training.sdk.fireworks_client import FireworksClient
from fireworks.training.sdk._core.lib.internal_client_holder import InternalClientHolder

NAME = "accounts/customer/trainingSessions/ts-reserved"
MARKER = "exclusive-owner-nonce"


@pytest.fixture
def platform(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict]:
    state = {"session": {"name": NAME, "displayName": MARKER}, "status": 200, "requests": []}

    def handle(request: httpx.Request) -> httpx.Response:
        state["requests"].append(request)
        if request.url.path == "/v1/accounts":
            return httpx.Response(200, json={"accounts": [{"name": "accounts/customer"}]})
        return httpx.Response(state["status"], json=state["session"])

    clients = []

    def make_client(_verify: bool) -> httpx.Client:
        client = httpx.Client(transport=httpx.MockTransport(handle))
        clients.append(client)
        return client

    monkeypatch.setattr(_rest_client, "_make_sync_client", make_client)
    yield state
    for client in clients:
        client.close()


@pytest.fixture
def native_holder(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    create = AsyncMock(side_effect=AssertionError("must not create another session"))
    monkeypatch.setattr(InternalClientHolder, "_create_session", create)
    monkeypatch.setattr(InternalClientHolder, "_session_heartbeat", AsyncMock(return_value=None))
    monkeypatch.setattr(internal_client_holder, "init_telemetry", lambda *_args, **_kwargs: None)
    return create


def test_reservation_reuses_exact_id_and_marker(platform: dict) -> None:
    with FireworksClient(api_key="test-key", base_url="https://example.test") as client:
        first = client.reserve_training_session("ts-reserved", display_name=MARKER)
        second = client.reserve_training_session("ts-reserved", display_name=MARKER)
    assert first == second == platform["session"]
    writes = [request for request in platform["requests"] if request.method == "POST"]
    assert len(writes) == 2
    for request in writes:
        assert request.url.path == "/v1/accounts/customer/trainingSessions"
        assert dict(request.url.params) == {"training_session_id": "ts-reserved"}
        assert request.content == b'{"displayName":"exclusive-owner-nonce","baseModel":""}'


@pytest.mark.parametrize("session_id", ["", "not-prefixed", "ts-../other", "ts-a?query=1", "ts-" + "a" * 61])
def test_invalid_reservation_id_fails_before_io(platform: dict, session_id: str) -> None:
    with FireworksClient(api_key="test-key") as client, pytest.raises(ValueError):
        client.reserve_training_session(session_id, display_name=MARKER)
    assert platform["requests"] == []


def test_reservation_cannot_adopt_an_existing_foreign_marker(platform: dict) -> None:
    platform["session"]["displayName"] = "another-owner"
    with FireworksClient(api_key="test-key") as client, pytest.raises(RuntimeError, match="ownership"):
        client.reserve_training_session("ts-reserved", display_name=MARKER)


@pytest.mark.parametrize("status", [401, 403, 409])
def test_get_does_not_treat_errors_as_absence(platform: dict, status: int) -> None:
    platform.update(status=status, session={"error": {"message": "not available"}})
    with FireworksClient(api_key="test-key") as client, pytest.raises(RuntimeError, match=f"HTTP {status}"):
        client.get_training_session(NAME)


def test_only_not_found_returns_none(platform: dict) -> None:
    platform.update(status=404, session={"error": {"message": "not found"}})
    with FireworksClient(api_key="test-key") as client:
        assert client.get_training_session(NAME) is None


def test_get_preserves_transport_failure_after_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable(*_args: object, **_kwargs: object) -> None:
        raise httpx.ConnectTimeout("transport unavailable")

    with FireworksClient(api_key="test-key") as client:
        client._account_id = "customer"
        monkeypatch.setattr(client, "_get", unavailable)
        with pytest.raises(httpx.ConnectTimeout):
            client.get_training_session(NAME)


def test_get_preserves_server_failure_after_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    with FireworksClient(api_key="test-key") as client:
        client._account_id = "customer"
        monkeypatch.setattr(client, "_get", lambda *_args, **_kwargs: httpx.Response(503, json={}))
        with pytest.raises(RuntimeError, match="HTTP 503"):
            client.get_training_session(NAME)


@pytest.mark.parametrize("name", ["accounts/other/trainingSessions/ts-reserved", NAME + "/other", NAME + "?query=1"])
def test_get_rejects_foreign_or_malformed_resource(platform: dict, name: str) -> None:
    with FireworksClient(api_key="test-key") as client, pytest.raises(ValueError):
        client.get_training_session(name)
    assert not any("trainingSessions" in request.url.path for request in platform["requests"])


def test_get_validates_response_identity(platform: dict) -> None:
    platform["session"]["name"] = "accounts/customer/trainingSessions/ts-other"
    with FireworksClient(api_key="test-key") as client, pytest.raises(RuntimeError, match="requested resource"):
        client.get_training_session(NAME)


@pytest.mark.parametrize("state", [None, "TRAINING_SESSION_STATE_UNSPECIFIED"])
def test_reserved_factory_initializes_fresh_counters_without_creating_session(
    platform: dict, native_holder: AsyncMock, state: str | None
) -> None:
    if state is not None:
        platform["session"]["state"] = state
    service = FiretitanServiceClient.from_reserved_training_session(
        NAME,
        expected_display_name=MARKER,
        api_key="test-key",
        base_url="https://example.test/training/v1/serverless",
        additional_headers={"X-Customer-Routing": "explicit"},
    )
    try:
        assert service.training_session_name == NAME
        assert service.holder.get_training_client_id() == 0
        assert service.holder.get_training_client_id() == 1
        assert service.holder._sampling_client_counter == 0
        assert service.holder._constructor_kwargs["default_headers"]["X-Customer-Routing"] == "explicit"
        assert all(request.headers["X-Customer-Routing"] == "explicit" for request in platform["requests"])
        assert all(request.headers["X-Api-Key"] == "test-key" for request in platform["requests"])
        assert [request.url.path for request in platform["requests"]] == ["/v1/accounts", f"/v1/{NAME}"]
        native_holder.assert_not_called()
    finally:
        service.close()


@pytest.mark.parametrize(
    "changes",
    [
        {"displayName": "another-owner"},
        {"baseModel": "accounts/fireworks/models/model"},
        {"state": "READY"},
        {"state": "FAILED"},
        {"state": "DELETING"},
        {"state": "EXPIRED"},
        {"state": "UNKNOWN_FUTURE_STATE"},
    ],
)
def test_factory_never_resets_bound_or_foreign_session_counters(
    platform: dict, native_holder: AsyncMock, changes: dict
) -> None:
    platform["session"].update(changes)
    with pytest.raises(ValueError):
        FiretitanServiceClient.from_reserved_training_session(NAME, expected_display_name=MARKER, api_key="test-key")
    native_holder.assert_not_called()


def test_factory_rejects_missing_session(platform: dict, native_holder: AsyncMock) -> None:
    platform.update(status=404, session={})
    with pytest.raises(ValueError, match="does not exist"):
        FiretitanServiceClient.from_reserved_training_session(NAME, expected_display_name=MARKER, api_key="test-key")
    native_holder.assert_not_called()


def test_shadow_holder_cannot_allocate_training_clients(native_holder: AsyncMock) -> None:
    holder = InternalClientHolder(session_id="ts-reserved", api_key="test-key", _client_config={})
    try:
        with pytest.raises(AssertionError):
            holder.get_training_client_id()
        assert holder._sampling_client_counter is None
        native_holder.assert_not_called()
    finally:
        holder.close()
