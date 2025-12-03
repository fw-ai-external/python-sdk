"""
Iterative Reinforcement Learning Workflow using the Fireworks SDK.

This script demonstrates an iterative reinforcement learning workflow where:
1. A deployment is created with hot reload enabled
2. For each RL step:
   - Generate rollouts using concurrent inference
   - Create and upload a dataset with rollouts and rewards
   - Run a reinforcement fine-tuning step
   - Wait for training completion
   - Hot reload the new LoRA adapter onto the deployment
   - Clean up the dataset
"""

from __future__ import annotations

import os
import json
import time
import random
import asyncio
import logging
from typing import Any
from collections import defaultdict

from dotenv import load_dotenv  # type: ignore[import-not-found]

from fireworks import AsyncFireworks
from fireworks._compat import model_dump

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


# Configuration
ACCOUNT_ID = os.environ["FIREWORKS_ACCOUNT_ID"]
BASE_MODEL = "accounts/fireworks/models/qwen2p5-7b-instruct"
DEPLOYMENT_ID = "my-base-deployment"
NUM_STEPS = 2
NUM_PROMPTS = 2
NUM_GENERATIONS_PER_PROMPT = 2
CONCURRENCY = 4
ROLLOUTS_DIR = "rollouts"

# Generate a unique run ID for this workflow execution
RUN_ID = int(time.time())


async def wait_for_deployment_ready(
    client: AsyncFireworks,
    deployment_id: str,
    timeout_seconds: int = 600,
    poll_interval: int = 10,
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
) -> dict[str, Any]:
    """Create a deployment with hot reload enabled, or get existing one."""
    logger.info(f"Checking for existing deployment: {deployment_id}")
    try:
        deployment = await client.deployments.get(deployment_id=deployment_id)
        logger.info(f"Found existing deployment: {deployment.name}")
        return model_dump(deployment)
    except Exception:
        logger.info(f"Creating deployment {deployment_id} with hot reload enabled...")
        logger.info(f"  Base model: {base_model}")
        deployment = await client.deployments.create(
            base_model=base_model,
            deployment_id=deployment_id,
            enable_hot_reload_latest_addon=True,
            min_replica_count=1,
            max_replica_count=1,
            accelerator_type="NVIDIA_H100_80GB",
        )
        logger.info(f"Created deployment: {deployment.name}")
        return model_dump(deployment)


async def generate_rollouts_and_rewards(
    client: AsyncFireworks,
    model: str,
    num_prompts: int = 10,
    num_generations_per_prompt: int = 8,
    concurrency: int = 100,
) -> list[dict[str, Any]]:
    """
    Generate rollouts and compute rewards for the given model using concurrent generation.
    Each sample contains multiple generations for Policy Optimization.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def generate_single_response(prompt_id: int, generation_id: int) -> dict[str, Any]:
        """Generate a single response for a given prompt."""
        async with semaphore:
            from fireworks.types.shared_params.chat_message import ChatMessage

            messages: list[ChatMessage] = [{"role": "user", "content": f"What is {prompt_id} + {prompt_id}?"}]

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=1.5,  # Higher temperature for more diverse responses
            )

            assistant_message = response.choices[0].message.content or ""

            # Randomize the reward score
            reward = random.random()

            return {
                "prompt_id": prompt_id,
                "generation_id": generation_id,
                "messages": messages + [{"role": "assistant", "content": assistant_message}],
                "evals": {"score": reward},
            }

    # Create all generation tasks concurrently
    tasks: list[asyncio.Task[dict[str, Any]]] = []
    for prompt_id in range(num_prompts):
        for generation_id in range(num_generations_per_prompt):
            task = asyncio.create_task(generate_single_response(prompt_id, generation_id))
            tasks.append(task)

    # Execute all generations concurrently
    logger.info(f"Starting {len(tasks)} concurrent generations...")
    start_time = time.time()
    num_completed = 0
    results: list[dict[str, Any]] = []

    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        num_completed += 1
        if num_completed % 10 == 0:
            elapsed = time.time() - start_time
            rate = num_completed / elapsed if elapsed > 0 else 0
            logger.info(f"Completed {num_completed}/{len(tasks)} generations ({rate:.1f}/s)")

    total_time = time.time() - start_time
    logger.info(f"All generations completed in {total_time:.1f}s")

    # Group results by prompt_id to create dataset rows
    prompt_generations_map: defaultdict[int, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        prompt_generations_map[result["prompt_id"]].append(result)

    dataset_rows: list[dict[str, Any]] = []
    for prompt_id in range(num_prompts):
        prompt_generations: list[dict[str, Any]] = prompt_generations_map[prompt_id]
        sample_generations: list[dict[str, Any]] = [
            {"messages": gen["messages"], "evals": gen["evals"]} for gen in prompt_generations
        ]
        dataset_rows.append({"samples": sample_generations})

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
            "display_name": f"RL Training Dataset - {dataset_id}",
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

    # Poll until dataset is ready (per README instructions)
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
    timeout_seconds: int = 3600,
    poll_interval: int = 10,
) -> dict[str, Any]:
    """Wait for a reinforcement fine-tuning step to complete."""
    logger.info(f"Waiting for training job {job_id} to complete (timeout: {timeout_seconds}s)...")
    start_time = time.time()

    # Terminal failure states (matching sdks/ raise_if_bad_state)
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

    The replace_merged_addon=True flag merges the new addon to the base model
    while unmerging/deleting any existing addon in the deployment.
    """
    logger.info("Loading LoRA adapter onto deployment...")
    logger.info(f"  Model: {model_name}")
    logger.info(f"  Deployment: {deployment_name}")
    await client.lora.load(
        model=model_name,
        deployment=deployment_name,
        replace_merged_addon=True,
    )
    logger.info("LoRA adapter loaded successfully")


async def run_reinforcement_learning() -> None:
    """Main function to run the iterative reinforcement learning workflow."""
    # Use default production client
    client = AsyncFireworks()

    logger.info("=" * 60)
    logger.info("Iterative Reinforcement Learning Workflow")
    logger.info("=" * 60)

    # Step 1: Create or get the base deployment
    logger.info("[Step 0] Setting up base deployment...")
    await create_or_get_deployment(
        client=client,
        deployment_id=DEPLOYMENT_ID,
        base_model=BASE_MODEL,
    )

    # Wait for deployment to be ready
    await wait_for_deployment_ready(
        client=client,
        deployment_id=DEPLOYMENT_ID,
    )

    # Iterative reinforcement learning loop
    deployment_name = f"accounts/{ACCOUNT_ID}/deployments/{DEPLOYMENT_ID}"

    for step in range(NUM_STEPS):
        logger.info("=" * 60)
        logger.info(f"Starting reinforcement learning step {step + 1}/{NUM_STEPS}")
        logger.info("=" * 60)

        # Generate rollouts and rewards using the deployment
        # (after step 0, the deployment will have the LoRA adapter loaded via hot reload)
        logger.info(f"[Step {step + 1}.1] Generating rollouts and computing rewards...")
        dataset_rows = await generate_rollouts_and_rewards(
            client=client,
            model=deployment_name,
            num_prompts=NUM_PROMPTS,
            num_generations_per_prompt=NUM_GENERATIONS_PER_PROMPT,
            concurrency=CONCURRENCY,
        )

        # Save rollouts to local file for inspection
        rollouts_filepath = save_rollouts_to_file(dataset_rows, step)

        # Create and upload dataset
        dataset_id = f"rl-dataset-{RUN_ID}-step-{step + 1}"
        logger.info(f"[Step {step + 1}.2] Creating and uploading dataset...")
        dataset_name = await create_and_upload_dataset(
            client=client,
            dataset_id=dataset_id,
            rollouts_filepath=rollouts_filepath,
        )

        # Create reinforcement fine-tuning step
        output_model_name = f"accounts/{ACCOUNT_ID}/models/rl-model-{RUN_ID}-v{step + 1}"
        from fireworks.types.shared_params.training_config import TrainingConfig

        training_config: TrainingConfig = {
            "output_model": output_model_name,
            "epochs": 1,
            "learning_rate": 1e-5,
        }
        if step == 0:
            training_config["base_model"] = BASE_MODEL
        else:
            training_config["warm_start_from"] = f"accounts/{ACCOUNT_ID}/models/rl-model-{RUN_ID}-v{step}"

        job_id = f"rl-job-{RUN_ID}-step-{step + 1}"
        logger.info(f"[Step {step + 1}.3] Starting reinforcement fine-tuning step...")
        logger.info(f"Creating job with ID: {job_id}")
        job = await client.reinforcement_fine_tuning_steps.create(
            rlor_trainer_job_id=job_id,
            dataset=dataset_name,
            display_name=f"RL Step {step + 1}",
            training_config=training_config,
        )
        logger.info(f"Created training job: {job.name}")

        # Wait for training completion
        logger.info(f"[Step {step + 1}.4] Waiting for training to complete...")
        await wait_for_training_completion(client=client, job_id=job_id)

        # Wait for the output model to be ready
        output_model_id = f"rl-model-{RUN_ID}-v{step + 1}"
        logger.info(f"[Step {step + 1}.5] Waiting for model to be ready...")
        await wait_for_model_ready(client=client, model_id=output_model_id)

        # Hot reload the new LoRA adapter onto the deployment
        # This swaps the model on the deployment without restarting it
        logger.info(f"[Step {step + 1}.6] Hot reloading new LoRA adapter...")
        await load_lora_adapter(
            client=client,
            deployment_name=deployment_name,
            model_name=output_model_name,
        )

        logger.info(f"Step {step + 1} completed! Model {output_model_name} is now active.")

        # Step 8: Clean up dataset
        logger.info(f"[Step {step + 1}.7] Cleaning up dataset...")
        try:
            await client.datasets.delete(
                dataset_id=dataset_id,
            )
            logger.info(f"Deleted dataset: {dataset_id}")
        except Exception as e:
            logger.warning(f"Failed to delete dataset: {e}")

    logger.info("=" * 60)
    logger.info("Reinforcement learning complete!")
    logger.info("=" * 60)
    final_model_name = f"accounts/{ACCOUNT_ID}/models/rl-model-{RUN_ID}-v{NUM_STEPS}"
    logger.info(f"Final model: {final_model_name}")


if __name__ == "__main__":
    asyncio.run(run_reinforcement_learning())
