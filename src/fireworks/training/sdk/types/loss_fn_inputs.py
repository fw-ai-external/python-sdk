from typing import Dict
from typing_extensions import TypeAlias

from fireworks.training.sdk.types.tensor_data import TensorData

__all__ = ["LossFnInputs"]

LossFnInputs: TypeAlias = Dict[str, TensorData]
