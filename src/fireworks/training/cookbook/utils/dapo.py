"""DAPO (Dynamic Advantage Policy Optimization) loss for GRPO training.

Uses PPO-style clipped surrogate objective with asymmetric clipping bounds:
the lower bound (eps_clip) and upper bound (eps_clip_high) can differ.
No explicit KL penalty -- divergence is controlled solely via clipping.

Reference: https://arxiv.org/abs/2503.14476

Example::

    Config(policy_loss="dapo", dapo=DAPOConfig(eps_clip=0.2, eps_clip_high=0.28))
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass

import torch
import tinker


@dataclass
class DAPOConfig:
    """DAPO clipping thresholds.

    ``eps_clip`` is the lower clipping bound (ratio >= 1 - eps_clip).
    ``eps_clip_high`` is the upper clipping bound (ratio <= 1 + eps_clip_high).
    Setting them equal recovers standard PPO clipping.
    """

    eps_clip: float = 0.2
    eps_clip_high: float = 0.28


def make_dapo_loss_fn(
    advantages: List[float],
    ref_logprobs: List[List[float]],
    inf_logprobs: List[List[float]],
    prompt_len: int,
    dapo_config: DAPOConfig | None = None,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """Build a DAPO loss closure.

    Computes the PPO clipped surrogate objective with asymmetric bounds.
    The importance ratio ``pi/pi_old`` is clipped to
    ``[1 - eps_clip, 1 + eps_clip_high]``.
    """
    if dapo_config is None:
        dapo_config = DAPOConfig()

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        total_loss = torch.tensor(0.0, requires_grad=True)
        total_kl = 0.0
        num_tokens = 0
        clip_frac_sum = 0.0
        clip_frac_count = 0
        response_start = max(0, prompt_len - 1)

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
                log_ratio = resp_pi - resp_inf
                ratio = torch.exp(log_ratio)
                clipped_ratio = torch.clamp(
                    ratio,
                    min=1.0 - dapo_config.eps_clip,
                    max=1.0 + dapo_config.eps_clip_high,
                )
                clip_frac_sum += (clipped_ratio != ratio).float().mean().item()
                clip_frac_count += 1

                adv_t = torch.tensor(adv, dtype=torch.float32)
                surr1 = -ratio * adv_t
                surr2 = -clipped_ratio * adv_t
                loss_i = torch.maximum(surr1, surr2).sum()
            else:
                loss_i = -(resp_pi * adv).sum()

            total_loss = total_loss + loss_i
            total_kl += (pi_detached - resp_ref).sum().item()
            num_tokens += resp_len

        metrics: Dict[str, float] = {
            "mean_kl": total_kl / num_tokens if num_tokens > 0 else 0.0,
            "dapo_clip_frac": clip_frac_sum / clip_frac_count if clip_frac_count > 0 else 0.0,
        }
        return total_loss, metrics

    return loss_fn
