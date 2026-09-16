"""Exercise result validation through real default and comms v2 futures."""

import asyncio
from types import SimpleNamespace
from contextlib import AsyncExitStack, asynccontextmanager

import numpy as np
import pytest
from tinker import types
from tinker.lib import api_future_impl

from fireworks.training.sdk.patches import _tinker_result_validation_patch as patch


@pytest.mark.asyncio
@pytest.mark.parametrize("comms", ["v1", "v2"])
async def test_future_preserves_public_result_and_restores_mode_after_validation_error(comms):
    raw = {
        "loss_fn_output_type": "ppo",
        "loss_fn_outputs": [{
            "logprobs": {"data": [-0.0, -1.25], "dtype": "float32"},
            "sparse": {"data": [0.5], "dtype": "float32", "shape": [1, 4],
                       "sparse_crow_indices": [0, 1], "sparse_col_indices": [3]},
        }],
        "metrics": {"loss:sum": -1.25},
    }
    cls = patch.CommsV2APIFuture if comms == "v2" else api_future_impl._APIFuture
    future = object.__new__(cls)
    future.model_cls = types.ForwardBackwardOutput
    future.untyped_future = SimpleNamespace(request_id="result-validation")
    future.get_telemetry = lambda: None
    async with AsyncExitStack() as stack:
        result = await future._handle_outcome(
            api_future_impl._SuccessJson(result_dict=raw), api_future_impl._LoopState(), stack, 1, 0.0,
        )
        assert patch._result_comms.get() == "v1"
        assert type(result) is types.ForwardBackwardOutput
        assert result.loss_fn_output_type == "ppo" and result.metrics == raw["metrics"]
        tensors = result.loss_fn_outputs[0]
        assert all(type(tensor) is types.TensorData for tensor in tensors.values())
        assert tensors["logprobs"].to_numpy().tobytes() == np.array([-0.0, -1.25], dtype=np.float32).tobytes()
        sparse = tensors["sparse"]
        assert (sparse.data, sparse.shape, sparse.sparse_crow_indices, sparse.sparse_col_indices) == (
            [0.5], [1, 4], [0, 1], [3],
        )

        raw["loss_fn_outputs"][0]["logprobs"]["data"] = ["invalid"] * 100
        with pytest.raises(ValueError) as failure:
            await future._handle_outcome(
                api_future_impl._SuccessJson(result_dict=raw), api_future_impl._LoopState(), stack, 1, 0.0,
            )
        assert failure.value.__cause__.error_count() == (2 if comms == "v2" else 200)
        assert patch._result_comms.get() == "v1"


@pytest.mark.asyncio
async def test_cancelled_result_budget_wait_keeps_other_tasks_in_default_mode():
    entered = asyncio.Event()

    @asynccontextmanager
    async def acquire(_size):
        assert patch._result_comms.get() == "v2"
        entered.set()
        await asyncio.Event().wait()
        yield

    future = object.__new__(patch.CommsV2APIFuture)
    future.holder = SimpleNamespace(_inflight_response_bytes_semaphore=SimpleNamespace(acquire=acquire))

    async def wait_for_budget():
        try:
            async with AsyncExitStack() as stack:
                await future._handle_outcome(
                    api_future_impl._MetadataOnly(payload_size=1),
                    api_future_impl._LoopState(), stack, 1, 0.0,
                )
        finally:
            assert patch._result_comms.get() == "v1"

    task = asyncio.create_task(wait_for_budget())
    await asyncio.wait_for(entered.wait(), timeout=5)
    assert patch._result_comms.get() == "v1"
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
