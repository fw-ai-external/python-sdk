"""Compare native public behavior to the captured pre-migration SDK contract."""

from __future__ import annotations

import json
import inspect
from pathlib import Path

import pytest

from fireworks.training.sdk import client as sdk_client
from tests_training.runtime_probe import shape, wire_probe

_BASELINE = json.loads((Path(__file__).parent / "fixtures/native_runtime_contract.json").read_text())


def test_reserved_training_session_factory_signature() -> None:
    # shape() captures ordinary methods; this explicitly covers the new
    # classmethod without changing the frozen pre-migration contract.
    cls = sdk_client.FiretitanServiceClient
    assert isinstance(vars(cls)["from_reserved_training_session"], classmethod)
    method = cls.from_reserved_training_session
    assert not inspect.iscoroutinefunction(method)
    assert [[p.name, str(p.kind), str(p.default)] for p in inspect.signature(method).parameters.values()] == [
        ["name", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"],
        ["expected_display_name", "KEYWORD_ONLY", "<class 'inspect._empty'>"],
        ["api_key", "KEYWORD_ONLY", "None"],
        ["base_url", "KEYWORD_ONLY", "None"],
        ["additional_headers", "KEYWORD_ONLY", "None"],
    ]


@pytest.mark.parametrize("route", ["dedicated", "serverless"])
@pytest.mark.parametrize("comms", ["v1", "v2"])
def test_native_json_operations_match_frozen_baseline(route: str, comms: str) -> None:
    assert wire_probe(route, comms) == _BASELINE["wire"][route + "-" + comms]


@pytest.mark.parametrize(
    "cls",
    [sdk_client.FiretitanServiceClient, sdk_client.FiretitanTrainingClient, sdk_client.FiretitanSamplingClient],
)
def test_native_public_method_signatures_match_frozen_baseline(cls: type) -> None:
    current = shape(cls)
    if cls is sdk_client.FiretitanTrainingClient:
        assert current.pop("validate_loss_capabilities") == {
            "async": False,
            "params": [
                ["self", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"],
                ["loss_fn", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"],
                ["loss_fn_config", "POSITIONAL_OR_KEYWORD", "None"],
            ],
        }
        assert current.pop("unload_model") == {
            "async": False,
            "params": [["self", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"]],
        }
    if cls is sdk_client.FiretitanServiceClient:
        assert current.pop("delete_training_session") == {
            "async": False,
            "params": [["self", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"]],
        }
        assert current.pop("log_training_metrics") == {
            "async": False,
            "params": [
                ["self", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"],
                ["record", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"],
            ],
        }
        backend_mode = ["backend_managed_concurrency", "KEYWORD_ONLY", "False"]
        for method in (
            "create_sampling_client",
            "create_deployment_sampler_for_model",
            "create_inference_deployment_sampler",
            "create_deployment_sampler",
        ):
            params = current[method]["params"]
            assert backend_mode in params
            params.remove(backend_mode)
    if cls is sdk_client.FiretitanSamplingClient:
        # Credential-free sampler handles (Tinker get_sampler_handle / from_sampler_handle).
        assert current.pop("get_sampler_handle") == {
            "async": False,
            "params": [["self", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"]],
        }
        assert current.pop("from_sampler_handle") == {
            "async": False,
            "params": [
                ["handle", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"],
                ["api_key", "KEYWORD_ONLY", "None"],
                ["tokenizer", "KEYWORD_ONLY", "None"],
            ],
        }
    expected = dict(_BASELINE["api"][cls.__name__])
    if cls is sdk_client.FiretitanTrainingClient:
        for name in (
            "save_weights_and_get_sampling_client",
            "save_weights_and_get_sampling_client_async",
            "save_weights_and_get_sampling_client_submit",
        ):
            expected.pop(name)
            assert not hasattr(cls, name)
    assert current == expected
