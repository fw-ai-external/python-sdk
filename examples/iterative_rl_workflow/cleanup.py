"""
Cleanup script for GSM8K RLOR trainer jobs.

This script finds and deletes all reinforcement fine-tuning trainer jobs
that match the trainer job ID prefix used by train.py.

Example usage:
    python cleanup.py           # Dry run - shows what would be deleted
    python cleanup.py --delete  # Actually delete the jobs
"""

from __future__ import annotations

import asyncio
import argparse
import logging

from dotenv import load_dotenv
from fireworks import AsyncFireworks
import fireworks

from train import TRAINER_JOB_ID_PREFIX

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Suppress HTTP request logs from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Cleanup GSM8K RLOR trainer jobs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete the jobs (default is dry run)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default=TRAINER_JOB_ID_PREFIX,
        help="Trainer job ID prefix to match",
    )
    return parser.parse_args()


async def cleanup_trainer_jobs(prefix: str, delete: bool) -> None:
    """Find and optionally delete trainer jobs matching the prefix."""
    client = AsyncFireworks()

    try:
        logger.info(f"Searching for trainer jobs with prefix: {prefix}")

        # List all reinforcement fine-tuning jobs
        jobs_to_delete: list[str] = []

        async for job in client.reinforcement_fine_tuning_steps.list():
            # Extract job ID from the name (format: accounts/{account}/rlorTrainerJobs/{job_id})
            if job.name:
                job_id = job.name.split("/")[-1]
                if job_id.startswith(prefix):
                    jobs_to_delete.append(job_id)
                    logger.info(f"Found matching job: {job_id} (state: {job.state})")

        if not jobs_to_delete:
            logger.info("No matching trainer jobs found.")
            return

        logger.info(f"Found {len(jobs_to_delete)} matching trainer job(s)")

        if not delete:
            logger.info("Dry run mode - no jobs will be deleted. Use --delete to actually delete.")
            return

        # Delete the jobs
        for job_id in jobs_to_delete:
            try:
                await client.reinforcement_fine_tuning_steps.delete(job_id)
                logger.info(f"Deleted trainer job: {job_id}")
            except fireworks.NotFoundError:
                logger.warning(f"Job {job_id} not found (may have been already deleted)")
            except Exception as e:
                logger.error(f"Failed to delete job {job_id}: {e}")

        logger.info(f"Cleanup complete. Deleted {len(jobs_to_delete)} job(s).")

    finally:
        await client.close()


async def main() -> None:
    """Main entry point."""
    args = parse_args()
    await cleanup_trainer_jobs(prefix=args.prefix, delete=args.delete)


if __name__ == "__main__":
    asyncio.run(main())

