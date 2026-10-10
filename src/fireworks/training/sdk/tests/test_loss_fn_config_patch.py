"""Target-policy support choices survive serialization and fail closed before submission."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from tinker import TrainingClient
from tinker.lib._pydantic_conv import to_pydantic_input
from tinker.types.forward_backward_input import ForwardBackwardInput

import fireworks.training.sdk.patches  # noqa: F401
from fireworks.training.sdk.client import FiretitanTrainingClient, _CreateModelResponse


@pytest.mark.parametrize("support_choice", ["full_vocabulary", "sampling_support"])
def test_support_choice_mode_survives_wire_conversion(support_choice):
    config = {"target_logprob_support": support_choice, "clip_low_threshold": 0.2}
    body = to_pydantic_input(ForwardBackwardInput(data=[], loss_fn="ppo", loss_fn_config=config)).model_dump(
        mode="json"
    )
    assert body["loss_fn_config"] == config
    assert body["loss_fn_config"]["target_logprob_support"] == support_choice


@pytest.mark.parametrize("value", [None, False, True, 1, "true"])
def test_only_explicit_boolean_capability_is_known(value):
    response = _CreateModelResponse(model_id="m", supports_target_logprob_support=value)
    assert response.supports_target_logprob_support is (value if type(value) is bool else None)


@pytest.mark.parametrize("capability", [False, None])
def test_sampling_support_on_old_trainer_fails_before_submission(capability):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.supports_target_logprob_support = capability
    with pytest.raises(ValueError, match="does not advertise target_logprob_support"):
        client.forward_backward([], "ppo", {"target_logprob_support": "sampling_support"})


@pytest.mark.parametrize(
    "config", [None, {"target_logprob_support": "full_vocabulary"}, {"target_logprob_support": "sampling_support"}]
)
def test_support_choice_selection_reaches_submission_unchanged(config):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.supports_target_logprob_support = (config or {}).get("target_logprob_support") == "sampling_support"
    with (
        patch.object(client, "_log_r3_request_error"),
        patch.object(client, "_can_run_firetitan_chunked_requests", return_value=False),
        patch.object(TrainingClient, "forward_backward", return_value="submitted") as submit,
    ):
        assert client.forward_backward([], "ppo", config) == "submitted"
        submit.assert_called_once_with([], "ppo", config)


@pytest.mark.parametrize("value", [True, None, "top_tokens"])
@pytest.mark.parametrize("operation", ["forward", "forward_backward"])
def test_invalid_support_choice_is_rejected_before_submission(value, operation):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    with pytest.raises(ValueError, match="target_logprob_support must be"):
        getattr(client, operation)([], "ppo", {"target_logprob_support": value})


@pytest.mark.parametrize(
    "key,value",
    [
        ("replay", False),
        ("replay", True),
        ("logprob_normalization", "sampling_support"),
        ("importance_sampling", {"target_policy": {"support": "behavior_policy"}}),
    ],
)
@pytest.mark.parametrize("operation", ["forward", "forward_backward"])
def test_old_support_keys_are_rejected_with_migration_hint(key, value, operation):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    with pytest.raises(ValueError, match=f"{key} is unsupported; use loss_fn_config.target_logprob_support"):
        getattr(client, operation)([], "ppo", {key: value})


@pytest.mark.parametrize("capability", [False, True])
def test_sampling_support_forward_fails_before_submission(capability):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.supports_target_logprob_support = capability
    with pytest.raises(ValueError, match="requires forward_backward, not forward"):
        client.forward([], "ppo", {"target_logprob_support": "sampling_support"})


@pytest.mark.parametrize("config", [None, {"target_logprob_support": "full_vocabulary"}])
def test_full_vocabulary_forward_reaches_submission_unchanged(config):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.holder = SimpleNamespace(_client_config=None, run_coroutine_threadsafe=asyncio.run)

    async def submit(chunks, send, *, request_type):
        assert request_type == "Forward"
        future = asyncio.get_running_loop().create_future()
        future.set_result(await send(0, []))
        return future

    with (
        patch.object(client, "_log_r3_request_error"),
        patch.object(client, "_chunked_requests", return_value=[]),
        patch.object(client, "_run_chunked_requests", side_effect=submit),
        patch.object(client, "_send_single_forward_request", new_callable=AsyncMock, return_value="submitted") as send,
    ):
        assert client.forward([], "ppo", config) == "submitted"
        send.assert_awaited_once_with(0, [], "ppo", config)
