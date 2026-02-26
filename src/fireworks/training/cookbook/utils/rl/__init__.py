"""RL-specific utilities: losses, PP recommendation, importance sampling, router replay."""

__all__ = [
    "DAPOConfig",
    "GSPOConfig",
    "ISConfig",
    "PPBatchRecommendation",
    "PromptGroup",
    "build_r3_routing_matrices",
    "compute_pp_recommendation",
    "make_dapo_loss_fn",
    "make_grpo_loss_fn",
    "make_gspo_loss_fn",
    "make_tis_weights_fn",
]

from fireworks.training.cookbook.utils.rl.pp import PPBatchRecommendation, compute_pp_recommendation
from fireworks.training.cookbook.utils.rl.dapo import DAPOConfig, make_dapo_loss_fn
from fireworks.training.cookbook.utils.rl.gspo import GSPOConfig, make_gspo_loss_fn
from fireworks.training.cookbook.utils.rl.losses import PromptGroup, make_grpo_loss_fn
from fireworks.training.cookbook.utils.rl.router_replay import build_r3_routing_matrices
from fireworks.training.cookbook.utils.rl.importance_sampling import ISConfig, make_tis_weights_fn
