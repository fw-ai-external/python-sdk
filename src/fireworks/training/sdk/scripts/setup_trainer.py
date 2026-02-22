#!/usr/bin/env python3
"""Create an RLOR trainer job and wait until RUNNING.

Outputs trainer job ID and endpoint for downstream test scripts.

Usage:
    python setup_trainer.py \
        --display-name ablation-eager \
        --extra-args "--forward-only --no-compile" \
        --custom-image-tag dev-chengxili-r3-v5 \
        --region US_OHIO_1 \
        --node-count 2 \
        --skip-validations
"""

from __future__ import annotations

import os
import sys
import json
import time
import logging
import argparse

from fireworks.training.sdk import TrainerJobConfig, TrainerJobManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description="Create and monitor an RLOR trainer job")
    p.add_argument("--display-name", required=True, help="Display name for the trainer job")
    p.add_argument("--base-model", default="accounts/fireworks/models/kimi-k2p5")
    p.add_argument("--custom-image-tag", default="dev-chengxili-r3-v5")
    p.add_argument("--region", default="US_OHIO_1")
    p.add_argument("--node-count", type=int, default=2)
    p.add_argument(
        "--extra-args",
        type=str,
        default="--forward-only",
        help="Space-separated extra args for trainer (e.g. '--forward-only --no-compile')",
    )
    p.add_argument("--timeout-s", type=float, default=1200)
    p.add_argument("--poll-interval-s", type=float, default=5.0)
    p.add_argument("--skip-validations", action="store_true")
    p.add_argument("--lora-rank", type=int, default=0)
    p.add_argument("--max-seq-len", type=int, default=4096)
    p.add_argument("--accelerator-type", type=str, default=None)
    p.add_argument("--accelerator-count", type=int, default=None)
    p.add_argument("--fireworks-api-key", default=None)
    p.add_argument("--fireworks-account-id", default=None)
    p.add_argument("--fireworks-base-url", default=None)
    p.add_argument("--additional-headers", type=str, default=None)
    p.add_argument("--output-file", default="trainer_info.json", help="Output JSON file with trainer info")
    return p.parse_args()


def main():
    args = parse_args()

    fw_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
    fw_account_id = args.fireworks_account_id or os.environ.get("FIREWORKS_ACCOUNT_ID")
    fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai"
    fw_additional_headers = None
    if args.additional_headers:
        try:
            fw_additional_headers = json.loads(args.additional_headers)
        except json.JSONDecodeError:
            logger.warning("Could not parse additional headers")

    if not fw_api_key or not fw_account_id:
        raise RuntimeError("Set FIREWORKS_API_KEY and FIREWORKS_ACCOUNT_ID")

    rlor_mgr = TrainerJobManager(
        api_key=fw_api_key,
        account_id=fw_account_id,
        base_url=fw_base_url,
        additional_headers=fw_additional_headers,
    )

    extra_args_list = args.extra_args.split() if args.extra_args else []

    config = TrainerJobConfig(
        base_model=args.base_model,
        lora_rank=args.lora_rank,
        max_context_length=args.max_seq_len,
        learning_rate=1e-5,
        gradient_accumulation_steps=1,
        node_count=args.node_count,
        display_name=args.display_name,
        hot_load_deployment_id=None,
        region=args.region,
        skip_validations=args.skip_validations,
        custom_image_tag=args.custom_image_tag,
        extra_args=extra_args_list or None,
        accelerator_type=args.accelerator_type,
        accelerator_count=args.accelerator_count,
    )

    logger.info("Creating trainer job: %s", args.display_name)
    logger.info("  Base model: %s", args.base_model)
    logger.info("  Image tag: %s", args.custom_image_tag)
    logger.info("  Region: %s", args.region)
    logger.info("  Nodes: %d", args.node_count)
    logger.info("  Extra args: %s", extra_args_list)

    t_start = time.time()
    endpoint = rlor_mgr.create_and_wait(
        config,
        poll_interval_s=args.poll_interval_s,
        timeout_s=args.timeout_s,
    )
    elapsed = time.time() - t_start

    logger.info(
        "TRAINER_READY %s %s (%.0fs)",
        endpoint.job_id,
        endpoint.base_url,
        elapsed,
    )

    output = {
        "job_id": endpoint.job_id,
        "job_name": endpoint.job_name,
        "base_url": endpoint.base_url,
        "display_name": args.display_name,
        "extra_args": extra_args_list,
        "elapsed_s": elapsed,
    }
    with open(args.output_file, "w") as f:
        json.dump(output, f, indent=2)
    logger.info("  Info written to: %s", args.output_file)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("TRAINER_FAILED: %s", e)
        sys.exit(1)
