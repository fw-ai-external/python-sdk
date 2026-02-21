"""E2E test for GRPO training on qwen3-30b-a3b (MoE).

Full pipeline: policy + reference trainers, deployment with hotloading,
Router Replay (R3), and Truncated Importance Sampling (TIS).

Requires:
  FIREWORKS_API_KEY     — API key with dev access
  FIREWORKS_ACCOUNT_ID  — defaults to "pyroworks-dev"
  FIREWORKS_BASE_URL    — defaults to "https://dev.api.fireworks.ai"
"""

from __future__ import annotations

import re
import time

import pytest

from fireworks.training.cookbook.utils import DeployConfig, HotloadConfig, InfraConfig, ISConfig
from fireworks.training.cookbook.recipes.grpo_loop import Config, main
from fireworks.training.cookbook.tests.conftest import GSM8K_SAMPLE_URL


def _gsm8k_reward(completion: str, row: dict) -> float:
    """Extract a numeric answer from the completion and compare to ground truth."""
    gt = row.get("ground_truth", "")
    numbers = re.findall(r"-?\d+(?:\.\d+)?", completion)
    if numbers and gt:
        gt_numbers = re.findall(r"-?\d+(?:\.\d+)?", gt)
        if gt_numbers and numbers[-1] == gt_numbers[-1]:
            return 1.0
    return 0.0


@pytest.mark.e2e
@pytest.mark.timeout(3600)
class TestGRPOE2E:
    """GRPO on qwen3-30b-a3b with R3, TIS, and hotloading."""

    def test_grpo_full_pipeline(
        self,
        sdk_managers,
        e2e_region,
        e2e_model,
        e2e_training_accelerator,
        e2e_deployment_accelerator,
        e2e_deployment_shape,
        custom_image_tag,
    ):
        rlor_mgr, deploy_mgr = sdk_managers
        ts = int(time.time())

        # Monkey-patch the reward function into the module
        import cookbook.recipes.grpo_loop as grpo_mod

        grpo_mod.reward_fn = _gsm8k_reward

        config = Config(
            base_model=e2e_model,
            dataset=GSM8K_SAMPLE_URL,
            group_size=4,
            max_rows=10,
            epochs=1,
            grad_accum=2,
            max_seq_len=4096,
            router_replay=True,
            importance_sampling=ISConfig(enabled=True, clip_high=10.0),
            infra=InfraConfig(
                region=e2e_region,
                skip_validations=True,
                accelerator_type=e2e_training_accelerator,
                custom_image_tag=custom_image_tag,
            ),
            deployment=DeployConfig(
                deployment_id=f"grpo-e2e-{ts}",
                create_deployment=True,
                deployment_shape=e2e_deployment_shape,
                deployment_region=e2e_region,
            ),
            hotload=HotloadConfig(
                hot_load_interval=1,
                first_checkpoint_type="base",
                hot_load_before_training=True,
                hot_load_timeout=600,
            ),
        )

        metrics = main(config, rlor_mgr=rlor_mgr, deploy_mgr=deploy_mgr)

        assert isinstance(metrics, dict)
        assert "steps" in metrics
        assert metrics["steps"] >= 2, "Expected at least 2 optimizer steps"
