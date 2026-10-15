"""Public operations must reflect the selected Fireworks endpoint's capabilities."""

from __future__ import annotations

import itertools
from collections.abc import Iterator

import httpx
import pytest

from fireworks.training.sdk import FiretitanServiceClient

_REST_OPERATIONS = (
    "get_training_run",
    "get_training_run_by_tinker_path",
    "list_training_runs",
    "list_checkpoints",
    "list_user_checkpoints",
    "get_session",
    "list_sessions",
    "get_sampler",
    "delete_checkpoint",
    "delete_checkpoint_from_tinker_path",
    "get_checkpoint_archive_url",
    "get_checkpoint_archive_url_from_tinker_path",
    "publish_checkpoint_from_tinker_path",
    "unpublish_checkpoint_from_tinker_path",
    "set_checkpoint_ttl_from_tinker_path",
    "get_audit_log",
    "assign_session_project",
)


@pytest.fixture(params=("managed", "dedicated", "serverless"))
def endpoint(request: pytest.FixtureRequest) -> Iterator[tuple[FiretitanServiceClient, list[httpx.Request]]]:
    requests: list[httpx.Request] = []

    def respond(message: httpx.Request) -> httpx.Response:
        requests.append(message)
        if message.url.path.endswith("/weights_info"):
            return httpx.Response(
                200,
                json={
                    "base_model": "accounts/fireworks/models/server-model",
                    "is_lora": True,
                    "lora_rank": 4,
                    "train_unembed": False,
                    "train_mlp": False,
                    "train_attn": True,
                },
            )
        if message.url.path.endswith("/get_server_capabilities"):
            return httpx.Response(200, json={"supported_models": [{"model_name": "server-model"}]})
        raise AssertionError(f"Unexpected request: {message.method} {message.url.path}")

    if request.param == "managed":
        service = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-test",
            base_model="accounts/fireworks/models/config-model",
            tokenizer_model="test-tokenizer",
            lora_rank=8,
        )
    else:
        suffix = "serverless" if request.param == "serverless" else "rlorTrainerJobs/account/job"
        service = FiretitanServiceClient(
            api_key="fw-test",
            base_url="https://trainer.test/training/v1/" + suffix,
            _skip_session=True,
            _client_config={"use_pyqwest_transport": False},
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        )
    try:
        yield service, requests
    finally:
        service.close()


@pytest.mark.parametrize("operation,async_suffix", tuple(itertools.product(_REST_OPERATIONS, ("", "_async"))))
def test_tinker_only_rest_operations_are_not_exposed(endpoint, operation: str, async_suffix: str) -> None:
    service, requests = endpoint
    method = operation + async_suffix
    with pytest.raises(AttributeError, match=method):
        getattr(service.create_rest_client(), method)("arbitrary-id", "checkpoint")
    assert requests == []


def test_weights_metadata_is_serverless_only_and_authoritative(endpoint) -> None:
    service, requests = endpoint
    rest = service.create_rest_client()
    if not getattr(service, "_training_base_url", "").endswith("/serverless"):
        with pytest.raises(NotImplementedError, match="serverless"):
            rest.get_weights_info_by_tinker_path("account/run-real/step-1")
        assert requests == []
        return
    metadata = rest.get_weights_info_by_tinker_path("account/run-real/step-1").result()
    assert metadata.base_model == "accounts/fireworks/models/server-model"
    assert metadata.lora_rank == 4
    assert metadata.train_mlp is False
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path.endswith("/weights_info")
    assert requests[0].content == b'{"tinker_path":"account/run-real/step-1"}'


def test_server_capabilities_are_never_synthesized(endpoint) -> None:
    service, requests = endpoint
    if service._managed_config is not None or getattr(service, "_training_base_url", "").endswith("/serverless"):
        with pytest.raises(NotImplementedError):
            service.get_server_capabilities()
        assert requests == []
        return
    capabilities = service.get_server_capabilities()
    assert [model.model_name for model in capabilities.supported_models] == ["server-model"]
    assert len(requests) == 1
    assert requests[0].url.path.endswith("/get_server_capabilities")
