import os
import json
import time

import httpx
from dotenv import load_dotenv

from fireworks import Fireworks, ConflictError
from fireworks.types import Dataset

load_dotenv()

# Constants
TRAIN_FILE_NAME = "train.jsonl"
EVALUATION_FILE_NAME = "evaluation.jsonl"
TRAIN_DATASET_ID = "train-dataset"
EVALUATION_DATASET_ID = "evaluation-dataset"
MODEL_NAME = "accounts/fireworks/models/qwen3-30b-a3b-instruct-2507"
SFTJ_DISPLAY_NAME = "My Supervised Fine-Tuning Job"
SFTJ_LEARNING_RATE = 1e-5
SFTJ_LEARNING_RATE_WARMUP_STEPS = 200
SFTJ_EPOCHS = 1
SFTJ_LORA_RANK = 16
SFTJ_GRADIENT_ACCUMULATION_STEPS = 2
SFTJ_BATCH_SIZE = 16384
SFTJ_MAX_CONTEXT_LENGTH = 16384


def create_and_upload_dataset(
    client: Fireworks, dataset_id: str, file_name: str, example_count: int
) -> Dataset:
    """Create a dataset, upload a file, and validate the upload to Fireworks."""
    # Create the dataset (skip if it already exists)
    try:
        dataset = client.datasets.create(
            dataset_id=dataset_id,
            dataset={
                "exampleCount": example_count,
            },
        )
    except ConflictError:
        print(f"Dataset {dataset_id} already exists, skipping creation")
        dataset = client.datasets.get(dataset_id=dataset_id)
        return dataset

    # Upload the file
    upload_endpoint = client.datasets.get_upload_endpoint(
        dataset_id=dataset_id,
        filename_to_size={
            file_name: os.path.getsize(file_name),
        },
    )

    with open(file_name, "rb") as f:
        response = httpx.put(
            upload_endpoint.filename_to_signed_urls[file_name],
            content=f.read(),
            headers={
                "Content-Type": "application/octet-stream",
                "x-goog-content-length-range": f"{os.path.getsize(file_name)},{os.path.getsize(file_name)}",
            },
        )
        response.raise_for_status()

    # Validate the upload
    client.datasets.validate_upload(dataset_id=dataset_id, body={})

    return dataset


# 0) write jsonl to a file
train_dataset = [
    {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "Paris."},
        ]
    }
]
evaluation_dataset = [
    {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "Paris."},
        ]
    }
]
with open(TRAIN_FILE_NAME, "w") as f:
    for item in train_dataset:
        f.write(json.dumps(item) + "\n")
with open(EVALUATION_FILE_NAME, "w") as f:
    for item in evaluation_dataset:
        f.write(json.dumps(item) + "\n")

# Remember to set the environment variables:
# FIREWORKS_ACCOUNT_ID="your-account-id"
# FIREWORKS_API_KEY="your-api-key"
client = Fireworks()

# 1) Upload dataset
train_dataset = create_and_upload_dataset(
    client, TRAIN_DATASET_ID, TRAIN_FILE_NAME, len(train_dataset)
)
evaluation_dataset = create_and_upload_dataset(
    client, EVALUATION_DATASET_ID, EVALUATION_FILE_NAME, len(evaluation_dataset)
)

# 2) Create SFTJ
sftj = client.supervised_fine_tuning_jobs.create(
    dataset=train_dataset.name,
    evaluation_dataset=evaluation_dataset.name,
    base_model=MODEL_NAME,
    display_name=SFTJ_DISPLAY_NAME,
    learning_rate=SFTJ_LEARNING_RATE,
    learning_rate_warmup_steps=SFTJ_LEARNING_RATE_WARMUP_STEPS,
    epochs=SFTJ_EPOCHS,
    lora_rank=SFTJ_LORA_RANK,
    gradient_accumulation_steps=SFTJ_GRADIENT_ACCUMULATION_STEPS,
    batch_size=SFTJ_BATCH_SIZE,
    max_context_length=SFTJ_MAX_CONTEXT_LENGTH,
)

print("Go to the following URL to monitor the SFTJ:")
print(
    f"https://app.fireworks.ai/dashboard/fine-tuning/supervised/{sftj.name.split('/')[-1]}"
)

while sftj.state != "JOB_STATE_COMPLETED":
    time.sleep(5)
    sftj_id = sftj.name.split("/")[-1]
    sftj = client.supervised_fine_tuning_jobs.get(sftj_id)
    print(f"SFTJ state: {sftj.state}")

print("SFTJ completed")
