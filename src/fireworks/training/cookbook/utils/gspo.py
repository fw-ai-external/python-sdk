"""GSPO (Group Sequence Policy Optimization) loss for GRPO training.

Like GRPO but uses **sequence-level KL** divergence instead of per-token KL.
The KL is averaged across all response tokens in each sequence, then
broadcast back to every token as a uniform penalty.  This prevents
individual high-KL tokens from dominating the penalty signal.

Example::

    Config(policy_loss="gspo", gspo=GSPOConfig(kl_beta=0.001))
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
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """Build a GSPO loss closure.

    Same as GRPO but the KL penalty uses sequence-level KL (mean over
    response tokens per sequence) instead of per-token KL.
    """
    if gspo_config is None:
        gspo_config = GSPOConfig()

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        total_loss = torch.tensor(0.0, requires_grad=True)
        total_kl = 0.0
        num_tokens = 0
        response_start = max(0, prompt_len - 1)

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

            loss_i = ((-adv + gspo_config.kl_beta * seq_kl) * resp_pi).sum()
            total_loss = total_loss + loss_i

            total_kl += seq_kl.item() * resp_len
            num_tokens += resp_len

        metrics: Dict[str, float] = {
            "mean_kl": total_kl / num_tokens if num_tokens > 0 else 0.0,
        }
        return total_loss, metrics

    return loss_fn
