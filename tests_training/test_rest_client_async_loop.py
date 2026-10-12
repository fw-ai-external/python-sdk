"""The cached AsyncClient must be rebuilt when the running event loop changes.

httpx.AsyncClient pools connections bound to the loop that created them, but
the client object itself does not report closed when that loop closes. A
caller driving requests via ``asyncio.run()`` per call (fresh loop each time,
e.g. a sync adapter in a worker thread) would get the stale client back and
die with "RuntimeError: Event loop is closed" on connection cleanup.
"""

import asyncio

from fireworks.training.sdk._rest_client import _RestClient


def _make_client() -> _RestClient:
    return _RestClient(api_key="test-key", base_url="https://example.invalid")


def test_async_client_rebuilt_across_loops():
    client = _make_client()

    async def grab():
        return client._get_async_client()

    first = asyncio.run(grab())
    second = asyncio.run(grab())
    # The first loop is closed; its client must not be reused even though
    # first.is_closed is still False.
    assert second is not first


def test_async_client_reused_within_one_loop():
    client = _make_client()

    async def grab_twice():
        return client._get_async_client(), client._get_async_client()

    a, b = asyncio.run(grab_twice())
    assert a is b  # same loop -> connection pool preserved


def test_externally_set_client_adopted_not_discarded():
    # Tests (and some callers) inject a client with a MockTransport directly;
    # the first use must adopt it on the current loop, not rebuild over it.
    import httpx

    client = _make_client()
    injected = httpx.AsyncClient(transport=httpx.MockTransport(lambda _req: httpx.Response(200)))
    client._async_client = injected

    async def grab():
        return client._get_async_client()

    assert asyncio.run(grab()) is injected
