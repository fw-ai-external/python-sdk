"""Importance Sampling (TIS) for GRPO training.

Provides a pluggable importance sampling system: a built-in ``vanilla_tis``
strategy (clamped importance ratios) and a ``TISFunction`` type so users
can supply their own.

Example -- built-in vanilla::

    ISConfig(enabled=True, clip_high=10.0)

Example -- custom function::

    def my_tis(policy_lp, inf_lp, config):
        rho = torch.exp(policy_lp - inf_lp)
        weights = torch.where(rho < 3.0, rho, torch.zeros_like(rho))
        return weights, {"custom_mean_rho": rho.mean().item()}

    ISConfig(enabled=True, method=my_tis)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Union

import tinker
import torch

TISFunction = Callable[
    [torch.Tensor, torch.Tensor, "ISConfig"],
    Tuple[torch.Tensor, Dict[str, float]],
]


@dataclass
class ISConfig:
    """Importance sampling configuration."""

    enabled: bool = False
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


def make_grpo_tis_loss_fn(
    advantages: List[float],
    ref_logprobs: List[List[float]],
    inf_logprobs: List[List[float]],
    prompt_len: int,
    kl_beta: float = 0.001,
    is_config: ISConfig | None = None,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """Build a GRPO loss closure with Truncated Importance Sampling."""
    if is_config is None:
        is_config = ISConfig(enabled=True)
    tis_fn = resolve_tis_function(is_config.method)

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        total_loss = torch.tensor(0.0, requires_grad=True)
        total_kl = 0.0
        total_rho = 0.0
        num_tokens = 0
        response_start = max(0, prompt_len - 1)
        agg_tis: Dict[str, float] = {}

        for i, pi_logprobs in enumerate(logprobs_list):
            adv = advantages[i]
            ref_lp = ref_logprobs[i]
            inf_lp = inf_logprobs[i]

            resp_pi = pi_logprobs[response_start:]
            resp_len = len(resp_pi)
            if resp_len == 0:
                continue

            resp_ref = torch.tensor(
                [ref_lp[response_start + j] if (response_start + j) < len(ref_lp) else 0.0 for j in range(resp_len)],
                dtype=torch.float32,
            )

            pi_detached = resp_pi.detach()

            if inf_lp:
                resp_inf = torch.tensor(
                    [
                        inf_lp[response_start + j] if (response_start + j) < len(inf_lp) else pi_detached[j].item()
                        for j in range(resp_len)
                    ],
                    dtype=torch.float32,
                )
                weights, tis_metrics = tis_fn(pi_detached, resp_inf, is_config)
                for k, v in tis_metrics.items():
                    agg_tis[k] = agg_tis.get(k, 0.0) + v
            else:
                weights = torch.ones_like(pi_detached)

            loss_i = (weights * (-adv + kl_beta) * resp_pi).sum()
            total_loss = total_loss + loss_i

            total_kl += (pi_detached - resp_ref).sum().item()
            total_rho += weights.sum().item()
            num_tokens += resp_len

        metrics: Dict[str, float] = {
            "mean_kl": total_kl / num_tokens if num_tokens > 0 else 0.0,
            "mean_importance_ratio": total_rho / num_tokens if num_tokens > 0 else 1.0,
        }
        n_samples = len(logprobs_list) or 1
        for k, v in agg_tis.items():
            metrics[k] = v / n_samples
        return total_loss, metrics

    return loss_fn
