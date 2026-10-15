"""Checkpoint REST operations supported by Fireworks training endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fireworks.training.sdk import types
from fireworks.training.sdk._core.lib.telemetry_provider import TelemetryProvider
from fireworks.training.sdk._core.lib.client_connection_pool_type import ClientConnectionPoolType
from fireworks.training.sdk._core.lib.public_interfaces.api_future import APIFuture

if TYPE_CHECKING:
    from fireworks.training.sdk._core.lib.telemetry import Telemetry
    from fireworks.training.sdk._core.lib.internal_client_holder import InternalClientHolder


class RestClient(TelemetryProvider):
    """Query checkpoints using the selected endpoint's supported operations.

    Serverless endpoints support checkpoint weights metadata. Use the native
    training/service clients for checkpoint listing and promotion. Tinker-only
    REST operations are not part of this interface.
    """

    def __init__(
        self,
        holder: InternalClientHolder | None,
        *,
        serverless: bool = False,
    ) -> None:
        self.holder = holder
        self._serverless = serverless

    def get_weights_info_by_tinker_path(self, tinker_path: str) -> APIFuture[types.WeightsInfoResponse]:
        """Read real checkpoint metadata from a serverless endpoint."""
        if not self._serverless or self.holder is None:
            raise NotImplementedError(
                "Checkpoint weights metadata is available only through a serverless endpoint. "
                "For a dedicated trainer, create a training client with its explicit configuration and load_state()."
            )
        holder = self.holder

        async def read() -> types.WeightsInfoResponse:
            async def send() -> types.WeightsInfoResponse:
                with holder.aclient(ClientConnectionPoolType.TRAIN) as client:
                    return await client.post(
                        "/api/v1/weights_info",
                        body={"tinker_path": tinker_path},
                        cast_to=types.WeightsInfoResponse,
                    )

            return await holder.execute_with_retries(send)

        return holder.run_coroutine_threadsafe(read())

    def get_telemetry(self) -> Telemetry | None:
        return self.holder.get_telemetry() if self.holder is not None else None
