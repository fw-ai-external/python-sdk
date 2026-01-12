# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["BaseModelDetails"]


class BaseModelDetails(BaseModel):
    checkpoint_format: Optional[Literal["CHECKPOINT_FORMAT_UNSPECIFIED", "NATIVE", "HUGGINGFACE", "UNINITIALIZED"]] = (
        FieldInfo(alias="checkpointFormat", default=None)
    )

    default_precision: Optional[
        Literal[
            "PRECISION_UNSPECIFIED",
            "FP16",
            "FP8",
            "FP8_MM",
            "FP8_AR",
            "FP8_MM_KV_ATTN",
            "FP8_KV",
            "FP8_MM_V2",
            "FP8_V2",
            "FP8_MM_KV_ATTN_V2",
            "NF4",
            "FP4",
            "BF16",
            "FP4_BLOCKSCALED_MM",
            "FP4_MX_MOE",
        ]
    ] = FieldInfo(alias="defaultPrecision", default=None)
    """Default precision of the model."""

    api_model_type: Optional[str] = FieldInfo(alias="modelType", default=None)
    """The type of the model."""

    moe: Optional[bool] = None
    """If true, this is a Mixture of Experts (MoE) model.

    For serverless models, this affects the price per token.
    """

    parameter_count: Optional[str] = FieldInfo(alias="parameterCount", default=None)
    """The number of model parameters.

    For serverless models, this determines the price per token.
    """

    supports_fireattention: Optional[bool] = FieldInfo(alias="supportsFireattention", default=None)
    """Whether this model supports fireattention."""

    supports_mtp: Optional[bool] = FieldInfo(alias="supportsMtp", default=None)
    """If true, this model supports MTP."""

    tunable: Optional[bool] = None
    """If true, this model is available for fine-tuning."""

    world_size: Optional[int] = FieldInfo(alias="worldSize", default=None)
    """
    The default number of GPUs the model is served with. If not specified, the
    default is 1.
    """
