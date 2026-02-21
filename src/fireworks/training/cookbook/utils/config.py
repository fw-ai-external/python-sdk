"""Shared configuration dataclasses for cookbook recipes."""

from __future__ import annotations

from typing import Dict, Callable
from dataclasses import dataclass

from fireworks.training.sdk.client import FiretitanTrainingClient
from fireworks.training.sdk.deployment import DeploymentConfig

DEFAULT_ADAM = dict(beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.01)

RewardFn = Callable[[str, dict], float]
"""Signature: (completion_text, dataset_row) -> reward_float."""

EvalFn = Callable[[int, FiretitanTrainingClient], Dict[str, float]]
"""Called every eval_every steps: (global_step, policy_client) -> metrics_dict."""

StepCallback = Callable[[int, Dict[str, float]], None]
"""Called after each optimizer step: (global_step, step_metrics) -> None."""


@dataclass
class InfraConfig:
    """GPU, region, and image settings."""

    region: str | None = None
    custom_image_tag: str | None = None
    accelerator_type: str | None = None
    accelerator_count: int | None = None
    skip_validations: bool = False
    node_count: int = 1
    extra_args: list[str] | None = None


@dataclass
class DeployConfig:
    """Inference deployment settings."""

    deployment_id: str | None = None
    create_deployment: bool = True
    deployment_shape: str | None = None
    deployment_region: str | None = None
    deployment_accelerator_type: str | None = None
    hot_load_bucket_type: str = "FW_HOSTED"
    deployment_timeout_s: float = 1800
    deployment_extra_args: list[str] | None = None
    tokenizer_model: str | None = None
    """HuggingFace model name for the tokenizer (e.g. ``Qwen/Qwen3-1.7B``).
    Required for recipes that use client-side tokenization (GRPO)."""

    def to_deployment_config(
        self,
        base_model: str,
        infra: InfraConfig,
    ) -> DeploymentConfig:
        """Produce an SDK-level DeploymentConfig from cookbook settings."""
        skip_validation = infra.skip_validations and not self.deployment_shape
        return DeploymentConfig(
            deployment_id=self.deployment_id,
            base_model=base_model,
            deployment_shape=self.deployment_shape,
            region=self.deployment_region or infra.region or "US_VIRGINIA_1",
            accelerator_type=self.deployment_accelerator_type or infra.accelerator_type,
            hot_load_bucket_type=self.hot_load_bucket_type,
            skip_shape_validation=skip_validation,
            extra_args=self.deployment_extra_args,
        )


@dataclass
class HotloadConfig:
    """Checkpoint and weight-sync settings."""

    hot_load_interval: int = 1
    dcp_save_interval: int = 0
    first_checkpoint_type: str = "base"
    hot_load_before_training: bool = False
    hot_load_timeout: int = 600


@dataclass
class WandBConfig:
    """Weights & Biases logging settings."""

    entity: str | None = None
    project: str | None = None
    run_name: str | None = None


@dataclass
class ResumeConfig:
    """Checkpoint resume settings."""

    resume_from: str | None = None
    resume_job_id: str | None = None
    step_offset: int | None = None
