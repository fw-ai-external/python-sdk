"""Loss functions for GRPO, DPO, and SFT training."""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import tinker
import torch
import torch.nn.functional as F


def make_grpo_loss_fn(
    advantages: List[float],
    ref_logprobs: List[List[float]],
    prompt_len: int,
    kl_beta: float = 0.001,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """GRPO policy-gradient loss with KL penalty against a reference model.

    This is the basic (on-policy) GRPO loss without importance weighting.
    For importance-weighted GRPO, use ``make_grpo_tis_loss_fn`` via
    ``ISConfig(enabled=True)``.
    """

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

            loss_i = ((-adv + kl_beta) * resp_pi).sum()
            total_loss = total_loss + loss_i

            total_kl += (resp_pi.detach() - resp_ref).sum().item()
            num_tokens += resp_len

        metrics: Dict[str, float] = {
            "mean_kl": total_kl / num_tokens if num_tokens > 0 else 0.0,
        }
        return total_loss, metrics

    return loss_fn


def make_dpo_loss_fn(
    ref_chosen: List[float],
    ref_rejected: List[float],
    response_start: int,
    beta: float,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """DPO loss: -log(sigmoid(beta * margin))."""
    ref_chosen_t = torch.tensor(ref_chosen, dtype=torch.float32)
    ref_rejected_t = torch.tensor(ref_rejected, dtype=torch.float32)

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        assert len(logprobs_list) == 2
        pi_chosen = logprobs_list[0][response_start:].sum()
        pi_rejected = logprobs_list[1][response_start:].sum()
        rc = ref_chosen_t[response_start:].sum()
        rr = ref_rejected_t[response_start:].sum()

        margin = (pi_chosen - rc) - (pi_rejected - rr)
        dpo_loss = -F.logsigmoid(beta * margin)

        with torch.no_grad():
            metrics = {
                "dpo_loss": dpo_loss.item(),
                "margin": margin.item(),
                "accuracy": 1.0 if margin.item() > 0 else 0.0,
                "chosen_reward": beta * (pi_chosen.item() - rc.item()),
                "rejected_reward": beta * (pi_rejected.item() - rr.item()),
            }
        return dpo_loss, metrics

    return loss_fn


def make_sft_loss_fn(
    response_start: int,
    target_tokens: List[int],
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """Cross-entropy loss over response tokens only."""
    targets = torch.tensor(target_tokens, dtype=torch.long)

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        lp = logprobs_list[0]
        resp_lp = lp[response_start:]
        resp_t = targets[response_start:]
        n = max(len(resp_t), 1)
        ce = -resp_lp.sum() / n
        with torch.no_grad():
            ppl = torch.exp(ce).item()
        return ce, {"ce_loss": ce.item(), "ppl": ppl, "response_tokens": len(resp_t)}

    return loss_fn
