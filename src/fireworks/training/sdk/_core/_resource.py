from __future__ import annotations

from typing import TYPE_CHECKING

import anyio

if TYPE_CHECKING:
    from fireworks.training.sdk._core._client import AsyncTrainingHTTPClient


class AsyncAPIResource:
    _client: AsyncTrainingHTTPClient

    def __init__(self, client: AsyncTrainingHTTPClient) -> None:
        self._client = client
        self._get = client.get
        self._post = client.post
        self._patch = client.patch
        self._put = client.put
        self._delete = client.delete
        self._get_api_list = client.get_api_list

    async def _sleep(self, seconds: float) -> None:
        await anyio.sleep(seconds)
