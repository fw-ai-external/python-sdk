"""Release selection is resolved at service construction without changing default routing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from collections.abc import Iterator

import pytest

from fireworks.training.sdk.client import (
    TRAINING_RELEASE_CHANNEL_ENV,
    TRAINING_RELEASE_CHANNEL_HEADER,
    FiretitanServiceClient,
    FiretitanSamplingClient,
)
from fireworks.training.sdk._core.lib.public_interfaces.service_client import ServiceClient


@pytest.fixture
def base_client_init(monkeypatch: pytest.MonkeyPatch) -> Iterator[MagicMock]:
    monkeypatch.delenv(TRAINING_RELEASE_CHANNEL_ENV, raising=False)
    monkeypatch.delenv("TINKER_BASE_URL", raising=False)
    with patch.object(ServiceClient, "__init__", return_value=None) as constructor:
        yield constructor


def test_explicit_channel_is_forwarded_without_mutating_headers(base_client_init: MagicMock) -> None:
    headers = {"X-Test": "preserved", "fireworks-release-channel": "canary-old"}
    service = FiretitanServiceClient(api_key="fw-test", release_channel="canary-selected", default_headers=headers)

    sent_headers = base_client_init.call_args.kwargs["default_headers"]
    assert sent_headers[TRAINING_RELEASE_CHANNEL_HEADER] == "canary-selected"
    assert sent_headers["X-Test"] == "preserved"
    assert "fireworks-release-channel" not in sent_headers
    assert headers["fireworks-release-channel"] == "canary-old"
    assert service._serverless_sampling_headers()[TRAINING_RELEASE_CHANNEL_HEADER] == "canary-selected"


def test_environment_channel_is_resolved_once(base_client_init: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-original")
    service = FiretitanServiceClient(api_key="fw-test")
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-later")

    assert base_client_init.call_args.kwargs["default_headers"][TRAINING_RELEASE_CHANNEL_HEADER] == "canary-original"
    assert service._serverless_sampling_headers()[TRAINING_RELEASE_CHANNEL_HEADER] == "canary-original"


def test_sampler_handle_preserves_channel_after_environment_changes(
    base_client_init: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-original")
    service = FiretitanServiceClient(api_key="fw-test")
    sampler = FiretitanSamplingClient.create(
        inference_url="https://training.example.test/training/v1/serverless",
        model="accounts/test-account/trainingSessions/ts-test",
        api_key="fw-test",
        additional_headers=service._serverless_sampling_headers(),
    )
    try:
        handle = sampler.get_sampler_handle()
    finally:
        sampler.close()
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-later")
    restored = FiretitanSamplingClient.from_sampler_handle(handle, api_key="fw-restored")
    try:
        assert restored.deployment_sampler.additional_headers[TRAINING_RELEASE_CHANNEL_HEADER] == "canary-original"
    finally:
        restored.close()


def test_explicit_channel_overrides_environment(base_client_init: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-environment")
    FiretitanServiceClient(api_key="fw-test", release_channel="canary-explicit")

    assert base_client_init.call_args.kwargs["default_headers"][TRAINING_RELEASE_CHANNEL_HEADER] == "canary-explicit"


def test_explicit_empty_channel_selects_default(base_client_init: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-environment")
    service = FiretitanServiceClient(
        api_key="fw-test", release_channel="", default_headers={"fireworks-release-channel": "canary-header"}
    )

    assert not any("release-channel" in name.lower() for name in base_client_init.call_args.kwargs["default_headers"])
    assert not any("release-channel" in name.lower() for name in service._serverless_sampling_headers())


def test_omitted_channel_preserves_default_behavior(base_client_init: MagicMock) -> None:
    service = FiretitanServiceClient(api_key="fw-test")

    assert TRAINING_RELEASE_CHANNEL_HEADER not in base_client_init.call_args.kwargs["default_headers"]
    assert TRAINING_RELEASE_CHANNEL_HEADER not in service._serverless_sampling_headers()
    assert "release_channel" not in base_client_init.call_args.kwargs


def test_non_string_channel_cannot_silently_select_default(base_client_init: MagicMock) -> None:
    with pytest.raises(ValueError, match="must be a string or None"):
        FiretitanServiceClient(api_key="fw-test", release_channel=False)  # type: ignore[arg-type]
    base_client_init.assert_not_called()


@pytest.mark.parametrize("env_channel", [None, "canary-environment"])
def test_manual_header_is_preserved(
    base_client_init: MagicMock, monkeypatch: pytest.MonkeyPatch, env_channel: str | None
) -> None:
    if env_channel is not None:
        monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, env_channel)
    FiretitanServiceClient(api_key="fw-test", default_headers={"fireworks-release-channel": "canary-header"})

    sent_headers = base_client_init.call_args.kwargs["default_headers"]
    assert sent_headers["fireworks-release-channel"] == "canary-header"
    assert TRAINING_RELEASE_CHANNEL_HEADER not in sent_headers


def test_dedicated_client_ignores_environment(base_client_init: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-environment")
    FiretitanServiceClient(api_key="fw-test", base_url="https://trainer.example.test")

    assert TRAINING_RELEASE_CHANNEL_HEADER not in base_client_init.call_args.kwargs["default_headers"]


def test_dedicated_client_rejects_explicit_channel(base_client_init: MagicMock) -> None:
    with pytest.raises(ValueError, match="only supported for serverless training"):
        FiretitanServiceClient(
            api_key="fw-test", base_url="https://trainer.example.test", release_channel="canary-selected"
        )
    base_client_init.assert_not_called()


def test_managed_client_ignores_environment(base_client_init: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-environment")
    service = FiretitanServiceClient(api_key="fw-test", managed_config=object())

    base_client_init.assert_not_called()
    assert TRAINING_RELEASE_CHANNEL_HEADER not in service._serverless_sampling_headers()


def test_managed_client_rejects_explicit_channel(base_client_init: MagicMock) -> None:
    with pytest.raises(ValueError, match="only supported for serverless training"):
        FiretitanServiceClient(api_key="fw-test", managed_config=object(), release_channel="canary-selected")
    base_client_init.assert_not_called()


def test_environment_endpoint_is_resolved_before_channel(
    base_client_init: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TINKER_BASE_URL", "https://training.example.test/training/v1/serverless/")
    monkeypatch.setenv(TRAINING_RELEASE_CHANNEL_ENV, "canary-environment")
    FiretitanServiceClient(api_key="fw-test")

    assert base_client_init.call_args.kwargs["default_headers"][TRAINING_RELEASE_CHANNEL_HEADER] == "canary-environment"
