"""Closing a ``FiretitanSamplingClient`` with requests in flight.

A weight sync swaps to a new snapshot's sampling client and closes the old one
while its turns are still generating. Those turns must keep streaming to
completion so their trajectories continue, every request must return its
concurrency slot, and the controller must not read the swap as congestion.
"""

from __future__ import annotations

import time
import asyncio
import threading
from typing import Any

import pytest
from tinker import types as tinker_types

from fireworks.training.sdk.client import FiretitanSamplingClient, SamplingClientClosedError
from fireworks.training.sdk.sampling import ServerMetrics, DeploymentSampler
from fireworks.training.sdk.concurrency import AdaptiveConcurrencyController

_CHOICE: dict[str, Any] = {
    "text": "out",
    "finish_reason": "stop",
    "raw_output": {"completion_token_ids": [40, 50]},
    "logprobs": {"content": [{"logprob": -0.3, "sampling_logprob": -0.3}, {"logprob": -0.4, "sampling_logprob": -0.4}]},
}


def _blocking_client(
    controller: AdaptiveConcurrencyController, release: threading.Event
) -> tuple[FiretitanSamplingClient, list[int]]:
    """A client whose deployment streams until ``release`` is set."""
    sampler = DeploymentSampler(
        inference_url="https://api.example.com",
        model="accounts/fireworks/models/gpt-oss-20b",
        api_key="key",
        tokenizer=None,
        concurrency_controller=controller,
    )
    started: list[int] = []

    async def _stream(*args, **kwargs):
        started.append(1)
        while not release.is_set():
            await asyncio.sleep(0.01)
        return {"choices": [_CHOICE]}, ServerMetrics()

    sampler.async_completions_stream = _stream
    return FiretitanSamplingClient(sampler), started


def _submit(client: FiretitanSamplingClient, n: int):
    return [
        client.sample(
            prompt=tinker_types.ModelInput.from_ints([10, 20, 30]),
            num_samples=1,
            sampling_params=tinker_types.SamplingParams(max_tokens=2),
        )
        for _ in range(n)
    ]


def _wait_until(predicate, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() > deadline:
            raise AssertionError("condition not reached before timeout")
        time.sleep(0.01)


def test_close_lets_in_flight_turns_finish_without_blocking():
    controller = AdaptiveConcurrencyController(initial_window=8, adjustment_interval=0)
    release = threading.Event()
    client, started = _blocking_client(controller, release)
    futures = _submit(client, 3)
    _wait_until(lambda: len(started) == 3)

    started_close = time.monotonic()
    client.close()
    assert time.monotonic() - started_close < 1.0
    assert not any(future.done() for future in futures)

    release.set()
    for future in futures:
        assert future.result(timeout=5).sequences[0].tokens == [40, 50]
    assert client._drain_thread is not None
    client._drain_thread.join(timeout=10)
    assert controller.in_flight == 0
    assert controller.window_size == 8


def test_new_snapshot_client_samples_while_old_one_drains():
    controller = AdaptiveConcurrencyController(initial_window=8, adjustment_interval=0)
    old_release = threading.Event()
    old, old_started = _blocking_client(controller, old_release)
    old_futures = _submit(old, 4)
    _wait_until(lambda: len(old_started) == 4)

    old.close()

    new_release = threading.Event()
    new, new_started = _blocking_client(controller, new_release)
    try:
        new_futures = _submit(new, 4)
        _wait_until(lambda: len(new_started) == 4)
        assert controller.in_flight == 8
        old_release.set()
        new_release.set()
        for future in old_futures + new_futures:
            assert future.result(timeout=5).sequences[0].tokens == [40, 50]
    finally:
        new.close()
    old._drain_thread.join(timeout=10)
    assert controller.in_flight == 0


def test_drain_timeout_cancels_stragglers_and_releases_slots():
    controller = AdaptiveConcurrencyController(initial_window=16, adjustment_interval=0)
    client, started = _blocking_client(controller, threading.Event())
    futures = _submit(client, 6)
    _wait_until(lambda: len(started) == 6)

    client.close(drain_timeout_s=0.2)

    for future in futures:
        with pytest.raises(SamplingClientClosedError):
            future.result(timeout=5)
    client._drain_thread.join(timeout=10)
    assert controller.in_flight == 0
    assert controller.window_size == 16


def test_close_without_drain_fails_fast():
    controller = AdaptiveConcurrencyController(initial_window=4, adjustment_interval=0)
    client, started = _blocking_client(controller, threading.Event())
    futures = _submit(client, 2)
    _wait_until(lambda: len(started) == 2)

    client.close(drain_timeout_s=0)

    for future in futures:
        with pytest.raises(SamplingClientClosedError):
            future.result(timeout=5)
    assert controller.in_flight == 0


def test_sample_after_close_raises_without_leaking_a_coroutine():
    controller = AdaptiveConcurrencyController(initial_window=2, adjustment_interval=0)
    client, _ = _blocking_client(controller, threading.Event())
    client.close()
    with pytest.raises(RuntimeError, match="closed"):
        _submit(client, 1)
    assert controller.in_flight == 0
