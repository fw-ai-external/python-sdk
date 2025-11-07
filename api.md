# Shared Types

```python
from fireworks.types import (
    DeployedModel,
    DeployedModelRef,
    InferenceParameters,
    Status,
    WandbConfig,
)
```

# Accounts

Types:

```python
from fireworks.types import Account, AccountListResponse
```

Methods:

- <code title="get /v1/accounts">client.accounts.<a href="./src/fireworks/resources/accounts.py">list</a>(\*\*<a href="src/fireworks/types/account_list_params.py">params</a>) -> <a href="./src/fireworks/types/account_list_response.py">AccountListResponse</a></code>
- <code title="get /v1/accounts/{account_id}">client.accounts.<a href="./src/fireworks/resources/accounts.py">get</a>(account_id, \*\*<a href="src/fireworks/types/account_get_params.py">params</a>) -> <a href="./src/fireworks/types/account.py">Account</a></code>

# BatchInferenceJobs

Types:

```python
from fireworks.types import BatchInferenceJob, BatchInferenceJobListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/batchInferenceJobs">client.batch_inference_jobs.<a href="./src/fireworks/resources/batch_inference_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks/types/batch_inference_job_create_params.py">params</a>) -> <a href="./src/fireworks/types/batch_inference_job.py">BatchInferenceJob</a></code>
- <code title="get /v1/accounts/{account_id}/batchInferenceJobs">client.batch_inference_jobs.<a href="./src/fireworks/resources/batch_inference_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks/types/batch_inference_job_list_params.py">params</a>) -> <a href="./src/fireworks/types/batch_inference_job_list_response.py">BatchInferenceJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}">client.batch_inference_jobs.<a href="./src/fireworks/resources/batch_inference_jobs.py">delete</a>(batch_inference_job_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}">client.batch_inference_jobs.<a href="./src/fireworks/resources/batch_inference_jobs.py">get</a>(batch_inference_job_id, \*, account_id, \*\*<a href="src/fireworks/types/batch_inference_job_get_params.py">params</a>) -> <a href="./src/fireworks/types/batch_inference_job.py">BatchInferenceJob</a></code>

# Datasets

Types:

```python
from fireworks.types import (
    Dataset,
    EvaluationResult,
    Splitted,
    Transformed,
    DatasetListResponse,
    DatasetGetUploadEndpointResponse,
    DatasetUploadResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/datasets">client.datasets.<a href="./src/fireworks/resources/datasets.py">create</a>(account_id, \*\*<a href="src/fireworks/types/dataset_create_params.py">params</a>) -> <a href="./src/fireworks/types/dataset.py">Dataset</a></code>
- <code title="patch /v1/accounts/{account_id}/datasets/{dataset_id}">client.datasets.<a href="./src/fireworks/resources/datasets.py">update</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks/types/dataset_update_params.py">params</a>) -> <a href="./src/fireworks/types/dataset.py">Dataset</a></code>
- <code title="get /v1/accounts/{account_id}/datasets">client.datasets.<a href="./src/fireworks/resources/datasets.py">list</a>(account_id, \*\*<a href="src/fireworks/types/dataset_list_params.py">params</a>) -> <a href="./src/fireworks/types/dataset_list_response.py">DatasetListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/datasets/{dataset_id}">client.datasets.<a href="./src/fireworks/resources/datasets.py">delete</a>(dataset_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/datasets/{dataset_id}">client.datasets.<a href="./src/fireworks/resources/datasets.py">get</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks/types/dataset_get_params.py">params</a>) -> <a href="./src/fireworks/types/dataset.py">Dataset</a></code>
- <code title="post /v1/accounts/{account_id}/datasets/{dataset_id}:getUploadEndpoint">client.datasets.<a href="./src/fireworks/resources/datasets.py">get_upload_endpoint</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks/types/dataset_get_upload_endpoint_params.py">params</a>) -> <a href="./src/fireworks/types/dataset_get_upload_endpoint_response.py">DatasetGetUploadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/datasets/{dataset_id}:upload">client.datasets.<a href="./src/fireworks/resources/datasets.py">upload</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks/types/dataset_upload_params.py">params</a>) -> <a href="./src/fireworks/types/dataset_upload_response.py">DatasetUploadResponse</a></code>
- <code title="post /v1/accounts/{account_id}/datasets/{dataset_id}:validateUpload">client.datasets.<a href="./src/fireworks/resources/datasets.py">validate_upload</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks/types/dataset_validate_upload_params.py">params</a>) -> object</code>

# Deployments

Types:

```python
from fireworks.types import (
    AutoTune,
    AutoscalingPolicy,
    Deployment,
    Placement,
    DeploymentListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/deployments">client.deployments.<a href="./src/fireworks/resources/deployments.py">create</a>(account_id, \*\*<a href="src/fireworks/types/deployment_create_params.py">params</a>) -> <a href="./src/fireworks/types/deployment.py">Deployment</a></code>
- <code title="patch /v1/accounts/{account_id}/deployments/{deployment_id}">client.deployments.<a href="./src/fireworks/resources/deployments.py">update</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks/types/deployment_update_params.py">params</a>) -> <a href="./src/fireworks/types/deployment.py">Deployment</a></code>
- <code title="get /v1/accounts/{account_id}/deployments">client.deployments.<a href="./src/fireworks/resources/deployments.py">list</a>(account_id, \*\*<a href="src/fireworks/types/deployment_list_params.py">params</a>) -> <a href="./src/fireworks/types/deployment_list_response.py">DeploymentListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/deployments/{deployment_id}">client.deployments.<a href="./src/fireworks/resources/deployments.py">delete</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks/types/deployment_delete_params.py">params</a>) -> object</code>
- <code title="get /v1/accounts/{account_id}/deployments/{deployment_id}">client.deployments.<a href="./src/fireworks/resources/deployments.py">get</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks/types/deployment_get_params.py">params</a>) -> <a href="./src/fireworks/types/deployment.py">Deployment</a></code>
- <code title="post /v1/accounts/{account_id}/deployments/{deployment_id}:undelete">client.deployments.<a href="./src/fireworks/resources/deployments.py">undelete</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks/types/deployment_undelete_params.py">params</a>) -> <a href="./src/fireworks/types/deployment.py">Deployment</a></code>

# Models

Types:

```python
from fireworks.types import (
    BaseModelDetails,
    ConversationConfig,
    Model,
    PeftDetails,
    TypeDate,
    ModelListResponse,
    ModelGetDownloadEndpointResponse,
    ModelGetUploadEndpointResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/models">client.models.<a href="./src/fireworks/resources/models.py">create</a>(account_id, \*\*<a href="src/fireworks/types/model_create_params.py">params</a>) -> <a href="./src/fireworks/types/model.py">Model</a></code>
- <code title="patch /v1/accounts/{account_id}/models/{model_id}">client.models.<a href="./src/fireworks/resources/models.py">update</a>(model_id, \*, account_id, \*\*<a href="src/fireworks/types/model_update_params.py">params</a>) -> <a href="./src/fireworks/types/model.py">Model</a></code>
- <code title="get /v1/accounts/{account_id}/models">client.models.<a href="./src/fireworks/resources/models.py">list</a>(account_id, \*\*<a href="src/fireworks/types/model_list_params.py">params</a>) -> <a href="./src/fireworks/types/model_list_response.py">ModelListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/models/{model_id}">client.models.<a href="./src/fireworks/resources/models.py">delete</a>(model_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}">client.models.<a href="./src/fireworks/resources/models.py">get</a>(model_id, \*, account_id, \*\*<a href="src/fireworks/types/model_get_params.py">params</a>) -> <a href="./src/fireworks/types/model.py">Model</a></code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}:getDownloadEndpoint">client.models.<a href="./src/fireworks/resources/models.py">get_download_endpoint</a>(model_id, \*, account_id, \*\*<a href="src/fireworks/types/model_get_download_endpoint_params.py">params</a>) -> <a href="./src/fireworks/types/model_get_download_endpoint_response.py">ModelGetDownloadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/models/{model_id}:getUploadEndpoint">client.models.<a href="./src/fireworks/resources/models.py">get_upload_endpoint</a>(model_id, \*, account_id, \*\*<a href="src/fireworks/types/model_get_upload_endpoint_params.py">params</a>) -> <a href="./src/fireworks/types/model_get_upload_endpoint_response.py">ModelGetUploadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/models/{model_id}:prepare">client.models.<a href="./src/fireworks/resources/models.py">prepare</a>(model_id, \*, account_id, \*\*<a href="src/fireworks/types/model_prepare_params.py">params</a>) -> object</code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}:validateUpload">client.models.<a href="./src/fireworks/resources/models.py">validate_upload</a>(model_id, \*, account_id, \*\*<a href="src/fireworks/types/model_validate_upload_params.py">params</a>) -> object</code>

# ReinforcementFineTuningJobs

Types:

```python
from fireworks.types import ReinforcementFineTuningJob, ReinforcementFineTuningJobListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/reinforcementFineTuningJobs">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks/resources/reinforcement_fine_tuning_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks/types/reinforcement_fine_tuning_job_create_params.py">params</a>) -> <a href="./src/fireworks/types/reinforcement_fine_tuning_job.py">ReinforcementFineTuningJob</a></code>
- <code title="get /v1/accounts/{account_id}/reinforcementFineTuningJobs">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks/resources/reinforcement_fine_tuning_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks/types/reinforcement_fine_tuning_job_list_params.py">params</a>) -> <a href="./src/fireworks/types/reinforcement_fine_tuning_job_list_response.py">ReinforcementFineTuningJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks/resources/reinforcement_fine_tuning_jobs.py">delete</a>(reinforcement_fine_tuning_job_id, \*, account_id) -> object</code>
- <code title="post /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}:cancel">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks/resources/reinforcement_fine_tuning_jobs.py">cancel</a>(reinforcement_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks/types/reinforcement_fine_tuning_job_cancel_params.py">params</a>) -> object</code>
- <code title="get /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks/resources/reinforcement_fine_tuning_jobs.py">get</a>(reinforcement_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks/types/reinforcement_fine_tuning_job_get_params.py">params</a>) -> <a href="./src/fireworks/types/reinforcement_fine_tuning_job.py">ReinforcementFineTuningJob</a></code>
- <code title="post /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}:resume">client.reinforcement_fine_tuning_jobs.<a href="./src/fireworks/resources/reinforcement_fine_tuning_jobs.py">resume</a>(reinforcement_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks/types/reinforcement_fine_tuning_job_resume_params.py">params</a>) -> <a href="./src/fireworks/types/reinforcement_fine_tuning_job.py">ReinforcementFineTuningJob</a></code>

# SupervisedFineTuningJobs

Types:

```python
from fireworks.types import SupervisedFineTuningJob, SupervisedFineTuningJobListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/supervisedFineTuningJobs">client.supervised_fine_tuning_jobs.<a href="./src/fireworks/resources/supervised_fine_tuning_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks/types/supervised_fine_tuning_job_create_params.py">params</a>) -> <a href="./src/fireworks/types/supervised_fine_tuning_job.py">SupervisedFineTuningJob</a></code>
- <code title="get /v1/accounts/{account_id}/supervisedFineTuningJobs">client.supervised_fine_tuning_jobs.<a href="./src/fireworks/resources/supervised_fine_tuning_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks/types/supervised_fine_tuning_job_list_params.py">params</a>) -> <a href="./src/fireworks/types/supervised_fine_tuning_job_list_response.py">SupervisedFineTuningJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}">client.supervised_fine_tuning_jobs.<a href="./src/fireworks/resources/supervised_fine_tuning_jobs.py">delete</a>(supervised_fine_tuning_job_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}">client.supervised_fine_tuning_jobs.<a href="./src/fireworks/resources/supervised_fine_tuning_jobs.py">get</a>(supervised_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks/types/supervised_fine_tuning_job_get_params.py">params</a>) -> <a href="./src/fireworks/types/supervised_fine_tuning_job.py">SupervisedFineTuningJob</a></code>
- <code title="post /v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}:resume">client.supervised_fine_tuning_jobs.<a href="./src/fireworks/resources/supervised_fine_tuning_jobs.py">resume</a>(supervised_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks/types/supervised_fine_tuning_job_resume_params.py">params</a>) -> <a href="./src/fireworks/types/supervised_fine_tuning_job.py">SupervisedFineTuningJob</a></code>

# Users

Types:

```python
from fireworks.types import User, UserListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/users">client.users.<a href="./src/fireworks/resources/users.py">create</a>(account_id, \*\*<a href="src/fireworks/types/user_create_params.py">params</a>) -> <a href="./src/fireworks/types/user.py">User</a></code>
- <code title="patch /v1/accounts/{account_id}/users/{user_id}">client.users.<a href="./src/fireworks/resources/users.py">update</a>(user_id, \*, account_id, \*\*<a href="src/fireworks/types/user_update_params.py">params</a>) -> <a href="./src/fireworks/types/user.py">User</a></code>
- <code title="get /v1/accounts/{account_id}/users">client.users.<a href="./src/fireworks/resources/users.py">list</a>(account_id, \*\*<a href="src/fireworks/types/user_list_params.py">params</a>) -> <a href="./src/fireworks/types/user_list_response.py">UserListResponse</a></code>
- <code title="get /v1/accounts/{account_id}/users/{user_id}">client.users.<a href="./src/fireworks/resources/users.py">get</a>(user_id, \*, account_id, \*\*<a href="src/fireworks/types/user_get_params.py">params</a>) -> <a href="./src/fireworks/types/user.py">User</a></code>

# APIKeys

Types:

```python
from fireworks.types import APIKey, APIKeyListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/users/{user_id}/apiKeys">client.api_keys.<a href="./src/fireworks/resources/api_keys.py">create</a>(user_id, \*, account_id, \*\*<a href="src/fireworks/types/api_key_create_params.py">params</a>) -> <a href="./src/fireworks/types/api_key.py">APIKey</a></code>
- <code title="get /v1/accounts/{account_id}/users/{user_id}/apiKeys">client.api_keys.<a href="./src/fireworks/resources/api_keys.py">list</a>(user_id, \*, account_id, \*\*<a href="src/fireworks/types/api_key_list_params.py">params</a>) -> <a href="./src/fireworks/types/api_key_list_response.py">APIKeyListResponse</a></code>
- <code title="post /v1/accounts/{account_id}/users/{user_id}/apiKeys:delete">client.api_keys.<a href="./src/fireworks/resources/api_keys.py">delete</a>(user_id, \*, account_id, \*\*<a href="src/fireworks/types/api_key_delete_params.py">params</a>) -> object</code>

# Lora

Types:

```python
from fireworks.types import LoraListResponse
```

Methods:

- <code title="patch /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.lora.<a href="./src/fireworks/resources/lora.py">update</a>(deployed_model_id, \*, account_id, \*\*<a href="src/fireworks/types/lora_update_params.py">params</a>) -> <a href="./src/fireworks/types/shared/deployed_model.py">DeployedModel</a></code>
- <code title="get /v1/accounts/{account_id}/deployedModels">client.lora.<a href="./src/fireworks/resources/lora.py">list</a>(account_id, \*\*<a href="src/fireworks/types/lora_list_params.py">params</a>) -> <a href="./src/fireworks/types/lora_list_response.py">LoraListResponse</a></code>
- <code title="get /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.lora.<a href="./src/fireworks/resources/lora.py">get</a>(deployed_model_id, \*, account_id, \*\*<a href="src/fireworks/types/lora_get_params.py">params</a>) -> <a href="./src/fireworks/types/shared/deployed_model.py">DeployedModel</a></code>
- <code title="post /v1/accounts/{account_id}/deployedModels">client.lora.<a href="./src/fireworks/resources/lora.py">load</a>(account_id, \*\*<a href="src/fireworks/types/lora_load_params.py">params</a>) -> <a href="./src/fireworks/types/shared/deployed_model.py">DeployedModel</a></code>
- <code title="delete /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.lora.<a href="./src/fireworks/resources/lora.py">unload</a>(deployed_model_id, \*, account_id) -> object</code>

# Secrets

Types:

```python
from fireworks.types import Secret, SecretListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/secrets">client.secrets.<a href="./src/fireworks/resources/secrets.py">create</a>(account_id, \*\*<a href="src/fireworks/types/secret_create_params.py">params</a>) -> <a href="./src/fireworks/types/secret.py">Secret</a></code>
- <code title="patch /v1/accounts/{account_id}/secrets/{secret_id}">client.secrets.<a href="./src/fireworks/resources/secrets.py">update</a>(secret_id, \*, account_id, \*\*<a href="src/fireworks/types/secret_update_params.py">params</a>) -> <a href="./src/fireworks/types/secret.py">Secret</a></code>
- <code title="get /v1/accounts/{account_id}/secrets">client.secrets.<a href="./src/fireworks/resources/secrets.py">list</a>(account_id, \*\*<a href="src/fireworks/types/secret_list_params.py">params</a>) -> <a href="./src/fireworks/types/secret_list_response.py">SecretListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/secrets/{secret_id}">client.secrets.<a href="./src/fireworks/resources/secrets.py">delete</a>(secret_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/secrets/{secret_id}">client.secrets.<a href="./src/fireworks/resources/secrets.py">get</a>(secret_id, \*, account_id, \*\*<a href="src/fireworks/types/secret_get_params.py">params</a>) -> <a href="./src/fireworks/types/secret.py">Secret</a></code>

# DpoJobs

Types:

```python
from fireworks.types import DpoJob, DpoJobListResponse, DpoJobGetMetricsFileEndpointResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/dpoJobs">client.dpo_jobs.<a href="./src/fireworks/resources/dpo_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks/types/dpo_job_create_params.py">params</a>) -> <a href="./src/fireworks/types/dpo_job.py">DpoJob</a></code>
- <code title="get /v1/accounts/{account_id}/dpoJobs">client.dpo_jobs.<a href="./src/fireworks/resources/dpo_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks/types/dpo_job_list_params.py">params</a>) -> <a href="./src/fireworks/types/dpo_job_list_response.py">DpoJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/dpoJobs/{dpo_job_id}">client.dpo_jobs.<a href="./src/fireworks/resources/dpo_jobs.py">delete</a>(dpo_job_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/dpoJobs/{dpo_job_id}">client.dpo_jobs.<a href="./src/fireworks/resources/dpo_jobs.py">get</a>(dpo_job_id, \*, account_id, \*\*<a href="src/fireworks/types/dpo_job_get_params.py">params</a>) -> <a href="./src/fireworks/types/dpo_job.py">DpoJob</a></code>
- <code title="get /v1/accounts/{account_id}/dpoJobs/{dpo_job_id}:getMetricsFileEndpoint">client.dpo_jobs.<a href="./src/fireworks/resources/dpo_jobs.py">get_metrics_file_endpoint</a>(dpo_job_id, \*, account_id) -> <a href="./src/fireworks/types/dpo_job_get_metrics_file_endpoint_response.py">DpoJobGetMetricsFileEndpointResponse</a></code>
