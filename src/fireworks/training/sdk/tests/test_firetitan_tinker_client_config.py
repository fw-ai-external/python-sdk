from __future__ import annotations

from types import SimpleNamespace
from typing import Any, NoReturn, cast

import pytest
from tinker.types.client_config_response import ClientConfigResponse
from tinker.lib.public_interfaces.training_client import TrainingClient

from fireworks.training.sdk.client import (
    FIRETITAN_TINKER_CLIENT_CONFIG,
    FiretitanTrainingClient,
)


def _make_training_client(client_config: SimpleNamespace) -> FiretitanTrainingClient:
    return FiretitanTrainingClient(
        holder=SimpleNamespace(_client_config=client_config),
        model_seq_id=1,
        model_id="accounts/test/models/model",
    )


def test_default_firetitan_tinker_config_enables_parallel_fwdbwd_chunks() -> None:
    assert FIRETITAN_TINKER_CLIENT_CONFIG["parallel_fwdbwd_chunks"] is True
    assert FIRETITAN_TINKER_CLIENT_CONFIG["parallel_fwdbwd_chunks"] is ClientConfigResponse().parallel_fwdbwd_chunks


@pytest.mark.parametrize("parallel_fwdbwd_chunks", [False, True])
def test_forward_backward_preserves_requested_parallel_fwdbwd_config(
    monkeypatch: pytest.MonkeyPatch,
    parallel_fwdbwd_chunks: bool,
) -> None:
    client_config = SimpleNamespace(
        parallel_fwdbwd_chunks=parallel_fwdbwd_chunks,
        proto_write_fwdbwd=False,
        proto_compress_fwdbwd=False,
    )
    client = _make_training_client(client_config)
    sentinel = object()
    observed: dict[str, bool] = {}

    def fake_forward_backward(
        _self: Any,
        _data: list[Any],
        _loss_fn: Any,
        _loss_fn_config: dict[str, float] | None = None,
    ) -> object:
        observed["parallel_fwdbwd_chunks"] = cast(bool, _self.holder._client_config.parallel_fwdbwd_chunks)
        return sentinel

    monkeypatch.setattr(TrainingClient, "forward_backward", fake_forward_backward)

    assert cast(Any, client).forward_backward([], "ppo") is sentinel
    assert observed["parallel_fwdbwd_chunks"] is parallel_fwdbwd_chunks
    assert client_config.parallel_fwdbwd_chunks is parallel_fwdbwd_chunks


@pytest.mark.parametrize(
    ("proto_write_fwdbwd", "proto_compress_fwdbwd"),
    [(True, False), (False, True), (True, True)],
)
def test_forward_backward_rejects_proto_transport_even_with_parallel_chunks(
    monkeypatch: pytest.MonkeyPatch,
    proto_write_fwdbwd: bool,
    proto_compress_fwdbwd: bool,
) -> None:
    client_config = SimpleNamespace(
        parallel_fwdbwd_chunks=True,
        proto_write_fwdbwd=proto_write_fwdbwd,
        proto_compress_fwdbwd=proto_compress_fwdbwd,
    )
    client = _make_training_client(client_config)

    def fail_if_called(
        _self: Any,
        _data: list[Any],
        _loss_fn: Any,
        _loss_fn_config: dict[str, float] | None = None,
    ) -> NoReturn:
        raise AssertionError("proto transport should fail before forwarding")

    monkeypatch.setattr(TrainingClient, "forward_backward", fail_if_called)

    with pytest.raises(NotImplementedError, match="proto forward_backward transport"):
        cast(Any, client).forward_backward([], "ppo")
