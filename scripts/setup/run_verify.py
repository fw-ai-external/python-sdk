#!/usr/bin/env python3
"""Orchestrate 3 ablation test runs using pre-created resources.

Reads deployment and trainer info from JSON files or CLI args, validates
that all resources are alive, then runs verify_logprobs.py for each test
configuration.

Usage:
    python run_verify.py \
        --deployment-id verify-ablation-20260216 \
        --compiled-trainer-id <id> \
        --eager-trainer-id <id> \
        --output-dir ./ablation_results
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description="Run 3 ablation tests with pre-created resources")

    # Resource IDs
    p.add_argument("--deployment-id", required=True, help="Pre-created deployment ID")
    p.add_argument("--compiled-trainer-id", required=True, help="Pre-created compiled trainer job ID")
    p.add_argument("--eager-trainer-id", required=True, help="Pre-created eager trainer job ID")

    # Output
    p.add_argument(
        "--output-dir", default=None, help="Base directory for results (default: ablation_results_<timestamp>)"
    )

    # Debug
    p.add_argument("--debug-completion-tokens", type=int, default=20)
    p.add_argument("--debug-top-logprobs", type=int, default=5)

    # Shared verify args
    p.add_argument("--base-model", default="accounts/fireworks/models/kimi-k2p5")
    p.add_argument("--dataset", default="data/ifbench_sample.jsonl")
    p.add_argument("--max-rows", type=int, default=3)
    p.add_argument("--max-new-tokens", type=int, default=2000)
    p.add_argument("--max-seq-len", type=int, default=4096)
    p.add_argument("--reasoning-effort", default="false")
    p.add_argument("--tokenizer-path", default="moonshotai/Kimi-K2-Instruct")
    p.add_argument("--lora-rank", type=int, default=0)
    p.add_argument("--reference-node-count", type=int, default=2)
    p.add_argument("--custom-image-tag", default="dev-chengxili-r3-v5")
    p.add_argument("--region", default="US_OHIO_1")

    # Auth
    p.add_argument("--fireworks-api-key", default=None)
    p.add_argument("--fireworks-account-id", default=None)
    p.add_argument("--fireworks-base-url", default=None)
    p.add_argument("--additional-headers", type=str, default=None)
    p.add_argument("--hotload-api-url", default="https://api.fireworks.ai")

    # Execution
    p.add_argument(
        "--test",
        type=str,
        default=None,
        help="Run only a specific test: 'eager_current', 'eager_greedy', or 'compiled_greedy'",
    )
    return p.parse_args()


# =========================================================================
# Test definitions
# =========================================================================

TESTS = [
    {
        "name": "eager_current",
        "description": "Eager (--no-compile) + Current sampling (temp=1.0)",
        "trainer_key": "eager",
        "temperature": 1.0,
        "group_size": 2,
        "reference_extra_args": "--forward-only --no-compile",
        "extra_verify_args": [],
    },
    {
        "name": "eager_greedy",
        "description": "Eager (--no-compile) + Greedy (temp=0)",
        "trainer_key": "eager",
        "temperature": 0,
        "group_size": 1,
        "reference_extra_args": "--forward-only --no-compile",
        "extra_verify_args": [],
    },
    {
        "name": "compiled_greedy",
        "description": "Compiled (torch.compile) + Greedy (temp=0)",
        "trainer_key": "compiled",
        "temperature": 0,
        "group_size": 1,
        "reference_extra_args": "--forward-only",
        "extra_verify_args": [],
    },
    {
        "name": "decode_only",
        "description": "Decode-only logprobs (no echo), compiled + greedy",
        "trainer_key": "compiled",
        "temperature": 0,
        "group_size": 1,
        "reference_extra_args": "--forward-only",
        "extra_verify_args": ["--no-echo"],
    },
    {
        "name": "scoring_pass",
        "description": "Scoring pass (prefill-vs-prefill), compiled + greedy",
        "trainer_key": "compiled",
        "temperature": 0,
        "group_size": 1,
        "reference_extra_args": "--forward-only",
        "extra_verify_args": ["--scoring-pass"],
    },
    {
        "name": "kv_cache_zero",
        "description": "KV cache len=0, compiled + greedy",
        "trainer_key": "compiled",
        "temperature": 0,
        "group_size": 1,
        "reference_extra_args": "--forward-only",
        "extra_verify_args": ["--prompt-cache-max-len", "0"],
    },
]


def build_verify_command(
    test: dict,
    args: argparse.Namespace,
    trainer_id: str,
    log_dir: str,
) -> list[str]:
    """Build the verify_logprobs.py command for one test."""
    cmd = [
        sys.executable,
        "verify_logprobs.py",
        "--log-dir",
        log_dir,
        "--base-model",
        args.base_model,
        "--dataset",
        args.dataset,
        "--max-rows",
        str(args.max_rows),
        "--max-new-tokens",
        str(args.max_new_tokens),
        "--max-seq-len",
        str(args.max_seq_len),
        "--group-size",
        str(test["group_size"]),
        "--temperature",
        str(test["temperature"]),
        "--reasoning-effort",
        args.reasoning_effort,
        "--tokenizer-path",
        args.tokenizer_path,
        "--lora-rank",
        str(args.lora_rank),
        "--router-replay",
        "--hotload-deployment-id",
        args.deployment_id,
        "--trainer-job-id",
        trainer_id,
        f"--reference-extra-args={test['reference_extra_args']}",
        "--debug-completion-tokens",
        str(args.debug_completion_tokens),
        "--debug-top-logprobs",
        str(args.debug_top_logprobs),
        "--skip-validations",
        "--custom-image-tag",
        args.custom_image_tag,
        "--region",
        args.region,
        "--reference-node-count",
        str(args.reference_node_count),
    ]

    fw_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY", "")
    fw_account_id = args.fireworks_account_id or os.environ.get("FIREWORKS_ACCOUNT_ID", "")
    fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai")

    if fw_api_key:
        cmd.extend(["--fireworks-api-key", fw_api_key])
    if fw_account_id:
        cmd.extend(["--fireworks-account-id", fw_account_id])
    if fw_base_url:
        cmd.extend(["--fireworks-base-url", fw_base_url])
    if args.additional_headers:
        cmd.extend(["--additional-headers", args.additional_headers])
    if args.hotload_api_url:
        cmd.extend(["--hotload-api-url", args.hotload_api_url])

    extra = test.get("extra_verify_args", [])
    if extra:
        cmd.extend(extra)

    return cmd


def run_test(test: dict, args: argparse.Namespace, output_dir: str) -> dict:
    """Run a single ablation test and return results."""
    trainer_id = args.eager_trainer_id if test["trainer_key"] == "eager" else args.compiled_trainer_id
    log_dir = os.path.join(output_dir, test["name"])
    os.makedirs(log_dir, exist_ok=True)

    cmd = build_verify_command(test, args, trainer_id, log_dir)

    logger.info("=" * 80)
    logger.info("TEST: %s", test["description"])
    logger.info("  Trainer: %s (%s)", trainer_id, test["trainer_key"])
    logger.info("  Temperature: %s", test["temperature"])
    logger.info("  Group size: %s", test["group_size"])
    logger.info("  Log dir: %s", log_dir)
    logger.info("=" * 80)

    t_start = time.time()
    result = subprocess.run(cmd, capture_output=False)
    elapsed = time.time() - t_start

    results_file = os.path.join(log_dir, "verify_logprobs_results.json")
    results = {}
    if os.path.exists(results_file):
        with open(results_file) as f:
            results = json.load(f)

    status = "PASS" if result.returncode == 0 else "FAIL"
    logger.info("  %s: %s (%.0fs, exit=%d)", test["name"], status, elapsed, result.returncode)

    return {
        "name": test["name"],
        "description": test["description"],
        "status": status,
        "elapsed_s": elapsed,
        "returncode": result.returncode,
        "results": results.get("final", {}),
    }


def main():
    args = parse_args()

    output_dir = args.output_dir or f"ablation_results_{time.strftime('%Y%m%d%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)

    logger.info("=== Ablation Test Runner ===")
    logger.info("  Deployment: %s", args.deployment_id)
    logger.info("  Compiled trainer: %s", args.compiled_trainer_id)
    logger.info("  Eager trainer: %s", args.eager_trainer_id)
    logger.info("  Output dir: %s", output_dir)

    tests_to_run = TESTS
    if args.test:
        tests_to_run = [t for t in TESTS if t["name"] == args.test]
        if not tests_to_run:
            logger.error("Unknown test: %s. Choose from: %s", args.test, ", ".join(t["name"] for t in TESTS))
            sys.exit(1)

    all_results = []
    for test in tests_to_run:
        result = run_test(test, args, output_dir)
        all_results.append(result)

    # Print summary table
    logger.info("\n" + "=" * 80)
    logger.info("ABLATION SUMMARY")
    logger.info("=" * 80)
    logger.info(
        "%-20s %-8s %-12s %-12s %-12s %-12s", "Test", "Status", "Comp Diff", "Prompt Diff", "Max Diff", "KL k1"
    )
    logger.info("-" * 80)
    for r in all_results:
        final = r["results"]
        logger.info(
            "%-20s %-8s %-12s %-12s %-12s %-12s",
            r["name"],
            r["status"],
            (
                f"{final.get('avg_completion_mean_diff', 'N/A'):.6f}"
                if isinstance(final.get("avg_completion_mean_diff"), (int, float))
                else "N/A"
            ),
            (
                f"{final.get('avg_prompt_mean_diff', 'N/A'):.6f}"
                if isinstance(final.get("avg_prompt_mean_diff"), (int, float))
                else "N/A"
            ),
            (
                f"{final.get('max_all_max_diff', 'N/A'):.6f}"
                if isinstance(final.get("max_all_max_diff"), (int, float))
                else "N/A"
            ),
            (
                f"{final.get('avg_completion_k1', 'N/A'):.6f}"
                if isinstance(final.get("avg_completion_k1"), (int, float))
                else "N/A"
            ),
        )

    # Save summary
    summary_path = os.path.join(output_dir, "ablation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(all_results, f, indent=2)
    logger.info("\nSummary saved to: %s", summary_path)


if __name__ == "__main__":
    main()
