"""
GSM8K RLOR Training Example using Fireworks SDK.

This script demonstrates an iterative reinforcement learning workflow using GSM8K:
1. Load prompts from the GSM8K dataset (without assistant responses)
2. Generate rollouts using a base model
3. Score outputs by comparing with ground truth answers
4. Run reinforcement fine-tuning steps
5. Repeat for multiple epochs
"""

from __future__ import annotations

import os
import re
import json
import time
import asyncio
import logging
import argparse
from typing import Any
from collections import defaultdict

import fsspec
from dotenv import load_dotenv

from fireworks import AsyncFireworks
from fireworks._compat import model_dump
from fireworks.types.shared_params.training_config import TrainingConfig

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

# Configuration - set these environment variables before running
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "")
BASE_URL = os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai")
ACCOUNT_ID = os.environ.get("FIREWORKS_ACCOUNT_ID", "")

# Base model for training - update this to your desired model
BASE_MODEL = os.environ.get("FIREWORKS_BASE_MODEL", "accounts/fireworks/models/qwen3-32b")

# Default values (can be overridden via CLI)
DEFAULT_DEPLOYMENT_ID = "gsm8k-rlor"
DEFAULT_NUM_EPOCHS = 2
DEFAULT_CHUNK_SIZE = 100
DEFAULT_TOTAL_PROMPTS = 1000
DEFAULT_NUM_GENERATIONS_PER_PROMPT = 4
DEFAULT_CONCURRENCY = 64

ROLLOUTS_DIR = "rollouts"
# Path to the GSM8K dataset file (local or remote via fsspec, e.g., gs://, s3://)
DATASET_FILE = os.environ.get("DATASET_FILE", "dataset_with_ground_truth.jsonl")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="GSM8K RLOR Training Example - Iterative RL workflow using Fireworks SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--keep-alive",
        action="store_true",
        default=True,
        help="Use keep-alive mode (single trainer job for multiple steps) instead of standard mode. "
        "This is more performant as it avoids the overhead of creating a new trainer job for each step, "
        "keeping the model warm in GPU memory between training iterations.",
    )
    parser.add_argument(
        "--deployment-id",
        type=str,
        default=DEFAULT_DEPLOYMENT_ID,
        help="Deployment ID for the hot-reload inference deployment",
    )
    parser.add_argument(
        "--num-epochs",
        type=int,
        default=DEFAULT_NUM_EPOCHS,
        help="Number of epochs to run",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Number of prompts per training step",
    )
    parser.add_argument(
        "--total-prompts",
        type=int,
        default=DEFAULT_TOTAL_PROMPTS,
        help="Total prompts to use from dataset",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help="Number of concurrent generation requests",
    )
    parser.add_argument(
        "--run-id",
        type=int,
        default=None,
        help="Run ID for this workflow (default: current timestamp)",
    )
    return parser.parse_args()


def load_gsm8k_prompts(filepath: str, limit: int | None = None) -> list[dict[str, Any]]:
    """Load GSM8K prompts from JSONL file, stripping assistant messages.

    Supports local files and remote files (e.g., gs://, s3://) via fsspec.
    """
    prompts = []
    try:
        with fsspec.open(filepath, "r") as f:
            for i, line in enumerate(f):
                if limit is not None and i >= limit:
                    break
                data = json.loads(line.strip())
                # Keep only system and user messages (strip assistant response)
                messages = [msg for msg in data["messages"] if msg["role"] != "assistant"]
                prompts.append(
                    {
                        "prompt_id": i,
                        "messages": messages,
                        "ground_truth": data.get("ground_truth", ""),
                    }
                )
        logger.info(f"Loaded {len(prompts)} prompts from {filepath}")
        return prompts
    except Exception as e:
        # Fallback to dummy data if file not found for testing
        logger.warning(f"Dataset file {filepath} not found or failed to load: {e}. Using dummy prompts.")
        return [
            {
                "prompt_id": i,
                "messages": [{"role": "user", "content": f"What is {i}+{i}?"}],
                "ground_truth": f"<answer>{i + i}</answer>",
            }
            for i in range(min(limit or 10, 10))
        ]


def extract_answer(text: str) -> str | None:
    """Extract the answer from <answer> tags."""
    match = re.search(r"<answer>\s*(.*?)\s*</answer>", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def compute_reward(generated_answer: str, ground_truth: str) -> float:
    """Compute reward by comparing generated answer with ground truth.

    Returns 1.0 for exact match, 0.0 otherwise.
    """
    gen_ans = extract_answer(generated_answer)
    gt_ans = extract_answer(ground_truth)

    if gen_ans is None or gt_ans is None:
        return 0.0

    # Normalize: strip whitespace and convert to lowercase
    gen_ans = gen_ans.strip().lower()
    gt_ans = gt_ans.strip().lower()

    # Try numeric comparison for math problems
    try:
        gen_num = float(gen_ans.replace(",", "").replace("$", ""))
        gt_num = float(gt_ans.replace(",", "").replace("$", ""))
        return 1.0 if abs(gen_num - gt_num) < 1e-6 else 0.0
    except (ValueError, AttributeError):
        pass

    return 1.0 if gen_ans == gt_ans else 0.0


async def wait_for_deployment_ready(
    client: AsyncFireworks,
    deployment_id: str,
    timeout_seconds: int = 1200,
    poll_interval: int = 15,
) -> None:
    """Wait for a deployment to be ready."""
    logger.info(f"Waiting for deployment {deployment_id} to be ready (timeout: {timeout_seconds}s)...")
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        deployment = await client.deployments.get(
            deployment_id=deployment_id,
        )
        state = deployment.state
        elapsed = int(time.time() - start_time)
        logger.info(f"Deployment state: {state} (elapsed: {elapsed}s)")

        if state == "READY":
            logger.info("Deployment is ready!")
            return
        elif state in ("FAILED", "DELETED", "DELETING"):
            raise Exception(f"Deployment entered bad state: {state}")

        await asyncio.sleep(poll_interval)

    raise TimeoutError(f"Deployment did not become ready within {timeout_seconds} seconds")


async def create_or_get_deployment(
    client: AsyncFireworks,
    deployment_id: str,
    base_model: str,
    api_key: str,
) -> dict[str, Any]:
    """Create a deployment with hot reload and direct route enabled, or get existing one."""
    logger.info(f"Checking for existing deployment: {deployment_id}")
    try:
        deployment = await client.deployments.get(deployment_id=deployment_id)
        logger.info(f"Found existing deployment: {deployment.name}")
        return model_dump(deployment)
    except Exception:
        logger.info(f"Creating deployment {deployment_id} with hot reload and direct route enabled...")
        logger.info(f"  Base model: {base_model}")
        deployment = await client.deployments.create(
            base_model=base_model,
            deployment_id=deployment_id,
            enable_hot_reload_latest_addon=True,
            min_replica_count=1,
            max_replica_count=1,
            # Use a deployment shape appropriate for your base model
            deployment_shape=os.environ.get(
                "FIREWORKS_DEPLOYMENT_SHAPE",
                "accounts/fireworks/deploymentShapes/rft-qwen3-32b",
            ),
            # Enable direct route for faster inference
            direct_route_type="INTERNET",
            direct_route_api_keys=[api_key],
            # Direct route requires a specific region
            placement={"region": "US_VIRGINIA_1"},
        )
        logger.info(f"Created deployment: {deployment.name}")
        return model_dump(deployment)


async def get_direct_route_url(
    client: AsyncFireworks,
    deployment_id: str,
    account_id: str,
) -> str | None:
    """Get the direct route URL for a deployment, if available."""
    logger.info(f"Checking direct route URL for deployment {deployment_id}...")

    deployment = await client.deployments.get(deployment_id=deployment_id)
    deployment_dict = model_dump(deployment)

    # Check if direct route is enabled
    direct_route_type = deployment_dict.get("direct_route_type") or deployment_dict.get("directRouteType")
    if direct_route_type and direct_route_type not in ("DIRECT_ROUTE_TYPE_UNSPECIFIED", None, ""):
        # Get region from placement
        placement = deployment_dict.get("placement") or {}
        region = placement.get("region", "").lower().replace("_", "-")

        # If region is not set or unspecified, try to get from the deployment
        if not region or region == "region-unspecified":
            # Try alternative field names
            region = deployment_dict.get("region", "").lower().replace("_", "-")

        if region and region != "region-unspecified":
            # Construct the direct route URL
            # Format: https://{account}-{deployment}.{region}.direct.fireworks.ai
            direct_route_url = f"https://{account_id}-{deployment_id}.{region}.direct.fireworks.ai"
            logger.info(f"Direct route URL: {direct_route_url}")
            return direct_route_url
        else:
            logger.warning("Direct route enabled but region not available to construct URL")
    else:
        logger.info(f"Direct route not enabled on this deployment (type: {direct_route_type})")

    return None


async def generate_rollouts_and_rewards(
    client: AsyncFireworks,
    model: str,
    prompts: list[dict[str, Any]],
    num_generations_per_prompt: int = 4,
    concurrency: int = 32,
    direct_route_url: str | None = None,
    api_key: str | None = None,
    lora_model_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    Generate rollouts and compute rewards for the given prompts.
    Each sample contains multiple generations for Policy Optimization.

    If direct_route_url is provided, uses direct route for faster inference.
    Otherwise, uses the regular API gateway with the deployment name.

    For direct route with LoRA adapter, lora_model_name should be provided
    (e.g., accounts/.../models/...).
    """
    # Use direct route client if available, otherwise use regular client
    owns_inference_client = False
    if direct_route_url and api_key:
        inference_client = AsyncFireworks(
            api_key=api_key,
            base_url=direct_route_url,
        )
        owns_inference_client = True  # We created this client, so we need to close it
        # For direct route: use model name if available, otherwise use base model
        if lora_model_name:
            inference_model = lora_model_name
            logger.info(f"Using direct route with LoRA model: {lora_model_name}")
        else:
            # First epoch - use the base model
            inference_model = BASE_MODEL
            logger.info(f"Using direct route with base model: {inference_model}")
    else:
        inference_client = client
        inference_model = model
        logger.info(f"Using regular API gateway for inference: {model}")

    semaphore = asyncio.Semaphore(concurrency)

    async def generate_single_response(prompt: dict[str, Any], generation_id: int) -> dict[str, Any]:
        """Generate a single response for a given prompt with simple retry logic."""
        async with semaphore:
            messages = prompt["messages"]
            ground_truth = prompt.get("ground_truth", "")
            prompt_id = prompt["prompt_id"]

            max_retries = 3
            retry_delay = 5.0  # seconds

            for attempt in range(max_retries):
                try:
                    response = await inference_client.chat.completions.create(
                        model=inference_model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2048,
                    )

                    content = response.choices[0].message.content
                    # Ensure content is a string (handle case where it might be a list)
                    if isinstance(content, list):
                        assistant_message = "".join(str(item) for item in content)
                    else:
                        assistant_message = str(content) if content else ""

                    # Compute reward by comparing with ground truth
                    reward = compute_reward(assistant_message, ground_truth)

                    return {
                        "prompt_id": prompt_id,
                        "generation_id": generation_id,
                        "messages": messages + [{"role": "assistant", "content": assistant_message}],
                        "evals": {"score": reward},
                        "success": True,
                    }
                except Exception as e:
                    error_str = str(e)
                    # Retry on transient errors (429, 500, 502, 503, 504)
                    if any(code in error_str for code in ["429", "500", "502", "503", "504"]):
                        if attempt < max_retries - 1:
                            logger.info(
                                f"Transient error for prompt {prompt_id}, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})"
                            )
                            await asyncio.sleep(retry_delay)
                            continue
                    logger.warning(f"Generation failed for prompt {prompt_id}: {e}")
                    return {
                        "prompt_id": prompt_id,
                        "generation_id": generation_id,
                        "messages": messages + [{"role": "assistant", "content": ""}],
                        "evals": {"score": 0.0},
                        "success": False,
                    }

            # Should not reach here, but just in case
            return {
                "prompt_id": prompt_id,
                "generation_id": generation_id,
                "messages": messages + [{"role": "assistant", "content": ""}],
                "evals": {"score": 0.0},
                "success": False,
            }

    # Create all generation tasks concurrently
    tasks: list[asyncio.Task[dict[str, Any]]] = []
    for prompt in prompts:
        for generation_id in range(num_generations_per_prompt):
            task = asyncio.create_task(generate_single_response(prompt, generation_id))
            tasks.append(task)

    # Execute all generations concurrently
    logger.info(f"Starting {len(tasks)} concurrent generations...")
    start_time = time.time()
    num_completed = 0
    num_successful = 0
    total_reward = 0.0
    results: list[dict[str, Any]] = []

    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        num_completed += 1
        if result["success"]:
            num_successful += 1
            total_reward += result["evals"]["score"]
        if num_completed % 20 == 0:
            elapsed = time.time() - start_time
            rate = num_completed / elapsed if elapsed > 0 else 0
            avg_reward = total_reward / num_successful if num_successful > 0 else 0
            logger.info(
                f"Completed {num_completed}/{len(tasks)} generations ({rate:.1f}/s, avg_reward: {avg_reward:.3f})"
            )

    total_time = time.time() - start_time
    avg_reward = total_reward / num_successful if num_successful > 0 else 0
    logger.info(
        f"All generations completed in {total_time:.1f}s (success: {num_successful}/{num_completed}, avg_reward: {avg_reward:.3f})"
    )

    # Group results by prompt_id to create dataset rows
    prompt_generations_map: defaultdict[int, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        if result["success"]:
            prompt_generations_map[result["prompt_id"]].append(result)

    dataset_rows: list[dict[str, Any]] = []
    skipped_prompts = 0
    for prompt_id in sorted(prompt_generations_map.keys()):
        prompt_generations: list[dict[str, Any]] = prompt_generations_map[prompt_id]
        # Only include prompts that have EXACTLY num_generations_per_prompt successful generations
        # This is required by RLOR validation
        if len(prompt_generations) == num_generations_per_prompt:
            sample_generations: list[dict[str, Any]] = [
                {"messages": gen["messages"], "evals": gen["evals"]} for gen in prompt_generations
            ]
            dataset_rows.append({"samples": sample_generations})
        else:
            skipped_prompts += 1

    if skipped_prompts > 0:
        logger.warning(
            f"Skipped {skipped_prompts} prompts that didn't have exactly {num_generations_per_prompt} generations"
        )
    logger.info(f"Created {len(dataset_rows)} dataset rows (each with {num_generations_per_prompt} generations)")

    # Close the inference client if we created it
    if owns_inference_client:
        await inference_client.close()

    return dataset_rows


def save_rollouts_to_file(
    dataset_rows: list[dict[str, Any]],
    step: int,
) -> str:
    """Save rollouts to a local file for inspection."""
    os.makedirs(ROLLOUTS_DIR, exist_ok=True)
    filename = f"step-{step + 1}-rollouts-{int(time.time())}.jsonl"
    filepath = os.path.join(ROLLOUTS_DIR, filename)

    with open(filepath, "w") as f:
        for row in dataset_rows:
            f.write(json.dumps(row, indent=None) + "\n")

    file_size = os.path.getsize(filepath)
    logger.info(f"Saved rollouts to {filepath} ({file_size} bytes)")
    return filepath


def example_count(rollouts_filepath: str) -> int:
    """Count the number of examples (non-empty lines) in the rollouts file."""
    with open(rollouts_filepath) as f:
        return sum(1 for line in f if line.strip())


async def create_and_upload_dataset(
    client: AsyncFireworks,
    dataset_id: str,
    rollouts_filepath: str,
    timeout_seconds: int = 300,
    poll_interval: int = 2,
) -> str:
    """Create a dataset, upload from the saved rollouts file, and wait for it to be ready."""
    # Create the dataset
    logger.info(f"Creating dataset {dataset_id}...")
    try:
        dataset = await client.datasets.create(
            dataset_id=dataset_id,
            dataset={
                "display_name": f"GSM8K RL Training Dataset - {dataset_id}",
                "example_count": str(example_count(rollouts_filepath)),
            },
        )
        logger.info(f"Created dataset: {dataset.name}")
    except Exception as e:
        logger.warning(f"Dataset creation failed (maybe exists): {e}")
        # Try to get existing
        try:
            dataset = await client.datasets.get(dataset_id=dataset_id)
            logger.info(f"Found existing dataset: {dataset.name}")
        except Exception as get_error:
            raise e from get_error

    # Upload the rollouts file
    logger.info(f"Uploading dataset from {rollouts_filepath}...")
    with open(rollouts_filepath, "rb") as f:
        await client.datasets.upload(
            dataset_id=dataset_id,
            file=f,
        )
    logger.info("Dataset file uploaded, waiting for processing...")

    # Poll until dataset is ready
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        dataset = await client.datasets.get(
            dataset_id=dataset_id,
        )
        state = dataset.state
        elapsed = int(time.time() - start_time)
        logger.info(f"Dataset state: {state} (elapsed: {elapsed}s)")

        if state == "READY":
            logger.info("Dataset is ready!")
            if dataset.name is None:
                raise ValueError("Dataset name is None")
            return dataset.name
        elif state in ("UPLOADING", "STATE_UNSPECIFIED"):
            await asyncio.sleep(poll_interval)
        else:
            raise Exception(f"Unexpected dataset state: {state}")

    raise TimeoutError(f"Dataset did not become ready within {timeout_seconds} seconds")


async def wait_for_training_completion(
    client: AsyncFireworks,
    job_id: str,
    timeout_seconds: int = 7200,
    poll_interval: int = 30,
) -> dict[str, Any]:
    """Wait for a reinforcement fine-tuning step to complete."""
    logger.info(f"Waiting for training job {job_id} to complete (timeout: {timeout_seconds}s)...")
    start_time = time.time()

    # Terminal failure states
    failure_states = {
        "JOB_STATE_FAILED",
        "JOB_STATE_FAILED_CLEANING_UP",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_EXPIRED",
        "JOB_STATE_EXPIRED_CLEANING_UP",
        "JOB_STATE_DELETING_CLEANING_UP",
    }

    while time.time() - start_time < timeout_seconds:
        job = await client.reinforcement_fine_tuning_steps.get(
            rlor_trainer_job_id=job_id,
        )

        state = job.state
        elapsed = int(time.time() - start_time)
        logger.info(f"Training state: {state} (elapsed: {elapsed}s)")

        if state == "JOB_STATE_COMPLETED":
            total_time = time.time() - start_time
            logger.info(f"Training completed in {total_time:.1f}s!")
            return model_dump(job)
        elif state in failure_states:
            raise Exception(f"Training job entered bad state: {state}")

        await asyncio.sleep(poll_interval)

    raise TimeoutError(f"Training did not complete within {timeout_seconds} seconds")


async def wait_for_model_ready(
    client: AsyncFireworks,
    model_id: str,
    timeout_seconds: int = 600,
    poll_interval: int = 10,
) -> None:
    """Wait for a model to be ready after training."""
    logger.info(f"Waiting for model {model_id} to be ready (timeout: {timeout_seconds}s)...")
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        model = await client.models.get(
            model_id=model_id,
        )

        state = model.state
        elapsed = int(time.time() - start_time)
        logger.info(f"Model state: {state} (elapsed: {elapsed}s)")

        if state == "READY":
            logger.info("Model is ready!")
            return
        # STATE_UNSPECIFIED and UPLOADING are transient states, continue waiting
        await asyncio.sleep(poll_interval)

    raise TimeoutError(f"Model did not become ready within {timeout_seconds} seconds")


async def load_lora_adapter(
    client: AsyncFireworks,
    deployment_name: str,
    model_name: str,
) -> None:
    """
    Load a LoRA adapter onto a deployment using hot reload.
    """
    logger.info("Loading LoRA adapter onto deployment...")
    logger.info(f"  Model: {model_name}")
    logger.info(f"  Deployment: {deployment_name}")
    await client.lora.load(
        model=model_name,
        deployment=deployment_name,
        replace_merged_addon=True,
    )
    logger.info("LoRA adapter load request sent")


async def wait_for_lora_deployed(
    client: AsyncFireworks,
    model_name: str,
    timeout_seconds: int = 300,
    poll_interval: int = 5,
) -> str | None:
    """
    Wait for the LoRA adapter to be fully deployed by polling the deployed model state.

    The deployed model goes through states: DEPLOYING -> DEPLOYED
    We wait until state is DEPLOYED.

    Returns the deployed model name (e.g., accounts/.../deployedModels/...) for use with direct route.
    """
    logger.info(f"Waiting for LoRA adapter to be deployed (timeout: {timeout_seconds}s)...")
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        try:
            # Get the deployed model state using lora.list()
            deployed_models = await client.lora.list()

            # Find the deployed model matching our model name
            target_model = None
            for dm in deployed_models.deployed_models or []:
                dm_dict = model_dump(dm)
                if dm_dict.get("model") == model_name:
                    target_model = dm_dict
                    break

            if target_model:
                state = target_model.get("state", "STATE_UNSPECIFIED")
                elapsed = int(time.time() - start_time)
                logger.info(f"Deployed model state: {state} (elapsed: {elapsed}s)")

                if state == "DEPLOYED":
                    deployed_model_name = target_model.get("name")
                    logger.info("LoRA adapter is fully deployed and ready!")
                    logger.info(f"Deployed model name: {deployed_model_name}")
                    return deployed_model_name
                elif state in ("STATE_UNSPECIFIED", "DEPLOYING", "UPDATING"):
                    # Still loading, continue polling
                    pass
                elif state == "UNDEPLOYING":
                    raise Exception("Deployed model is unexpectedly undeploying")
            else:
                elapsed = int(time.time() - start_time)
                logger.info(f"Deployed model not found yet, waiting... (elapsed: {elapsed}s)")

        except Exception as e:
            if "not found" not in str(e).lower():
                logger.warning(f"Error checking deployed model state: {e}")

        await asyncio.sleep(poll_interval)

    raise TimeoutError(f"LoRA adapter did not become deployed within {timeout_seconds} seconds")


async def execute_training_step(
    client: AsyncFireworks,
    job_id: str,
    dataset: str,
    output_model: str,
) -> None:
    """
    Execute a training step on a running keep-alive trainer job.

    Note: warm_start_from and reference_model are auto-filled by the trainer.
    """
    logger.info(f"Executing training step for job {job_id}...")
    logger.info(f"  Dataset: {dataset}")
    logger.info(f"  Output Model: {output_model}")

    # Construct payload for ExecuteRlorTrainStep
    payload = {
        "name": f"accounts/{ACCOUNT_ID}/rlorTrainerJobs/{job_id}",
        "dataset": dataset,
        "output_model": output_model,
    }

    # Use the SDK's post method with cast_to=object since we don't need typed response
    # URL needs /v1/ prefix to match the REST API path
    url = f"/v1/accounts/{ACCOUNT_ID}/rlorTrainerJobs/{job_id}:executeTrainStep"

    try:
        await client.post(
            url,
            body=payload,
            cast_to=object,  # Required by SDK, we don't care about response type
        )
        logger.info("Training step execution signalled successfully")
    except Exception as e:
        logger.error(f"Failed to signal training step: {e}")
        raise e


async def cleanup_trainer_job(client: AsyncFireworks, job_id: str) -> None:
    """Clean up a keep-alive trainer job by deleting it."""
    try:
        logger.info(f"Cleaning up trainer job: {job_id}")
        # SDK delete method takes rlor_trainer_job_id as positional arg
        await client.reinforcement_fine_tuning_steps.delete(job_id)
        logger.info(f"Successfully deleted trainer job: {job_id}")
    except Exception as e:
        logger.warning(f"Failed to cleanup trainer job {job_id}: {e}")


async def wait_for_model_ready_or_job_fail(
    client: AsyncFireworks,
    model_id: str,
    job_id: str,
    timeout_seconds: int = 7200,
    poll_interval: int = 30,
) -> None:
    """Wait for model to be READY or job to FAIL."""
    logger.info(f"Waiting for model {model_id} to be ready (timeout: {timeout_seconds}s)...")
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        # Check model status
        try:
            model = await client.models.get(model_id=model_id)
            state = model.state
            logger.info(f"Model state: {state}")
            if state == "READY":
                logger.info("Model is ready!")
                return
            elif state == "FAILED":
                raise Exception(f"Model creation failed: {state}")
        except Exception as e:
            # Re-raise if it's a failure state exception, otherwise log and continue
            if "Model creation failed" in str(e):
                raise
            logger.warning(f"Error checking model status (might not exist yet): {e}")

        # Check job status for failure
        try:
            job = await client.reinforcement_fine_tuning_steps.get(rlor_trainer_job_id=job_id)
            if job.state in ("JOB_STATE_FAILED", "JOB_STATE_CANCELLED"):
                raise Exception(f"Training job failed or cancelled: {job.state}")
        except Exception as e:
            logger.warning(f"Error checking job status: {e}")

        elapsed = int(time.time() - start_time)
        logger.info(f"Elapsed: {elapsed}s")
        await asyncio.sleep(poll_interval)

    raise TimeoutError(f"Model did not become ready within {timeout_seconds} seconds")


async def run_gsm8k_rlor(args: argparse.Namespace) -> None:
    """Main function to run the GSM8K RLOR training workflow."""

    # Extract args into local variables for clarity
    use_keep_alive = args.keep_alive
    deployment_id = args.deployment_id
    num_epochs = args.num_epochs
    chunk_size = args.chunk_size
    total_prompts = args.total_prompts
    concurrency = args.concurrency
    run_id = args.run_id if args.run_id else int(time.time())

    # Validate required configuration
    if not FIREWORKS_API_KEY:
        raise ValueError("FIREWORKS_API_KEY environment variable is required")
    if not ACCOUNT_ID:
        raise ValueError("FIREWORKS_ACCOUNT_ID environment variable is required")

    # Create client with the specified API key, account ID, and base URL
    client = AsyncFireworks(
        api_key=FIREWORKS_API_KEY,
        account_id=ACCOUNT_ID,
        base_url=BASE_URL,
    )

    logger.info("=" * 60)
    logger.info("GSM8K RLOR Training Workflow")
    if use_keep_alive:
        logger.info("(Keep-Alive Mode)")
    else:
        logger.info("(Standard Mode)")
    logger.info("=" * 60)
    logger.info(f"Account: {ACCOUNT_ID}")
    logger.info(f"Base Model: {BASE_MODEL}")
    logger.info(f"Deployment ID: {deployment_id}")
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Total Prompts: {total_prompts}")
    logger.info(f"Chunk Size: {chunk_size}")
    logger.info(f"Num Epochs: {num_epochs}")
    logger.info(f"Concurrency: {concurrency}")
    logger.info("=" * 60)

    # Load all GSM8K prompts
    all_prompts = load_gsm8k_prompts(DATASET_FILE, limit=total_prompts)
    num_chunks = (len(all_prompts) + chunk_size - 1) // chunk_size
    logger.info(f"Will process {num_chunks} chunks per epoch")

    trainer_job_id = f"gsm8k-rlor-trainer-{run_id}"

    if use_keep_alive:
        # Step 1: Create keep-alive trainer job (ONCE)
        logger.info(f"Creating keep-alive trainer job: {trainer_job_id}")

        # Delete any existing job first since we need a fresh keep-alive job
        try:
            await client.reinforcement_fine_tuning_steps.delete(trainer_job_id)
            logger.info(f"Deleted existing trainer job: {trainer_job_id}")
            await asyncio.sleep(2)  # Wait for cleanup
        except Exception:
            pass  # Job doesn't exist, that's fine

        # Create new trainer job
        logger.info("Creating new trainer job...")

        keep_alive_training_config: TrainingConfig = {
            "base_model": BASE_MODEL,
            "learning_rate": 1e-5,
            "lora_rank": 8,
            "max_context_length": 4096,
            "batch_size": 32768,
        }

        await client.reinforcement_fine_tuning_steps.create(
            rlor_trainer_job_id=trainer_job_id,
            dataset="",  # No initial dataset for keep-alive
            display_name=f"GSM8K RL Trainer {run_id}",
            training_config=keep_alive_training_config,
            # Use extra_body to pass keep_alive and reward_weights since they're new proto fields not in the SDK yet
            extra_body={
                "keep_alive": True,
                "reward_weights": ["score"],  # Reward key used in our dataset evals
            },
        )
        logger.info(f"Created trainer job: {trainer_job_id}")

        # Wait for job to be in RUNNING state (IDLE phase)
        await asyncio.sleep(10)

    # Step 2: Create or get the base deployment
    logger.info("[Step 0] Setting up base deployment...")
    await create_or_get_deployment(
        client=client,
        deployment_id=deployment_id,
        base_model=BASE_MODEL,
        api_key=FIREWORKS_API_KEY,
    )
    await wait_for_deployment_ready(client=client, deployment_id=deployment_id)

    direct_route_url = await get_direct_route_url(client=client, deployment_id=deployment_id, account_id=ACCOUNT_ID)

    deployment_name = f"accounts/{ACCOUNT_ID}/deployments/{deployment_id}"
    current_lora_model: str | None = None
    step = 0

    try:
        for epoch in range(num_epochs):
            logger.info(f"Starting epoch {epoch + 1}/{num_epochs}")

            for chunk_idx in range(num_chunks):
                chunk_start = chunk_idx * chunk_size
                chunk_end = min(chunk_start + chunk_size, len(all_prompts))
                chunk_prompts = all_prompts[chunk_start:chunk_end]
                step += 1

                logger.info(f"[Step {step}] Processing chunk {chunk_idx + 1}/{num_chunks}")

                # 1. Rollout
                logger.info("Generating rollouts...")
                dataset_rows = await generate_rollouts_and_rewards(
                    client=client,
                    model=deployment_name,
                    prompts=chunk_prompts,
                    concurrency=concurrency,
                    direct_route_url=direct_route_url,
                    api_key=FIREWORKS_API_KEY,
                    lora_model_name=current_lora_model,
                )

                if not dataset_rows:
                    logger.warning("No successful rollouts, skipping step")
                    continue

                # 2. Upload Dataset
                rollouts_filepath = save_rollouts_to_file(dataset_rows, step - 1)
                dataset_id = f"gsm8k-rl-dataset-{run_id}-step-{step}"
                dataset_name = await create_and_upload_dataset(
                    client=client,
                    dataset_id=dataset_id,
                    rollouts_filepath=rollouts_filepath,
                )

                # 3. Execute Train Step (or Create Job)
                output_model_name = f"accounts/{ACCOUNT_ID}/models/gsm8k-rl-model-{run_id}-v{step}"
                output_model_id = f"gsm8k-rl-model-{run_id}-v{step}"

                if use_keep_alive:
                    logger.info(f"Signalling trainer for step {step} -> {output_model_name}")
                    await execute_training_step(
                        client=client,
                        job_id=trainer_job_id,
                        dataset=dataset_name,
                        output_model=output_model_name,
                    )
                    # 4. Wait for Output Model (Keep-Alive)
                    logger.info("Waiting for training to complete (keep-alive)...")
                    await wait_for_model_ready_or_job_fail(
                        client=client, model_id=output_model_id, job_id=trainer_job_id
                    )

                else:
                    # Standard Mode: Create a new job for each step
                    job_id = f"gsm8k-rl-job-{run_id}-step-{step}"
                    logger.info(f"Creating standard RLOR job {job_id} -> {output_model_name}")

                    standard_training_config: TrainingConfig = {
                        "output_model": output_model_name,
                        "epochs": 1,
                        "learning_rate": 1e-5,
                        "lora_rank": 8,
                        "max_context_length": 4096,
                        "batch_size": 32768,
                        "base_model": BASE_MODEL,
                    }

                    await client.reinforcement_fine_tuning_steps.create(
                        rlor_trainer_job_id=job_id,
                        dataset=dataset_name,
                        display_name=f"GSM8K RL Step {step}",
                        training_config=standard_training_config,
                    )

                    # 4. Wait for Training (Standard)
                    logger.info("Waiting for training to complete (standard)...")
                    await wait_for_training_completion(client=client, job_id=job_id)
                    await wait_for_model_ready(client=client, model_id=output_model_id)

                # 5. Hot Reload
                logger.info("Hot reloading...")
                await load_lora_adapter(client=client, deployment_name=deployment_name, model_name=output_model_name)
                await wait_for_lora_deployed(client=client, model_name=output_model_name)

                current_lora_model = output_model_name
                logger.info(f"Step {step} completed.")

                # Cleanup dataset
                try:
                    await client.datasets.delete(dataset_id=dataset_id)
                except Exception:
                    pass

        logger.info("RLOR training complete!")

    except Exception as e:
        logger.error(f"Training failed with error: {e}")
        raise
    finally:
        # Cleanup keep-alive trainer job on exit (success or failure)
        if use_keep_alive:
            await cleanup_trainer_job(client, trainer_job_id)
        # Properly close the async client to avoid SSL transport errors on exit
        await client.close()


async def main() -> None:
    """Main entry point with proper async cleanup."""
    args = parse_args()
    try:
        await run_gsm8k_rlor(args)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
