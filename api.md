# Accounts

Types:

```python
from fireworks_ai.types import Account, AccountListResponse
```

Methods:

- <code title="get /v1/accounts">client.accounts.<a href="./src/fireworks_ai/resources/accounts.py">list</a>(\*\*<a href="src/fireworks_ai/types/account_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/account_list_response.py">AccountListResponse</a></code>
- <code title="get /v1/accounts/{account_id}">client.accounts.<a href="./src/fireworks_ai/resources/accounts.py">get</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/account.py">Account</a></code>

# BatchInferenceJobs

Types:

```python
from fireworks_ai.types import (
    BatchInferenceJobCreateResponse,
    BatchInferenceJobListResponse,
    BatchInferenceJobGetResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/batchInferenceJobs">client.batch_inference_jobs.<a href="./src/fireworks_ai/resources/batch_inference_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/batch_inference_job_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/batch_inference_job_create_response.py">BatchInferenceJobCreateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/batchInferenceJobs">client.batch_inference_jobs.<a href="./src/fireworks_ai/resources/batch_inference_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/batch_inference_job_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/batch_inference_job_list_response.py">BatchInferenceJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}">client.batch_inference_jobs.<a href="./src/fireworks_ai/resources/batch_inference_jobs.py">delete</a>(batch_inference_job_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}">client.batch_inference_jobs.<a href="./src/fireworks_ai/resources/batch_inference_jobs.py">get</a>(batch_inference_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/batch_inference_job_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/batch_inference_job_get_response.py">BatchInferenceJobGetResponse</a></code>

# Datasets

Types:

```python
from fireworks_ai.types import (
    DatasetCreateResponse,
    DatasetUpdateResponse,
    DatasetListResponse,
    DatasetGetResponse,
    DatasetGetUploadEndpointResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/datasets">client.datasets.<a href="./src/fireworks_ai/resources/datasets.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/dataset_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/dataset_create_response.py">DatasetCreateResponse</a></code>
- <code title="patch /v1/accounts/{account_id}/datasets/{dataset_id}">client.datasets.<a href="./src/fireworks_ai/resources/datasets.py">update</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/dataset_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/dataset_update_response.py">DatasetUpdateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/datasets">client.datasets.<a href="./src/fireworks_ai/resources/datasets.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/dataset_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/dataset_list_response.py">DatasetListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/datasets/{dataset_id}">client.datasets.<a href="./src/fireworks_ai/resources/datasets.py">delete</a>(dataset_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/datasets/{dataset_id}">client.datasets.<a href="./src/fireworks_ai/resources/datasets.py">get</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/dataset_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/dataset_get_response.py">DatasetGetResponse</a></code>
- <code title="post /v1/accounts/{account_id}/datasets/{dataset_id}:getUploadEndpoint">client.datasets.<a href="./src/fireworks_ai/resources/datasets.py">get_upload_endpoint</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/dataset_get_upload_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/dataset_get_upload_endpoint_response.py">DatasetGetUploadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/datasets/{dataset_id}:validateUpload">client.datasets.<a href="./src/fireworks_ai/resources/datasets.py">validate_upload</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/dataset_validate_upload_params.py">params</a>) -> object</code>

# DeployedModels

Types:

```python
from fireworks_ai.types import (
    DeployedModelCreateResponse,
    DeployedModelUpdateResponse,
    DeployedModelListResponse,
    DeployedModelGetResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/deployedModels">client.deployed_models.<a href="./src/fireworks_ai/resources/deployed_models.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/deployed_model_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployed_model_create_response.py">DeployedModelCreateResponse</a></code>
- <code title="patch /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.deployed_models.<a href="./src/fireworks_ai/resources/deployed_models.py">update</a>(deployed_model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/deployed_model_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployed_model_update_response.py">DeployedModelUpdateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/deployedModels">client.deployed_models.<a href="./src/fireworks_ai/resources/deployed_models.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/deployed_model_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployed_model_list_response.py">DeployedModelListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.deployed_models.<a href="./src/fireworks_ai/resources/deployed_models.py">delete</a>(deployed_model_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.deployed_models.<a href="./src/fireworks_ai/resources/deployed_models.py">get</a>(deployed_model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/deployed_model_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployed_model_get_response.py">DeployedModelGetResponse</a></code>

# Deployments

Types:

```python
from fireworks_ai.types import (
    DeploymentCreateResponse,
    DeploymentUpdateResponse,
    DeploymentListResponse,
    DeploymentGetResponse,
    DeploymentUndeleteResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/deployments">client.deployments.<a href="./src/fireworks_ai/resources/deployments.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/deployment_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployment_create_response.py">DeploymentCreateResponse</a></code>
- <code title="patch /v1/accounts/{account_id}/deployments/{deployment_id}">client.deployments.<a href="./src/fireworks_ai/resources/deployments.py">update</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/deployment_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployment_update_response.py">DeploymentUpdateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/deployments">client.deployments.<a href="./src/fireworks_ai/resources/deployments.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/deployment_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployment_list_response.py">DeploymentListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/deployments/{deployment_id}">client.deployments.<a href="./src/fireworks_ai/resources/deployments.py">delete</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/deployment_delete_params.py">params</a>) -> object</code>
- <code title="get /v1/accounts/{account_id}/deployments/{deployment_id}">client.deployments.<a href="./src/fireworks_ai/resources/deployments.py">get</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/deployment_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployment_get_response.py">DeploymentGetResponse</a></code>
- <code title="post /v1/accounts/{account_id}/deployments/{deployment_id}:undelete">client.deployments.<a href="./src/fireworks_ai/resources/deployments.py">undelete</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/deployment_undelete_params.py">params</a>) -> <a href="./src/fireworks_ai/types/deployment_undelete_response.py">DeploymentUndeleteResponse</a></code>

# Models

Types:

```python
from fireworks_ai.types import (
    ModelCreateResponse,
    ModelUpdateResponse,
    ModelListResponse,
    ModelGetResponse,
    ModelGetDownloadEndpointResponse,
    ModelGetUploadEndpointResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/models">client.models.<a href="./src/fireworks_ai/resources/models.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/model_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/model_create_response.py">ModelCreateResponse</a></code>
- <code title="patch /v1/accounts/{account_id}/models/{model_id}">client.models.<a href="./src/fireworks_ai/resources/models.py">update</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/model_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/model_update_response.py">ModelUpdateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/models">client.models.<a href="./src/fireworks_ai/resources/models.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/model_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/model_list_response.py">ModelListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/models/{model_id}">client.models.<a href="./src/fireworks_ai/resources/models.py">delete</a>(model_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}">client.models.<a href="./src/fireworks_ai/resources/models.py">get</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/model_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/model_get_response.py">ModelGetResponse</a></code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}:getDownloadEndpoint">client.models.<a href="./src/fireworks_ai/resources/models.py">get_download_endpoint</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/model_get_download_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/model_get_download_endpoint_response.py">ModelGetDownloadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/models/{model_id}:getUploadEndpoint">client.models.<a href="./src/fireworks_ai/resources/models.py">get_upload_endpoint</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/model_get_upload_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/model_get_upload_endpoint_response.py">ModelGetUploadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/models/{model_id}:prepare">client.models.<a href="./src/fireworks_ai/resources/models.py">prepare</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/model_prepare_params.py">params</a>) -> object</code>

# ReinforcementFineTuningJobs

Types:

```python
from fireworks_ai.types import (
    ReinforcementFineTuningJobCreateResponse,
    ReinforcementFineTuningJobListResponse,
    ReinforcementFineTuningJobGetResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/reinforcementFineTuningJobs">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/reinforcement_fine_tuning_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/reinforcement_fine_tuning_job_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/reinforcement_fine_tuning_job_create_response.py">ReinforcementFineTuningJobCreateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/reinforcementFineTuningJobs">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/reinforcement_fine_tuning_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/reinforcement_fine_tuning_job_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/reinforcement_fine_tuning_job_list_response.py">ReinforcementFineTuningJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/reinforcement_fine_tuning_jobs.py">delete</a>(reinforcement_fine_tuning_job_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/reinforcement_fine_tuning_jobs.py">get</a>(reinforcement_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/reinforcement_fine_tuning_job_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/reinforcement_fine_tuning_job_get_response.py">ReinforcementFineTuningJobGetResponse</a></code>

# SupervisedFineTuningJobs

Types:

```python
from fireworks_ai.types import (
    SupervisedFineTuningJobCreateResponse,
    SupervisedFineTuningJobListResponse,
    SupervisedFineTuningJobGetResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/supervisedFineTuningJobs">client.supervised_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/supervised_fine_tuning_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/supervised_fine_tuning_job_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/supervised_fine_tuning_job_create_response.py">SupervisedFineTuningJobCreateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/supervisedFineTuningJobs">client.supervised_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/supervised_fine_tuning_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/supervised_fine_tuning_job_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/supervised_fine_tuning_job_list_response.py">SupervisedFineTuningJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}">client.supervised_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/supervised_fine_tuning_jobs.py">delete</a>(supervised_fine_tuning_job_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}">client.supervised_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/supervised_fine_tuning_jobs.py">get</a>(supervised_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/supervised_fine_tuning_job_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/supervised_fine_tuning_job_get_response.py">SupervisedFineTuningJobGetResponse</a></code>

# Users

Types:

```python
from fireworks_ai.types import (
    UserCreateResponse,
    UserUpdateResponse,
    UserListResponse,
    UserGetResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/users">client.users.<a href="./src/fireworks_ai/resources/users.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/user_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/user_create_response.py">UserCreateResponse</a></code>
- <code title="patch /v1/accounts/{account_id}/users/{user_id}">client.users.<a href="./src/fireworks_ai/resources/users.py">update</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/user_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/user_update_response.py">UserUpdateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/users">client.users.<a href="./src/fireworks_ai/resources/users.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/user_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/user_list_response.py">UserListResponse</a></code>
- <code title="get /v1/accounts/{account_id}/users/{user_id}">client.users.<a href="./src/fireworks_ai/resources/users.py">get</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/user_get_params.py">params</a>) -> <a href="./src/fireworks_ai/types/user_get_response.py">UserGetResponse</a></code>

# APIKeys

Types:

```python
from fireworks_ai.types import APIKeyCreateResponse, APIKeyListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/users/{user_id}/apiKeys">client.api_keys.<a href="./src/fireworks_ai/resources/api_keys.py">create</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/api_key_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/api_key_create_response.py">APIKeyCreateResponse</a></code>
- <code title="get /v1/accounts/{account_id}/users/{user_id}/apiKeys">client.api_keys.<a href="./src/fireworks_ai/resources/api_keys.py">list</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/api_key_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/api_key_list_response.py">APIKeyListResponse</a></code>
- <code title="post /v1/accounts/{account_id}/users/{user_id}/apiKeys:delete">client.api_keys.<a href="./src/fireworks_ai/resources/api_keys.py">delete</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/api_key_delete_params.py">params</a>) -> object</code>
