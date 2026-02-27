"""Cookbook utilities -- infrastructure, losses, data, logging, and more.

RL-specific utilities (GRPO/DAPO/GSPO losses, TIS, R3, batching) live in
``fireworks.training.cookbook.utils.rl``.
"""

__all__ = [
    "DEFAULT_ADAM",
    "DeployConfig",
    "EvalFn",
    "HotloadConfig",
    "InfraConfig",
    "ReconnectableClient",
    "ResumeConfig",
    "RewardFn",
    "StepCallback",
    "WandBConfig",
    "compute_advantages",
    "create_trainer_job",
    "resolve_and_apply_shape",
    "encode_text",
    "extract_text",
    "find_common_prefix_length",
    "load_jsonl_dataset",
    "load_preference_dataset",
    "log_metrics_json",
    "make_dpo_loss_fn",
    "make_orpo_loss_fn",
    "make_batch_sft_loss_fn",
    "make_sft_loss_fn",
    "setup_deployment",
    "setup_resume",
    "setup_training_client",
    "setup_wandb",
    "validate_config",
    "validate_preflight",
    "wandb_finish",
    "wandb_log",
]

from fireworks.training.cookbook.utils.data import (
    encode_text,
    extract_text,
    compute_advantages,
    load_jsonl_dataset,
    load_preference_dataset,
    find_common_prefix_length,
)
from fireworks.training.cookbook.utils.infra import (
    setup_deployment,
    create_trainer_job,
    setup_training_client,
    resolve_and_apply_shape,
)
from fireworks.training.cookbook.utils.client import ReconnectableClient
from fireworks.training.cookbook.utils.config import (
    DEFAULT_ADAM,
    EvalFn,
    RewardFn,
    InfraConfig,
    WandBConfig,
    DeployConfig,
    ResumeConfig,
    StepCallback,
    HotloadConfig,
)
from fireworks.training.cookbook.utils.losses import (
    make_dpo_loss_fn,
    make_orpo_loss_fn,
    make_sft_loss_fn,
    make_batch_sft_loss_fn,
)
from fireworks.training.cookbook.utils.resume import setup_resume
from fireworks.training.cookbook.utils.logging import (
    wandb_log,
    setup_wandb,
    wandb_finish,
    log_metrics_json,
)
from fireworks.training.cookbook.utils.validation import validate_config, validate_preflight
