"""GSPO (Group Sequence Policy Optimization) loss for GRPO training.

Like GRPO but uses **sequence-level KL** divergence instead of per-token KL.
The KL is averaged across all response tokens in each sequence, then
broadcast back to every token as a uniform penalty.  This prevents
individual high-KL tokens from dominating the penalty signal.

TIS can be composed on top via ``tis_weights_fn``.

Example::

    Config(policy_loss="gspo", gspo=GSPOConfig(kl_beta=0.001))
    Config(policy_loss="gspo", tis_enabled=True)  # GSPO + TIS
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass

import torch
import tinker


@dataclass
class GSPOConfig:
    """GSPO configuration."""

    kl_beta: float = 0.001
    """KL penalty coefficient (applied to the sequence-level KL)."""


def make_gspo_loss_fn(
    advantages: List[float],
    ref_logprobs: List[List[float]],
    prompt_len: int,
    gspo_config: GSPOConfig | None = None,
    tis_weights_fn: Callable | None = None,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """Build a GSPO loss closure.

    Same as GRPO but the KL penalty uses sequence-level KL (mean over
    response tokens per sequence) instead of per-token KL.

    Pass *tis_weights_fn* to apply TIS correction on top.
    """
    if gspo_config is None:
        gspo_config = GSPOConfig()

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

            resp_pi = pi_logprobs[response_start:]
            resp_len = len(resp_pi)
            if resp_len == 0:
                continue

            resp_ref = torch.tensor(
                [ref_lp[response_start + j] if (response_start + j) < len(ref_lp) else 0.0 for j in range(resp_len)],
                dtype=torch.float32,
            )

            pi_detached = resp_pi.detach()
            per_token_kl = pi_detached - resp_ref
            seq_kl = per_token_kl.mean()

            per_token_loss = (-adv + gspo_config.kl_beta * seq_kl) * resp_pi

            if tis_weights_fn:
                weights, tis_metrics = tis_weights_fn(pi_detached, i)
                per_token_loss = per_token_loss * weights
                total_rho += weights.sum().item()
                for k, v in tis_metrics.items():
                    agg_tis[k] = agg_tis.get(k, 0.0) + v

            total_loss = total_loss + per_token_loss.sum()
            total_kl += seq_kl.item() * resp_len
            num_tokens += resp_len

        metrics: Dict[str, float] = {
            "mean_kl": total_kl / num_tokens if num_tokens > 0 else 0.0,
        }
        if tis_weights_fn:
            metrics["mean_importance_ratio"] = total_rho / num_tokens if num_tokens > 0 else 1.0
            n_samples = len(logprobs_list) or 1
            for k, v in agg_tis.items():
                metrics[k] = v / n_samples
        return total_loss, metrics

    return loss_fn
