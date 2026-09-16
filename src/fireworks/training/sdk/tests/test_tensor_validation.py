"""The optimized union accepts the same tensor values as Tinker's schema."""

import asyncio
from types import SimpleNamespace
from typing import List, Union

import numpy as np
import pytest
from pydantic import TypeAdapter, ValidationError
from tinker.lib import _pydantic_conv

from fireworks.training.sdk._comms import get_comms, comms_context
from fireworks.training.sdk.patches._tinker_tensor_validation_patch import CommsV2TensorData


@pytest.mark.asyncio
async def test_concurrent_request_modes_are_isolated_and_restore_after_failure():
    tensor = SimpleNamespace(
        data=["invalid"] * 100, dtype="float32", shape=[100], sparse_crow_indices=None, sparse_col_indices=None
    )

    async def validate(mode):
        with pytest.raises(ValidationError) as failure:
            with comms_context(mode):
                await asyncio.sleep(0)
                _pydantic_conv._to_pydantic_tensor_data(tensor)
        assert get_comms() == "v1"
        return failure.value.error_count()

    assert await asyncio.gather(validate("v2"), validate("v1")) == [2, 200]


@pytest.mark.parametrize(
    "values",
    [
        [],
        [1, 2, -100],
        [0.1, -0.0, 1e-40, 1e30],
        [1.0, -0.0],
        [True, False],
        [1, 0.1],
        ["1", "2"],
        [2**80],
        [float("inf")],
    ],
)
def test_tensor_union_value_parity(values):
    reference = TypeAdapter(Union[List[int], List[float]])
    expected = reference.validate_python(values)
    actual = CommsV2TensorData(data=values, dtype="float32", shape=[len(values)]).data
    assert actual == expected
    assert list(map(type, actual)) == list(map(type, expected))
    assert np.asarray(actual, dtype=np.float64).tobytes() == np.asarray(expected, dtype=np.float64).tobytes()
