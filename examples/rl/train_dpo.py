#!/usr/bin/env python3
"""
Direct Preference Optimization (DPO) Training via Tinker SDK

This script demonstrates DPO training using the Tinker SDK's forward_backward_custom API.
It's designed as a reference implementation for the Fireworks AI cookbook.

Notes:
- Importing `fireworks.rl` applies the Fireworks compatibility patches to Tinker automatically
  (if Tinker is installed). This script relies on that behavior and does not call patching
  functions directly.
- This script uses REST API calls to create/monitor RLOR trainer jobs and (optionally) a
  hotload-enabled inference deployment, and uses the Tinker SDK to drive training.

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Callable, List

import requests
import tinker
import torch
import torch.nn.functional as F
import urllib3

# Importing fireworks.rl applies the Fireworks compatibility patches to Tinker
# automatically (if Tinker is installed). This adds checkpoint_type support to
# save_weights_for_sampler.
import fireworks.rl  # noqa: F401


# Suppress SSL warnings for direct route requests (self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False


# =============================================================================
# RLOR Trainer Job Creation (REST API)
# =============================================================================


@dataclass
class RlorServiceEndpoint:
    """Info returned after creating an RLOR service-mode trainer job."""

    job_name: str
    job_id: str
    base_url: str


def log(msg: str) -> None:
    print(msg, flush=True)


def warn(msg: str) -> None:
    print(f"[warn] {msg}", flush=True)


def _build_headers(api_key: str, additional_headers: dict | None = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if additional_headers:
        headers.update(additional_headers)
    return headers


def _parse_additional_headers(additional_headers_json: str | None) -> dict | None:
    if not additional_headers_json:
        return None
    try:
        return json.loads(additional_headers_json)
    except json.JSONDecodeError:
        warn(f"Invalid JSON for additional headers: {additional_headers_json}")
        return None


def _create_rlor_job(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    base_model: str,
    lora_rank: int,
    max_context_length: int,
    learning_rate: float,
    gradient_accumulation_steps: int,
    node_count: int,
    display_name: str | None = None,
    hot_load_deployment_id: str | None = None,
    region: str | None = None,
    skip_validations: bool = False,
    custom_image_tag: str | None = None,
) -> dict:
    url = f"{base_url}/v1/accounts/{account_id}/rlorTrainerJobs"
    query_params: list[str] = []
    if hot_load_deployment_id:
        query_params.append(f"deploymentId={hot_load_deployment_id}")
    if skip_validations:
        query_params.append("skipValidations=true")
    if query_params:
        url = f"{url}?{'&'.join(query_params)}"

    headers = _build_headers(api_key, additional_headers)
    payload: dict[str, Any] = {
        "serviceMode": True,
        "keepAlive": False,
        "nodeCount": node_count,
        "dataset": "",
        "trainingConfig": {
            "baseModel": base_model,
            "loraRank": lora_rank,
            "maxContextLength": max_context_length,
            "learningRate": learning_rate,
            "gradientAccumulationSteps": gradient_accumulation_steps,
        },
    }
    if display_name:
        payload["displayName"] = display_name
    if hot_load_deployment_id:
        payload["hotLoadDeploymentId"] = hot_load_deployment_id
    if region:
        payload["trainingConfig"]["region"] = region
    if custom_image_tag:
        payload["trainingConfig"]["customImageTag"] = custom_image_tag

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _get_rlor_job(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    job_id: str,
) -> dict:
    url = f"{base_url}/v1/accounts/{account_id}/rlorTrainerJobs/{job_id}"
    headers = _build_headers(api_key, additional_headers)
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _delete_rlor_job(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    job_id: str,
) -> None:
    url = f"{base_url}/v1/accounts/{account_id}/rlorTrainerJobs/{job_id}"
    headers = _build_headers(api_key, additional_headers)
    resp = requests.delete(url, headers=headers, timeout=30)
    resp.raise_for_status()


def create_rlor_service_job_and_wait(
    *,
    api_key: str,
    account_id: str,
    base_model: str,
    lora_rank: int,
    max_context_length: int,
    learning_rate: float,
    gradient_accumulation_steps: int,
    node_count: int = 1,
    display_name: str | None = None,
    hot_load_deployment_id: str | None = None,
    region: str | None = None,
    skip_validations: bool = False,
    custom_image_tag: str | None = None,
    base_url: str | None = None,
    additional_headers: dict | None = None,
    poll_interval_s: float = 5.0,
    timeout_s: float = 15 * 60,
) -> RlorServiceEndpoint:
    if base_url is None:
        base_url = "https://api.fireworks.ai"

    job = _create_rlor_job(
        api_key=api_key,
        account_id=account_id,
        base_url=base_url,
        additional_headers=additional_headers,
        base_model=base_model,
        lora_rank=lora_rank,
        max_context_length=max_context_length,
        learning_rate=learning_rate,
        gradient_accumulation_steps=gradient_accumulation_steps,
        node_count=node_count,
        display_name=display_name,
        hot_load_deployment_id=hot_load_deployment_id,
        region=region,
        skip_validations=skip_validations,
        custom_image_tag=custom_image_tag,
    )

    job_name = job.get("name", "")
    job_id = job_name.split("/")[-1] if "/" in job_name else job_name
    log(f"Created RLOR job: {job_id}")

    start = time.time()
    while time.time() - start < timeout_s:
        job = _get_rlor_job(api_key, account_id, base_url, additional_headers, job_id)
        state = job.get("state", "")
        endpoint = job.get("directRouteHandle", "")

        elapsed = int(time.time() - start)
        log(
            f"  [{elapsed}s] State: {state}, Endpoint: {endpoint[:50]}..."
            if endpoint
            else f"  [{elapsed}s] State: {state}"
        )

        if state == "JOB_STATE_FAILED":
            msg = job.get("status", {}).get("message", "unknown")
            raise RuntimeError(f"RLOR job failed: {msg}")

        if state == "JOB_STATE_RUNNING" and endpoint:
            if endpoint.startswith("http://"):
                endpoint = "https://" + endpoint[7:]
            elif not endpoint.startswith("https://"):
                endpoint = "https://" + endpoint
            endpoint = endpoint.rstrip("/")
            return RlorServiceEndpoint(job_name=job_name, job_id=job_id, base_url=endpoint)

        time.sleep(poll_interval_s)

    raise TimeoutError(f"RLOR job did not become ready within {timeout_s}s")


# =============================================================================
# DPO loss fn for forward_backward_custom
# =============================================================================


def make_dpo_loss_fn(
    ref_chosen_logprobs: List[float],
    ref_rejected_logprobs: List[float],
    response_start_idx: int,
    beta: float,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], tuple[torch.Tensor, dict[str, float]]]:
    ref_chosen_tensor = torch.tensor(ref_chosen_logprobs, dtype=torch.float32)
    ref_rejected_tensor = torch.tensor(ref_rejected_logprobs, dtype=torch.float32)

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> tuple[torch.Tensor, dict[str, float]]:
        assert len(logprobs_list) == 2, f"Expected 2 sequences, got {len(logprobs_list)}"

        pi_chosen_tensor = logprobs_list[0]
        pi_rejected_tensor = logprobs_list[1]

        pi_chosen_sum = pi_chosen_tensor[response_start_idx:].sum()
        pi_rejected_sum = pi_rejected_tensor[response_start_idx:].sum()
        ref_chosen_sum = ref_chosen_tensor[response_start_idx:].sum()
        ref_rejected_sum = ref_rejected_tensor[response_start_idx:].sum()

        margin = (pi_chosen_sum - ref_chosen_sum) - (pi_rejected_sum - ref_rejected_sum)
        dpo_loss = -F.logsigmoid(beta * margin)

        with torch.no_grad():
            margin_val = margin.item()
            loss_val = dpo_loss.item()
            accuracy = 1.0 if margin_val > 0 else 0.0
            chosen_reward = beta * (pi_chosen_sum.item() - ref_chosen_sum.item())
            rejected_reward = beta * (pi_rejected_sum.item() - ref_rejected_sum.item())

        metrics = {
            "dpo_loss": loss_val,
            "margin": margin_val,
            "accuracy": accuracy,
            "chosen_reward": chosen_reward,
            "rejected_reward": rejected_reward,
        }

        return dpo_loss, metrics

    return loss_fn


# =============================================================================
# Minimal dataset loader (JSONL) expected to match train_dpo_tinker_sdk.py
# =============================================================================


def load_preference_jsonl(path: str, max_rows: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if len(rows) >= max_rows:
                break
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DPO Training via Tinker SDK (Fireworks cookbook)")
    parser.add_argument("--api-key", default="tml-local", help="API key for the trainer's Tinker endpoint")
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--dataset", required=True, help="Path to preference JSONL")
    parser.add_argument("--max-rows", type=int, default=1000)

    parser.add_argument("--fireworks-api-key", default=None)
    parser.add_argument("--fireworks-account-id", default=None)
    parser.add_argument("--fireworks-base-url", default=None)
    parser.add_argument("--additional-headers", type=str, default=None)

    parser.add_argument("--rlor-node-count", type=int, default=1)
    parser.add_argument("--rlor-display-name", type=str, default=None)
    parser.add_argument("--region", type=str, default=None)
    parser.add_argument("--skip-validations", action="store_true")
    parser.add_argument("--custom-image-tag", type=str, default=None)
    parser.add_argument("--rlor-timeout-s", type=float, default=15 * 60)
    parser.add_argument("--rlor-poll-interval-s", type=float, default=5.0)

    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--beta", type=float, default=0.1)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=4)

    parser.add_argument("--wandb-entity", type=str, default=None)
    parser.add_argument("--wandb-project", type=str, default="dpo-tinker")
    parser.add_argument("--wandb-run-name", type=str, default=None)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    use_wandb = WANDB_AVAILABLE and args.wandb_entity is not None
    if use_wandb:
        wandb.init(
            entity=args.wandb_entity,
            project=args.wandb_project,
            name=args.wandb_run_name,
            config={
                "beta": args.beta,
                "lr": args.lr,
                "epochs": args.epochs,
                "grad_accum": args.grad_accum,
                "max_rows": args.max_rows,
            },
        )

    fw_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
    fw_account_id = args.fireworks_account_id or os.environ.get("FIREWORKS_ACCOUNT_ID")
    fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai"
    fw_additional_headers = _parse_additional_headers(
        args.additional_headers or os.environ.get("FIREWORKS_ADDITIONAL_HEADERS")
    )
    if not fw_api_key or not fw_account_id:
        raise RuntimeError("Set FIREWORKS_API_KEY and FIREWORKS_ACCOUNT_ID (or pass --fireworks-*)")

    log("Creating RLOR trainer job (policy)...")
    endpoint = create_rlor_service_job_and_wait(
        api_key=fw_api_key,
        account_id=fw_account_id,
        base_url=fw_base_url,
        additional_headers=fw_additional_headers,
        base_model=args.base_model,
        lora_rank=0,
        max_context_length=4096,
        learning_rate=args.lr,
        gradient_accumulation_steps=args.grad_accum,
        node_count=args.rlor_node_count,
        display_name=args.rlor_display_name or "dpo-policy",
        hot_load_deployment_id=None,
        region=args.region,
        skip_validations=args.skip_validations,
        custom_image_tag=args.custom_image_tag,
        poll_interval_s=args.rlor_poll_interval_s,
        timeout_s=args.rlor_timeout_s,
    )
    log(f"  Trainer ready: {endpoint.base_url}")

    service = tinker.ServiceClient(base_url=endpoint.base_url, api_key=args.api_key)
    training_client = service.create_lora_training_client(base_model=args.base_model, rank=0)

    data_rows = load_preference_jsonl(args.dataset, args.max_rows)
    if not data_rows:
        raise RuntimeError("No data loaded")

    # Expected JSONL format: each row has chosen_tokens, rejected_tokens, prompt_len
    # Tokens should include prompt + response.
    valid = [r for r in data_rows if r.get("chosen_tokens") and r.get("rejected_tokens")]
    if not valid:
        raise RuntimeError("No valid preference pairs (expected chosen_tokens/rejected_tokens)")

    # Cache initial reference logprobs from the initial policy (policy==ref at step 0)
    ref_cache: dict[int, dict[str, Any]] = {}
    for i, row in enumerate(valid):
        chosen_tokens = list(row["chosen_tokens"])
        rejected_tokens = list(row["rejected_tokens"])
        prompt_len = int(row.get("prompt_len", 0) or 0)
        response_start_idx = max(0, prompt_len - 1)

        chosen_datum = tinker.Datum(
            model_input=tinker.ModelInput.from_ints(chosen_tokens[:-1]),
            loss_fn_inputs={
                "target_tokens": tinker.TensorData(
                    data=chosen_tokens[1:],
                    dtype="int64",
                    shape=[len(chosen_tokens) - 1],
                ),
            },
        )
        rejected_datum = tinker.Datum(
            model_input=tinker.ModelInput.from_ints(rejected_tokens[:-1]),
            loss_fn_inputs={
                "target_tokens": tinker.TensorData(
                    data=rejected_tokens[1:],
                    dtype="int64",
                    shape=[len(rejected_tokens) - 1],
                ),
            },
        )
        fwd = training_client.forward([chosen_datum, rejected_datum], "cross_entropy").result()
        ref_cache[i] = {
            "prompt_len": prompt_len,
            "response_start_idx": response_start_idx,
            "ref_chosen": list(fwd.loss_fn_outputs[0]["logprobs"].data),
            "ref_rejected": list(fwd.loss_fn_outputs[1]["logprobs"].data),
            "chosen_tokens": chosen_tokens,
            "rejected_tokens": rejected_tokens,
        }

    log(f"Cached reference logprobs for {len(ref_cache)} pairs")

    step = 0
    accum = 0
    epoch_metrics = {"dpo_loss": 0.0, "margin": 0.0, "accuracy": 0.0}

    for _epoch in range(args.epochs):
        for i in range(len(ref_cache)):
            cached = ref_cache[i]
            chosen_tokens = cached["chosen_tokens"]
            rejected_tokens = cached["rejected_tokens"]
            response_start_idx = cached["response_start_idx"]

            chosen_datum = tinker.Datum(
                model_input=tinker.ModelInput.from_ints(chosen_tokens[:-1]),
                loss_fn_inputs={
                    "target_tokens": tinker.TensorData(
                        data=chosen_tokens[1:],
                        dtype="int64",
                        shape=[len(chosen_tokens) - 1],
                    ),
                },
            )
            rejected_datum = tinker.Datum(
                model_input=tinker.ModelInput.from_ints(rejected_tokens[:-1]),
                loss_fn_inputs={
                    "target_tokens": tinker.TensorData(
                        data=rejected_tokens[1:],
                        dtype="int64",
                        shape=[len(rejected_tokens) - 1],
                    ),
                },
            )

            loss_fn = make_dpo_loss_fn(
                ref_chosen_logprobs=cached["ref_chosen"],
                ref_rejected_logprobs=cached["ref_rejected"],
                response_start_idx=response_start_idx,
                beta=args.beta,
            )

            result = training_client.forward_backward_custom([chosen_datum, rejected_datum], loss_fn).result()
            m = result.metrics
            epoch_metrics["dpo_loss"] += float(m.get("dpo_loss", 0.0))
            epoch_metrics["margin"] += float(m.get("margin", 0.0))
            epoch_metrics["accuracy"] += float(m.get("accuracy", 0.0))

            accum += 1
            if accum >= args.grad_accum:
                training_client.optim_step(
                    tinker.AdamParams(learning_rate=args.lr, beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.01)
                ).result()
                step += 1
                avg_loss = epoch_metrics["dpo_loss"] / accum
                avg_margin = epoch_metrics["margin"] / accum
                avg_acc = epoch_metrics["accuracy"] / accum
                log(f"Step {step} | Loss: {avg_loss:.4f} | Margin: {avg_margin:+.4f} | Acc: {avg_acc:.2%}")
                if use_wandb:
                    wandb.log(
                        {
                            "train/dpo_loss": avg_loss,
                            "train/margin": avg_margin,
                            "train/accuracy": avg_acc,
                            "train/step": step,
                        },
                        step=step,
                    )
                epoch_metrics = {"dpo_loss": 0.0, "margin": 0.0, "accuracy": 0.0}
                accum = 0

    if use_wandb:
        wandb.finish()


if __name__ == "__main__":
    main()


