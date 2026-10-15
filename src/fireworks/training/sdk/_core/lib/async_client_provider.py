from __future__ import annotations

import asyncio
from typing import Any, TypeVar, Protocol
from contextlib import AbstractContextManager
from collections.abc import Coroutine

from fireworks.training.sdk._core._client import AsyncTrainingHTTPClient
from fireworks.training.sdk._core.lib.client_connection_pool_type import ClientConnectionPoolType
from fireworks.training.sdk._core.lib.public_interfaces.api_future import AwaitableConcurrentFuture

T = TypeVar("T")


class AsyncTrainingClientProvider(Protocol):
    # both of the following methods should be threadsafe
    def get_loop(self) -> asyncio.AbstractEventLoop: ...

    def run_coroutine_threadsafe(
        self,
        coro: Coroutine[Any, Any, T],
    ) -> AwaitableConcurrentFuture[T]: ...

    # must be called and used within the provided event loop
    def aclient(
        self, client_pool_type: ClientConnectionPoolType
    ) -> AbstractContextManager[AsyncTrainingHTTPClient]: ...
