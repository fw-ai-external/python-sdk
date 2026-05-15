# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["BaseModelDetailsParam"]


class BaseModelDetailsParam(TypedDict, total=False):
    checkpoint_format: Annotated[
        Literal["CHECKPOINT_FORMAT_UNSPECIFIED", "NATIVE", "HUGGINGFACE", "UNINITIALIZED"],
        PropertyInfo(alias="checkpointFormat"),
    ]

    huggingface_files: Annotated[SequenceNotStr[str], PropertyInfo(alias="huggingfaceFiles")]
    """A list of Hugging Face files associated with this model.

    Specified if and only if the checkpoint_format is HUGGINGFACE.
    """

    model_type: Annotated[str, PropertyInfo(alias="modelType")]
    """The type of the model."""

    moe: bool
    """If true, this is a Mixture of Experts (MoE) model.

    For serverless models, this affects the price per token.
    """

    parameter_count: Annotated[str, PropertyInfo(alias="parameterCount")]
    """The number of model parameters.

    For serverless models, this determines the price per token.
    """

    supports_fireattention: Annotated[bool, PropertyInfo(alias="supportsFireattention")]
    """Whether this model supports fireattention."""

    supports_mtp: Annotated[bool, PropertyInfo(alias="supportsMtp")]
    """If true, this model supports MTP."""

    tunable: bool
    """Deprecated: V1 training stack only.

    Use per-category tunable flags on Model instead.
    """

    world_size: Annotated[int, PropertyInfo(alias="worldSize")]
    """
    The default number of GPUs the model is served with. If not specified, the
    default is 1.
    """
