"""Tests for rollout/batch metric naming."""

from __future__ import annotations

from types import SimpleNamespace

from fireworks.training.cookbook.utils.rl.losses import PromptGroup
from fireworks.training.cookbook.utils.rl.metrics import build_loop_metrics, compute_step_metrics


def _make_prompt_group() -> PromptGroup:
    target = SimpleNamespace(shape=[3], data=[11, 12, 13])
    datum = SimpleNamespace(loss_fn_inputs={"target_tokens": target})
    return PromptGroup(
        data=[datum],
        advantages=[1.0],
        ref_logprobs=[[0.1, 0.1, 0.1]],
        prompt_len=2,
        rewards=[1.0],
        inf_logprobs=[[-0.2, -0.3, -0.4]],
        completion_lens=[2],
        truncated=[False],
    )


class TestBuildLoopMetrics:
    def test_filter_reject_ratio(self):
        loop_metrics = build_loop_metrics(
            prompt_groups=[_make_prompt_group()],
            train_step=3,
            total_wait_time=1.0,
            filter_drops=2,
            sample_fails=1,
            step_metrics={"perf/step_time": 2.0},
            all_raw_rewards=[1.0, 0.0],
        )

        assert loop_metrics["rollout/filter_reject_ratio"] == 2 / 3
        assert "rollout/filter_drop_ratio" not in loop_metrics
        assert "rollout/zero_std_ratio" not in loop_metrics


class TestComputeStepMetrics:
    def test_uses_canonical_loop_stats_keys(self):
        metrics = compute_step_metrics(
            prompt_groups=[_make_prompt_group()],
            fwd_bwd_results=[SimpleNamespace(metrics={"loss": 0.5})],
            optim_result=SimpleNamespace(metrics={"lr": 1e-5}),
            n_accum=4,
            timing_metrics={"perf/fwd_bwd_time": 1.0},
            loop_stats={
                "valid_prompt_groups": 6,
                "total_sampled": 7,
                "filter_drops": 1,
                "sample_fails": 2,
                "all_raw_rewards": [1.0, 0.0],
                "fwd_bwd_group_counts": [2, 4],
            },
            completions_per_prompt=8,
        )

        assert metrics["rollout/valid_prompt_groups"] == 6
        assert metrics["rollout/filter_reject_ratio"] == 1 / 7
        assert metrics["rollout/sample_fail_count"] == 2
        assert metrics["batch/mean_prompt_groups_per_fwd_bwd"] == 3.0
        assert metrics["batch/max_prompt_groups_per_fwd_bwd"] == 4
        assert metrics["batch/min_prompt_groups_per_fwd_bwd"] == 2
        assert metrics["batch/mean_samples_per_fwd_bwd"] == 24.0

        assert "rollout/valid_prompts" not in metrics
        assert "rollout/filter_ratio" not in metrics
        assert "rollout/sample_fails" not in metrics
        assert "batch/mean_groups_per_fwd_bwd" not in metrics
