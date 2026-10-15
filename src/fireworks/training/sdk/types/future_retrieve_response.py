from typing import Union
from typing_extensions import TypeAlias

from fireworks.training.sdk.types.try_again_response import TryAgainResponse
from fireworks.training.sdk.types.optim_step_response import OptimStepResponse
from fireworks.training.sdk.types.create_model_response import CreateModelResponse
from fireworks.training.sdk.types.load_weights_response import LoadWeightsResponse
from fireworks.training.sdk.types.save_weights_response import SaveWeightsResponse
from fireworks.training.sdk.types.unload_model_response import UnloadModelResponse
from fireworks.training.sdk.types.forward_backward_output import ForwardBackwardOutput
from fireworks.training.sdk.types.request_failed_response import RequestFailedResponse
from fireworks.training.sdk.types.save_weights_for_sampler_response import SaveWeightsForSamplerResponse

__all__ = ["FutureRetrieveResponse"]

FutureRetrieveResponse: TypeAlias = Union[
    TryAgainResponse,
    ForwardBackwardOutput,
    OptimStepResponse,
    SaveWeightsResponse,
    LoadWeightsResponse,
    SaveWeightsForSamplerResponse,
    CreateModelResponse,
    UnloadModelResponse,
    RequestFailedResponse,
]
