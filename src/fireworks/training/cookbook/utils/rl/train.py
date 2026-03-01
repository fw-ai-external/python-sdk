"""RL training loop orchestration for Fireworks recipes.

Provides ``run_rl_loop`` -- a streaming loop that launches all sampling
coroutines concurrently, accumulates valid prompt groups, fires ``fwd_bwd``
when the buffer reaches ``max_prompt_groups_per_fwd_bwd``, and runs
``optim_step`` after ``prompt_groups_per_step`` prompt groups are collected.

Filtering:

  Pass ``dynamic_filter_fn`` to reject rollout results at the scheduling
  layer (e.g. filter constant-reward groups).  The sampling coroutine
  should return ``None`` for hard failures; ``dynamic_filter_fn`` handles
  soft rejection of valid-but-unwanted results.
"""

from __future__ import annotations

import time
import asyncio
import logging
from typing import Any, Callable, Iterable, Coroutine
from dataclasses import dataclass

from tqdm import tqdm

from fireworks.training.cookbook.utils.timer import Timer
from fireworks.training.cookbook.utils.rl.losses import PromptGroup
from fireworks.training.cookbook.utils.rl.metrics import build_loop_metrics

logger = logging.getLogger(__name__)

__all__ = [
    "MinibatchTrainFns",
    "DynamicFilterFn",
    "run_rl_loop",
]

# -- Types -------------------------------------------------------------------

DynamicFilterFn = Callable[[PromptGroup], bool]
"""Filter callback applied after sampling, before training.

Return ``True`` to accept the group into the training buffer,
``False`` to discard it.  This runs after sampling and before training.
"""


@dataclass
class MinibatchTrainFns:
    """Split training callbacks for streaming minibatch mode.

    Instead of one monolithic ``train_step_fn`` that receives all prompt
    groups at once, these three callbacks are invoked incrementally as
    data arrives.
    """

    ref_forward_one: Callable[[PromptGroup], None]
    """Compute reference logprobs for one prompt group."""

    fwd_bwd_one: Callable[[list[PromptGroup]], Any]
    """Run forward_backward_custom on one micro-batch. Returns an APIFuture
    (non-blocking). Fired when the buffer reaches
    ``max_prompt_groups_per_fwd_bwd``."""

    finish_step: Callable[[int, list[PromptGroup], list, int, dict], tuple[int, dict]]
    """optim_step + hotload + metrics. Called after all fwd_bwd calls for a
    step complete. Signature: (step, all_groups, fwd_bwd_results, n_accum,
    loop_stats) -> (new_step, metrics).  ``loop_stats`` contains
    valid_prompt_groups, total_sampled, filter_drops, sample_fails."""


# -- Main entry point -------------------------------------------------------


async def run_rl_loop(
    sample_fns: Iterable[Coroutine[Any, Any, PromptGroup | None]],
    *,
    minibatch_fns: MinibatchTrainFns,
    prompt_groups_per_step: int = 1,
    max_concurrent: int = 32,
    dynamic_filter_fn: DynamicFilterFn | None = None,
    global_step: int = 0,
    metrics_callback: Callable[[dict[str, Any]], None] | None = None,
    min_prompt_groups_per_fwd_bwd: int | None = None,
    max_prompt_groups_per_fwd_bwd: int | None = None,
    completions_per_prompt: int = 1,
) -> int:
    """Run the streaming RL training loop.

    Launches all sampling coroutines concurrently (capped by
    ``max_concurrent``).  Prompt groups accumulate until
    ``min_prompt_groups_per_fwd_bwd`` is reached, then ``fwd_bwd_one`` fires
    (with at most ``max_prompt_groups_per_fwd_bwd`` groups).
    ``optim_step`` runs after ``prompt_groups_per_step`` groups are collected.

    Args:
        min_prompt_groups_per_fwd_bwd: Minimum prompt groups to trigger a
            ``fwd_bwd_one`` call.
        max_prompt_groups_per_fwd_bwd: Max prompt groups per ``fwd_bwd_one``
            call.
        completions_per_prompt: Completions per prompt (for logging and batch
            stats).
    """
    coros = list(sample_fns)

    if max_prompt_groups_per_fwd_bwd is None:
        max_prompt_groups_per_fwd_bwd = prompt_groups_per_step
    if min_prompt_groups_per_fwd_bwd is None:
        min_prompt_groups_per_fwd_bwd = max_prompt_groups_per_fwd_bwd

    return await _stream_loop(
        coros, minibatch_fns, prompt_groups_per_step, global_step,
        min_prompt_groups_per_fwd_bwd, max_prompt_groups_per_fwd_bwd,
        completions_per_prompt, max_concurrent,
        dynamic_filter_fn, metrics_callback,
    )


# -- Stream mode (greedy batching with max_batch_size cap) -------------------


async def _stream_loop(
    coros: list[Coroutine],
    fns: MinibatchTrainFns,
    prompt_groups_per_step: int,
    global_step: int,
    min_prompt_groups_per_fwd_bwd: int,
    max_prompt_groups_per_fwd_bwd: int,
    completions_per_prompt: int,
    max_concurrent: int,
    dynamic_filter_fn: DynamicFilterFn | None,
    metrics_callback: Callable[[dict[str, Any]], None] | None = None,
) -> int:
    """Streaming loop with greedy fwd_bwd batching.

    All sampling coros are launched at once (capped by ``max_concurrent``).
    Prompt groups accumulate in a buffer.  ``fwd_bwd_one`` fires when the buffer
    reaches ``min_prompt_groups_per_fwd_bwd`` (sending up to
    ``max_prompt_groups_per_fwd_bwd`` prompt groups per call).  ``optim_step``
    runs after ``prompt_groups_per_step`` valid prompt groups are collected for
    the step.
    """
    queue: asyncio.Queue[PromptGroup | None] = asyncio.Queue()
    sem = asyncio.Semaphore(max_concurrent)
    worker_error: BaseException | None = None

    async def _worker(coro: Coroutine) -> None:
        nonlocal worker_error
        try:
            async with sem:
                result = await coro
            queue.put_nowait(result)
        except BaseException as exc:
            if worker_error is None:
                worker_error = exc
            queue.put_nowait(None)

    tasks = {asyncio.create_task(_worker(c)) for c in coros}

    total_wait_time = 0.0
    filter_drops = 0
    sample_fails = 0
    all_raw_rewards: list[float] = []
    total_sampled = 0
    step_start_time = time.time()

    minibatch_prompt_groups: list[PromptGroup] = []
    step_prompt_groups: list[PromptGroup] = []
    fwd_bwd_futures: list = []
    fwd_bwd_prompt_group_counts: list[int] = []
    fwd_bwd_call_count = 0

    pbar = tqdm(total=prompt_groups_per_step, desc="sampling", unit="prompt_grp", dynamic_ncols=True)

    async def _flush_and_finish_step() -> None:
        """Flush remaining buffer, run optim_step, reset state."""
        nonlocal global_step, fwd_bwd_call_count
        nonlocal total_wait_time, filter_drops, sample_fails
        nonlocal total_sampled, step_start_time
        nonlocal minibatch_prompt_groups, step_prompt_groups, fwd_bwd_futures, fwd_bwd_prompt_group_counts
        nonlocal all_raw_rewards

        if minibatch_prompt_groups:
            logger.info(
                "[stream] step %d | fwd_bwd %d (%d groups, %d samples)",
                global_step + 1, fwd_bwd_call_count + 1,
                len(minibatch_prompt_groups), len(minibatch_prompt_groups) * completions_per_prompt,
            )
            fwd_bwd_prompt_group_counts.append(len(minibatch_prompt_groups))
            t0 = time.time()
            fut = await asyncio.to_thread(fns.fwd_bwd_one, minibatch_prompt_groups)
            Timer().add("fwd_bwd", time.time() - t0)
            fwd_bwd_futures.append(fut)
            minibatch_prompt_groups = []
            fwd_bwd_call_count += 1

        logger.info(
            "[stream] step %d | %d fwd_bwd done, running optim_step",
            global_step + 1, fwd_bwd_call_count,
        )
        fwd_bwd_results = [f.result() for f in fwd_bwd_futures]
        loop_stats = {
            "valid_prompt_groups": len(step_prompt_groups),
            "total_sampled": total_sampled,
            "filter_drops": filter_drops,
            "sample_fails": sample_fails,
            "all_raw_rewards": list(all_raw_rewards),
            "fwd_bwd_group_counts": fwd_bwd_prompt_group_counts,
        }
        global_step, step_metrics = await asyncio.to_thread(
            fns.finish_step, global_step, step_prompt_groups,
            fwd_bwd_results, fwd_bwd_call_count, loop_stats,
        )
        if metrics_callback is not None:
            loop_metrics = build_loop_metrics(
                prompt_groups=step_prompt_groups,
                train_step=global_step,
                total_wait_time=total_wait_time,
                filter_drops=filter_drops,
                sample_fails=sample_fails,
                step_metrics=step_metrics,
                all_raw_rewards=all_raw_rewards,
                step_wall_time=time.time() - step_start_time,
            )
            metrics_callback(loop_metrics)

        minibatch_prompt_groups = []
        step_prompt_groups = []
        fwd_bwd_futures = []
        fwd_bwd_prompt_group_counts = []
        fwd_bwd_call_count = 0
        total_wait_time = 0.0
        filter_drops = 0
        sample_fails = 0
        all_raw_rewards = []
        total_sampled = 0
        step_start_time = time.time()

    for _ in range(len(coros)):
        t_wait = time.time()
        item = await queue.get()
        total_wait_time += time.time() - t_wait

        if worker_error is not None:
            for t in tasks:
                if not t.done():
                    t.cancel()
            pbar.close()
            raise RuntimeError(f"Sampling worker failed: {worker_error}") from worker_error

        if item is None:
            sample_fails += 1
            total_sampled += 1
            pbar.set_postfix(sampled=total_sampled, failed=sample_fails, filtered=filter_drops)
            continue

        total_sampled += 1
        all_raw_rewards.extend(item.rewards)
        if dynamic_filter_fn is not None and not dynamic_filter_fn(item):
            filter_drops += 1
            pbar.set_postfix(sampled=total_sampled, failed=sample_fails, filtered=filter_drops)
            continue

        t0 = time.time()
        await asyncio.to_thread(fns.ref_forward_one, item)
        Timer().add("ref_forward", time.time() - t0)

        minibatch_prompt_groups.append(item)
        step_prompt_groups.append(item)
        pbar.update(1)
        pbar.set_postfix(sampled=total_sampled, failed=sample_fails, filtered=filter_drops)

        if len(minibatch_prompt_groups) >= min_prompt_groups_per_fwd_bwd:
            batch = minibatch_prompt_groups[:max_prompt_groups_per_fwd_bwd]
            minibatch_prompt_groups = minibatch_prompt_groups[max_prompt_groups_per_fwd_bwd:]
            logger.info(
                "[stream] step %d | fwd_bwd %d (%d groups, %d samples)",
                global_step + 1, fwd_bwd_call_count + 1,
                len(batch), len(batch) * completions_per_prompt,
            )
            fwd_bwd_prompt_group_counts.append(len(batch))
            t0 = time.time()
            fut = await asyncio.to_thread(fns.fwd_bwd_one, batch)
            Timer().add("fwd_bwd", time.time() - t0)
            fwd_bwd_futures.append(fut)
            fwd_bwd_call_count += 1

        if len(step_prompt_groups) >= prompt_groups_per_step:
            pbar.close()
            await _flush_and_finish_step()
            pbar = tqdm(total=prompt_groups_per_step, desc="sampling", unit="prompt_grp", dynamic_ncols=True)

    pbar.close()

    if step_prompt_groups:
        await _flush_and_finish_step()

    return global_step
