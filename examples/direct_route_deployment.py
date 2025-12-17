import time
from typing import Optional
from typing_extensions import Literal

from dotenv import load_dotenv  # type: ignore[import-not-found]

import fireworks
from fireworks import Fireworks
from fireworks.types import Deployment

load_dotenv()

DEPLOYMENT_ID = "test-deployment-v4"
DIRECT_ROUTE_API_KEY = "MY_API_KEY"
MODEL_NAME = "accounts/fireworks/models/qwen3-0p6b"
DIRECT_ROUTE_TYPE: Literal["INTERNET"] = "INTERNET"
ACCELERATOR_TYPE: Literal["NVIDIA_H200_141GB"] = "NVIDIA_H200_141GB"
PLACEMENT_REGION: Literal["US_VIRGINIA_1"] = "US_VIRGINIA_1"
POLL_INTERVAL_SECONDS = 1

client = Fireworks()

deployment: Optional[Deployment] = None
try:
    deployment = client.deployments.get(deployment_id=DEPLOYMENT_ID)
except fireworks.NotFoundError:
    pass

if deployment is None:
    print("Creating deployment...")
    deployment = client.deployments.create(
        base_model=MODEL_NAME,
        deployment_id=DEPLOYMENT_ID,
        direct_route_type=DIRECT_ROUTE_TYPE,
        direct_route_api_keys=[DIRECT_ROUTE_API_KEY],
        accelerator_type=ACCELERATOR_TYPE,
        placement={"region": PLACEMENT_REGION},
    )
elif deployment.state == "DELETED" or deployment.state == "DELETING":
    print(
        "Deployment with ID is deleted meaning it won't show in the UI "
        "but is queryable via API, update the DEPLOYMENT_ID to a new value"
    )
    exit(1)
else:
    print(f"Deployment {DEPLOYMENT_ID} already exists and is not deleted")
if deployment.name is None:
    raise ValueError("Deployment name is None")
deployment_id = deployment.name.split("/")[-1]
print(f"You can monitor the deployment at: https://app.fireworks.ai/dashboard/deployments/{deployment_id}")

print("Polling for deployment to be ready...")
while deployment.state != "READY":
    time.sleep(POLL_INTERVAL_SECONDS)
    deployment = client.deployments.get(deployment_id=deployment_id)
    print(f"Deployment state: {deployment.state}")

if deployment.name is None:
    raise ValueError("Deployment name is None")
print(f"Deployment is ready! {deployment.name}")

if deployment.direct_route_handle is None:
    raise ValueError("Deployment direct_route_handle is None")
direct_route_client = Fireworks(
    base_url=f"https://{deployment.direct_route_handle}",
    api_key=DIRECT_ROUTE_API_KEY,
)

response = direct_route_client.chat.completions.create(
    model=MODEL_NAME,
    messages=[{"role": "user", "content": "Hello!"}],
)

print(response.choices[0].message.content)

print("--------------------------------")
# Prompt user y/n to delete the deployment
delete_deployment = input("Do you want to delete the deployment? (y/n): ")
if delete_deployment == "y":
    print("Deleting deployment...")
    client.deployments.delete(deployment_id=deployment_id, ignore_checks=True)
    print(f"Deployment {deployment_id} deleted")
else:
    print("Deployment not deleted")
