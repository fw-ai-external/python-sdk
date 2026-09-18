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
    sampler.routing_matrix_format = "parquet_v1"
    sampler.r3_store_id = "test"
    prompt = [11, 12, 13, 14, 15]
    echo_count = 5 if echo_last is None else min(echo_last, 5)
    ids = (prompt[-echo_count:] if echo_count else []) + [21, 22]
    routes = refs(len(ids), 100)
    choice = {
        "text": "ok",
        "raw_output": {"completion_token_ids": ids},
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
    with pytest.raises(ValueError, match="acknowledge"):
        sampler._parse_completions_result({"choices": [choice]}, prompt, None, True, True, True, True)


def test_model_input_copy_clears_the_previous_routing_representation():
    # The training client installs these extensions; do not depend on test order.
    from tinker import types

    import fireworks.training.sdk.patches  # noqa: F401
    from fireworks.training.sdk.routing import routing_model_input_kwargs

    original = types.ModelInput.from_ints([1, 2], routing_matrices=["a", "b"])
    updated = original.model_copy(update=routing_model_input_kwargs(refs(2)))
    assert updated.routing_matrix_format == "parquet_v1"
    assert updated.routing_matrices is None
    assert updated.routing_references == refs(2).to_dict()
    restored = updated.model_copy(update=routing_model_input_kwargs(["a", "b"]))
    assert restored.routing_matrix_format is None
    assert restored.routing_references is None
    assert restored.routing_matrices == ["a", "b"]
