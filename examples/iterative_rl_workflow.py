"""
GSM8K RLOR Training Example using Fireworks SDK.

This script demonstrates an iterative reinforcement learning workflow using GSM8K:
1. Load prompts from the GSM8K dataset (without assistant responses)
2. Generate rollouts using qwen3-32b
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
from typing import Any
from collections import defaultdict

from fireworks import AsyncFireworks
from fireworks._compat import model_dump

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Suppress HTTP request logs from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

# Configuration
FIREWORKS_API_KEY = "YOUR_API_KEY"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"
BASE_MODEL = "accounts/fireworks/models/qwen3-32b"
DEPLOYMENT_ID = "gsm8k-rlor"
NUM_EPOCHS = 2
CHUNK_SIZE = 100  # number of prompts per training step
TOTAL_PROMPTS = 1000  # total prompts to use from dataset
NUM_GENERATIONS_PER_PROMPT = 4  # multiple generations per prompt for policy optimization
CONCURRENCY = 64
ROLLOUTS_DIR = "rollouts"
DATASET_FILE = "dataset_with_ground_truth_column_1000.jsonl"

# Generate a unique run ID for this workflow execution
RUN_ID = int(time.time())


def load_gsm8k_prompts(filepath: str, limit: int | None = None) -> list[dict[str, Any]]:
    """Load GSM8K prompts from JSONL file, stripping assistant messages."""
    prompts: list[dict[str, Any]] = []
    with open(filepath, "r") as f:
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
            # Use the pre-configured RFT deployment shape for qwen3-32b
            deployment_shape="accounts/fireworks/deploymentShapes/rft-qwen3-32b",
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
        placement: dict[str, Any] = deployment_dict.get("placement") or {}
        region: str = str(placement.get("region", "")).lower().replace("_", "-")

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
    if direct_route_url and api_key:
        inference_client = AsyncFireworks(
            api_key=api_key,
            base_url=direct_route_url,
        )
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
            ground_truth = prompt["ground_truth"]
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

                    # Handle content which can be str, list, or None
                    content = response.choices[0].message.content
                    if content is None:
                        assistant_message = ""
                    elif isinstance(content, str):
                        assistant_message = content
                    else:
                        # content is a list of ContentUnionMember1, extract text
                        assistant_message = "".join(item.text or "" for item in content if item.text)

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
    dataset = await client.datasets.create(
        dataset_id=dataset_id,
        dataset={
            "display_name": f"GSM8K RL Training Dataset - {dataset_id}",
            "example_count": str(example_count(rollouts_filepath)),
        },
    )
    logger.info(f"Created dataset: {dataset.name}")

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


async def run_gsm8k_rlor() -> None:
    """Main function to run the GSM8K RLOR training workflow."""
    # Create client with the specified API key and account ID
    client = AsyncFireworks(api_key=FIREWORKS_API_KEY, account_id=ACCOUNT_ID)

    logger.info("=" * 60)
    logger.info("GSM8K RLOR Training Workflow")
    logger.info("=" * 60)
    logger.info(f"Account: {ACCOUNT_ID}")
    logger.info(f"Base Model: {BASE_MODEL}")
    logger.info(f"Total Prompts: {TOTAL_PROMPTS}")
    logger.info(f"Chunk Size: {CHUNK_SIZE}")
    logger.info(f"Num Epochs: {NUM_EPOCHS}")
    logger.info(f"Generations per Prompt: {NUM_GENERATIONS_PER_PROMPT}")
    logger.info("=" * 60)

    # Load all GSM8K prompts
    all_prompts = load_gsm8k_prompts(DATASET_FILE, limit=TOTAL_PROMPTS)
    num_chunks = (len(all_prompts) + CHUNK_SIZE - 1) // CHUNK_SIZE
    logger.info(f"Will process {num_chunks} chunks per epoch")

    # Step 1: Create or get the base deployment
    logger.info("[Step 0] Setting up base deployment...")
    await create_or_get_deployment(
        client=client,
        deployment_id=DEPLOYMENT_ID,
        base_model=BASE_MODEL,
        api_key=FIREWORKS_API_KEY,
    )

    # Wait for deployment to be ready
    await wait_for_deployment_ready(
        client=client,
        deployment_id=DEPLOYMENT_ID,
    )

    # Check if direct route is available
    logger.info("[Step 0.1] Checking for direct route...")
    direct_route_url = await get_direct_route_url(
        client=client,
        deployment_id=DEPLOYMENT_ID,
        account_id=ACCOUNT_ID,
    )
    if direct_route_url:
        logger.info(f"Using direct route: {direct_route_url}")
    else:
        logger.info("Direct route not available, will use regular API gateway")

    # Iterative reinforcement learning loop
    deployment_name = f"accounts/{ACCOUNT_ID}/deployments/{DEPLOYMENT_ID}"
    # Track the current LoRA model name for direct route (None = use base model)
    current_lora_model: str | None = None
    # Track the global step number across all epochs and chunks
    step = 0

    for epoch in range(NUM_EPOCHS):
        logger.info("=" * 60)
        logger.info(f"Starting epoch {epoch + 1}/{NUM_EPOCHS}")
        logger.info("=" * 60)

        # Process all chunks within this epoch
        for chunk_idx in range(num_chunks):
            chunk_start = chunk_idx * CHUNK_SIZE
            chunk_end = min(chunk_start + CHUNK_SIZE, len(all_prompts))
            chunk_prompts = all_prompts[chunk_start:chunk_end]
            step += 1

            logger.info("-" * 40)
            logger.info(
                f"[Epoch {epoch + 1}, Chunk {chunk_idx + 1}/{num_chunks}] Processing prompts {chunk_start}-{chunk_end - 1} (step {step})"
            )
            logger.info("-" * 40)

            # Generate rollouts and rewards for this chunk
            logger.info(f"[Step {step}.1] Generating rollouts...")
            dataset_rows = await generate_rollouts_and_rewards(
                client=client,
                model=deployment_name,
                prompts=chunk_prompts,
                num_generations_per_prompt=NUM_GENERATIONS_PER_PROMPT,
                concurrency=CONCURRENCY,
                direct_route_url=direct_route_url,
                api_key=FIREWORKS_API_KEY,
                lora_model_name=current_lora_model,
            )

            if not dataset_rows:
                logger.error("No successful rollouts generated. Skipping chunk.")
                continue

            # Save rollouts to local file for inspection
            rollouts_filepath = save_rollouts_to_file(dataset_rows, step - 1)

            # Create and upload dataset
            dataset_id = f"gsm8k-rl-dataset-{RUN_ID}-step-{step}"
            logger.info(f"[Step {step}.2] Creating and uploading dataset...")
            dataset_name = await create_and_upload_dataset(
                client=client,
                dataset_id=dataset_id,
                rollouts_filepath=rollouts_filepath,
            )

            # Create reinforcement fine-tuning step
            output_model_name = f"accounts/{ACCOUNT_ID}/models/gsm8k-rl-model-{RUN_ID}-v{step}"
            from fireworks.types.shared_params.training_config import TrainingConfig

            training_config: TrainingConfig = {
                "output_model": output_model_name,
                "epochs": 1,
                "learning_rate": 1e-5,
                "lora_rank": 8,
                "max_context_length": 4096,
                "batch_size": 32768,
            }
            if step == 1:
                training_config["base_model"] = BASE_MODEL
            else:
                training_config["warm_start_from"] = f"accounts/{ACCOUNT_ID}/models/gsm8k-rl-model-{RUN_ID}-v{step - 1}"

            job_id = f"gsm8k-rl-job-{RUN_ID}-step-{step}"
            logger.info(f"[Step {step}.3] Starting reinforcement fine-tuning step...")
            logger.info(f"Creating job with ID: {job_id}")
            job = await client.reinforcement_fine_tuning_steps.create(
                rlor_trainer_job_id=job_id,
                dataset=dataset_name,
                display_name=f"GSM8K RL Step {step} (Epoch {epoch + 1}, Chunk {chunk_idx + 1})",
                training_config=training_config,
            )
            logger.info(f"Created training job: {job.name}")

            # Wait for training completion
            logger.info(f"[Step {step}.4] Waiting for training to complete...")
            await wait_for_training_completion(client=client, job_id=job_id)

            # Wait for the output model to be ready
            output_model_id = f"gsm8k-rl-model-{RUN_ID}-v{step}"
            logger.info(f"[Step {step}.5] Waiting for model to be ready...")
            await wait_for_model_ready(client=client, model_id=output_model_id)

            # Hot reload the new LoRA adapter onto the deployment
            logger.info(f"[Step {step}.6] Hot reloading new LoRA adapter...")
            await load_lora_adapter(
                client=client,
                deployment_name=deployment_name,
                model_name=output_model_name,
            )

            # Wait for LoRA adapter to be fully deployed by polling deployed model state
            logger.info(f"[Step {step}.7] Waiting for LoRA adapter to be deployed...")
            await wait_for_lora_deployed(
                client=client,
                model_name=output_model_name,
                timeout_seconds=300,
                poll_interval=5,
            )

            # Use the model name (not deployed model name) for direct route in next step
            current_lora_model = output_model_name
            logger.info(f"Step {step} completed! Model {output_model_name} is now active.")

            # Clean up dataset
            logger.info(f"[Step {step}.8] Cleaning up dataset...")
            try:
                await client.datasets.delete(
                    dataset_id=dataset_id,
                )
                logger.info(f"Deleted dataset: {dataset_id}")
            except Exception as e:
                logger.warning(f"Failed to delete dataset: {e}")

        logger.info(f"Epoch {epoch + 1} completed!")

    logger.info("=" * 60)
    logger.info("RLOR training complete!")
    logger.info("=" * 60)
    total_steps = NUM_EPOCHS * num_chunks
    final_model_name = f"accounts/{ACCOUNT_ID}/models/gsm8k-rl-model-{RUN_ID}-v{total_steps}"
    logger.info(f"Final model: {final_model_name}")


if __name__ == "__main__":
    asyncio.run(run_gsm8k_rlor())
