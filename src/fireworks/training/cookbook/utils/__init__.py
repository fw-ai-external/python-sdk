"""Cookbook utilities -- infrastructure, losses, data, logging, and more."""

from fireworks.training.cookbook.utils.config import (
    DEFAULT_ADAM,
    DeployConfig,
    EvalFn,
    HotloadConfig,
    InfraConfig,
    ResumeConfig,
    RewardFn,
    StepCallback,
    WandBConfig,
)
from fireworks.training.cookbook.utils.client import ReconnectableClient
from fireworks.training.cookbook.utils.data import (
    compute_advantages,
    encode_text,
    extract_text,
    find_common_prefix_length,
    load_jsonl_dataset,
    load_preference_dataset,
)
from fireworks.training.cookbook.utils.infra import (
    create_trainer_job,
    setup_deployment,
    setup_training_client,
)
from fireworks.training.cookbook.utils.logging import (
    log_metrics_json,
    setup_wandb,
    wandb_finish,
    wandb_log,
)
from fireworks.training.cookbook.utils.losses import (
    make_dpo_loss_fn,
    make_grpo_loss_fn,
    make_sft_loss_fn,
)
from fireworks.training.cookbook.utils.resume import setup_resume
from fireworks.training.cookbook.utils.validation import validate_config, validate_preflight
from fireworks.training.cookbook.utils.importance_sampling import ISConfig, make_grpo_tis_loss_fn
from fireworks.training.cookbook.utils.router_replay import build_r3_routing_matrices
