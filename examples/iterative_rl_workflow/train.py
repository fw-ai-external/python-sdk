"""
GSM8K RLOR Training Example using Fireworks SDK.

This script demonstrates an iterative reinforcement learning workflow using GSM8K:
1. Load prompts from the GSM8K dataset (without assistant responses)
2. Generate rollouts using a base model
3. Score outputs by comparing with ground truth answers
4. Run reinforcement fine-tuning steps
5. Repeat for multiple epochs

Example usage:
    python gsm8k.py \
        --base-model accounts/fireworks/models/qwen3-32b \
        --direct-route-api-key <your-direct-route-api-key>
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
import fireworks
from fireworks.types import TrainingConfig
from fireworks.types.deployment import Deployment
from fireworks.types.shared.deployed_model import DeployedModel

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

# Default values (can be overridden via CLI)
DEFAULT_RUN_PREFIX = "gsm8k-rlor"
DEFAULT_NUM_EPOCHS = 2
DEFAULT_CHUNK_SIZE = 100
DEFAULT_TOTAL_PROMPTS = 1000
DEFAULT_NUM_GENERATIONS_PER_PROMPT = 4
DEFAULT_CONCURRENCY = 64
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5.0
DEFAULT_DEPLOYMENT_TIMEOUT = 1200
DEFAULT_DATASET_TIMEOUT = 300
DEFAULT_TRAINING_TIMEOUT = 7200
DEFAULT_LORA_TIMEOUT = 300
DEFAULT_DIRECT_ROUTE_REGION = "US_VIRGINIA_1"
DEFAULT_LEARNING_RATE = 1e-5
DEFAULT_LORA_RANK = 8
DEFAULT_MAX_CONTEXT_LENGTH = 4096
DEFAULT_MODEL_POLL_INTERVAL = 10
DEFAULT_BATCH_SIZE = 32768

ROLLOUTS_DIR = "rollouts"
# Path to the GSM8K dataset file (local or remote via fsspec, e.g., gs://, s3://)
DATASET_FILE = os.environ.get("DATASET_FILE", "gsm8k_dataset.jsonl")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="GSM8K RLOR Training Example - Iterative RL workflow using Fireworks SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--run-prefix",
        type=str,
        default=DEFAULT_RUN_PREFIX,
        help="Prefix for naming deployments, models, and datasets",
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
    parser.add_argument(
        "--num-generations",
        type=int,
        default=DEFAULT_NUM_GENERATIONS_PER_PROMPT,
        help="Number of generations per prompt for rollouts",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help="Temperature for generation sampling",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help="Maximum tokens per generation",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help="Maximum retries for transient API errors",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=DEFAULT_RETRY_DELAY,
        help="Delay in seconds between retries",
    )
    parser.add_argument(
        "--deployment-timeout",
        type=int,
        default=DEFAULT_DEPLOYMENT_TIMEOUT,
        help="Timeout in seconds for deployment to become ready",
    )
    parser.add_argument(
        "--dataset-timeout",
        type=int,
        default=DEFAULT_DATASET_TIMEOUT,
        help="Timeout in seconds for dataset upload to complete",
    )
    parser.add_argument(
        "--training-timeout",
        type=int,
        default=DEFAULT_TRAINING_TIMEOUT,
        help="Timeout in seconds for training job to complete",
    )
    parser.add_argument(
        "--lora-timeout",
        type=int,
        default=DEFAULT_LORA_TIMEOUT,
        help="Timeout in seconds for LoRA adapter to be deployed",
    )
    parser.add_argument(
        "--base-model",
        type=str,
        required=True,
        help="Base model to use for training (e.g., accounts/fireworks/models/qwen3-32b)",
    )
    parser.add_argument(
        "--direct-route-api-key",
        type=str,
        required=True,
        help="API key for direct route access to the deployment",
    )
    parser.add_argument(
        "--direct-route-region",
        type=str,
        default=DEFAULT_DIRECT_ROUTE_REGION,
        help="Region for direct route deployment (e.g., US_VIRGINIA_1)",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=DEFAULT_LEARNING_RATE,
        help="Learning rate for training",
    )
    parser.add_argument(
        "--lora-rank",
        type=int,
        default=DEFAULT_LORA_RANK,
        help="LoRA rank for training",
    )
    parser.add_argument(
        "--max-context-length",
        type=int,
        default=DEFAULT_MAX_CONTEXT_LENGTH,
        help="Maximum context length for training",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Batch size for training",
    )
    parser.add_argument(
        "--model-poll-interval",
        type=int,
        default=DEFAULT_MODEL_POLL_INTERVAL,
        help="Poll interval in seconds when waiting for model to be ready",
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
    timeout_seconds: int = DEFAULT_DEPLOYMENT_TIMEOUT,
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
    region: str = DEFAULT_DIRECT_ROUTE_REGION,
) -> Deployment:
    """Create a deployment with hot reload and direct route enabled, or get existing one."""
    logger.info(f"Checking for existing deployment: {deployment_id}")
    try:
        deployment = await client.deployments.get(deployment_id=deployment_id)
        logger.info(f"Found existing deployment: {deployment.name}")
        return deployment
    except fireworks.NotFoundError:
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
            placement={"region": region},
        )
        logger.info(f"Created deployment: {deployment.name}")
        return deployment


async def get_direct_route_url(
    deployment: Deployment,
    deployment_id: str,
    account_id: str,
) -> str:
    """Get the direct route URL for a deployment, if available."""
    logger.info(f"Checking direct route URL for deployment {deployment.name}...")

    # Check if direct route is enabled
    if deployment.direct_route_type and deployment.direct_route_type not in ("DIRECT_ROUTE_TYPE_UNSPECIFIED", ""):
        direct_route_url = f"https://{deployment.direct_route_handle}"
        logger.info(f"Direct route URL: {direct_route_url}")
        return direct_route_url
    else:
        raise ValueError("Direct route not enabled on this deployment")


async def generate_rollouts_and_rewards(
    prompts: list[dict[str, Any]],
    base_model: str,
    direct_route_url: str,
    direct_route_api_key: str,
    num_generations_per_prompt: int = DEFAULT_NUM_GENERATIONS_PER_PROMPT,
    concurrency: int = DEFAULT_CONCURRENCY,
    lora_model_name: str | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
) -> list[dict[str, Any]]:
    """
    Generate rollouts and compute rewards for the given prompts.
    Each sample contains multiple generations for Policy Optimization.

    If direct_route_url is provided, uses direct route for faster inference.
    Otherwise, uses the regular API gateway with the deployment name.

    For direct route with LoRA adapter, lora_model_name should be provided
    (e.g., accounts/.../models/...).
    """
    inference_client = AsyncFireworks(
        api_key=direct_route_api_key,
        base_url=direct_route_url,
    )

    if lora_model_name:
        inference_model = lora_model_name
        logger.info(f"Using direct route with LoRA model: {lora_model_name}")
    else:
        # First epoch - use the base model
        inference_model = base_model
        logger.info(f"Using direct route with base model: {inference_model}")

    semaphore = asyncio.Semaphore(concurrency)

    async def generate_single_response(prompt: dict[str, Any], generation_id: int) -> dict[str, Any]:
        """Generate a single response for a given prompt with simple retry logic."""
        async with semaphore:
            messages = prompt["messages"]
            ground_truth = prompt.get("ground_truth", "")
            prompt_id = prompt["prompt_id"]

            for attempt in range(max_retries):
                try:
                    response = await inference_client.chat.completions.create(
                        model=inference_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
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
                except (fireworks.RateLimitError, fireworks.InternalServerError, fireworks.APIConnectionError) as e:
                    # Retry on transient errors (429 rate limit, 5xx server errors, connection issues)
                    if attempt < max_retries - 1:
                        logger.info(
                            f"Transient error for prompt {prompt_id}, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries}): {type(e).__name__}"
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    logger.warning(f"Generation failed for prompt {prompt_id} after {max_retries} attempts: {e}")
                    return {
                        "prompt_id": prompt_id,
                        "generation_id": generation_id,
                        "messages": messages + [{"role": "assistant", "content": ""}],
                        "evals": {"score": 0.0},
                        "success": False,
                    }
                except Exception as e:
                    # Non-retryable errors (4xx client errors, etc.)
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
    timeout_seconds: int = DEFAULT_DATASET_TIMEOUT,
    poll_interval: int = 2,
) -> str:
    """Create a dataset, upload from the saved rollouts file, and wait for it to be ready."""
    # Create the dataset
    logger.info(f"Creating dataset {dataset_id}...")
    try:
        dataset = await client.datasets.create(
            dataset_id=dataset_id,
            dataset={
                "display_name": dataset_id[:63],
                "example_count": str(example_count(rollouts_filepath)),
            },
        )
        logger.info(f"Created dataset: {dataset.name}")
    except fireworks.APIError as e:
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
    timeout_seconds: int = DEFAULT_LORA_TIMEOUT,
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
            target_model: DeployedModel | None = None
            for dm in deployed_models.deployed_models or []:
                if dm.model == model_name:
                    target_model = dm
                    break

            if target_model:
                state = target_model.state or "STATE_UNSPECIFIED"
                elapsed = int(time.time() - start_time)
                logger.info(f"Deployed model state: {state} (elapsed: {elapsed}s)")

                if state == "DEPLOYED":
                    logger.info("LoRA adapter is fully deployed and ready!")
                    logger.info(f"Deployed model name: {target_model.name}")
                    return target_model.name
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

    try:
        await client.reinforcement_fine_tuning_steps.execute(
            rlor_trainer_job_id=job_id,
            dataset=dataset,
            output_model=output_model,
        )
        logger.info("Training step execution signalled successfully")
    except fireworks.FireworksError as e:
        logger.error(f"Failed to signal training step: {e}")
        raise


async def cleanup_trainer_job(client: AsyncFireworks, job_id: str) -> None:
    """Clean up a keep-alive trainer job by deleting it."""
    try:
        logger.info(f"Cleaning up trainer job: {job_id}")
        # SDK delete method takes rlor_trainer_job_id as positional arg
        await client.reinforcement_fine_tuning_steps.delete(job_id)
        logger.info(f"Successfully deleted trainer job: {job_id}")
    except Exception as e:
        logger.warning(f"Failed to cleanup trainer job {job_id}: {e}")


async def wait_for_trainer_job_running(
    client: AsyncFireworks,
    job_id: str,
    timeout_seconds: int = 300,
    poll_interval: int = 5,
) -> None:
    """Wait for the trainer job to be in RUNNING state."""
    logger.info(f"Waiting for trainer job {job_id} to be running (timeout: {timeout_seconds}s)...")
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        try:
            job = await client.reinforcement_fine_tuning_steps.get(rlor_trainer_job_id=job_id)
            state = job.state
            elapsed = int(time.time() - start_time)
            logger.info(f"Trainer job state: {state} (elapsed: {elapsed}s)")

            if state == "JOB_STATE_RUNNING":
                logger.info("Trainer job is running!")
                return
            elif state in ("JOB_STATE_FAILED", "JOB_STATE_CANCELLED"):
                raise Exception(f"Trainer job failed or cancelled: {state}")
        except Exception as e:
            if "failed or cancelled" in str(e).lower():
                raise
            logger.warning(f"Error checking trainer job status: {e}")

        await asyncio.sleep(poll_interval)

    raise TimeoutError(f"Trainer job did not become running within {timeout_seconds} seconds")


async def wait_for_model_ready_or_job_fail(
    client: AsyncFireworks,
    model_id: str,
    job_id: str,
    timeout_seconds: int = DEFAULT_TRAINING_TIMEOUT,
    poll_interval: int = DEFAULT_MODEL_POLL_INTERVAL,
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
        except fireworks.NotFoundError as e:
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
    run_prefix = args.run_prefix
    deployment_id = f"{run_prefix}"
    num_epochs = args.num_epochs
    chunk_size = args.chunk_size
    total_prompts = args.total_prompts
    concurrency = args.concurrency
    run_id = args.run_id if args.run_id else int(time.time())
    num_generations = args.num_generations
    temperature = args.temperature
    max_tokens = args.max_tokens
    max_retries = args.max_retries
    retry_delay = args.retry_delay
    deployment_timeout = args.deployment_timeout
    dataset_timeout = args.dataset_timeout
    training_timeout = args.training_timeout
    lora_timeout = args.lora_timeout
    base_model = args.base_model
    direct_route_api_key = args.direct_route_api_key
    direct_route_region = args.direct_route_region
    learning_rate = args.learning_rate
    lora_rank = args.lora_rank
    max_context_length = args.max_context_length
    batch_size = args.batch_size
    model_poll_interval = args.model_poll_interval

    # Get account ID from environment (SDK will pick it up automatically)
    account_id = os.environ.get("FIREWORKS_ACCOUNT_ID", "")

    # Create client with the specified API key, account ID, and base URL
    client = AsyncFireworks()

    logger.info("=" * 60)
    logger.info("GSM8K RLOR Training Workflow")
    logger.info("=" * 60)
    logger.info(f"Account: {account_id}")
    logger.info(f"Base Model: {base_model}")
    logger.info(f"Run Prefix: {run_prefix}")
    logger.info(f"Deployment ID: {deployment_id}")
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Total Prompts: {total_prompts}")
    logger.info(f"Chunk Size: {chunk_size}")
    logger.info(f"Num Epochs: {num_epochs}")
    logger.info(f"Concurrency: {concurrency}")
    logger.info(f"Num Generations: {num_generations}")
    logger.info(f"Temperature: {temperature}")
    logger.info(f"Max Tokens: {max_tokens}")
    logger.info(f"Max Retries: {max_retries}")
    logger.info(f"Retry Delay: {retry_delay}")
    logger.info(f"Deployment Timeout: {deployment_timeout}")
    logger.info(f"Dataset Timeout: {dataset_timeout}")
    logger.info(f"Training Timeout: {training_timeout}")
    logger.info(f"LoRA Timeout: {lora_timeout}")
    logger.info(f"Direct Route Region: {direct_route_region}")
    logger.info(f"Learning Rate: {learning_rate}")
    logger.info(f"LoRA Rank: {lora_rank}")
    logger.info(f"Max Context Length: {max_context_length}")
    logger.info(f"Batch Size: {batch_size}")
    logger.info("=" * 60)

    # Load all GSM8K prompts
    all_prompts = load_gsm8k_prompts(DATASET_FILE, limit=total_prompts)
    num_chunks = (len(all_prompts) + chunk_size - 1) // chunk_size
    logger.info(f"Will process {num_chunks} chunks per epoch")

    trainer_job_id = f"{run_prefix}-trainer-{run_id}"

    # Step 1: Create keep-alive trainer job (ONCE)
    logger.info(f"Creating keep-alive trainer job: {trainer_job_id}")

    # Delete any existing job first since we need a fresh keep-alive job
    try:
        await client.reinforcement_fine_tuning_steps.delete(trainer_job_id)
        logger.info(f"Deleted existing trainer job: {trainer_job_id}")
        await asyncio.sleep(2)  # Wait for cleanup
    except fireworks.NotFoundError as e:
        pass  # Job doesn't exist, that's fine

    # Create new trainer job
    logger.info("Creating new trainer job...")

    keep_alive_training_config: TrainingConfig = {
        "base_model": base_model,
        "learning_rate": learning_rate,
        "lora_rank": lora_rank,
        "max_context_length": max_context_length,
        "batch_size": batch_size,
    }

    await client.reinforcement_fine_tuning_steps.create(
        rlor_trainer_job_id=trainer_job_id,
        display_name=f"{run_prefix} Trainer {run_id}",
        training_config=keep_alive_training_config,
        keep_alive=True,
        # The documenation for `reward_weights` is poorly documented, it is
        # actually used to assign a field for the reward
        reward_weights=["score"],
    )
    logger.info(f"Created trainer job: {trainer_job_id}")

    # Wait for job to be in RUNNING state (IDLE phase)
    await wait_for_trainer_job_running(client=client, job_id=trainer_job_id)

    # Step 2: Create or get the base deployment
    logger.info("[Step 0] Setting up base deployment...")
    deployment = await create_or_get_deployment(
        client=client,
        deployment_id=deployment_id,
        base_model=base_model,
        api_key=direct_route_api_key,
        region=direct_route_region,
    )
    logger.info(f"You can view the deployment at https://app.fireworks.ai/dashboard/deployments/{deployment_id}")
    await wait_for_deployment_ready(client=client, deployment_id=deployment_id, timeout_seconds=deployment_timeout)

    direct_route_url = await get_direct_route_url(deployment=deployment, deployment_id=deployment_id, account_id=account_id)

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
                    direct_route_url=direct_route_url,
                    direct_route_api_key=direct_route_api_key,
                    prompts=chunk_prompts,
                    base_model=base_model,
                    num_generations_per_prompt=num_generations,
                    concurrency=concurrency,
                    lora_model_name=current_lora_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                )

                if not dataset_rows:
                    logger.warning("No successful rollouts, skipping step")
                    continue

                # 2. Upload Dataset
                rollouts_filepath = save_rollouts_to_file(dataset_rows, step - 1)
                dataset_id = f"{run_prefix}-dataset-{run_id}-step-{step}"
                dataset_name = await create_and_upload_dataset(
                    client=client,
                    dataset_id=dataset_id,
                    rollouts_filepath=rollouts_filepath,
                    timeout_seconds=dataset_timeout,
                )

                # 3. Execute Train Step
                output_model_id = f"{run_prefix}-model-{run_id}-v{step}"
                output_model_name = f"accounts/{account_id}/models/{output_model_id}"

                logger.info(f"Signalling trainer for step {step} -> {output_model_name}")
                await execute_training_step(
                    client=client,
                    job_id=trainer_job_id,
                    dataset=dataset_name,
                    output_model=output_model_name,
                )

                # 4. Wait for Output Model
                logger.info("Waiting for training to complete...")
                await wait_for_model_ready_or_job_fail(
                    client=client,
                    model_id=output_model_id,
                    job_id=trainer_job_id,
                    timeout_seconds=training_timeout,
                    poll_interval=model_poll_interval,
                )

                # 5. Hot Reload
                logger.info("Hot reloading...")
                await load_lora_adapter(client=client, deployment_name=deployment.name, model_name=output_model_name)
                await wait_for_lora_deployed(client=client, model_name=output_model_name, timeout_seconds=lora_timeout)

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
