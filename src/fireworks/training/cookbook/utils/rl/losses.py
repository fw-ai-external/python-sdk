"""RL loss functions, shared helpers, and data types."""

from __future__ import annotations

from typing import Dict, List, Tuple, Union, Callable
from dataclasses import field, dataclass

import torch
import tinker


@dataclass
class PromptGroup:
    """Processed data from one prompt's rollout, ready for training."""

    data: List[tinker.Datum]
    advantages: List[float]
    ref_logprobs: List[List[float]]
    prompt_len: int
    rewards: List[float]
    inf_logprobs: List[List[float]] = field(default_factory=list)


def _normalize_prompt_lens(prompt_len: Union[int, List[int]], n: int) -> List[int]:
    """Accept ``int`` (single prompt_len for all datums) or ``List[int]``."""
    if isinstance(prompt_len, int):
        return [prompt_len] * n
    return list(prompt_len)


def make_grpo_loss_fn(
    advantages: List[float],
    ref_logprobs: List[List[float]],
    prompt_len: Union[int, List[int]],
    kl_beta: float = 0.001,
    tis_weights_fn: Callable | None = None,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """GRPO policy-gradient loss with KL penalty against a reference model.

    ``prompt_len`` may be a single int (all datums share the same prompt
    length) or a per-datum list for multi-prompt batched calls.

    Pass *tis_weights_fn* (from :func:`make_tis_weights_fn`) to apply
    TIS train-inference mismatch correction on top of the base loss.
    """
    prompt_lens = _normalize_prompt_lens(prompt_len, len(advantages))

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        total_loss = torch.tensor(0.0, requires_grad=True)
        total_kl = 0.0
        total_rho = 0.0
        num_tokens = 0
        agg_tis: Dict[str, float] = {}

        for i, pi_logprobs in enumerate(logprobs_list):
            adv = advantages[i]
            ref_lp = ref_logprobs[i]
            response_start = max(0, prompt_lens[i] - 1)

            resp_pi = pi_logprobs[response_start:]
            resp_len = len(resp_pi)
            if resp_len == 0:
                continue

            resp_ref = torch.tensor(
                [ref_lp[response_start + j] if (response_start + j) < len(ref_lp) else 0.0 for j in range(resp_len)],
                dtype=torch.float32,
            )

            per_token_loss = (-adv + kl_beta) * resp_pi

            if tis_weights_fn:
                weights, tis_metrics = tis_weights_fn(resp_pi.detach(), i)
                per_token_loss = per_token_loss * weights
                total_rho += weights.sum().item()
                for k, v in tis_metrics.items():
                    agg_tis[k] = agg_tis.get(k, 0.0) + v

            total_loss = total_loss + per_token_loss.sum()
            total_kl += (resp_pi.detach() - resp_ref).sum().item()
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
