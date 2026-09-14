"""Bound numeric-union errors during Fireworks training request conversion.

Tinker's public and wire schemas remain unchanged. A request-local context
selects this private schema, including when native Tinker and Fireworks clients share
an event loop. CommsV2 F/B response validation uses a separate future context.
"""

from typing import List, Union, Annotated

from pydantic import FailFast
from tinker.lib import _pydantic_conv
from tinker.types._pydantic_types.tensor_data import TensorData

from fireworks.training.sdk._comms import get_comms


class CommsV2TensorData(TensorData):
    # The metadata class is hashable on Python 3.11 / Pydantic 2.9.2.
    data: Union[Annotated[List[int], FailFast], Annotated[List[float], FailFast]]


def _apply_tensor_validation_patch() -> None:
    original = _pydantic_conv._to_pydantic_tensor_data
    if getattr(original, "_fireworks_comms_v2", False):
        return

    def convert_tensor(tensor):
        if get_comms() != "v2":
            return original(tensor)
        return CommsV2TensorData(
            data=tensor.data,
            dtype=tensor.dtype,
            shape=tensor.shape,
            sparse_crow_indices=tensor.sparse_crow_indices,
            sparse_col_indices=tensor.sparse_col_indices,
        )

    convert_tensor._fireworks_comms_v2 = True
    _pydantic_conv._to_pydantic_tensor_data = convert_tensor


_apply_tensor_validation_patch()
