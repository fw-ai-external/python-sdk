#!/usr/bin/env python3
"""Standalone script to test DCP checkpoint loading on a fresh RLOR trainer.

Creates a new trainer job, resolves the cross-job DCP checkpoint path from
a previous job, and attempts to load it. This isolates the resume/load step
from the full DPO resume E2E test.

Usage:
    FIREWORKS_API_KEY=fw_3ZkNBrXgLw1EJ4y77kqSMBU5 python scripts/test_dcp_resume_load.py \
        --source-job-id gtsjw9vu4rfnqall \
        --checkpoint-name step-4
"""

from __future__ import annotations

import argparse
import logging
import os
import time

from fireworks.training.sdk.trainer import TrainerJobConfig, TrainerJobManager
from fireworks.training.sdk.client import FiretitanServiceClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Test DCP checkpoint load in isolation")
    parser.add_argument("--source-job-id", required=True, help="Phase 1 job ID that saved the DCP checkpoint")
    parser.add_argument("--checkpoint-name", default="step-4", help="DCP checkpoint name (e.g. step-4)")
    parser.add_argument("--base-model", default="accounts/fireworks/models/qwen3-30b-a3b")
    parser.add_argument("--region", default="US_OHIO_1")
    parser.add_argument("--load-timeout", type=int, default=1800, help="Timeout in seconds for checkpoint load")
    args = parser.parse_args()

    api_key = os.environ["FIREWORKS_API_KEY"]
    account = os.environ.get("FIREWORKS_ACCOUNT_ID", "pyroworks-dev")
    base_url = os.environ.get("FIREWORKS_BASE_URL", "https://dev.api.fireworks.ai")

    rlor_mgr = TrainerJobManager(api_key=api_key, account_id=account, base_url=base_url)

    logger.info("Creating trainer job for checkpoint load test...")
    endpoint = rlor_mgr.create_and_wait(
        TrainerJobConfig(
            base_model=args.base_model,
            max_context_length=4096,
            learning_rate=1e-5,
            gradient_accumulation_steps=2,
            node_count=1,
            display_name="dcp-load-test",
            region=args.region,
            skip_validations=True,
        )
    )
    job_id = endpoint.job_id
    logger.info("Trainer job ready: %s (url: %s)", job_id, endpoint.base_url)

    svc = FiretitanServiceClient(base_url=endpoint.base_url, api_key="tml-local")
    client = svc.create_training_client(base_model=args.base_model, lora_rank=0)

    logger.info("Resolving checkpoint path: name=%s, source_job_id=%s", args.checkpoint_name, args.source_job_id)
    checkpoint_ref = client.resolve_checkpoint_path(
        args.checkpoint_name,
        source_job_id=args.source_job_id,
    )
    logger.info("Resolved checkpoint path: %s", checkpoint_ref)

    logger.info("Loading checkpoint (timeout=%ds)...", args.load_timeout)
    t0 = time.time()
    try:
        client.load_state_with_optimizer(checkpoint_ref).result(timeout=args.load_timeout)
        elapsed = time.time() - t0
        logger.info("SUCCESS: Checkpoint loaded in %.1fs", elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        logger.error("FAILED after %.1fs: %s", elapsed, e)
        raise
    finally:
        logger.info("Cleaning up trainer job %s...", job_id)
        try:
            rlor_mgr.delete(job_id)
            logger.info("Job %s deleted.", job_id)
        except Exception as cleanup_err:
            logger.warning("Cleanup failed: %s", cleanup_err)


if __name__ == "__main__":
    main()
