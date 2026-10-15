"""Cross-call F/B uploads overlap; mutations retain their admission barrier."""

from __future__ import annotations

import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

import fireworks.training.sdk._core as tinker
from tests_training.test_client import TestParallelChunkSubmission as _ChunkHelpers


class _Future:
    def __init__(self, coroutine):
        self.task = asyncio.create_task(coroutine)

    def future(self):
        return self.task

    async def result_async(self, timeout=None):
        return await self.task


@pytest.fixture
def client(monkeypatch):
    helper = _ChunkHelpers()
    for name in ("_APIFuture", "CommsV2APIFuture"):
        monkeypatch.setattr("fireworks.training.sdk.client." + name, helper._FakeAPIFuture)
    monkeypatch.setattr("fireworks.training.sdk.client._CombinedAPIFuture", helper._FakeCombinedAPIFuture)
    c = helper._make_client(parallel=True, send_order=[])
    c._request_id_lock = threading.RLock()
    c._request_id_counter = 0
    c._chunked_requests = lambda data: [(c._get_request_id(), data)]
    c.holder.run_coroutine_threadsafe.side_effect = _Future
    return c


def _datum():
    return _ChunkHelpers()._datum()


@pytest.mark.parametrize("comms", ["v1", "v2"])
def test_multichunk_forward_joins_the_same_pending_backward(client, comms):
    async def scenario():
        client._comms = comms
        started, release = asyncio.Event(), asyncio.Event()
        forwards = []

        async def backward(rid, _data):
            started.set()
            await release.wait()
            return rid + 1

        async def forward(rid, _data):
            forwards.append(rid)
            return rid + 1

        client._send_single_forward_backward_request = lambda rid, data, *_: backward(rid, data)
        pending = client.forward_backward([_datum()], "ppo")
        await asyncio.wait_for(started.wait(), 1)
        client._send_single_forward_request = lambda rid, data, *_: forward(rid, data)
        del client._chunked_requests
        client._chunked_requests_generator = lambda data: [[datum] for datum in data]
        request = client.forward([_datum(), _datum()], "cross_entropy")
        # Both forward chunks enter the same ACK barrier before it is released.
        for _ in range(10):
            await asyncio.sleep(0)
        assert not forwards and not request.future().done()
        release.set()
        assert await pending.result_async() == [1]
        assert await request.result_async() == [2, 3]
        assert sorted(forwards) == [1, 2]
        assert not client._http_admissions

    asyncio.run(scenario())


@pytest.mark.parametrize("comms", ["v1", "v2"])
def test_slow_ack_does_not_block_the_next_group(client, comms):
    async def scenario():
        client._comms = comms
        both_started = asyncio.Event()
        release = asyncio.Event()
        started = []

        async def send(request_id, _data):
            started.append(request_id)
            if len(started) == 2:
                both_started.set()
            await release.wait()
            return request_id + 1

        client._send_single_forward_backward_request = lambda rid, data, *_: send(rid, data)
        futures = [client.forward_backward([_datum()], "ppo") for _ in range(2)]
        await asyncio.wait_for(both_started.wait(), 1)
        assert all(not f.future().done() for f in futures)
        release.set()
        assert [await f.result_async() for f in futures] == [[1], [2]]

    asyncio.run(scenario())


def test_upload_limit_is_shared_across_logical_calls(client, monkeypatch):
    monkeypatch.setattr("fireworks.training.sdk.client._parallel_chunk_send_concurrency", lambda: 2)

    async def scenario():
        release = asyncio.Event()
        two_started = asyncio.Event()
        active = peak = 0

        async def send(rid, _data):
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            if active == 2:
                two_started.set()
            await release.wait()
            active -= 1
            return rid + 1

        client._send_single_forward_backward_request = lambda rid, data, *_: send(rid, data)
        futures = [client.forward_backward([_datum()], "ppo") for _ in range(6)]
        await asyncio.wait_for(two_started.wait(), 1)
        assert peak == 2
        release.set()
        assert [await f.result_async() for f in futures] == [[i] for i in range(1, 7)]
        assert peak == 2

    asyncio.run(scenario())


@pytest.mark.parametrize("failed", [False, True])
def test_optimizer_joins_all_prior_uploads_and_refuses_failed_admission(client, failed):
    async def scenario():
        started = asyncio.Event()
        release = [asyncio.Event(), asyncio.Event()]
        sends = []
        optimizer_sent = []

        async def send(rid, _data):
            sends.append(rid)
            if len(sends) == 2:
                started.set()
            await release[rid].wait()
            if failed and rid == 0:
                raise RuntimeError("upload failed")
            return rid + 1

        async def optimizer(*, request, extra_body):
            optimizer_sent.append(request.seq_id)
            return request.seq_id

        training = client.holder.aclient.return_value.__enter__().training
        training.optim_step = optimizer
        client._send_single_forward_backward_request = lambda rid, data, *_: send(rid, data)
        groups = [client.forward_backward([_datum()], "ppo") for _ in range(2)]
        mutation = client.optim_step(tinker.AdamParams(learning_rate=1e-5))
        await asyncio.wait_for(started.wait(), 1)
        release[0].set()
        await asyncio.sleep(0.01)
        assert not optimizer_sent and not mutation.future().done()
        release[1].set()
        outcomes = await asyncio.gather(*(f.result_async() for f in groups), return_exceptions=True)
        if failed:
            assert isinstance(outcomes[0], RuntimeError)
            with pytest.raises(RuntimeError, match="upload failed"):
                await mutation.result_async()
            assert not optimizer_sent
        else:
            assert await mutation.result_async() == 3
            assert optimizer_sent == [3]
            assert not client._http_admissions

    asyncio.run(scenario())


def test_retry_preserves_sequence_while_other_groups_upload(client):
    async def scenario():
        retry_started = asyncio.Event()
        second_started = asyncio.Event()
        release_retry = asyncio.Event()
        attempts = []

        async def send(rid, _data):
            attempts.append(rid)
            if rid == 0 and attempts.count(0) == 1:
                retry_started.set()
                raise RuntimeError("transient")
            if rid == 0:
                await release_retry.wait()
            else:
                second_started.set()
            return rid + 1

        async def retry(fn, *args):
            try:
                return await fn(*args)
            except RuntimeError:
                return await fn(*args)

        client.holder.execute_with_retries.side_effect = retry
        client._send_single_forward_backward_request = lambda rid, data, *_: send(rid, data)
        groups = [client.forward_backward([_datum()], "ppo") for _ in range(2)]
        await asyncio.wait_for(retry_started.wait(), 1)
        await asyncio.wait_for(second_started.wait(), 1)
        release_retry.set()
        assert [await f.result_async() for f in groups] == [[1], [2]]
        assert attempts.count(0) == 2 and attempts.count(1) == 1
        assert client._turn_counter == 2

    asyncio.run(scenario())


def test_cancel_joins_admitted_uploads_and_retires_all_chunk_turns(client, monkeypatch):
    monkeypatch.setattr("fireworks.training.sdk.client._parallel_chunk_send_concurrency", lambda: 2)

    async def scenario():
        started = asyncio.Event()
        release = asyncio.Event()
        sent = []

        async def send(rid, _data):
            sent.append(rid)
            if len(sent) == 2:
                started.set()
            await release.wait()
            return rid + 1

        request = asyncio.create_task(
            client._run_chunked_requests([(i, [_datum()]) for i in range(4)], send, request_type="ForwardBackward")
        )
        await asyncio.wait_for(started.wait(), 1)
        request.cancel()
        await asyncio.sleep(0)
        assert not request.done()
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await request
        assert sent == [0, 1, 2, 3]
        assert all(task.done() for task in client._http_admissions.values())
        assert client._turn_counter == 4

    asyncio.run(scenario())


def test_failed_chunk_does_not_cancel_later_uploads_or_leave_a_sequence_hole(client):
    async def scenario():
        later_started = asyncio.Event()
        release = asyncio.Event()
        sent = []

        async def send(rid, _data):
            sent.append(rid)
            if rid == 0:
                raise RuntimeError("bad upload")
            if len(sent) == 3:
                later_started.set()
            await release.wait()
            return rid + 1

        request = asyncio.create_task(
            client._run_chunked_requests([(i, [_datum()]) for i in range(3)], send, request_type="ForwardBackward")
        )
        await asyncio.wait_for(later_started.wait(), 1)
        assert not request.done()
        release.set()
        with pytest.raises(RuntimeError, match="bad upload"):
            await request
        assert client._turn_counter == 3
        assert all(t.done() for t in client._http_admissions.values())

    asyncio.run(scenario())


def test_explicit_serial_mode_keeps_serial_admission(client):
    async def scenario():
        client.holder._client_config.parallel_fwdbwd_chunks = False
        release = asyncio.Event()
        first_started = asyncio.Event()
        sent = []

        async def send(rid, _data):
            sent.append(rid)
            first_started.set()
            await release.wait()
            return rid + 1

        client._send_single_forward_backward_request = lambda rid, data, *_: send(rid, data)
        groups = [client.forward_backward([_datum()], "ppo") for _ in range(2)]
        await asyncio.wait_for(first_started.wait(), 1)
        await asyncio.sleep(0.01)
        assert sent == [0]
        release.set()
        assert [await f.result_async() for f in groups] == [[1], [2]]

    asyncio.run(scenario())


def test_threaded_callers_reserve_contiguous_chunk_ranges(client):
    del client._chunked_requests

    def chunks(_data):
        for _ in range(3):
            time.sleep(0.002)
            yield [_datum()]

    client._chunked_requests_generator = chunks
    with ThreadPoolExecutor(max_workers=4) as executor:
        groups = list(executor.map(lambda _: client._chunked_requests([]), range(12)))
    ranges = [[rid for rid, _ in group] for group in groups]
    assert all(ids == list(range(ids[0], ids[0] + 3)) for ids in ranges)
    assert sorted(rid for ids in ranges for rid in ids) == list(range(36))
