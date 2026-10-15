"""Caller timeouts and terminal cleanup preserve in-flight training work."""

from __future__ import annotations

import json
import time
import base64
import asyncio
from concurrent.futures import Future

import httpx
import pytest

from fireworks.training import sdk
from fireworks.training.sdk._core.lib.api_future_impl import _APIFuture
from fireworks.training.sdk._core.lib.internal_client_holder import ClientConnectionPool
from fireworks.training.sdk._core.lib.public_interfaces.api_future import AwaitableConcurrentFuture


@pytest.mark.parametrize("close_on_holder_loop", [False, True])
def test_service_close_stops_jwt_refresh_before_closing_its_transport(close_on_holder_loop):
    claims = base64.urlsafe_b64encode(json.dumps({"exp": time.time() + 3600}).encode()).decode().rstrip("=")
    token = f"eyJ.{claims}.signature"
    exchanges = []

    def exchange(request):
        exchanges.append(request.url.path)
        return httpx.Response(200, json={"jwt": token})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(exchange))
    service = sdk.ServiceClient(
        api_key="fw-test",
        base_url="https://trainer.test",
        _skip_session=True,
        _jwt_auth_seed=token,
        _client_config={"pjwt_auth_enabled": True, "use_pyqwest_transport": False},
        http_client=http_client,
    )

    async def refresh_task():
        # The seeded provider starts asynchronously on the holder loop.
        await asyncio.sleep(0)
        task = service.holder._default_auth._refresh_task
        assert task is not None and not task.done()
        # Exercise the refresh connection so close must release it too.
        assert await service.holder._default_auth._fetch() == token
        return task

    task = service.holder.run_coroutine_threadsafe(refresh_task()).result(timeout=5)
    try:
        if close_on_holder_loop:

            async def close_on_loop():
                service.close()
                for _ in range(100):
                    if http_client.is_closed:
                        return
                    await asyncio.sleep(0.001)
                pytest.fail("JWT transport did not close")

            service.holder.run_coroutine_threadsafe(close_on_loop()).result(timeout=5)
        else:
            service.close()
        assert task.done()
        assert http_client.is_closed
        assert exchanges == ["/api/v1/auth/token"]
        service.close()
    finally:
        service.close()
        # Also clean up when exercising the pre-fix implementation.
        service.holder.get_loop().call_soon_threadsafe(task.cancel)


@pytest.mark.parametrize("wrapper", [AwaitableConcurrentFuture, _APIFuture])
@pytest.mark.parametrize("cancel", [False, True])
def test_one_waiter_cannot_cancel_the_shared_result(wrapper, cancel):
    async def run():
        pending = Future()
        inner = AwaitableConcurrentFuture(pending)
        if wrapper is _APIFuture:
            future = object.__new__(_APIFuture)
            future._future = inner
        else:
            future = inner
        if cancel:
            waiter = asyncio.create_task(future.result_async())
            await asyncio.sleep(0)
            waiter.cancel()
            with pytest.raises(asyncio.CancelledError):
                await waiter
        else:
            with pytest.raises(TimeoutError):
                await future.result_async(timeout=0.001)
        assert not pending.cancelled()
        pending.set_result("completed")
        assert await future.result_async(timeout=1) == "completed"

    asyncio.run(run())


@pytest.mark.parametrize("close_on_holder_loop", [False, True])
def test_unload_waits_for_earlier_optimizer_result_and_closes_transport(close_on_holder_loop):
    requests = []
    started = asyncio.Event()
    release = asyncio.Event()

    async def respond(request):
        operation = request.url.path.rsplit("/", 1)[-1]
        requests.append(operation)
        if operation == "optim_step":
            started.set()
            await release.wait()
            return httpx.Response(200, json={"request_id": "optim"})
        if operation == "unload_model":
            return httpx.Response(200, json={"request_id": "unload"})
        if operation == "retrieve_future":
            request_id = json.loads(request.content)["request_id"]
            if request_id == "optim":
                await asyncio.sleep(0.02)
                requests.append("optimizer_completed")
                return httpx.Response(200, json={"metrics": {}})
            return httpx.Response(200, json={"model_id": "model-1", "type": "unload_model"})
        raise AssertionError(operation)

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    service = sdk.ServiceClient(
        api_key="fw-test",
        base_url="https://trainer.test",
        _skip_session=True,
        http_client=http_client,
        _client_config={"use_pyqwest_transport": False},
    )
    client = sdk.TrainingClient(service.holder, 0, "model-1")

    async def run():
        optimizer = client.optim_step(sdk.AdamParams(learning_rate=0.001))
        await asyncio.wait_for(started.wait(), 1)
        unload = client.unload_model()
        await asyncio.sleep(0.01)
        assert "unload_model" not in requests
        with pytest.raises(RuntimeError, match="unloading"):
            client.optim_step(sdk.AdamParams(learning_rate=0.001))
        release.set()
        assert (await unload.result_async(timeout=2)).model_id == "model-1"
        assert (await optimizer.result_async(timeout=2)).metrics == {}
        assert requests.index("optimizer_completed") < requests.index("unload_model")

    try:
        service.holder.run_coroutine_threadsafe(run()).result(timeout=5)
        if close_on_holder_loop:

            async def close_on_loop():
                service.close()
                for _ in range(100):
                    if http_client.is_closed:
                        return
                    await asyncio.sleep(0.001)
                raise AssertionError("Transport did not close on the holder loop")

            service.holder.run_coroutine_threadsafe(close_on_loop()).result(timeout=5)
    finally:
        service.close()
    assert http_client.is_closed
    assert service.holder.get_loop().is_running()


@pytest.mark.parametrize("managed_base_url", [None, "https://control-plane.test"])
def test_default_serverless_rest_uses_the_actual_http_endpoint(monkeypatch, managed_base_url):
    monkeypatch.delenv("TINKER_BASE_URL", raising=False)
    monkeypatch.setenv("FIREWORKS_BASE_URL", "https://environment-control-plane.test")
    calls = []

    def respond(request):
        calls.append(str(request.url))
        return httpx.Response(200, json={"base_model": "model", "is_lora": True, "lora_rank": 8})

    service = sdk.ServiceClient(
        api_key="fw-test",
        managed_base_url=managed_base_url,
        _skip_session=True,
        _client_config={"use_pyqwest_transport": False},
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
    )
    try:
        assert service._managed_base_url == (managed_base_url or "https://environment-control-plane.test")
        with pytest.raises(NotImplementedError, match="Serverless"):
            service.get_server_capabilities()
        assert calls == []
        assert service.create_rest_client().get_weights_info_by_tinker_path("account/run/step").result().lora_rank == 8
        assert calls == ["https://api.fireworks.ai/training/v1/serverless/api/v1/weights_info"]
    finally:
        service.close()


def test_pool_closes_replaced_connections_and_rejects_reuse():
    async def run():
        pool = ClientConnectionPool(
            asyncio.get_running_loop(),
            1,
            {
                "api_key": "fw-test",
                "base_url": "https://trainer.test",
                "max_retries": 0,
            },
        )
        with pytest.raises(sdk.APIConnectionError):
            with pool.aclient() as retired:
                response = httpx.Response(
                    400, headers={"content-length": "0"}, request=httpx.Request("POST", "https://trainer.test")
                )
                raise sdk.APIStatusError("reconnect", response=response, body=None)
        with pool.aclient() as current:
            assert current is not retired
        await pool.close()
        assert retired.is_closed() and current.is_closed()
        with pytest.raises(RuntimeError, match="closed"):
            with pool.aclient():
                pass
        await pool.close()

    asyncio.run(run())


def test_config_pool_keeps_a_shared_http_client_open_until_holder_close():
    from fireworks.training.sdk._core.lib.internal_client_holder import InternalClientHolder
    from fireworks.training.sdk._core.lib.client_connection_pool_type import ClientConnectionPoolType

    def respond(request):
        if request.url.path.endswith("/client/config"):
            return httpx.Response(200, json={"use_pyqwest_transport": False})
        return httpx.Response(200, json={"ok": True})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    holder = InternalClientHolder(
        api_key="fw-test",
        base_url="https://trainer.test",
        http_client=http_client,
        _skip_session=True,
        _strict_response_validation=True,
    )

    async def run():
        with holder.aclient(ClientConnectionPoolType.TRAIN) as client:
            assert await client.get("/probe", cast_to=dict[str, bool]) == {"ok": True}

    try:
        assert not http_client.is_closed
        holder.run_coroutine_threadsafe(run()).result(timeout=5)
    finally:
        holder.close()
    assert http_client.is_closed


def test_unload_drains_a_compound_operation_before_its_first_request():
    from fireworks.training.sdk._core import TrainingClient

    calls = []
    results = {}

    def respond(request):
        operation = request.url.path.rsplit("/", 1)[-1]
        body = json.loads(request.content)
        calls.append(operation)
        if operation == "retrieve_future":
            return httpx.Response(200, json=results[body["request_id"]])
        request_id = str(len(results))
        if operation == "save_weights_for_sampler":
            results[request_id] = {"path": body["path"]}
        elif operation == "unload_model":
            results[request_id] = {"model_id": "model-1", "type": "unload_model"}
        else:
            raise AssertionError(operation)
        return httpx.Response(200, json={"request_id": request_id})

    service = sdk.ServiceClient(
        api_key="fw-test",
        base_url="https://trainer.test",
        _skip_session=True,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        _client_config={"use_pyqwest_transport": False},
    )
    client = sdk.TrainingClient(service.holder, 0, "model-1")

    async def run():
        # The native wrapper reserves its inner sequence after submission.
        future = TrainingClient.save_weights_for_sampler(client, "checkpoint")
        # Both submissions occur before the event loop starts the compound task.
        unload = client.unload_model()
        assert (await future.result_async(timeout=5)).path == "checkpoint"
        await unload.result_async(timeout=5)
        assert calls.index("save_weights_for_sampler") < calls.index("unload_model")

    try:
        service.holder.run_coroutine_threadsafe(run()).result(timeout=10)
    finally:
        service.close()


def test_failed_unload_can_retry_cleanup_without_reopening_training():
    attempts = []

    def respond(request):
        if request.url.path.endswith("/unload_model"):
            attempts.append(request)
            if len(attempts) == 1:
                return httpx.Response(503, json={"error": "unavailable"})
            return httpx.Response(200, json={"request_id": "unload"})
        return httpx.Response(200, json={"model_id": "model-1", "type": "unload_model"})

    service = sdk.ServiceClient(
        api_key="fw-test",
        base_url="https://trainer.test",
        _skip_session=True,
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        _client_config={"use_pyqwest_transport": False},
    )
    client = sdk.TrainingClient(service.holder, 0, "model-1")
    try:
        with pytest.raises(sdk.APIStatusError):
            client.unload_model().result(timeout=5)
        with pytest.raises(RuntimeError, match="unloading"):
            client.optim_step(sdk.AdamParams(learning_rate=0.001))
        retry = client.unload_model()
        assert retry.result(timeout=5).model_id == "model-1"
        assert client.unload_model() is retry
        assert len(attempts) == 2
    finally:
        service.close()


def _operation_client():
    calls = []

    def respond(request):
        operation = request.url.path.rsplit("/", 1)[-1]
        body = json.loads(request.content)
        calls.append((operation, body.get("seq_id")))
        if operation == "optim_step":
            return httpx.Response(200, json={"request_id": f"optim-{body['seq_id']}"})
        if operation == "unload_model":
            return httpx.Response(200, json={"request_id": "unload"})
        if operation == "retrieve_future":
            result = (
                {"model_id": "model-1", "type": "unload_model"} if body["request_id"] == "unload" else {"metrics": {}}
            )
            return httpx.Response(200, json=result)
        raise AssertionError(operation)

    service = sdk.ServiceClient(
        api_key="fw-test",
        base_url="https://trainer.test",
        _skip_session=True,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        _client_config={"use_pyqwest_transport": False},
    )
    return service, sdk.TrainingClient(service.holder, 0, "model-1"), calls


def test_unload_cannot_strand_a_reserved_turn_between_threads(monkeypatch):
    from threading import Event
    from concurrent.futures import ThreadPoolExecutor

    service, client, calls = _operation_client()
    reserved, release = Event(), Event()
    get_request_id = client._get_request_id

    def pause_first_reservation():
        request_id = get_request_id()
        if request_id == 0:
            reserved.set()
            assert release.wait(5)
        return request_id

    monkeypatch.setattr(client, "_get_request_id", pause_first_reservation)
    try:
        with ThreadPoolExecutor(max_workers=2) as workers:
            first = workers.submit(client.optim_step, sdk.AdamParams(learning_rate=0.001))
            assert reserved.wait(5)
            second = workers.submit(client.optim_step, sdk.AdamParams(learning_rate=0.001)).result(timeout=5)
            unload = client.unload_model()
            with pytest.raises(TimeoutError):
                unload.result(timeout=0.02)
            release.set()
            assert first.result(timeout=5).result(timeout=5).metrics == {}
            assert second.result(timeout=5).metrics == {}
            assert unload.result(timeout=5).model_id == "model-1"
        assert [item for item in calls if item[0] in {"optim_step", "unload_model"}] == [
            ("optim_step", 1),
            ("optim_step", 2),
            ("unload_model", None),
        ]
    finally:
        release.set()
        service.close()


def test_raw_result_cancellation_cannot_skip_an_accepted_sequence_turn():
    from threading import Event

    service, client, calls = _operation_client()
    blocked, release = Event(), Event()

    def block_loop():
        blocked.set()
        release.wait(5)

    try:
        service.holder.get_loop().call_soon_threadsafe(block_loop)
        assert blocked.wait(5)
        operation = client.optim_step(sdk.AdamParams(learning_rate=0.001))
        assert not operation.future().cancel()
        second = client.optim_step(sdk.AdamParams(learning_rate=0.001))
        unload = client.unload_model()
        release.set()
        assert operation.result(timeout=5).metrics == {}
        assert second.result(timeout=5).metrics == {}
        assert unload.result(timeout=5).model_id == "model-1"
        assert [item for item in calls if item[0] in {"optim_step", "unload_model"}] == [
            ("optim_step", 1),
            ("optim_step", 2),
            ("unload_model", None),
        ]
    finally:
        release.set()
        service.close()


def test_checkpoint_listing_rejects_unload_instead_of_returning_empty():
    service, client, _ = _operation_client()
    try:
        client.unload_model().result(timeout=5)
        with pytest.raises(RuntimeError, match="unloading"):
            client.list_checkpoints()
    finally:
        service.close()


def test_chunk_validation_failure_does_not_consume_sequence_ids(monkeypatch):
    service, client, calls = _operation_client()

    def failing_chunks(data):
        yield data
        raise ValueError("invalid later datum")

    monkeypatch.setattr(client, "_chunked_requests_generator", failing_chunks)
    try:
        with pytest.raises(ValueError, match="invalid later datum"):
            client._chunked_requests([])
        assert client.optim_step(sdk.AdamParams(learning_rate=0.001)).result(timeout=5).metrics == {}
        assert client.unload_model().result(timeout=5).model_id == "model-1"
        assert ("optim_step", 1) in calls
    finally:
        service.close()


@pytest.mark.parametrize("comms", ["v1", "v2"])
@pytest.mark.parametrize("parallel,concurrency", [(False, 1), (True, 1), (True, 2), (True, 4)])
@pytest.mark.parametrize("early_unload", [False, True])
def test_failed_chunk_releases_queued_work_and_allows_unload(monkeypatch, comms, parallel, concurrency, early_unload):
    from threading import Event

    service, client, calls = _operation_client()
    entered, release, all_entered = Event(), Event(), Event()
    started = []
    client._comms = comms
    client.holder._client_config = client.holder._client_config.model_copy(update={"parallel_fwdbwd_chunks": parallel})
    monkeypatch.setattr("fireworks.training.sdk.client._parallel_chunk_send_concurrency", lambda: concurrency)
    monkeypatch.setattr(client, "_chunked_requests_generator", lambda data: [[datum] for datum in data])

    async def send(request_id, *_):
        started.append(request_id)
        if len(started) == 4:
            all_entered.set()
        if request_id == 0:
            entered.set()
            assert await asyncio.to_thread(release.wait, 5)
            raise ValueError("failed chunk upload")
        await asyncio.sleep(30)
        raise AssertionError("Other chunks should be cancelled after the failed upload")

    monkeypatch.setattr(client, "_send_single_forward_request", send)
    datum = sdk.Datum(
        model_input=sdk.ModelInput.from_ints([1]),
        loss_fn_inputs={"target_tokens": [2], "weights": [1.0]},
    )
    try:
        forward = client.forward([datum] * 4, "cross_entropy")
        assert entered.wait(5)
        if parallel and concurrency == 4:
            assert all_entered.wait(5)
        later = client.optim_step(sdk.AdamParams(learning_rate=0.001))
        unload = client.unload_model() if early_unload else None
        release.set()
        with pytest.raises(ValueError, match="failed chunk upload"):
            forward.result(timeout=5)
        if parallel and concurrency == 4:
            assert client._turn_counter == 4
        with pytest.raises(RuntimeError, match="sequence failed"):
            later.result(timeout=5)
        with pytest.raises(RuntimeError, match="unloading" if early_unload else "sequence failed"):
            client.optim_step(sdk.AdamParams(learning_rate=0.001))
        assert (unload or client.unload_model()).result(timeout=5).model_id == "model-1"
        assert not any(name == "optim_step" for name, _ in calls)
    finally:
        release.set()
        service.close()


@pytest.mark.parametrize("comms", ["v1", "v2"])
@pytest.mark.parametrize("concurrency", [1, 4])
def test_failed_backward_ack_stops_waiting_uploads_before_releasing_slots(monkeypatch, comms, concurrency):
    from threading import Event

    service, client, calls = _operation_client()
    entered, release, all_entered = Event(), Event(), Event()
    started = []
    client._comms = comms
    client.holder._client_config = client.holder._client_config.model_copy(update={"parallel_fwdbwd_chunks": True})
    monkeypatch.setattr("fireworks.training.sdk.client._parallel_chunk_send_concurrency", lambda: concurrency)
    monkeypatch.setattr(client, "_chunked_requests_generator", lambda data: [[datum] for datum in data])

    async def send(request_id, *_):
        started.append(request_id)
        entered.set()
        if len(started) == 4:
            all_entered.set()
        assert await asyncio.to_thread(release.wait, 5)
        raise ValueError("failed chunk upload")

    monkeypatch.setattr(client, "_send_single_forward_backward_request", send)
    datum = sdk.Datum(
        model_input=sdk.ModelInput.from_ints([1]),
        loss_fn_inputs={"target_tokens": [2], "weights": [1.0]},
    )
    try:
        backward = client.forward_backward([datum] * 4, "cross_entropy")
        assert entered.wait(5)
        if concurrency == 4:
            assert all_entered.wait(5)
        later = client.optim_step(sdk.AdamParams(learning_rate=0.001))
        unload = client.unload_model()
        release.set()
        with pytest.raises(ValueError, match="failed chunk upload"):
            backward.result(timeout=5)
        with pytest.raises((ValueError, RuntimeError), match="failed chunk upload|sequence failed"):
            later.result(timeout=5)
        assert unload.result(timeout=5).model_id == "model-1"
        assert len(started) == concurrency
        assert not any(name == "optim_step" for name, _ in calls)
    finally:
        release.set()
        service.close()
