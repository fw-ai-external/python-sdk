"""Compact routing must survive token slicing and actual API response alignment."""

import random

import pytest

from fireworks.training.sdk.routing import (
    RoutingReferences,
    mask_routing,
    concat_routing,
    routing_to_wire,
    routing_from_wire,
)
from fireworks.training.sdk.sampling import DeploymentSampler


def refs(length, start=0):
    return RoutingReferences.from_dict(
        {
            "length": length,
            "files": [
                {
                    "store_id": "test",
                    "file_id": "00000000-0000-0000-0000-000000000001",
                    "format": "parquet_v1",
                    "row_count": start + length,
                    "expires_at": 9999999999,
                }
            ],
            "spans": (
                [{"input_token_start": 0, "file_index": 0, "file_row_start": start, "count": length}] if length else []
            ),
        }
    )


def expand(value):
    result = []
    for span in value.spans:
        result.extend(
            [None] * span["count"]
            if span.get("file_index") is None
            else range(span["file_row_start"], span["file_row_start"] + span["count"])
        )
    return result


def test_compact_slicing_concatenation_and_serialization_match_token_oracle():
    value = concat_routing(refs(11), [""] * 7, refs(15, 100))
    oracle = list(range(11)) + [None] * 7 + list(range(100, 115))
    rng = random.Random(42)
    for _ in range(100):
        start, end = sorted([rng.randrange(-40, 40), rng.randrange(-40, 40)])
        piece = value[start:end]
        assert expand(piece) == oracle[start:end]
        assert len(piece) == len(oracle[start:end])
        assert routing_from_wire(routing_to_wire(piece)) == piece
    with pytest.raises(TypeError):
        list(value)
    with pytest.raises(ValueError):
        concat_routing(value, ["AQI="])


def test_fully_masked_routing_preserves_parquet_representation():
    result = mask_routing(refs(2), [False, False])
    assert isinstance(result, RoutingReferences)
    assert len(result) == 2
    assert expand(result) == [None, None]
    assert routing_from_wire(routing_to_wire(result)) == result


@pytest.mark.parametrize("echo_last", [None, 0, 2, 5, 10])
def test_parquet_full_and_partial_echo_alignment(echo_last):
    sampler = DeploymentSampler("http://unused", "test", "test")
    sampler.r3_store_id = "test"
    prompt = [11, 12, 13, 14, 15]
    echo_count = 5 if echo_last is None else min(echo_last, 5)
    ids = (prompt[-echo_count:] if echo_count else []) + [21, 22]
    routes = refs(len(ids), 100)
    choice = {
        "text": "ok",
        "token_ids": ids,
        "logprobs": {"content": [{"logprob": -1.0, "sampling_logprob": -1.0} for _ in ids]},
        "routing_references": routes.to_dict(),
        "r3_store_id": "test",
        "routing_matrix_format": "parquet_v1",
    }
    result = sampler._parse_completions_result(
        {"choices": [choice]}, prompt, None, True, True, echo_last is None, True, echo_last=echo_last
    )[0]
    drop = int(echo_count == 5)
    assert result.full_tokens == prompt + [21, 22]
    assert result.echoed_prompt_logprob_count == echo_count - drop
    assert expand(result.routing_matrices) == list(range(100 + drop, 100 + len(ids)))
    choice["r3_store_id"] = "other"
    with pytest.raises(ValueError, match="trainer's shared storage domain"):
        sampler._parse_completions_result({"choices": [choice]}, prompt, None, True, True, True, True)


@pytest.mark.parametrize("fault", ["all_gaps", "partial_gap", "wrong_length"])
def test_parquet_routing_requires_stored_rows_for_every_generated_token(fault):
    sampler = DeploymentSampler("http://unused", "test", "test")
    sampler.negotiate_routing_matrix_format("parquet_v1", "test")
    payload = refs(2 if fault != "wrong_length" else 1).to_dict()
    if fault == "all_gaps":
        payload["spans"] = [{"input_token_start": 0, "count": 2}]
    elif fault == "partial_gap":
        payload["spans"][0]["count"] = 1
        payload["spans"].append({"input_token_start": 1, "count": 1})
    error = RuntimeError if fault == "wrong_length" else ValueError
    try:
        with pytest.raises(error, match="R3 references"):
            sampler._parse_completions_result(
                {"choices": [{
                    "token_ids": [2, 3],
                    "routing_matrix_format": "parquet_v1",
                    "routing_references": payload,
                    "r3_store_id": "test",
                }]},
                [1], None, False, True, False, True,
            )
    finally:
        sampler.close()


@pytest.mark.parametrize("echo_last", [None, 0, 2, 5])
@pytest.mark.parametrize("echoed_rows", [True, False])
@pytest.mark.parametrize("column", ["top_sampling", "sampling_mask"])
def test_parquet_top_sampling_references_are_completion_only(echo_last, echoed_rows, column):
    sampler = DeploymentSampler("http://unused", "test", "test")
    sampler.r3_store_id = "test"
    prompt = [11, 12, 13, 14, 15]
    echo_count = 5 if echo_last is None else min(echo_last, 5)
    ids = (prompt[-echo_count:] if echo_count else []) + [21, 22]
    rows = len(ids) if echoed_rows else 2
    choice = {
        "text": "ok",
        "token_ids": ids,
        "logprobs": {"content": [{"logprob": -1.0, "sampling_logprob": -0.5} for _ in ids]},
        f"{column}_references": refs(rows, 100).to_dict(),
        f"{column}_format": "parquet_v1",
        "r3_store_id": "test",
    }

    def parse(value, requested=True):
        return sampler._parse_completions_result(
            {"choices": [value]},
            prompt,
            None,
            True,
            False,
            echo_last is None,
            True,
            echo_last=echo_last,
            top_sampling_requested=requested and column == "top_sampling",
            sampling_mask_requested=requested and column == "sampling_mask",
        )[0]

    result = parse(choice)
    assert expand(getattr(result, column + "_references")) == list(range(100 + rows - 2, 100 + rows))
    other = "sampling_mask" if column == "top_sampling" else "top_sampling"
    assert getattr(result, other + "_references") is None
    assert parse(choice, requested=False).top_sampling_references is None
    with pytest.raises(ValueError, match="trainer's shared storage domain"):
        parse({**choice, "r3_store_id": "other"})
    with pytest.raises(ValueError, match="did not return"):
        parse({key: value for key, value in choice.items() if key != f"{column}_references"})
    with pytest.raises(RuntimeError, match="align"):
        parse({**choice, f"{column}_references": refs(1, 100).to_dict()})


def test_top_sampling_references_survive_model_input_wire_serialization():
    import fireworks.training.sdk._core as tinker
    from fireworks.training.sdk._core._compat import model_dump
    from fireworks.training.sdk._core.lib._pydantic_conv import to_pydantic_request
    from fireworks.training.sdk.types.forward_backward_input import ForwardBackwardInput
    from fireworks.training.sdk.types.forward_backward_request import ForwardBackwardRequest

    references = concat_routing([""], refs(2, 7))
    model_input = tinker.ModelInput.from_ints([1, 2, 3], routing_matrices=refs(3), top_sampling_references=references)
    assert model_input.top_sampling_references == references.to_dict()
    assert model_input.routing_references == refs(3).to_dict()
    with pytest.raises(ValueError, match="every model input position"):
        tinker.ModelInput.from_ints([1, 2], top_sampling_references=references)
    datum = tinker.Datum(
        model_input=model_input,
        loss_fn_inputs={"target_tokens": tinker.TensorData(data=[2, 3, 4], dtype="int64", shape=[3])},
    )
    body = model_dump(
        to_pydantic_request(
            ForwardBackwardRequest(
                forward_backward_input=ForwardBackwardInput(
                    data=[datum],
                    loss_fn="reinforce",
                    loss_fn_config={"score_centering": True},
                ),
                model_id="model",
                seq_id=1,
            )
        ),
        exclude_unset=False,
        exclude_none=True,
        mode="json",
    )
    wire_input = body["forward_backward_input"]["data"][0]["model_input"]
    assert body["forward_backward_input"]["loss_fn"] == "reinforce"
    assert body["forward_backward_input"]["loss_fn_config"] == {"score_centering": True}
    assert RoutingReferences.from_dict(wire_input["top_sampling_references"]) == references
    assert wire_input["routing_references"] == refs(3).to_dict()
    assert "top_sampling_references" not in tinker.ModelInput.from_ints([1]).model_dump(exclude_unset=True)


def test_model_input_accepts_only_reference_routing() -> None:
    from fireworks.training.sdk import ModelInput
    from fireworks.training.sdk.routing import routing_model_input_kwargs

    data = ModelInput.from_ints([1, 2], routing_matrices=refs(2))
    assert data.routing_matrix_format == "parquet_v1"
    assert data.routing_references == refs(2).to_dict()
    assert data.model_copy(update=routing_model_input_kwargs(None)).routing_references is None
    with pytest.raises(ValueError, match="Inline routing"):
        ModelInput.from_ints([1, 2], routing_matrices=["a", "b"])


def test_independent_mask_head_files_survive_sdk_wire():
    from fireworks.training.sdk import ModelInput

    head, mask = refs(2, 100), refs(2, 200)
    model = ModelInput.from_ints([1, 2], top_sampling_references=head, sampling_mask_references=mask)
    assert model.model_dump()["top_sampling_references"] == head.to_dict()
    assert model.model_dump()["sampling_mask_references"] == mask.to_dict()
    assert model.top_sampling_references != model.sampling_mask_references


def test_sampling_parser_accepts_independent_mask_head_files():
    sampler = DeploymentSampler(model="m", api_key="test", inference_url="https://example.invalid/v1")
    sampler.r3_store_id = "test"
    choice = {
        "text": "x",
        "token_ids": [1, 2],
        "logprobs": {"content": [{"logprob": -0.5, "sampling_logprob": -0.5}] * 2},
        "top_sampling_format": "parquet_v1",
        "sampling_mask_format": "parquet_v1",
        "r3_store_id": "test",
        "top_sampling_references": refs(2, 100).to_dict(),
        "sampling_mask_references": refs(2, 200).to_dict(),
    }
    result = sampler._parse_completions_result(
        {"choices": [choice]},
        [10],
        None,
        True,
        False,
        False,
        True,
        top_sampling_requested=True,
        sampling_mask_requested=True,
    )[0]
    assert expand(result.top_sampling_references) == [100, 101]
    assert expand(result.sampling_mask_references) == [200, 201]


@pytest.mark.parametrize(
    "field", ["routing_references", "top_sampling_references", "sampling_mask_references", "sample_extra_references"]
)
def test_trainer_validates_shared_replay_references(field):
    from types import SimpleNamespace

    from fireworks.training.sdk import ModelInput
    from fireworks.training.sdk.client import FiretitanTrainingClient

    model = ModelInput.from_ints([1, 2])
    references = refs(2).to_dict()
    datum = SimpleNamespace(
        model_input=model.model_copy(update={field: references, "routing_matrix_format": "parquet_v1"})
    )
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client.r3_store_id = "test"
    client._validate_replay_references([datum])
    client.r3_store_id = "another"
    with pytest.raises(ValueError, match="different shared storage"):
        client._validate_replay_references([datum])
    client.r3_store_id = None
    with pytest.raises(ValueError, match="require trainer shared storage"):
        client._validate_replay_references([datum])
    client.r3_store_id = "test"
    datum.model_input = datum.model_input.model_copy(update={"chunks": model.append_int(3).chunks})
    with pytest.raises(ValueError, match="must match the model input token length"):
        client._validate_replay_references([datum])
