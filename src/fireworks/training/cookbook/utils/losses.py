"""Loss functions for GRPO, DPO, and SFT training."""

from __future__ import annotations

from typing import Dict, List, Tuple, Callable

import torch
import tinker
import torch.nn.functional as F


def make_grpo_loss_fn(
    advantages: List[float],
    ref_logprobs: List[List[float]],
    prompt_len: int,
    kl_beta: float = 0.001,
    tis_weights_fn: Callable | None = None,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """GRPO policy-gradient loss with KL penalty against a reference model.

    Pass *tis_weights_fn* (from :func:`make_tis_weights_fn`) to apply
    TIS train-inference mismatch correction on top of the base loss.
    """

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
    """Cross-entropy loss over response tokens only (single-sample)."""
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


def make_batch_sft_loss_fn(
    prompt_token_counts: List[int],
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """Cross-entropy loss over response tokens for a *batch* of samples.

    Each sample may have a different prompt length. The loss is averaged across
    all response tokens in the batch (token-level mean), matching the behaviour
    of ``train_sft_tinker_sdk.py``.

    Args:
        prompt_token_counts: Per-sample prompt token counts. Tokens before this
            boundary are masked (no gradient contribution).
    """

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        assert len(data) == len(logprobs_list)
        assert len(prompt_token_counts) == len(logprobs_list)

        total_loss = torch.tensor(0.0)
        total_response_tokens = 0
        total_nll = 0.0

        for i, logprobs in enumerate(logprobs_list):
            response_start = max(0, prompt_token_counts[i] - 1)
            response_logprobs = logprobs[response_start:]
            n = len(response_logprobs)
            if n == 0:
                continue
            sample_nll = -response_logprobs.sum()
            total_loss = total_loss + sample_nll
            total_response_tokens += n
            with torch.no_grad():
                total_nll += sample_nll.item()

        if total_response_tokens > 0:
            avg_loss = total_loss / total_response_tokens
        else:
            avg_loss = total_loss

        with torch.no_grad():
            avg_nll = total_nll / total_response_tokens if total_response_tokens > 0 else 0.0
            ppl = torch.exp(torch.tensor(avg_nll)).item()

        return avg_loss, {
            "ce_loss": avg_nll,
            "ce_loss_sum": total_nll,
            "ppl": ppl,
            "response_tokens": total_response_tokens,
            "batch_size": len(logprobs_list),
        }

    return loss_fn
