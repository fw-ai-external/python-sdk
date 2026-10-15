"""Native validation and array ownership on the native input boundary."""

from __future__ import annotations

import json
from collections import deque

import pytest

from fireworks.training.sdk import types
from fireworks.training.sdk.client import _tensor_value_count


@pytest.mark.parametrize(
    ("tokens", "container"),
    [([1, 2, 3], list), ((1, 2, 3), tuple), (range(1, 4), list), (deque([1, 2, 3]), deque)],
)
def test_token_json_preserves_values_and_python_sequence_type(tokens, container):
    chunk = types.EncodedTextChunk(tokens=tokens)
    assert type(chunk.tokens) is container
    assert type(chunk.model_dump(mode="python")["tokens"]) is container
    assert type(chunk.model_dump(mode="custom")["tokens"]) is container
    assert chunk.model_dump(mode="json") == {"tokens": [1, 2, 3], "type": "encoded_text"}
    assert json.loads(chunk.model_dump_json()) == chunk.model_dump(mode="json")


@pytest.mark.parametrize("mode", ["validation", "serialization"])
def test_token_json_schema_preserves_array_of_integer_contract(mode):
    assert types.EncodedTextChunk.model_json_schema(mode=mode)["properties"]["tokens"] == {
        "items": {"type": "integer"},
        "title": "Tokens",
        "type": "array",
    }


def test_sparse_size_estimation_counts_stored_values_without_lists_or_densification():
    class SparseTensor(types.TensorData):
        @property
        def data(self):
            raise AssertionError("Counting must not box sparse tensor elements")

        def to_numpy(self):
            raise AssertionError("Counting must not densify a sparse tensor")

    tensor = SparseTensor(
        data=[0.25, -0.0],
        dtype="float32",
        shape=[2, 4],
        sparse_crow_indices=[0, 1, 2],
        sparse_col_indices=[1, 3],
    )
    assert _tensor_value_count(tensor) == 2
