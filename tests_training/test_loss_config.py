"""Target-policy support choices survive serialization and fail closed before submission."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from concurrent.futures import Future

import pytest

from fireworks.training.sdk._core import TrainingClient
from fireworks.training.sdk.client import (
    FiretitanTrainingClient,
    _CreateModelResponse,
    _validate_score_centering_references,
)
from fireworks.training.sdk._core.lib._pydantic_conv import to_pydantic_input
from fireworks.training.sdk.types.forward_backward_input import ForwardBackwardInput
from fireworks.training.sdk._core.lib.public_interfaces.api_future import AwaitableConcurrentFuture


@pytest.mark.parametrize("support_choice", ["full_vocabulary", "sampling_support", "candidates"])
def test_support_choice_mode_survives_wire_conversion(support_choice):
    config = {"target_logprob_support": support_choice, "clip_low_threshold": 0.2}
    body = to_pydantic_input(ForwardBackwardInput(data=[], loss_fn="ppo", loss_fn_config=config)).model_dump(
        mode="json"
    )
    assert body["loss_fn_config"] == config
    assert body["loss_fn_config"]["target_logprob_support"] == support_choice


@pytest.mark.parametrize("value", [None, False, True, 1, "true"])
@pytest.mark.parametrize(
    "field",
    [
        "supports_target_logprob_support",
        "supports_reinforce",
        "supports_score_centering",
        "supports_mc_score_centering",
        "supports_policy_importance_sampling",
        "supports_policy_diagnostics",
    ],
)
def test_only_explicit_boolean_capability_is_known(value, field: str) -> None:
    response = _CreateModelResponse(model_id="m", **{field: value})
    assert getattr(response, field) is (value if type(value) is bool else None)


@pytest.mark.parametrize(
    "reinforce,centering,config",
    [
        (None, True, None),
        (False, True, None),
        (True, None, {"score_centering": True}),
        (True, False, {"score_centering": True}),
    ],
)
@pytest.mark.parametrize("method", ["forward", "forward_backward"])
def test_unsupported_reinforce_fails_before_submission(reinforce, centering, config, method: str) -> None:
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_reinforce = reinforce
    client.supports_score_centering = centering
    with pytest.raises(ValueError, match="Trainer does not advertise"):
        getattr(client, method)([], "reinforce", config)


@pytest.mark.parametrize("config", [None, {"score_centering": False}, {"score_centering": True, "weighting": "mis"}])
def test_reinforce_configuration_reaches_submission_unchanged(config) -> None:
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_reinforce = True
    client.supports_score_centering = (config or {}).get("score_centering", False)
    client.supports_mc_score_centering = True
    with (
        patch.object(client, "_log_r3_request_error"),
        patch.object(client, "_can_run_firetitan_chunked_requests", return_value=False),
        patch.object(TrainingClient, "forward_backward", return_value="submitted") as submit,
    ):
        assert client.forward_backward([], "reinforce", config) == "submitted"
        submit.assert_called_once_with([], "reinforce", config)


@pytest.mark.parametrize("capability", [False, None])
def test_sampling_support_on_old_trainer_fails_before_submission(capability):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_target_logprob_support = capability
    with pytest.raises(ValueError, match="does not advertise target_logprob_support"):
        client.forward_backward([], "ppo", {"target_logprob_support": "sampling_support"})


@pytest.mark.parametrize(
    "config", [None, {"target_logprob_support": "full_vocabulary"}, {"target_logprob_support": "sampling_support"}]
)
def test_support_choice_selection_reaches_submission_unchanged(config):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_target_logprob_support = (config or {}).get("target_logprob_support") == "sampling_support"
    with (
        patch.object(client, "_log_r3_request_error"),
        patch.object(client, "_can_run_firetitan_chunked_requests", return_value=False),
        patch.object(TrainingClient, "forward_backward", return_value="submitted") as submit,
    ):
        assert client.forward_backward([], "ppo", config) == "submitted"
        submit.assert_called_once_with([], "ppo", config)


def test_candidates_support_reaches_submission_unchanged():
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    config = {"target_logprob_support": "candidates"}
    with (
        patch.object(client, "_log_r3_request_error"),
        patch.object(client, "_can_run_firetitan_chunked_requests", return_value=False),
        patch.object(TrainingClient, "forward_backward", return_value="submitted") as submit,
    ):
        client.forward_backward([], "cross_entropy", config)
        submit.assert_called_once_with([], "cross_entropy", config)


@pytest.mark.parametrize("value", [True, None, "top_tokens"])
@pytest.mark.parametrize("operation", ["forward", "forward_backward"])
def test_invalid_support_choice_is_rejected_before_submission(value, operation):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
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
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    with pytest.raises(ValueError, match=f"{key} is unsupported; use loss_fn_config.target_logprob_support"):
        getattr(client, operation)([], "ppo", {key: value})


@pytest.mark.parametrize("capability", [False, True])
@pytest.mark.parametrize("support", ["sampling_support", "candidates"])
def test_non_vocabulary_support_forward_fails_before_submission(capability, support):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_target_logprob_support = capability
    with pytest.raises(ValueError, match=f"'{support}' requires forward_backward, not forward"):
        client.forward([], "cross_entropy", {"target_logprob_support": support})


@pytest.mark.parametrize("config", [None, {"target_logprob_support": "full_vocabulary"}])
def test_full_vocabulary_forward_reaches_submission_unchanged(config):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")

    def complete(coro):
        pending = Future()
        pending.set_result(asyncio.run(coro))
        return AwaitableConcurrentFuture(pending)

    client.holder = SimpleNamespace(_client_config=None, run_coroutine_threadsafe=complete)

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
        assert client.forward([], "ppo", config).result() == "submitted"
        send.assert_awaited_once_with(0, [], "ppo", config)


@pytest.mark.parametrize("method", ["forward", "forward_backward"])
@pytest.mark.parametrize("capability", [None, False])
def test_server_policy_correction_requires_capability(method: str, capability: bool | None) -> None:
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_policy_importance_sampling = capability
    with pytest.raises(ValueError, match="does not advertise server policy TIS/MIS"):
        getattr(client, method)([], "ppo", {"weighting": "mis", "anchor_logprob_source": "current_detached"})


@pytest.mark.parametrize("diagnostics", [False, True])
def test_supported_policy_correction_is_submitted_unchanged(diagnostics) -> None:
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_policy_importance_sampling = True
    client.supports_policy_diagnostics = diagnostics
    config = {"weighting": "mis", "anchor_logprob_source": "current_detached", "weight_low": 0.2, "weight_high": 5.0}
    if diagnostics:
        config["report_policy_diagnostics"] = True
    with (
        patch.object(client, "_log_r3_request_error"),
        patch.object(client, "_can_run_firetitan_chunked_requests", return_value=False),
        patch.object(TrainingClient, "forward_backward", return_value="submitted") as submit,
    ):
        assert client.forward_backward([], "ppo", config) == "submitted"
        submit.assert_called_once_with([], "ppo", config)


@pytest.mark.parametrize("method", ["forward", "forward_backward"])
@pytest.mark.parametrize("capability", [None, False])
def test_policy_diagnostics_requires_capability(method, capability):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_policy_diagnostics = capability
    with pytest.raises(ValueError, match="does not advertise replay policy diagnostics"):
        getattr(client, method)([], "ppo", {"report_policy_diagnostics": True})


@pytest.mark.parametrize(
    "estimator,capability",
    [
        ("extra_sampling", "supports_mc_score_centering"),
        ("top_sampling", "supports_topk_score_centering"),
    ],
)
def test_sampler_kl_uses_the_selected_score_centering_capability(estimator, capability):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.supports_reinforce = True
    config = {"score_centering": True, "score_centering_estimator": estimator, "sampler_kl_coeff": 0.01}
    with pytest.raises(ValueError, match="does not advertise"):
        client.validate_loss_capabilities("reinforce", config)
    setattr(client, capability, True)
    client.validate_loss_capabilities("reinforce", config)


@pytest.mark.parametrize(
    ("loss_fn", "message"),
    [("reinforce", "requires score_centering=True"), ("ppo", "requires loss_fn='reinforce'")],
)
def test_sampler_kl_requires_score_centered_reinforce_before_submission(loss_fn, message):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.supports_reinforce = True
    with pytest.raises(ValueError, match=message):
        client.validate_loss_capabilities(loss_fn, {"sampler_kl_coeff": 0.01})


@pytest.mark.parametrize("loss_fn", ["importance_sampling", "ppo", "dppo", "gspo", "cross_entropy"])
@pytest.mark.parametrize("config", [{"score_centering": True}, {"score_centering_estimator": "mc"}])
def test_score_centering_requires_reinforce_before_submission(loss_fn, config):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.supports_policy_importance_sampling = True
    with pytest.raises(ValueError, match=f"requires loss_fn='reinforce', got '{loss_fn}'"):
        client._validate_loss_capabilities(loss_fn, config)


@pytest.mark.parametrize("estimator", [None, "extra_sampling"])
def test_implicit_and_explicit_extra_sampling_require_capability(estimator: str | None) -> None:
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.supports_reinforce = client.supports_score_centering = True
    config = {"score_centering": True}
    if estimator is not None:
        config["score_centering_estimator"] = estimator
    with pytest.raises(ValueError, match="extra sampling score centering"):
        client.validate_loss_capabilities("reinforce", config)
    client.supports_mc_score_centering = True
    client.validate_loss_capabilities("reinforce", config)


def test_explicit_top_sampling_requires_its_own_capability() -> None:
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.supports_reinforce = client.supports_score_centering = True
    config = {"score_centering": True, "score_centering_estimator": "top_sampling"}
    with pytest.raises(ValueError, match="does not advertise top sampling"):
        client.validate_loss_capabilities("reinforce", config)
    client.supports_topk_score_centering = True
    client.validate_loss_capabilities("reinforce", config)
    with pytest.raises(ValueError, match="must be 'top_sampling' or 'extra_sampling'"):
        client.validate_loss_capabilities("reinforce", {**config, "score_centering_estimator": "topk"})


@pytest.mark.parametrize("method", ["forward", "forward_backward"])
@pytest.mark.parametrize("estimator", [None, "extra_sampling", "top_sampling"])
def test_mixed_sc_candidate_references_fail_before_submission(method: str, estimator: str | None) -> None:
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_topk_score_centering = True
    client.supports_reinforce = client.supports_score_centering = client.supports_mc_score_centering = True
    config = {"score_centering": True}
    if estimator is not None:
        config["score_centering_estimator"] = estimator
    datum = SimpleNamespace(model_input=SimpleNamespace(top_sampling_references={}, sample_extra_references={}))
    with pytest.raises(ValueError, match="top sampling and extra sampling SC candidates are mutually exclusive"):
        getattr(client, method)([datum], "reinforce", config)


@pytest.mark.parametrize(
    "estimator,top,extra,message",
    [
        ("extra_sampling", True, False, "require score_centering_estimator='top_sampling'"),
        ("extra_sampling", False, False, "sample_extra_tokens=16"),
        ("top_sampling", False, True, "require extra sampling"),
        ("top_sampling", False, False, "requires top_sampling_references"),
    ],
)
def test_sc_reference_mismatch_has_capture_guidance(estimator: str, top: bool, extra: bool, message: str) -> None:
    datum = SimpleNamespace(
        model_input=SimpleNamespace(
            top_sampling_references={} if top else None,
            sample_extra_references={} if extra else None,
        )
    )
    with pytest.raises(ValueError, match=message):
        _validate_score_centering_references([datum], estimator)


def test_deprecated_mc_name_warns_and_submits_canonical_config() -> None:
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_reinforce = client.supports_score_centering = client.supports_mc_score_centering = True
    config = {"score_centering": True, "score_centering_estimator": "mc"}
    with (
        pytest.warns(DeprecationWarning, match="'mc' is deprecated; use 'extra_sampling'") as warnings,
        patch.object(client, "_log_r3_request_error"),
        patch.object(client, "_can_run_firetitan_chunked_requests", return_value=False),
        patch.object(TrainingClient, "forward_backward", return_value="submitted") as submit,
    ):
        assert client.forward_backward([], "reinforce", config) == "submitted"
    assert len(warnings) == 1
    submit.assert_called_once_with([], "reinforce", {**config, "score_centering_estimator": "extra_sampling"})
    assert config["score_centering_estimator"] == "mc"
    with pytest.warns(DeprecationWarning, match="'mc' is deprecated; use 'extra_sampling'") as warnings:
        client.validate_loss_capabilities("reinforce", config)
    assert len(warnings) == 1


@pytest.mark.parametrize("capability", [None, False, True])
@pytest.mark.parametrize("method", ["validate_loss_capabilities", "forward_backward"])
def test_mc_replay_checks_capability_at_startup_and_runtime(capability, method):
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    TrainingClient.__init__(client, SimpleNamespace(), 0, "model-test")
    client.supports_reinforce = client.supports_score_centering = client.supports_mc_score_centering = True
    if capability is not None:
        client.supports_target_logprob_support = capability
    config = {"score_centering": True, "target_logprob_support": "sampling_support"}
    with (
        patch.object(TrainingClient, "forward_backward", return_value="submitted") as submit,
        patch.object(client, "_log_r3_request_error"),
        patch.object(client, "_can_run_firetitan_chunked_requests", return_value=False),
    ):

        def invoke():
            if method == "validate_loss_capabilities":
                return client.validate_loss_capabilities("reinforce", config)
            return client.forward_backward([], "reinforce", config)

        if capability is True:
            invoke()
        else:
            with pytest.raises(ValueError, match="does not advertise target_logprob_support"):
                invoke()
            submit.assert_not_called()
        client.validate_loss_capabilities("reinforce", {"score_centering": True})


def test_tinker_sc_sampling_is_exclusive_and_preserves_generation_filter():
    from fireworks.training.sdk.client import FiretitanSamplingClient, FiretitanSamplingParams

    with pytest.raises(ValueError, match="mutually exclusive"):
        FiretitanSamplingParams(max_tokens=1, sample_extra_tokens=4, top_sampling_logprobs=2)
    params = FiretitanSamplingParams(max_tokens=1, top_k=8, sample_extra_tokens=4, r3_ttl_seconds=60)
    kwargs = FiretitanSamplingClient._sampling_kwargs(params)
    assert (
        kwargs["top_k"],
        kwargs["sample_extra_tokens"],
        kwargs["sample_extra_format"],
        kwargs["r3_ttl_seconds"],
    ) == (8, 4, "parquet_v1", 60)
