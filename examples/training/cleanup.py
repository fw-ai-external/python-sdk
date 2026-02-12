#!/usr/bin/env python3
"""
Manual cleanup utility for training resources.

Use this script when training exits unexpectedly (e.g., process kill, machine
shutdown, network disconnect) and automatic atexit cleanup did not run.

Dry-run by default:
    python examples/training/cleanup.py \
        --rlor-job-id "<policy_job_id>" \
        --rlor-job-id "<reference_job_id>" \
        --deployment-id "<deployment_id>"

Actually delete resources:
    python examples/training/cleanup.py \
        --rlor-job-id "<policy_job_id>" \
        --rlor-job-id "<reference_job_id>" \
        --deployment-id "<deployment_id>" \
        --delete
"""

from __future__ import annotations

import os
import argparse
from collections.abc import Sequence

from shared import log, warn, delete_rlor_job, delete_deployment, parse_additional_headers


def _unique(values: Sequence[str]) -> list[str]:
    """Return values in stable order without duplicates."""
    return list(dict.fromkeys(v for v in values if v))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cleanup RLOR trainer jobs and deployments from training examples",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--fireworks-api-key",
        default=os.environ.get("FIREWORKS_API_KEY"),
        help="Fireworks API key. Defaults to FIREWORKS_API_KEY env var.",
    )
    parser.add_argument(
        "--fireworks-account-id",
        default=os.environ.get("FIREWORKS_ACCOUNT_ID"),
        help="Fireworks account ID. Defaults to FIREWORKS_ACCOUNT_ID env var.",
    )
    parser.add_argument(
        "--fireworks-base-url",
        default=os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai"),
        help="Fireworks API base URL.",
    )
    parser.add_argument(
        "--additional-headers",
        default=os.environ.get("FIREWORKS_ADDITIONAL_HEADERS"),
        help='Optional JSON headers, e.g. \'{"X-Custom-Header":"value"}\'.',
    )

    parser.add_argument(
        "--rlor-job-id",
        action="append",
        default=[],
        help="RLOR trainer job ID to delete. Pass multiple times for policy/reference jobs.",
    )
    parser.add_argument(
        "--deployment-id",
        action="append",
        default=[],
        help="Deployment ID to delete. Pass multiple times if needed.",
    )

    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete resources. Without this flag, script runs in dry-run mode.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    rlor_job_ids = _unique(args.rlor_job_id)
    deployment_ids = _unique(args.deployment_id)
    additional_headers = parse_additional_headers(args.additional_headers)

    if not rlor_job_ids and not deployment_ids:
        raise RuntimeError("Specify at least one --rlor-job-id or --deployment-id.")

    log("Planned cleanup:")
    for job_id in rlor_job_ids:
        log(f"  RLOR job: {job_id}")
    for deployment_id in deployment_ids:
        log(f"  Deployment: {deployment_id}")

    if not args.delete:
        log("Dry run only. Re-run with --delete to actually remove resources.")
        return

    if not args.fireworks_api_key or not args.fireworks_account_id:
        raise RuntimeError(
            "Deleting resources requires FIREWORKS_API_KEY and FIREWORKS_ACCOUNT_ID "
            "(or pass --fireworks-api-key / --fireworks-account-id)."
        )

    failures = 0

    for job_id in rlor_job_ids:
        try:
            log(f"Deleting RLOR job: {job_id}")
            delete_rlor_job(
                api_key=args.fireworks_api_key,
                account_id=args.fireworks_account_id,
                base_url=args.fireworks_base_url,
                additional_headers=additional_headers,
                job_id=job_id,
            )
            log(f"  Deleted RLOR job: {job_id}")
        except Exception as exc:
            failures += 1
            warn(f"  Failed to delete RLOR job {job_id}: {exc}")

    for deployment_id in deployment_ids:
        try:
            log(f"Deleting deployment: {deployment_id}")
            delete_deployment(
                api_key=args.fireworks_api_key,
                account_id=args.fireworks_account_id,
                base_url=args.fireworks_base_url,
                additional_headers=additional_headers,
                deployment_id=deployment_id,
            )
            log(f"  Deleted deployment: {deployment_id}")
        except Exception as exc:
            failures += 1
            warn(f"  Failed to delete deployment {deployment_id}: {exc}")

    if failures > 0:
        raise RuntimeError(f"Cleanup completed with {failures} failure(s).")

    log("Cleanup complete.")


if __name__ == "__main__":
    main()
