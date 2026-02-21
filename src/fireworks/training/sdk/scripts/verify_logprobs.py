#!/usr/bin/env python3
"""
Verify forward logprobs between training (RLOR reference) and inference (deployment).

Sets up a reference RLOR job (forward-only, no backward/optimizer) and a deployment,
samples from the deployment to get inference logprobs, then runs a forward pass on
the reference trainer to get training logprobs, and compares them token-by-token.

Usage:
    python verify_logprobs.py \
        --base-model "accounts/fireworks/models/kimi-k2p5" \
        --dataset data/ifbench_sample.jsonl \
        --log-dir ./verify_logprobs_run \
        --deployment-shape "accounts/pyroworks-dev/deploymentShapes/rft-kimi-k2p5-r3" \
        --create-deployment \
        --hotload-deployment-id "verify-logprobs-$(date +%s)" \
        --custom-image-tag "dev-chengxili-r3-v5" \
        --region US_OHIO_1 \
        --skip-validations \
        --max-rows 3 \
        --group-size 2
"""

from __future__ import annotations

import argparse
import atexit
import concurrent.futures
import json
import logging
import math
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
import tinker
import torch
import transformers

from fireworks.training.sdk import (
    DeploymentConfig,
    DeploymentInfo,
    DeploymentManager,
    DeploymentSampler,
    FiretitanServiceClient,
    FiretitanTrainingClient,
    TrainerJobConfig,
    TrainerJobManager,
    TrainerServiceEndpoint,
    SampledCompletion,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Suppress noisy tinker telemetry 404 warnings
logging.getLogger("tinker").setLevel(logging.ERROR)
logging.getLogger("tinker.lib.telemetry").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)


# =============================================================================
# Scoring Pass (prefill-vs-prefill)
# =============================================================================


def get_prefill_logprobs(
    url: str,
    tokens: List[int],
    api_key: str = "",
    model: str = "",
) -> List[float]:
    """Get logprobs for a token sequence by running a prefill scoring pass.

    Sends the full token sequence to /inference/v1/completions as a "prompt"
    with echo=True to get pure prefill logprobs for every position. This gives
    teacher-forced logprobs that are directly comparable to training logprobs.

    Alignment: inference[i] = P(tokens[i] | tokens[0:i]), where [0] is None.
    We shift by 1 so result[i] = P(tokens[i+1] | tokens[0:i+1]), matching
    the trainer convention.
    """
    if not tokens or len(tokens) < 2:
        return [0.0] * (len(tokens) - 1) if tokens else []

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-Api-Key": api_key,
    }
    payload: Dict[str, Any] = {
        "prompt": tokens,
        "max_tokens": 1,
        "echo": True,
        "logprobs": 1,
        "prompt_cache_max_len": 0,
    }
    if model:
        payload["model"] = model
    resp = requests.post(
        f"{url}/inference/v1/completions",
        json=payload,
        headers=headers,
        timeout=180,
    )
    resp.raise_for_status()

    result = resp.json()
    choices = result.get("choices", [])
    if not choices:
        return [0.0] * (len(tokens) - 1)

    logprobs_data = choices[0].get("logprobs", {})
    token_logprobs = logprobs_data.get("token_logprobs", [])

    aligned_logprobs = token_logprobs[1 : len(tokens)]
    logprobs = [lp if lp is not None else 0.0 for lp in aligned_logprobs]
    expected_len = len(tokens) - 1
    while len(logprobs) < expected_len:
        logprobs.append(0.0)

    return logprobs


# =============================================================================
# Logprob Comparison
# =============================================================================


def compare_logprobs(
    training_logprobs: List[float],
    inference_logprobs: List[float],
    tokens: List[int],
    prompt_len: int,
    label: str = "",
    router_replay: bool = False,
    routing_matrices: Optional[List[str]] = None,
    logprobs_echoed: bool = False,
    inference_top_logprobs: Optional[List] = None,
    training_top_k: Optional[Dict] = None,
    debug_completion_tokens: int = 0,
    debug_top_logprobs: int = 5,
) -> Dict[str, Any]:
    """Compare training vs inference logprobs token-by-token.

    Args:
        training_logprobs: Per-token logprobs from reference trainer forward.
        inference_logprobs: Per-token logprobs from deployment API.
        tokens: Full token sequence (prompt + completion).
        prompt_len: Number of prompt tokens.
        label: Label for this comparison (e.g., "sample-0").
        router_replay: Whether R3 routing matrices were used.
        routing_matrices: Per-position routing matrices (if R3).
        logprobs_echoed: From SampledCompletion.logprobs_echoed. True means
            inference_logprobs covers all P+C-1 positions (training-aligned).
        inference_top_logprobs: Per-position top-K logprobs from inference.
        debug_completion_tokens: Print top-K debug for the first N completion
            token positions (0 = disabled).
        debug_top_logprobs: How many top logprobs to show per debug position.

    Returns:
        Dict with detailed comparison metrics.
    """
    response_start = max(0, prompt_len - 1)

    # Use explicit flag from SDK to determine logprob format.
    # echoed = all positions (training-aligned), not completion-only.
    inf_is_completion_only = not logprobs_echoed

    # Per-token comparison
    prompt_diffs = []
    completion_diffs = []
    all_diffs = []
    # Log-ratios for KL estimators: log(π_inf / π_train) = inf_lp - train_lp
    prompt_log_ratios = []
    completion_log_ratios = []
    all_log_ratios = []
    per_token_details = []

    for j in range(len(training_logprobs)):
        train_lp = training_logprobs[j]

        # Map inference logprob index
        if inf_is_completion_only:
            inf_idx = j - response_start
            inf_lp = inference_logprobs[inf_idx] if 0 <= inf_idx < len(inference_logprobs) else None
        else:
            inf_lp = inference_logprobs[j] if j < len(inference_logprobs) else None

        diff = abs(train_lp - inf_lp) if inf_lp is not None else None
        log_ratio = (inf_lp - train_lp) if inf_lp is not None else None
        region = "PROMPT" if j < response_start else "COMPLETION"

        target_tok = tokens[j + 1] if j + 1 < len(tokens) else -1

        detail = {
            "pos": j,
            "region": region,
            "target_token": target_tok,
            "training_lp": train_lp,
            "inference_lp": inf_lp,
            "abs_diff": diff,
        }
        if routing_matrices and j < len(routing_matrices):
            detail["has_routing"] = bool(routing_matrices[j])
        per_token_details.append(detail)

        if diff is not None:
            all_diffs.append(diff)
            all_log_ratios.append(log_ratio)
            if j < response_start:
                prompt_diffs.append(diff)
                prompt_log_ratios.append(log_ratio)
            else:
                completion_diffs.append(diff)
                completion_log_ratios.append(log_ratio)

    # Aggregate metrics
    def _kl_stats(log_ratios: List[float]) -> Dict[str, float]:
        """Compute KL divergence estimators from per-token log-ratios.

        log_ratio = log(π_θ / π_ref) = inf_lp - train_lp

        k1 = E[log_ratio]                         (unbiased, can be negative)
        k2 = E[0.5 * log_ratio^2]                 (always ≥ 0, low variance)
        k3 = E[exp(log_ratio) - 1 - log_ratio]    (always ≥ 0, stable)
        """
        if not log_ratios:
            return {"k1": 0, "k2": 0, "k3": 0}
        t = torch.tensor(log_ratios, dtype=torch.float32)
        return {
            "k1": t.mean().item(),
            "k2": (0.5 * t**2).mean().item(),
            "k3": (t.exp() - 1 - t).mean().item(),
        }

    def _stats(diffs: List[float]) -> Dict[str, float]:
        if not diffs:
            return {"mean": 0, "max": 0, "min": 0, "std": 0, "count": 0}
        t = torch.tensor(diffs, dtype=torch.float32)
        return {
            "mean": t.mean().item(),
            "max": t.max().item(),
            "min": t.min().item(),
            "std": t.std().item() if len(diffs) > 1 else 0.0,
            "count": len(diffs),
        }

    metrics = {
        "label": label,
        "prompt_len": prompt_len,
        "total_tokens": len(tokens),
        "training_lp_len": len(training_logprobs),
        "inference_lp_len": len(inference_logprobs),
        "inf_is_completion_only": inf_is_completion_only,
        "router_replay": router_replay,
        "all": {**_stats(all_diffs), **_kl_stats(all_log_ratios)},
        "prompt": {**_stats(prompt_diffs), **_kl_stats(prompt_log_ratios)},
        "completion": {**_stats(completion_diffs), **_kl_stats(completion_log_ratios)},
    }

    # ---- Detailed per-token diagnostic ----
    # Show: first 10 prompt tokens, boundary (last 5 prompt + first 15 completion),
    # last 5 tokens, and any tokens with large diffs (> 0.1)
    HEAD_PROMPT = 10
    BOUNDARY_BEFORE = 5
    BOUNDARY_AFTER = 15
    TAIL = 5
    LARGE_DIFF_THRESHOLD = 0.1

    lines = []
    show_indices = set()

    # First HEAD_PROMPT tokens
    for i in range(min(HEAD_PROMPT, len(per_token_details))):
        show_indices.add(i)
    # Boundary around response_start
    for i in range(
        max(0, response_start - BOUNDARY_BEFORE), min(len(per_token_details), response_start + BOUNDARY_AFTER)
    ):
        show_indices.add(i)
    # Last TAIL tokens
    for i in range(max(0, len(per_token_details) - TAIL), len(per_token_details)):
        show_indices.add(i)
    # Large diffs
    large_diff_indices = []
    for i, d in enumerate(per_token_details):
        if d["abs_diff"] is not None and d["abs_diff"] > LARGE_DIFF_THRESHOLD:
            show_indices.add(i)
            large_diff_indices.append(i)

    # Track completion token count for debug_completion_tokens
    completion_count = 0
    # Also ensure first N completion tokens are always shown when debug is on
    if debug_completion_tokens > 0:
        comp_shown = 0
        for i, d in enumerate(per_token_details):
            if d["region"] == "COMPLETION":
                if comp_shown < debug_completion_tokens:
                    show_indices.add(i)
                    comp_shown += 1
                else:
                    break

    prev_shown = -1
    for i in sorted(show_indices):
        d = per_token_details[i]
        if i > prev_shown + 1 and prev_shown >= 0:
            lines.append(f"  ... ({i - prev_shown - 1} positions omitted) ...")
        inf_str = f"{d['inference_lp']:.4f}" if d["inference_lp"] is not None else "N/A"
        diff_str = f"{d['abs_diff']:.6f}" if d["abs_diff"] is not None else "N/A"
        routing_str = ""
        if d.get("has_routing") is not None:
            routing_str = f" R3={'Y' if d['has_routing'] else 'N'}"
        flag = " <<<" if (d["abs_diff"] is not None and d["abs_diff"] > LARGE_DIFF_THRESHOLD) else ""
        lines.append(
            f"  pos={d['pos']:4d} [{d['region']:10s}] tok={d['target_token']:6d} | "
            f"train={d['training_lp']:8.4f}  inf={inf_str:>8s} | "
            f"diff={diff_str:>10s}{routing_str}{flag}"
        )
        # Debug top-K logprobs for the first N completion positions
        if d["region"] == "COMPLETION":
            completion_count += 1
            if (
                debug_completion_tokens > 0
                and completion_count <= debug_completion_tokens
                and inference_top_logprobs is not None
                and i < len(inference_top_logprobs)
                and inference_top_logprobs[i]
            ):
                top_entries = inference_top_logprobs[i][:debug_top_logprobs]
                top_strs = [f"tok={e.get('token', '?'):>8s} lp={e.get('logprob', 0.0):.4f}" for e in top_entries]
                lines.append(f"      INF top-{len(top_entries)}: {' | '.join(top_strs)}")
            # Training top-K debug
            if (
                debug_completion_tokens > 0
                and completion_count <= debug_completion_tokens
                and training_top_k is not None
            ):
                K = training_top_k["k"]
                tk_lps = training_top_k["logprobs"]
                tk_ids = training_top_k["indices"]
                if i * K < len(tk_lps):
                    trn_entries = []
                    for ki in range(min(K, debug_top_logprobs)):
                        idx = i * K + ki
                        if idx < len(tk_lps):
                            trn_entries.append(f"tok={int(tk_ids[idx]):>6d} lp={tk_lps[idx]:.4f}")
                    if trn_entries:
                        lines.append(f"      TRN top-{len(trn_entries)}: {' | '.join(trn_entries)}")
        prev_shown = i

    # Count tokens with large diffs by region
    large_prompt = sum(1 for i in large_diff_indices if per_token_details[i]["region"] == "PROMPT")
    large_completion = sum(1 for i in large_diff_indices if per_token_details[i]["region"] == "COMPLETION")

    logger.info(
        "Logprob comparison [%s]:\n"
        "  prompt_len=%d, total_tokens=%d\n"
        "  training_lps=%d, inference_lps=%d, inf_is_completion_only=%s\n"
        "  ALL:        mean_diff=%.6f  max_diff=%.6f  std=%.6f  (%d tokens)\n"
        "              KL: k1=%.6f  k2=%.6f  k3=%.6f\n"
        "  PROMPT:     mean_diff=%.6f  max_diff=%.6f  std=%.6f  (%d tokens)\n"
        "              KL: k1=%.6f  k2=%.6f  k3=%.6f\n"
        "  COMPLETION: mean_diff=%.6f  max_diff=%.6f  std=%.6f  (%d tokens)\n"
        "              KL: k1=%.6f  k2=%.6f  k3=%.6f\n"
        "  Large diffs (>%.2f): %d total (%d prompt, %d completion)\n"
        "  %s\n%s",
        label,
        prompt_len,
        len(tokens),
        len(training_logprobs),
        len(inference_logprobs),
        inf_is_completion_only,
        metrics["all"]["mean"],
        metrics["all"]["max"],
        metrics["all"]["std"],
        metrics["all"]["count"],
        metrics["all"]["k1"],
        metrics["all"]["k2"],
        metrics["all"]["k3"],
        metrics["prompt"]["mean"],
        metrics["prompt"]["max"],
        metrics["prompt"]["std"],
        metrics["prompt"]["count"],
        metrics["prompt"]["k1"],
        metrics["prompt"]["k2"],
        metrics["prompt"]["k3"],
        metrics["completion"]["mean"],
        metrics["completion"]["max"],
        metrics["completion"]["std"],
        metrics["completion"]["count"],
        metrics["completion"]["k1"],
        metrics["completion"]["k2"],
        metrics["completion"]["k3"],
        LARGE_DIFF_THRESHOLD,
        len(large_diff_indices),
        large_prompt,
        large_completion,
        "-" * 110,
        "\n".join(lines),
    )

    return metrics


def build_r3_routing_matrices(
    routing_matrices: Optional[List[str]], prompt_len: int, model_input_len: int
) -> Optional[List[str]]:
    """Build routing matrices aligned to model_input positions for Router Replay (R3).

    Same logic as train_grpo.py _build_r3_routing_matrices.
    """
    if not routing_matrices:
        return None

    rm = list(routing_matrices)
    if len(rm) == model_input_len:
        return rm

    expected = model_input_len - (prompt_len - 1)
    if len(rm) != expected:
        logger.warning(
            "R3: routing_matrices length (%d) != expected (%d). " "prompt_len=%d, model_input_len=%d.",
            len(rm),
            expected,
            prompt_len,
            model_input_len,
        )
    rm = [""] * (prompt_len - 1) + rm
    return rm[:model_input_len]


# =============================================================================
# Forward-only verification step
# =============================================================================


def do_verify_step(
    ref_client: FiretitanTrainingClient,
    sampled: List[SampledCompletion],
    prompt_idx: int,
    max_seq_len: int = 4096,
    router_replay: bool = False,
    debug_completion_tokens: int = 0,
    debug_top_logprobs: int = 5,
    scoring_pass: bool = False,
    scoring_url: str = "",
    scoring_api_key: str = "",
    scoring_model: str = "",
) -> Dict[str, Any]:
    """Run forward-only verification: compare training vs inference logprobs.

    No backward pass, no optimizer step.

    Returns:
        Dict with per-sample comparison metrics and aggregate summary.
    """
    t_start = time.time()

    # Build datums for batched forward
    fwd_datums: List[tinker.Datum] = []
    valid_indices: List[int] = []
    all_routing: List[Optional[List[str]]] = []

    for i, s in enumerate(sampled):
        ft = s.full_tokens
        if len(ft) < 2:
            continue
        if len(ft) > max_seq_len:
            logger.warning(
                "  Sample %d exceeds max_seq_len (%d > %d), skipping",
                i,
                len(ft),
                max_seq_len,
            )
            continue

        rm = build_r3_routing_matrices(s.routing_matrices, s.prompt_len, len(ft) - 1) if router_replay else None
        all_routing.append(rm)
        valid_indices.append(i)
        fwd_datums.append(
            tinker.Datum(
                model_input=tinker.ModelInput.from_ints(ft[:-1], routing_matrices=rm),
                loss_fn_inputs={"target_tokens": tinker.TensorData(data=ft[1:], dtype="int64", shape=[len(ft) - 1])},
            )
        )

    if not fwd_datums:
        return {"error": "no valid datums", "prompt_idx": prompt_idx}

    # Forward pass on reference trainer (frozen, no gradients)
    t_fwd = time.time()
    ref_future = ref_client.forward(fwd_datums, "cross_entropy")
    rfwd = ref_future.result(timeout=300)
    fwd_elapsed = time.time() - t_fwd

    # Compare logprobs per sample
    per_sample_metrics = []
    for batch_idx, sample_idx in enumerate(valid_indices):
        s = sampled[sample_idx]
        fwd_out = rfwd.loss_fn_outputs[batch_idx]
        training_lps = fwd_out["logprobs"].data
        inference_lps = s.inference_logprobs or []

        # Extract training top-K if available
        training_top_k_data = None
        trn_tk_lps_raw = fwd_out.get("top_k_logprobs")
        trn_tk_ids_raw = fwd_out.get("top_k_indices")
        if trn_tk_lps_raw is not None and trn_tk_ids_raw is not None:
            trn_tk_lps = trn_tk_lps_raw.data if hasattr(trn_tk_lps_raw, "data") else trn_tk_lps_raw.get("data", [])
            trn_tk_ids = trn_tk_ids_raw.data if hasattr(trn_tk_ids_raw, "data") else trn_tk_ids_raw.get("data", [])
            trn_tk_shape = trn_tk_lps_raw.shape if hasattr(trn_tk_lps_raw, "shape") else trn_tk_lps_raw.get("shape")
            if trn_tk_shape and len(trn_tk_shape) == 2:
                K = trn_tk_shape[1]
                training_top_k_data = {"logprobs": trn_tk_lps, "indices": trn_tk_ids, "k": K}

        if not inference_lps:
            logger.warning(
                "  Sample %d has no inference logprobs, skipping comparison",
                sample_idx,
            )
            continue

        metrics = compare_logprobs(
            training_logprobs=training_lps,
            inference_logprobs=inference_lps,
            tokens=s.full_tokens,
            prompt_len=s.prompt_len,
            label=f"prompt-{prompt_idx}/sample-{sample_idx}",
            router_replay=router_replay,
            routing_matrices=all_routing[batch_idx] if batch_idx < len(all_routing) else None,
            logprobs_echoed=getattr(s, "logprobs_echoed", False),
            inference_top_logprobs=getattr(s, "inference_top_logprobs", None),
            training_top_k=training_top_k_data,
            debug_completion_tokens=debug_completion_tokens,
            debug_top_logprobs=debug_top_logprobs,
        )
        per_sample_metrics.append(metrics)

        # Scoring pass: compare training prefill logprobs vs inference prefill logprobs
        if scoring_pass and scoring_url:
            try:
                scoring_lps = get_prefill_logprobs(
                    url=scoring_url,
                    tokens=s.full_tokens,
                    api_key=scoring_api_key,
                    model=scoring_model,
                )
                if scoring_lps:
                    compare_logprobs(
                        training_logprobs=training_lps,
                        inference_logprobs=scoring_lps,
                        tokens=s.full_tokens,
                        prompt_len=s.prompt_len,
                        label=f"SCORING-prompt-{prompt_idx}/sample-{sample_idx}",
                        router_replay=False,
                        routing_matrices=None,
                        logprobs_echoed=True,
                        debug_completion_tokens=debug_completion_tokens,
                        debug_top_logprobs=debug_top_logprobs,
                    )
            except Exception as e:
                logger.warning("  Scoring pass failed for sample %d: %s", sample_idx, e)

    # Aggregate across samples
    def _avg(vals):
        return sum(vals) / len(vals) if vals else 0

    all_mean_diffs = [m["all"]["mean"] for m in per_sample_metrics if m["all"]["count"] > 0]
    all_max_diffs = [m["all"]["max"] for m in per_sample_metrics if m["all"]["count"] > 0]
    comp_mean_diffs = [m["completion"]["mean"] for m in per_sample_metrics if m["completion"]["count"] > 0]
    comp_max_diffs = [m["completion"]["max"] for m in per_sample_metrics if m["completion"]["count"] > 0]
    prompt_mean_diffs = [m["prompt"]["mean"] for m in per_sample_metrics if m["prompt"]["count"] > 0]
    # KL estimators (completion tokens only — most relevant for training)
    comp_k1s = [m["completion"]["k1"] for m in per_sample_metrics if m["completion"]["count"] > 0]
    comp_k2s = [m["completion"]["k2"] for m in per_sample_metrics if m["completion"]["count"] > 0]
    comp_k3s = [m["completion"]["k3"] for m in per_sample_metrics if m["completion"]["count"] > 0]

    summary = {
        "prompt_idx": prompt_idx,
        "num_samples": len(per_sample_metrics),
        "fwd_elapsed_s": fwd_elapsed,
        "total_elapsed_s": time.time() - t_start,
        "avg_all_mean_diff": _avg(all_mean_diffs),
        "max_all_max_diff": max(all_max_diffs) if all_max_diffs else 0,
        "avg_completion_mean_diff": _avg(comp_mean_diffs),
        "max_completion_max_diff": max(comp_max_diffs) if comp_max_diffs else 0,
        "avg_prompt_mean_diff": _avg(prompt_mean_diffs),
        "avg_completion_k1": _avg(comp_k1s),
        "avg_completion_k2": _avg(comp_k2s),
        "avg_completion_k3": _avg(comp_k3s),
    }

    logger.info(
        "Prompt %d summary: %d samples | "
        "all_diff: mean=%.6f max=%.6f | "
        "completion_diff: mean=%.6f max=%.6f | "
        "KL(completion): k1=%.6f k2=%.6f k3=%.6f | "
        "fwd=%.1fs",
        prompt_idx,
        summary["num_samples"],
        summary["avg_all_mean_diff"],
        summary["max_all_max_diff"],
        summary["avg_completion_mean_diff"],
        summary["max_completion_max_diff"],
        summary["avg_completion_k1"],
        summary["avg_completion_k2"],
        summary["avg_completion_k3"],
        fwd_elapsed,
    )

    return summary


# =============================================================================
# CLI
# =============================================================================


def parse_args():
    p = argparse.ArgumentParser(
        description="Verify forward logprobs: training (RLOR reference) vs inference (deployment)"
    )
    p.add_argument("--log-dir", type=str, required=True, help="Directory for output logs")
    p.add_argument("--api-key", default="tml-local")
    p.add_argument("--base-model", required=True)
    p.add_argument("--fireworks-api-key", default=None)
    p.add_argument("--fireworks-account-id", default=None)
    p.add_argument("--fireworks-base-url", default=None)
    p.add_argument("--additional-headers", type=str, default=None)
    p.add_argument("--reference-node-count", type=int, default=1)
    p.add_argument("--hotload-deployment-id", type=str, default=None)
    p.add_argument("--create-deployment", action="store_true")
    p.add_argument("--deployment-shape", type=str, default=None)
    p.add_argument("--skip-shape-validation", action="store_true")
    p.add_argument("--deployment-timeout-s", type=float, default=600)
    p.add_argument("--skip-validations", action="store_true")
    p.add_argument("--custom-image-tag", type=str, default=None)
    p.add_argument("--rlor-timeout-s", type=float, default=15 * 60)
    p.add_argument("--rlor-poll-interval-s", type=float, default=5.0)
    p.add_argument("--region", type=str, default=None)
    p.add_argument("--deployment-region", type=str, default=None)
    p.add_argument("--accelerator-type", type=str, default=None)
    p.add_argument("--deployment-accelerator-type", type=str, default=None)
    p.add_argument("--accelerator-count", type=int, default=None)
    p.add_argument("--hot-load-bucket-type", type=str, default="FW_HOSTED")
    p.add_argument(
        "--deployment-extra-args",
        type=str,
        default=None,
        help="Comma-separated extra args for the deployment (appended to shape args).",
    )
    p.add_argument("--dataset", required=True, help="Path or URL to JSONL dataset")
    p.add_argument("--max-rows", type=int, default=3, help="Number of prompts to verify")
    p.add_argument("--max-seq-len", type=int, default=4096)
    p.add_argument("--group-size", type=int, default=2, help="Completions per prompt")
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument(
        "--debug-completion-tokens",
        type=int,
        default=0,
        help="Print top-K inference logprobs for the first N completion token " "positions (0 = disabled).",
    )
    p.add_argument(
        "--debug-top-logprobs",
        type=int,
        default=5,
        help="How many top logprobs to show per debug position (default 5).",
    )
    p.add_argument(
        "--reasoning-effort",
        type=str,
        default=None,
        help="Reasoning effort for completions (e.g. 'none', 'false').",
    )
    p.add_argument("--lora-rank", type=int, default=0)
    p.add_argument(
        "--trainer-job-id",
        type=str,
        default=None,
        help="Reuse an existing running RLOR trainer job instead of creating a new one.",
    )
    p.add_argument(
        "--reference-extra-args",
        type=str,
        default=None,
        help="Extra args for reference trainer (e.g. '--forward-only --no-compile').",
    )
    p.add_argument(
        "--router-replay",
        action="store_true",
        help="Enable R3: capture routing matrices during sampling and replay in training forward.",
    )
    p.add_argument(
        "--hotload-api-url",
        type=str,
        default="https://api.fireworks.ai",
    )
    p.add_argument(
        "--cleanup-on-exit",
        action="store_true",
        help="Delete RLOR job and deployment on exit.",
    )
    p.add_argument(
        "--tokenizer-path",
        type=str,
        default=None,
        help="Local path or HuggingFace hub name for the tokenizer "
        "(e.g. 'Qwen/Qwen3-1.7B'). Falls back to --base-model if not set.",
    )
    p.add_argument(
        "--no-echo",
        action="store_true",
        help="Use echo=False for sampling (decode-only logprobs, no prompt prefill logprobs).",
    )
    p.add_argument(
        "--prompt-cache-max-len",
        type=int,
        default=None,
        help="Set prompt_cache_max_len for sampling API call. 0 = disable cross-request KV cache.",
    )
    p.add_argument(
        "--scoring-pass",
        action="store_true",
        help="After generation, rescore full sequence via /v1/completions prefill "
        "to get pure prefill logprobs and compare against training.",
    )
    return p.parse_args()


# =============================================================================
# Main
# =============================================================================


def main():
    args = parse_args()

    log_dir = os.path.abspath(args.log_dir)
    os.makedirs(log_dir, exist_ok=True)

    # Add file handler so per-token diagnostics are captured even if tmux scrollback overflows
    fh = logging.FileHandler(os.path.join(log_dir, "verify.log"), mode="w")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logging.getLogger().addHandler(fh)

    logger.info("=== Logprob Verification: Training vs Inference ===")

    fw_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
    fw_account_id = args.fireworks_account_id or os.environ.get("FIREWORKS_ACCOUNT_ID")
    fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai"
    fw_additional_headers = None
    additional_headers_str = args.additional_headers or os.environ.get("FIREWORKS_ADDITIONAL_HEADERS")
    if additional_headers_str:
        try:
            fw_additional_headers = json.loads(additional_headers_str)
        except json.JSONDecodeError:
            logger.warning("Could not parse additional headers: %s", additional_headers_str[:100])

    if not fw_api_key or not fw_account_id:
        raise RuntimeError("Set FIREWORKS_API_KEY and FIREWORKS_ACCOUNT_ID")

    hotload_deployment_id = args.hotload_deployment_id

    # =========================================================================
    # SDK managers
    # =========================================================================
    rlor_mgr = TrainerJobManager(
        api_key=fw_api_key,
        account_id=fw_account_id,
        base_url=fw_base_url,
        additional_headers=fw_additional_headers,
    )
    deploy_mgr = DeploymentManager(
        api_key=fw_api_key,
        account_id=fw_account_id,
        base_url=fw_base_url,
        hotload_api_url=args.hotload_api_url,
        additional_headers=fw_additional_headers,
    )

    # =========================================================================
    # Build reference RLOR job config (forward-only)
    # =========================================================================
    ref_extra = args.reference_extra_args.split() if args.reference_extra_args else []
    if "--forward-only" not in ref_extra:
        ref_extra.append("--forward-only")
    if "--forward-only" in ref_extra and "--no-compile" not in ref_extra:
        if "qwen" in args.base_model.lower():
            ref_extra.append("--no-compile")
    ref_extra = ref_extra or None

    reference_config = TrainerJobConfig(
        base_model=args.base_model,
        lora_rank=args.lora_rank,
        max_context_length=args.max_seq_len,
        learning_rate=1e-5,  # unused for forward-only
        gradient_accumulation_steps=1,
        node_count=args.reference_node_count,
        display_name="verify-logprobs-ref",
        hot_load_deployment_id=None,
        region=args.region,
        skip_validations=args.skip_validations,
        custom_image_tag=args.custom_image_tag,
        extra_args=ref_extra,
        accelerator_type=args.accelerator_type,
        accelerator_count=args.accelerator_count,
    )

    # =========================================================================
    # Cleanup
    # =========================================================================
    reference_endpoint: TrainerServiceEndpoint | None = None
    cleanup_done = False

    def cleanup():
        nonlocal cleanup_done
        if cleanup_done:
            return
        cleanup_done = True
        if args.cleanup_on_exit:
            if reference_endpoint:
                try:
                    rlor_mgr.delete(reference_endpoint.job_id)
                    logger.info("Deleted reference RLOR job: %s", reference_endpoint.job_id)
                except Exception as e:
                    logger.warning("Failed to delete ref job: %s", e)
            if args.create_deployment and hotload_deployment_id:
                try:
                    deploy_mgr.delete(hotload_deployment_id)
                    logger.info("Deleted deployment: %s", hotload_deployment_id)
                except Exception as e:
                    logger.warning("Failed to delete deployment: %s", e)

    atexit.register(cleanup)

    # =========================================================================
    # Launch deployment + reference RLOR job in parallel
    # =========================================================================
    logger.info("\n[1/3] Launching deployment + reference RLOR job in parallel...")

    def _setup_deployment() -> DeploymentInfo | None:
        if args.create_deployment:
            if not hotload_deployment_id:
                raise RuntimeError("--create-deployment requires --hotload-deployment-id")
            dep_config = DeploymentConfig(
                deployment_id=hotload_deployment_id,
                base_model=args.base_model,
                deployment_shape=args.deployment_shape,
                region=args.deployment_region or args.region or "US_VIRGINIA_1",
                min_replica_count=1,  # Prevent scale-to-zero during verification
                accelerator_type=args.deployment_accelerator_type or args.accelerator_type,
                hot_load_bucket_type=args.hot_load_bucket_type,
                skip_shape_validation=args.skip_shape_validation,
            )
            info = deploy_mgr.create_or_get(dep_config)
            if info.state != "READY":
                info = deploy_mgr.wait_for_ready(hotload_deployment_id, timeout_s=args.deployment_timeout_s)
            logger.info("  Deployment ready: %s", info.name)
            return info
        elif hotload_deployment_id:
            return deploy_mgr.get(hotload_deployment_id)
        else:
            return None

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    deployment_future = executor.submit(_setup_deployment)

    if args.trainer_job_id:
        # Reuse an existing running trainer job.
        logger.info("  Reusing existing trainer job: %s", args.trainer_job_id)
        job = rlor_mgr.get(args.trainer_job_id)
        job_state = job.get("state", "")
        endpoint_url = job.get("directRouteHandle", "")
        if job_state != "JOB_STATE_RUNNING":
            raise RuntimeError(
                f"Trainer job {args.trainer_job_id} is in state {job_state}, " f"expected JOB_STATE_RUNNING"
            )
        if not endpoint_url:
            raise RuntimeError(f"Trainer job {args.trainer_job_id} has no directRouteHandle")
        reference_endpoint = TrainerServiceEndpoint(
            job_name=job.get("name", ""),
            job_id=args.trainer_job_id,
            base_url=endpoint_url,
        )
        reference_future = None
    else:
        reference_future = executor.submit(
            lambda: rlor_mgr.create_and_wait(
                reference_config,
                poll_interval_s=args.rlor_poll_interval_s,
                timeout_s=args.rlor_timeout_s,
            ),
        )

    # Wait for deployment first
    dep_info = deployment_future.result()

    inference_url = deploy_mgr.inference_url
    inference_model = dep_info.inference_model if dep_info else args.base_model

    if not args.tokenizer_path:
        raise ValueError(
            "--tokenizer-path is required for client-side tokenization. "
            "Set it to the HuggingFace model name (e.g. 'Qwen/Qwen3-1.7B')."
        )
    logger.info("Loading tokenizer from: %s", args.tokenizer_path)
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.tokenizer_path)

    sampler = DeploymentSampler(
        inference_url=inference_url,
        model=inference_model,
        api_key=fw_api_key,
        tokenizer=tokenizer,
    )

    # =========================================================================
    # Load dataset (while reference job may still be provisioning)
    # =========================================================================
    logger.info("\n[2/3] Loading dataset...")
    dataset = []
    source = args.dataset
    if source.startswith("http://") or source.startswith("https://"):
        import urllib.request

        with urllib.request.urlopen(source) as resp:
            for line in resp:
                line = line.decode("utf-8").strip()
                if line:
                    dataset.append(json.loads(line))
    else:
        with open(source) as f:
            for line in f:
                line = line.strip()
                if line:
                    dataset.append(json.loads(line))
    if args.max_rows:
        dataset = dataset[: args.max_rows]
    logger.info("  Loaded %d examples", len(dataset))

    if not dataset:
        raise RuntimeError("No data loaded!")

    # Warmup deployment — use more retries when reusing an existing deployment
    # since it may have scaled to zero and needs time to rescale.
    warmup_retries = 60 if not args.create_deployment else 30
    deploy_mgr.warmup(inference_model, max_retries=warmup_retries)

    # Wait for reference RLOR job
    if reference_future is not None:
        logger.info("\nWaiting for reference RLOR job...")
        reference_endpoint = reference_future.result()
    executor.shutdown(wait=False)
    logger.info("  Reference ready: %s", reference_endpoint.job_id)

    # =========================================================================
    # Helper: create/reconnect reference client (for retry on job death)
    # =========================================================================
    def _create_ref_client(endpoint: TrainerServiceEndpoint):
        svc = FiretitanServiceClient(base_url=endpoint.base_url, api_key=args.api_key)
        client = svc.create_training_client(base_model=args.base_model, lora_rank=args.lora_rank)
        return client

    def _reconnect_reference() -> Tuple[TrainerServiceEndpoint, FiretitanTrainingClient]:
        """Recreate RLOR job and training client after a failure."""
        nonlocal reference_endpoint
        logger.info("  Reconnecting: creating new reference RLOR job...")
        reference_endpoint = rlor_mgr.create_and_wait(
            reference_config,
            poll_interval_s=args.rlor_poll_interval_s,
            timeout_s=args.rlor_timeout_s,
        )
        logger.info("  Reconnected: %s", reference_endpoint.job_id)
        client = _create_ref_client(reference_endpoint)
        return reference_endpoint, client

    ref_client = _create_ref_client(reference_endpoint)

    # =========================================================================
    # [3/3] Verification loop
    # =========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("[3/3] Logprob verification loop (%d prompts, %d samples each)", len(dataset), args.group_size)
    logger.info("  Router Replay (R3): %s", "ENABLED" if args.router_replay else "DISABLED")
    logger.info("=" * 80)

    all_summaries = []
    MAX_FWD_RETRIES = 3

    for pidx, row in enumerate(dataset):
        messages = row.get("messages", [])
        gt = row.get("ground_truth", "")
        if not messages:
            continue
        input_msgs = [m for m in messages if m.get("role") != "assistant"]
        if not input_msgs:
            continue

        # Qwen3 /no_think
        sampling_msgs = list(input_msgs)
        if args.reasoning_effort and args.reasoning_effort.lower() in ("none", "false"):
            sampling_msgs = [{"role": "system", "content": "/no_think"}] + sampling_msgs

        prompt_preview = input_msgs[-1].get("content", "")[:80]
        logger.info("\n--- Prompt %d/%d: %s... ---", pidx + 1, len(dataset), prompt_preview)

        # Sample from deployment (token-in) with logprobs + echo (always use
        # echo to get all logprobs including prompt positions, not just completion)
        try:
            t_sample = time.time()
            use_echo = not args.no_echo
            sample_kwargs = dict(
                messages=sampling_msgs,
                n=args.group_size,
                max_tokens=args.max_new_tokens,
                temperature=args.temperature,
                logprobs=True,
                echo=use_echo,
                reasoning_effort=args.reasoning_effort,
            )
            if args.prompt_cache_max_len is not None:
                sample_kwargs["prompt_cache_max_len"] = args.prompt_cache_max_len
            if args.debug_completion_tokens > 0:
                sample_kwargs["top_logprobs"] = args.debug_top_logprobs
            if args.router_replay:
                sample_kwargs["include_routing_matrix"] = True
            sampled = sampler.sample_with_tokens(**sample_kwargs)
            sample_elapsed = time.time() - t_sample
        except Exception as e:
            logger.error("  Sampling failed: %s", e)
            continue

        if not sampled:
            logger.warning("  No completions returned")
            continue

        logger.info(
            "  Sampled %d completions in %.1fs (prompt_len=%d, comp_lens=%s, " "full_token_lens=%s, echoed=%s)",
            len(sampled),
            sample_elapsed,
            sampled[0].prompt_len,
            [len(s.full_tokens) - s.prompt_len for s in sampled],
            [len(s.full_tokens) for s in sampled],
            [s.logprobs_echoed for s in sampled],
        )

        # Log first token info (first sample only — prompt is shared)
        s0 = sampled[0]
        first_tok = s0.full_tokens[0] if s0.full_tokens else None
        logger.info(
            "  Server tokenization: first_token=%s, prompt_len=%d",
            first_tok,
            s0.prompt_len,
        )

        # Log inference logprob stats
        for si, s in enumerate(sampled):
            if s.inference_logprobs:
                logger.info(
                    "    sample-%d: inf_lps=%d, full_toks=%d, " "prompt_len=%d, echoed=%s, routing=%s",
                    si,
                    len(s.inference_logprobs),
                    len(s.full_tokens),
                    s.prompt_len,
                    s.logprobs_echoed,
                    len(s.routing_matrices) if s.routing_matrices else "None",
                )
            else:
                logger.warning("    sample-%d: NO inference logprobs!", si)

        # Forward on reference trainer with retry + reconnect
        summary = None
        for attempt in range(1, MAX_FWD_RETRIES + 1):
            try:
                summary = do_verify_step(
                    ref_client=ref_client,
                    sampled=sampled,
                    prompt_idx=pidx,
                    max_seq_len=args.max_seq_len,
                    router_replay=args.router_replay,
                    debug_completion_tokens=args.debug_completion_tokens,
                    debug_top_logprobs=args.debug_top_logprobs,
                    scoring_pass=args.scoring_pass,
                    scoring_url=inference_url if args.scoring_pass else "",
                    scoring_api_key=fw_api_key if args.scoring_pass else "",
                    scoring_model=inference_model if args.scoring_pass else "",
                )
                break
            except Exception as e:
                logger.warning("  Forward failed (attempt %d/%d): %s", attempt, MAX_FWD_RETRIES, e)
                if attempt < MAX_FWD_RETRIES:
                    logger.info("  Waiting 30s then reconnecting reference trainer...")
                    time.sleep(30)
                    try:
                        reference_endpoint, ref_client = _reconnect_reference()
                    except Exception as re:
                        logger.error("  Reconnect failed: %s", re)
                else:
                    logger.error(
                        "  Forward failed after %d retries, skipping prompt %d",
                        MAX_FWD_RETRIES,
                        pidx,
                    )
        if summary:
            all_summaries.append(summary)

    # =========================================================================
    # Final summary
    # =========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 80)

    valid_summaries = [s for s in all_summaries if "error" not in s]
    if valid_summaries:
        n = len(valid_summaries)
        avg_all_diff = sum(s["avg_all_mean_diff"] for s in valid_summaries) / n
        max_all_diff = max(s["max_all_max_diff"] for s in valid_summaries)
        avg_comp_diff = sum(s["avg_completion_mean_diff"] for s in valid_summaries) / n
        max_comp_diff = max(s["max_completion_max_diff"] for s in valid_summaries)
        avg_prompt_diff = sum(s["avg_prompt_mean_diff"] for s in valid_summaries) / n
        avg_comp_k1 = sum(s["avg_completion_k1"] for s in valid_summaries) / n
        avg_comp_k2 = sum(s["avg_completion_k2"] for s in valid_summaries) / n
        avg_comp_k3 = sum(s["avg_completion_k3"] for s in valid_summaries) / n

        logger.info("  Verified %d prompts, %d total samples", n, sum(s["num_samples"] for s in valid_summaries))
        logger.info("  ALL tokens:        avg_mean_diff=%.6f  max_diff=%.6f", avg_all_diff, max_all_diff)
        logger.info("  PROMPT tokens:     avg_mean_diff=%.6f", avg_prompt_diff)
        logger.info("  COMPLETION tokens: avg_mean_diff=%.6f  max_diff=%.6f", avg_comp_diff, max_comp_diff)
        logger.info("  KL divergence (completion): k1=%.6f  k2=%.6f  k3=%.6f", avg_comp_k1, avg_comp_k2, avg_comp_k3)

        if max_all_diff < 0.01:
            logger.info("  RESULT: PASS - logprobs match within 0.01 tolerance")
        elif max_all_diff < 0.1:
            logger.info("  RESULT: MARGINAL - max diff %.6f is between 0.01 and 0.1", max_all_diff)
        else:
            logger.info("  RESULT: FAIL - max diff %.6f exceeds 0.1 tolerance", max_all_diff)

        # Save results to log_dir
        results_path = os.path.join(log_dir, "verify_logprobs_results.json")
        with open(results_path, "w") as f:
            json.dump(
                {
                    "args": vars(args),
                    "summaries": valid_summaries,
                    "final": {
                        "avg_all_mean_diff": avg_all_diff,
                        "max_all_max_diff": max_all_diff,
                        "avg_completion_mean_diff": avg_comp_diff,
                        "max_completion_max_diff": max_comp_diff,
                        "avg_prompt_mean_diff": avg_prompt_diff,
                        "avg_completion_k1": avg_comp_k1,
                        "avg_completion_k2": avg_comp_k2,
                        "avg_completion_k3": avg_comp_k3,
                    },
                },
                f,
                indent=2,
            )
        logger.info("  Results saved to: %s", results_path)
    else:
        logger.error("  No valid comparisons completed!")

    cleanup()


if __name__ == "__main__":
    main()
