"""Compare native public behavior to the captured pre-migration SDK contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fireworks.training.sdk import client as sdk_client
from tests_training.runtime_probe import shape, wire_probe

_BASELINE = json.loads((Path(__file__).parent / "fixtures/native_runtime_contract.json").read_text())


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
        assert current.pop("unload_model") == {
            "async": False,
            "params": [["self", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"]],
        }
    if cls is sdk_client.FiretitanServiceClient:
        assert current.pop("delete_training_session") == {
            "async": False,
            "params": [["self", "POSITIONAL_OR_KEYWORD", "<class 'inspect._empty'>"]],
        }
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
