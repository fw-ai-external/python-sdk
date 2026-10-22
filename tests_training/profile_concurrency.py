"""Compare controller feedback traces and CPU cost without making network calls.

Run from the SDK checkout with its source on PYTHONPATH and matplotlib installed:
python tests_training/profile_concurrency.py --baseline /tmp/concurrency-before.py OUTPUT
The baseline must be the unmodified concurrency.py being compared, not an installed SDK.
"""

from __future__ import annotations

import ast
import sys
import json
import time
import pstats
import asyncio
import hashlib
import inspect
import logging
import argparse
import cProfile
import platform
import textwrap
import statistics
import importlib.util
from typing import Any
from pathlib import Path
from functools import partial

from fireworks.training.sdk.sampling import ServerMetrics
from fireworks.training.sdk.concurrency import FixedConcurrencyController, AdaptiveConcurrencyController


async def feedback_trace(factory: Any, scenario: str) -> dict[str, list[Any]]:
    controller = factory(initial_window=64, max_window=64)
    assert not getattr(controller, "_priority_admission", False)
    if scenario == "serverless":
        # All co-admitted 503 responses belong to one synthetic congestion burst.
        controller._now = lambda: 0.0
    windows = [controller.window_size]
    ema = [controller.ema_prefill_queue]
    ignored = [False]
    finish = asyncio.Event()

    async def complete(cohort: bool) -> None:
        await controller.acquire()
        admitted_at = time.monotonic()
        if cohort:
            await finish.wait()
        queue = 200.0 if scenario == "persistent" or (cohort and scenario == "transient") else 0.05
        metrics = ServerMetrics(prefill_queue_duration=queue, client_request_started_at=admitted_at)
        if scenario == "serverless":
            metrics = ServerMetrics(http_status_code=503 if cohort else 200)
        stale_before = getattr(controller, "_step_stale_prefill_observations", 0)
        controller.release(metrics)
        windows.append(controller.window_size)
        ema.append(controller.ema_prefill_queue)
        ignored.append(getattr(controller, "_step_stale_prefill_observations", 0) > stale_before)

    tasks = [asyncio.create_task(complete(True)) for _ in range(64)]
    await asyncio.sleep(0)
    assert controller.in_flight == 64
    finish.set()
    await asyncio.gather(*tasks)
    for _ in range(512):
        await complete(False)
    assert controller.in_flight == 0
    return {"windows": windows, "ema_prefill_queue_seconds": ema, "ignored_prefill_feedback": ignored}


async def small_window_recovery(factory: Any) -> int:
    controller = factory(initial_window=1, max_window=64)
    for completed in range(1, 33):
        await controller.acquire()
        controller.release(ServerMetrics(prefill_queue_duration=0.05, client_request_started_at=time.monotonic()))
        if controller.window_size > 1:
            return completed
    raise AssertionError("healthy controller did not increase within 32 fresh responses")


async def admission(factory: Any, count: int, *, queued: bool = False) -> None:
    controller = factory()
    metrics = ServerMetrics(prefill_queue_duration=0.05)

    async def worker(repeats: int) -> None:
        for _ in range(repeats):
            await controller.acquire()
            if queued:
                await asyncio.sleep(0)
            controller.release(metrics)

    workers = 64 if queued else 1
    await asyncio.gather(*(worker(count // workers) for _ in range(workers)))
    assert getattr(controller, "in_flight", 0) == 0


def cpu_cost(factory: Any, *, queued: bool = False) -> dict[str, Any]:
    count = 20480
    samples = []
    for _ in range(5):
        start = time.process_time()
        asyncio.run(admission(factory, count, queued=queued))
        samples.append((time.process_time() - start) * 1e6 / count)
    profiler = cProfile.Profile()
    profiler.runcall(asyncio.run, admission(factory, count, queued=queued))
    profile = [
        {"function": name, "calls": calls, "self_seconds": own, "cumulative_seconds": cumulative}
        for (file, _, name), (_, calls, own, cumulative, _) in pstats.Stats(profiler).stats.items()
        if "concurrency" in Path(file).name
        and name in ("acquire", "release", "_wake_waiters", "observe", "next_window", "_apply_interval_adjustment")
    ]
    return {"pairs": count, "cpu_us_per_pair": samples, "median_cpu_us": statistics.median(samples), "profile": profile}


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("concurrency_before", args.baseline)
    assert spec is not None and spec.loader is not None
    before = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = before
    spec.loader.exec_module(before)
    logging.disable(logging.CRITICAL)
    args.output.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "python": platform.python_version(),
        "machine": platform.machine(),
        "workload": "64 co-admitted requests, then 512 newly admitted responses; initial/max window 64",
        "limitations": "Synthetic feedback, not model throughput, GPU utilization, or learning-quality evidence.",
        "controllers": {},
        "priority_scheduling": False,
        "unchanged_components": {},
    }
    # A recovery comparison must not change either admission discipline.
    for name, old, new in [
        ("fixed_controller", before.FixedConcurrencyController, FixedConcurrencyController),
        ("adaptive_acquire", before.AdaptiveConcurrencyController.acquire, AdaptiveConcurrencyController.acquire),
        (
            "adaptive_wake_waiters",
            before.AdaptiveConcurrencyController._wake_waiters,
            AdaptiveConcurrencyController._wake_waiters,
        ),
        (
            "serverless_strategy",
            before._StatusCodeStrategy,
            sys.modules[AdaptiveConcurrencyController.__module__]._StatusCodeStrategy,
        ),
    ]:
        syntax = [ast.dump(ast.parse(textwrap.dedent(inspect.getsource(component)))) for component in (old, new)]
        assert syntax[0] == syntax[1], f"{name} changed: this is not an isolated feedback-policy comparison"
        report["unchanged_components"][name] = hashlib.sha256(syntax[0].encode()).hexdigest()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), layout="constrained")
    trace_details = {}
    for label, adaptive, fixed in (
        ("before", before.AdaptiveConcurrencyController, before.FixedConcurrencyController),
        ("proposed", AdaptiveConcurrencyController, FixedConcurrencyController),
    ):
        path = Path(inspect.getfile(adaptive))
        traces = {
            s: asyncio.run(feedback_trace(adaptive, s)) for s in ["healthy", "transient", "persistent", "serverless"]
        }
        costs = {
            "adaptive_serial": cpu_cost(partial(adaptive, initial_window=64, min_window=64, max_window=64)),
            "fixed_serial": cpu_cost(partial(fixed, 8)),
            "fixed_contended": cpu_cost(partial(fixed, 8), queued=True),
        }
        report["controllers"][label] = {
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "scenarios": {
                s: {
                    "after_cohort": v["windows"][64],
                    "after_fresh": v["windows"][-1],
                    "ignored_prefill_feedback": sum(v["ignored_prefill_feedback"]),
                }
                for s, v in traces.items()
            },
            "small_window_healthy_responses_until_growth": asyncio.run(small_window_recovery(adaptive)),
            "transient_milestones": {str(i): traces["transient"]["windows"][i] for i in [0, 32, 64, 96, 192, 320, 576]},
            "cpu": costs,
        }
        trace_details[label] = traces
        transient = traces["transient"]
        axes[0].step(range(len(transient["windows"])), transient["windows"], where="post", label=label)
        axes[1].semilogy(transient["ema_prefill_queue_seconds"], label=label)
        axes[2].bar(label, costs["adaptive_serial"]["median_cpu_us"])
    assert report["controllers"]["before"]["scenarios"]["transient"]["after_fresh"] == 1
    assert report["controllers"]["proposed"]["scenarios"]["transient"]["after_fresh"] == 64
    assert report["controllers"]["before"]["small_window_healthy_responses_until_growth"] == 32
    assert report["controllers"]["proposed"]["small_window_healthy_responses_until_growth"] == 1
    for scenario, expected in [("healthy", 64), ("persistent", 1), ("serverless", 48)]:
        assert all(data["scenarios"][scenario]["after_fresh"] == expected for data in report["controllers"].values())
    axes[0].axvline(64, color="gray", linestyle=":", label="fresh healthy responses begin")
    axes[0].set(xlabel="completed request", ylabel="request window", title="Synthetic transient-congestion trace")
    axes[0].legend(fontsize=8)
    axes[1].axvline(64, color="gray", linestyle=":")
    axes[1].set(
        xlabel="completed request", ylabel="EMA prefill queue (seconds, log scale)", title="Old EMA suppresses recovery"
    )
    axes[1].legend(fontsize=8)
    axes[2].set(ylabel="CPU microseconds / pair", title="Adaptive uncontended: 5 × 20,480 pairs")
    fig.savefig(args.output / "controller-profile.png", dpi=150)
    plt.close(fig)
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "controller-trace.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "priority_scheduling": False,
                "axis": "index 0 = initial state; index N = after N completed requests",
                "inputs": {
                    "initial_window": 64,
                    "max_window": 64,
                    "coadmitted_requests": 64,
                    "fresh_requests": 512,
                    "adjustment_interval": 32,
                    "healthy_queue_seconds": 0.05,
                    "congested_queue_seconds": 200.0,
                    "transient": "congested coadmitted cohort, then fresh healthy feedback",
                    "persistent": "all feedback congested",
                    "serverless": "one coadmitted 503 burst at frozen time, then status 200",
                },
                "source_sha256": {label: data["source_sha256"] for label, data in report["controllers"].items()},
                "windows": {
                    label: {s: v["windows"] for s, v in traces.items()} for label, traces in trace_details.items()
                },
                "feedback": {
                    label: {s: {k: values for k, values in v.items() if k != "windows"} for s, v in traces.items()}
                    for label, traces in trace_details.items()
                },
            }
        )
        + "\n"
    )
    for label, data in report["controllers"].items():
        print(label, data["scenarios"])


if __name__ == "__main__":
    main()
