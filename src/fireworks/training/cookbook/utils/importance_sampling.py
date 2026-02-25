"""Truncated Importance Sampling (TIS) for train-inference mismatch correction.

Provides per-token importance weighting that can be composed with **any**
base policy loss (GRPO, DAPO, GSPO, etc.).  The architecture follows
slime's orthogonal design: base loss computes per-token loss, TIS
multiplies by clipped importance weights, then the result is summed.

Usage -- enable TIS on any loss via ``tis_enabled``::

    Config(policy_loss="grpo", tis_enabled=True, tis=ISConfig(clip_high=10.0))
    Config(policy_loss="dapo", tis_enabled=True)   # TIS on top of PPO clipping
    Config(policy_loss="gspo", tis_enabled=True)   # TIS on top of seq-KL

Custom TIS function::

    def my_tis(policy_lp, inf_lp, config):
        rho = torch.exp(policy_lp - inf_lp)
        weights = torch.where(rho < 3.0, rho, torch.zeros_like(rho))
        return weights, {"custom_mean_rho": rho.mean().item()}

    Config(tis_enabled=True, tis=ISConfig(method=my_tis))
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Union, Callable
from dataclasses import dataclass

import torch

TISFunction = Callable[
    [torch.Tensor, torch.Tensor, "ISConfig"],
    Tuple[torch.Tensor, Dict[str, float]],
]

TISWeightsFn = Callable[
    [torch.Tensor, int],
    Tuple[torch.Tensor, Dict[str, float]],
]
"""Per-sample TIS weights function: ``(pi_detached, sample_idx) -> (weights, metrics)``."""


@dataclass
class ISConfig:
    """TIS (Truncated Importance Sampling) configuration.

    Used when ``tis_enabled=True`` on the GRPO Config.  Composable with
    any ``policy_loss`` setting.
    """

    clip_high: float = 10.0
    clip_low: float = 0.0
    method: Union[str, TISFunction] = "vanilla"


def vanilla_tis(
    policy_lp: torch.Tensor,
    inference_lp: torch.Tensor,
    config: ISConfig,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """Vanilla Truncated Importance Sampling with clamping."""
    rho = torch.exp(policy_lp - inference_lp)
    clamped = torch.clamp(rho, min=config.clip_low, max=config.clip_high)
    clip_frac = (clamped != rho).float().mean().item()
    metrics = {
        "tis_mean_ratio": rho.mean().item(),
        "tis_max_ratio": rho.max().item(),
        "tis_clip_frac": clip_frac,
    }
    return clamped, metrics


def resolve_tis_function(method: Union[str, TISFunction]) -> TISFunction:
    """Resolve a method name or callable to a concrete TIS function."""
    if callable(method):
        return method
    if method == "vanilla":
        return vanilla_tis
    raise ValueError(f"Unknown IS method: {method!r}. Use 'vanilla' or a custom callable.")


def make_tis_weights_fn(
    inf_logprobs: List[List[float]],
    prompt_len: int,
    tis_config: ISConfig | None = None,
) -> TISWeightsFn:
    """Create a per-sample TIS weights function.

    Returns a callable ``(pi_detached, sample_idx) -> (weights, metrics)``
    suitable for passing to any loss function's ``tis_weights_fn`` parameter.

    This decouples TIS from any specific loss algorithm -- the same weights
    function can be passed to ``make_grpo_loss_fn``, ``make_dapo_loss_fn``,
    ``make_gspo_loss_fn``, etc.

    Args:
        inf_logprobs: Per-sample inference logprobs (aligned to model_input).
        prompt_len: Number of prompt tokens (for response slicing).
        tis_config: Clipping thresholds and TIS method.
    """
    if tis_config is None:
        tis_config = ISConfig()
    tis_fn = resolve_tis_function(tis_config.method)
    response_start = max(0, prompt_len - 1)

    def weights_fn(
        pi_detached: torch.Tensor,
        sample_idx: int,
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        inf_lp = inf_logprobs[sample_idx]
        if not inf_lp:
            raise ValueError(
                f"TIS requires inference logprobs for sample {sample_idx} but got empty list. "
                f"Ensure logprobs=True is set when tis_enabled=True."
            )
        resp_len = len(pi_detached)
        resp_inf = torch.tensor(
            [
                inf_lp[response_start + j] if (response_start + j) < len(inf_lp) else pi_detached[j].item()
                for j in range(resp_len)
            ],
            dtype=torch.float32,
        )
        return tis_fn(pi_detached, resp_inf, tis_config)

    return weights_fn
