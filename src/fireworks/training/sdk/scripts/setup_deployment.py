#!/usr/bin/env python3
"""Create an inference deployment and wait until READY.

Outputs deployment ID and info for downstream test scripts.

Usage:
    python setup_deployment.py \
        --deployment-id verify-ablation-20260216 \
        --deployment-shape accounts/pyroworks-dev/deploymentShapes/rft-kimi-k2p5-r3 \
        --region US_OHIO_1
"""

from __future__ import annotations

import os
import sys
import json
import time
import logging
import argparse

from fireworks.training.sdk import DeploymentConfig, DeploymentManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description="Create and monitor an inference deployment")
    p.add_argument("--deployment-id", required=True, help="Deployment ID to create")
    p.add_argument(
        "--deployment-shape",
        required=True,
        help="Deployment shape (e.g. accounts/pyroworks-dev/deploymentShapes/rft-kimi-k2p5-r3)",
    )
    p.add_argument("--base-model", default="accounts/fireworks/models/kimi-k2p5")
    p.add_argument("--region", default="US_OHIO_1")
    p.add_argument("--timeout-s", type=float, default=1800)
    p.add_argument("--fireworks-api-key", default=None)
    p.add_argument("--fireworks-account-id", default=None)
    p.add_argument("--fireworks-base-url", default=None)
    p.add_argument("--additional-headers", type=str, default=None)
    p.add_argument("--hotload-api-url", default="https://api.fireworks.ai")
    p.add_argument("--output-file", default="deployment_info.json", help="Output JSON file with deployment info")
    p.add_argument("--skip-shape-validation", action="store_true")
    p.add_argument("--accelerator-type", type=str, default=None)
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

    deploy_mgr = DeploymentManager(
        api_key=fw_api_key,
        account_id=fw_account_id,
        base_url=fw_base_url,
        hotload_api_url=args.hotload_api_url,
        additional_headers=fw_additional_headers,
    )

    dep_config = DeploymentConfig(
        deployment_id=args.deployment_id,
        base_model=args.base_model,
        deployment_shape=args.deployment_shape,
        region=args.region,
        min_replica_count=1,
        accelerator_type=args.accelerator_type,
        skip_shape_validation=args.skip_shape_validation,
    )

    logger.info("Creating deployment: %s", args.deployment_id)
    logger.info("  Shape: %s", args.deployment_shape)
    logger.info("  Region: %s", args.region)

    t_start = time.time()
    info = deploy_mgr.create_or_get(dep_config)
    logger.info("  Initial state: %s", info.state)

    if info.state != "READY":
        logger.info("  Waiting for READY (timeout=%ds)...", int(args.timeout_s))
        info = deploy_mgr.wait_for_ready(args.deployment_id, timeout_s=args.timeout_s)

    elapsed = time.time() - t_start
    logger.info("DEPLOYMENT_READY %s (%.0fs)", args.deployment_id, elapsed)

    output = {
        "deployment_id": args.deployment_id,
        "state": info.state,
        "inference_model": info.inference_model,
        "elapsed_s": elapsed,
    }
    with open(args.output_file, "w") as f:
        json.dump(output, f, indent=2)
    logger.info("  Info written to: %s", args.output_file)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("DEPLOYMENT_FAILED: %s", e)
        sys.exit(1)
