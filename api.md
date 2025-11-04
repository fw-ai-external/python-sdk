# Accounts

Types:

```python
from fireworks_ai.types import (
    Account,
    AccountListResponse,
    AccountListAuditLogsResponse,
    AccountPreviewEvaluatorResponse,
    AccountValidateEvaluationAssertionsResponse,
)
```

Methods:

- <code title="get /v1/accounts/{account_id}">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">retrieve</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/account.py">Account</a></code>
- <code title="get /v1/accounts">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">list</a>(\*\*<a href="src/fireworks_ai/types/account_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/account_list_response.py">AccountListResponse</a></code>
- <code title="post /v1/accounts/{account_id}/batchJobs:batchDelete">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">batch_delete_batch_jobs</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_batch_delete_batch_jobs_params.py">params</a>) -> object</code>
- <code title="post /v1/accounts/{account_id}/environments:batchDelete">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">batch_delete_environments</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_batch_delete_environments_params.py">params</a>) -> object</code>
- <code title="post /v1/accounts/{account_id}/nodePools:batchDelete">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">batch_delete_node_pools</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_batch_delete_node_pools_params.py">params</a>) -> object</code>
- <code title="post /v1/accounts/{account_id}/evaluatorsV2">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">create_evaluator_v2</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_create_evaluator_v2_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_evaluator.py">GatewayEvaluator</a></code>
- <code title="post /v1/accounts/{account_id}/awsIamRoleBindings:delete">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">delete_aws_iam_role_binding</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_delete_aws_iam_role_binding_params.py">params</a>) -> object</code>
- <code title="post /v1/accounts/{account_id}/nodePoolBindings:delete">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">delete_node_pool_binding</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_delete_node_pool_binding_params.py">params</a>) -> object</code>
- <code title="get /v1/accounts/{account_id}/auditLogs">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">list_audit_logs</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_list_audit_logs_params.py">params</a>) -> <a href="./src/fireworks_ai/types/account_list_audit_logs_response.py">AccountListAuditLogsResponse</a></code>
- <code title="post /v1/accounts/{account_id}/evaluators:previewEvaluator">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">preview_evaluator</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_preview_evaluator_params.py">params</a>) -> <a href="./src/fireworks_ai/types/account_preview_evaluator_response.py">AccountPreviewEvaluatorResponse</a></code>
- <code title="post /v1/accounts/{account_id}:testeval">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">test_evaluation</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_test_evaluation_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/preview_evaluation_response.py">PreviewEvaluationResponse</a></code>
- <code title="post /v1/accounts/{account_id}/evaluations:validateAssertions">client.accounts.<a href="./src/fireworks_ai/resources/accounts/accounts.py">validate_evaluation_assertions</a>(account_id, \*\*<a href="src/fireworks_ai/types/account_validate_evaluation_assertions_params.py">params</a>) -> <a href="./src/fireworks_ai/types/account_validate_evaluation_assertions_response.py">AccountValidateEvaluationAssertionsResponse</a></code>

## PeftMergeJobs

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayJobState,
    GatewayPeftMergeJob,
    PeftMergeJobListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/PeftMergeJobs">client.accounts.peft_merge_jobs.<a href="./src/fireworks_ai/resources/accounts/peft_merge_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/peft_merge_job_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_peft_merge_job.py">GatewayPeftMergeJob</a></code>
- <code title="get /v1/accounts/{account_id}/PeftMergeJobs/{peft_merge_job_id}">client.accounts.peft_merge_jobs.<a href="./src/fireworks_ai/resources/accounts/peft_merge_jobs.py">retrieve</a>(peft_merge_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/peft_merge_job_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_peft_merge_job.py">GatewayPeftMergeJob</a></code>
- <code title="get /v1/accounts/{account_id}/PeftMergeJobs">client.accounts.peft_merge_jobs.<a href="./src/fireworks_ai/resources/accounts/peft_merge_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/peft_merge_job_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/peft_merge_job_list_response.py">PeftMergeJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/PeftMergeJobs/{peft_merge_job_id}">client.accounts.peft_merge_jobs.<a href="./src/fireworks_ai/resources/accounts/peft_merge_jobs.py">delete</a>(peft_merge_job_id, \*, account_id) -> object</code>

## AwsIamRoleBindings

Types:

```python
from fireworks_ai.types.accounts import GatewayAwsIamRoleBinding, AwsIamRoleBindingListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/awsIamRoleBindings">client.accounts.aws_iam_role_bindings.<a href="./src/fireworks_ai/resources/accounts/aws_iam_role_bindings.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/aws_iam_role_binding_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_aws_iam_role_binding.py">GatewayAwsIamRoleBinding</a></code>
- <code title="get /v1/accounts/{account_id}/awsIamRoleBindings">client.accounts.aws_iam_role_bindings.<a href="./src/fireworks_ai/resources/accounts/aws_iam_role_bindings.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/aws_iam_role_binding_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/aws_iam_role_binding_list_response.py">AwsIamRoleBindingListResponse</a></code>

## BatchInferenceJobs

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayBatchInferenceJob,
    GatewayInferenceParameters,
    BatchInferenceJobListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/batchInferenceJobs">client.accounts.batch_inference_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_inference_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_inference_job_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_batch_inference_job.py">GatewayBatchInferenceJob</a></code>
- <code title="get /v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}">client.accounts.batch_inference_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_inference_jobs.py">retrieve</a>(batch_inference_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_inference_job_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_batch_inference_job.py">GatewayBatchInferenceJob</a></code>
- <code title="get /v1/accounts/{account_id}/batchInferenceJobs">client.accounts.batch_inference_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_inference_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_inference_job_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/batch_inference_job_list_response.py">BatchInferenceJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}">client.accounts.batch_inference_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_inference_jobs.py">delete</a>(batch_inference_job_id, \*, account_id) -> object</code>

## BatchJobs

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayBatchJob,
    GatewayBatchJobState,
    GatewayNotebookExecutor,
    GatewayPythonExecutor,
    GatewayShellExecutor,
    BatchJobListResponse,
    BatchJobGetLogsResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/batchJobs">client.accounts.batch_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_job_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_batch_job.py">GatewayBatchJob</a></code>
- <code title="get /v1/accounts/{account_id}/batchJobs/{batch_job_id}">client.accounts.batch_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_jobs.py">retrieve</a>(batch_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_job_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_batch_job.py">GatewayBatchJob</a></code>
- <code title="patch /v1/accounts/{account_id}/batchJobs/{batch_job_id}">client.accounts.batch_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_jobs.py">update</a>(batch_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_job_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_batch_job.py">GatewayBatchJob</a></code>
- <code title="get /v1/accounts/{account_id}/batchJobs">client.accounts.batch_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_job_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/batch_job_list_response.py">BatchJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/batchJobs/{batch_job_id}">client.accounts.batch_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_jobs.py">delete</a>(batch_job_id, \*, account_id) -> object</code>
- <code title="post /v1/accounts/{account_id}/batchJobs/{batch_job_id}:cancel">client.accounts.batch_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_jobs.py">cancel</a>(batch_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_job_cancel_params.py">params</a>) -> object</code>
- <code title="get /v1/accounts/{account_id}/batchJobs/{batch_job_id}:getLogs">client.accounts.batch_jobs.<a href="./src/fireworks_ai/resources/accounts/batch_jobs.py">get_logs</a>(batch_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/batch_job_get_logs_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/batch_job_get_logs_response.py">BatchJobGetLogsResponse</a></code>

## Billing

Types:

```python
from fireworks_ai.types.accounts import TypeMoney, BillingGetSummaryResponse
```

Methods:

- <code title="get /v1/accounts/{account_id}/billing/summary">client.accounts.billing.<a href="./src/fireworks_ai/resources/accounts/billing.py">get_summary</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/billing_get_summary_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/billing_get_summary_response.py">BillingGetSummaryResponse</a></code>

## Clusters

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayCluster,
    GatewayClusterState,
    GatewayEksCluster,
    GatewayFakeCluster,
    GatewayStatus,
    ClusterListResponse,
    ClusterGetConnectionInfoResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/clusters">client.accounts.clusters.<a href="./src/fireworks_ai/resources/accounts/clusters.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/cluster_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_cluster.py">GatewayCluster</a></code>
- <code title="get /v1/accounts/{account_id}/clusters/{cluster_id}">client.accounts.clusters.<a href="./src/fireworks_ai/resources/accounts/clusters.py">retrieve</a>(cluster_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/cluster_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_cluster.py">GatewayCluster</a></code>
- <code title="patch /v1/accounts/{account_id}/clusters/{cluster_id}">client.accounts.clusters.<a href="./src/fireworks_ai/resources/accounts/clusters.py">update</a>(cluster_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/cluster_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_cluster.py">GatewayCluster</a></code>
- <code title="get /v1/accounts/{account_id}/clusters">client.accounts.clusters.<a href="./src/fireworks_ai/resources/accounts/clusters.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/cluster_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/cluster_list_response.py">ClusterListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/clusters/{cluster_id}">client.accounts.clusters.<a href="./src/fireworks_ai/resources/accounts/clusters.py">delete</a>(cluster_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/clusters/{cluster_id}:getConnectionInfo">client.accounts.clusters.<a href="./src/fireworks_ai/resources/accounts/clusters.py">get_connection_info</a>(cluster_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/cluster_get_connection_info_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/cluster_get_connection_info_response.py">ClusterGetConnectionInfoResponse</a></code>

## Datasets

Types:

```python
from fireworks_ai.types.accounts import (
    DatasetFormat,
    GatewayDataset,
    GatewayDatasetState,
    GatewayEvaluationResult,
    GatewaySplitted,
    GatewayTransformed,
    DatasetListResponse,
    DatasetGetDownloadEndpointResponse,
    DatasetGetUploadEndpointResponse,
    DatasetSplitResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/datasets">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/dataset_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_dataset.py">GatewayDataset</a></code>
- <code title="get /v1/accounts/{account_id}/datasets/{dataset_id}">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">retrieve</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/dataset_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_dataset.py">GatewayDataset</a></code>
- <code title="patch /v1/accounts/{account_id}/datasets/{dataset_id}">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">update</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/dataset_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_dataset.py">GatewayDataset</a></code>
- <code title="get /v1/accounts/{account_id}/datasets">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/dataset_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/dataset_list_response.py">DatasetListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/datasets/{dataset_id}">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">delete</a>(dataset_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/datasets/{dataset_id}:getDownloadEndpoint">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">get_download_endpoint</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/dataset_get_download_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/dataset_get_download_endpoint_response.py">DatasetGetDownloadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/datasets/{dataset_id}:getUploadEndpoint">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">get_upload_endpoint</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/dataset_get_upload_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/dataset_get_upload_endpoint_response.py">DatasetGetUploadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/datasets/{dataset_id}:splitDataset">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">split</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/dataset_split_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/dataset_split_response.py">DatasetSplitResponse</a></code>
- <code title="post /v1/accounts/{account_id}/datasets/{dataset_id}:validateUpload">client.accounts.datasets.<a href="./src/fireworks_ai/resources/accounts/datasets.py">validate_upload</a>(dataset_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/dataset_validate_upload_params.py">params</a>) -> object</code>

## DeployedModels

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayDeployedModel,
    GatewayDeployedModelState,
    DeployedModelListResponse,
)
```

Methods:

- <code title="get /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.accounts.deployed_models.<a href="./src/fireworks_ai/resources/accounts/deployed_models.py">retrieve</a>(deployed_model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployed_model_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployed_model.py">GatewayDeployedModel</a></code>
- <code title="patch /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.accounts.deployed_models.<a href="./src/fireworks_ai/resources/accounts/deployed_models.py">update</a>(deployed_model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployed_model_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployed_model.py">GatewayDeployedModel</a></code>
- <code title="get /v1/accounts/{account_id}/deployedModels">client.accounts.deployed_models.<a href="./src/fireworks_ai/resources/accounts/deployed_models.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployed_model_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/deployed_model_list_response.py">DeployedModelListResponse</a></code>
- <code title="post /v1/accounts/{account_id}/deployedModels">client.accounts.deployed_models.<a href="./src/fireworks_ai/resources/accounts/deployed_models.py">load</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployed_model_load_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployed_model.py">GatewayDeployedModel</a></code>
- <code title="delete /v1/accounts/{account_id}/deployedModels/{deployed_model_id}">client.accounts.deployed_models.<a href="./src/fireworks_ai/resources/accounts/deployed_models.py">unload</a>(deployed_model_id, \*, account_id) -> object</code>

## DeploymentShapes

Types:

```python
from fireworks_ai.types.accounts import (
    DeploymentPrecision,
    DeploymentShapePresetType,
    GatewayAcceleratorType,
    GatewayDeploymentShape,
    DeploymentShapeListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/deploymentShapes">client.accounts.deployment_shapes.<a href="./src/fireworks_ai/resources/accounts/deployment_shapes/deployment_shapes.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_shape_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployment_shape.py">GatewayDeploymentShape</a></code>
- <code title="get /v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}">client.accounts.deployment_shapes.<a href="./src/fireworks_ai/resources/accounts/deployment_shapes/deployment_shapes.py">retrieve</a>(deployment_shape_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_shape_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployment_shape.py">GatewayDeploymentShape</a></code>
- <code title="patch /v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}">client.accounts.deployment_shapes.<a href="./src/fireworks_ai/resources/accounts/deployment_shapes/deployment_shapes.py">update</a>(deployment_shape_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_shape_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployment_shape.py">GatewayDeploymentShape</a></code>
- <code title="get /v1/accounts/{account_id}/deploymentShapes">client.accounts.deployment_shapes.<a href="./src/fireworks_ai/resources/accounts/deployment_shapes/deployment_shapes.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_shape_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/deployment_shape_list_response.py">DeploymentShapeListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}">client.accounts.deployment_shapes.<a href="./src/fireworks_ai/resources/accounts/deployment_shapes/deployment_shapes.py">delete</a>(deployment_shape_id, \*, account_id) -> object</code>

### Versions

Types:

```python
from fireworks_ai.types.accounts.deployment_shapes import (
    GatewayDeploymentShapeVersion,
    VersionListResponse,
)
```

Methods:

- <code title="get /v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions/{version_id}">client.accounts.deployment_shapes.versions.<a href="./src/fireworks_ai/resources/accounts/deployment_shapes/versions.py">retrieve</a>(version_id, \*, account_id, deployment_shape_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_shapes/version_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/deployment_shapes/gateway_deployment_shape_version.py">GatewayDeploymentShapeVersion</a></code>
- <code title="patch /v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions/{version_id}">client.accounts.deployment_shapes.versions.<a href="./src/fireworks_ai/resources/accounts/deployment_shapes/versions.py">update</a>(version_id, \*, account_id, deployment_shape_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_shapes/version_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/deployment_shapes/gateway_deployment_shape_version.py">GatewayDeploymentShapeVersion</a></code>
- <code title="get /v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions">client.accounts.deployment_shapes.versions.<a href="./src/fireworks_ai/resources/accounts/deployment_shapes/versions.py">list</a>(deployment_shape_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_shapes/version_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/deployment_shapes/version_list_response.py">VersionListResponse</a></code>

## Deployments

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayAutoTune,
    GatewayAutoscalingPolicy,
    GatewayDeployment,
    GatewayDeploymentState,
    GatewayDirectRouteType,
    GatewayPlacement,
    GatewayRegion,
    DeploymentListResponse,
    DeploymentGetMetricsResponse,
    DeploymentGetTerminationMessageResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/deployments">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployment.py">GatewayDeployment</a></code>
- <code title="get /v1/accounts/{account_id}/deployments/{deployment_id}">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">retrieve</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployment.py">GatewayDeployment</a></code>
- <code title="patch /v1/accounts/{account_id}/deployments/{deployment_id}">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">update</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployment.py">GatewayDeployment</a></code>
- <code title="get /v1/accounts/{account_id}/deployments">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/deployment_list_response.py">DeploymentListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/deployments/{deployment_id}">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">delete</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_delete_params.py">params</a>) -> object</code>
- <code title="get /v1/accounts/{account_id}/deployments/{deployment_id}:metrics">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">get_metrics</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_get_metrics_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/deployment_get_metrics_response.py">DeploymentGetMetricsResponse</a></code>
- <code title="get /v1/accounts/{account_id}/deployments/{deployment_id}/terminationMessage">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">get_termination_message</a>(deployment_id, \*, account_id) -> <a href="./src/fireworks_ai/types/accounts/deployment_get_termination_message_response.py">DeploymentGetTerminationMessageResponse</a></code>
- <code title="patch /v1/accounts/{account_id}/deployments/{deployment_id}:scale">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">scale</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_scale_params.py">params</a>) -> object</code>
- <code title="post /v1/accounts/{account_id}/deployments/{deployment_id}:undelete">client.accounts.deployments.<a href="./src/fireworks_ai/resources/accounts/deployments/deployments.py">undelete</a>(deployment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/deployment_undelete_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_deployment.py">GatewayDeployment</a></code>

### Ledger

Types:

```python
from fireworks_ai.types.accounts.deployments import LedgerRetrieveResponse
```

Methods:

- <code title="get /v1/accounts/{account_id}/deployments/{deployment_id}/ledger">client.accounts.deployments.ledger.<a href="./src/fireworks_ai/resources/accounts/deployments/ledger.py">retrieve</a>(deployment_id, \*, account_id) -> <a href="./src/fireworks_ai/types/accounts/deployments/ledger_retrieve_response.py">LedgerRetrieveResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/deployments/{deployment_id}/ledger">client.accounts.deployments.ledger.<a href="./src/fireworks_ai/resources/accounts/deployments/ledger.py">reset</a>(deployment_id, \*, account_id) -> object</code>

## Environments

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayEnvironment,
    GatewayEnvironmentConnection,
    GatewayEnvironmentState,
    EnvironmentListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/environments">client.accounts.environments.<a href="./src/fireworks_ai/resources/accounts/environments.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/environment_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_environment.py">GatewayEnvironment</a></code>
- <code title="get /v1/accounts/{account_id}/environments/{environment_id}">client.accounts.environments.<a href="./src/fireworks_ai/resources/accounts/environments.py">retrieve</a>(environment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/environment_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_environment.py">GatewayEnvironment</a></code>
- <code title="patch /v1/accounts/{account_id}/environments/{environment_id}">client.accounts.environments.<a href="./src/fireworks_ai/resources/accounts/environments.py">update</a>(environment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/environment_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_environment.py">GatewayEnvironment</a></code>
- <code title="get /v1/accounts/{account_id}/environments">client.accounts.environments.<a href="./src/fireworks_ai/resources/accounts/environments.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/environment_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/environment_list_response.py">EnvironmentListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/environments/{environment_id}">client.accounts.environments.<a href="./src/fireworks_ai/resources/accounts/environments.py">delete</a>(environment_id, \*, account_id) -> object</code>
- <code title="post /v1/accounts/{account_id}/environments/{environment_id}:connect">client.accounts.environments.<a href="./src/fireworks_ai/resources/accounts/environments.py">connect</a>(environment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/environment_connect_params.py">params</a>) -> object</code>
- <code title="post /v1/accounts/{account_id}/environments/{environment_id}:disconnect">client.accounts.environments.<a href="./src/fireworks_ai/resources/accounts/environments.py">disconnect</a>(environment_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/environment_disconnect_params.py">params</a>) -> object</code>

## EvaluationJobs

Types:

```python
from fireworks_ai.types.accounts import GatewayEvaluationJob, EvaluationJobListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/evaluationJobs">client.accounts.evaluation_jobs.<a href="./src/fireworks_ai/resources/accounts/evaluation_jobs.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluation_job_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_evaluation_job.py">GatewayEvaluationJob</a></code>
- <code title="get /v1/accounts/{account_id}/evaluationJobs/{evaluation_job_id}">client.accounts.evaluation_jobs.<a href="./src/fireworks_ai/resources/accounts/evaluation_jobs.py">retrieve</a>(evaluation_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluation_job_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_evaluation_job.py">GatewayEvaluationJob</a></code>
- <code title="get /v1/accounts/{account_id}/evaluationJobs">client.accounts.evaluation_jobs.<a href="./src/fireworks_ai/resources/accounts/evaluation_jobs.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluation_job_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/evaluation_job_list_response.py">EvaluationJobListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/evaluationJobs/{evaluation_job_id}">client.accounts.evaluation_jobs.<a href="./src/fireworks_ai/resources/accounts/evaluation_jobs.py">delete</a>(evaluation_job_id, \*, account_id) -> object</code>

## Evaluations

Types:

```python
from fireworks_ai.types.accounts import (
    Assertion,
    Evaluation,
    PreviewEvaluationResponse,
    Provider,
    EvaluationListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/evaluations">client.accounts.evaluations.<a href="./src/fireworks_ai/resources/accounts/evaluations.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluation_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/evaluation.py">Evaluation</a></code>
- <code title="get /v1/accounts/{account_id}/evaluations/{evaluation_id}">client.accounts.evaluations.<a href="./src/fireworks_ai/resources/accounts/evaluations.py">retrieve</a>(evaluation_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluation_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/evaluation.py">Evaluation</a></code>
- <code title="get /v1/accounts/{account_id}/evaluations">client.accounts.evaluations.<a href="./src/fireworks_ai/resources/accounts/evaluations.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluation_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/evaluation_list_response.py">EvaluationListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/evaluations/{evaluation_id}">client.accounts.evaluations.<a href="./src/fireworks_ai/resources/accounts/evaluations.py">delete</a>(evaluation_id, \*, account_id) -> object</code>
- <code title="post /v1/accounts/{account_id}/evaluations/{evaluation_id}:preview">client.accounts.evaluations.<a href="./src/fireworks_ai/resources/accounts/evaluations.py">preview</a>(evaluation_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluation_preview_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/preview_evaluation_response.py">PreviewEvaluationResponse</a></code>

## Evaluators

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayEvaluator,
    EvaluatorListResponse,
    EvaluatorGetBuildLogEndpointResponse,
    EvaluatorGetUploadEndpointResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/evaluators">client.accounts.evaluators.<a href="./src/fireworks_ai/resources/accounts/evaluators.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluator_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_evaluator.py">GatewayEvaluator</a></code>
- <code title="get /v1/accounts/{account_id}/evaluators/{evaluator_id}">client.accounts.evaluators.<a href="./src/fireworks_ai/resources/accounts/evaluators.py">retrieve</a>(evaluator_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluator_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_evaluator.py">GatewayEvaluator</a></code>
- <code title="get /v1/accounts/{account_id}/evaluators">client.accounts.evaluators.<a href="./src/fireworks_ai/resources/accounts/evaluators.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluator_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/evaluator_list_response.py">EvaluatorListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/evaluators/{evaluator_id}">client.accounts.evaluators.<a href="./src/fireworks_ai/resources/accounts/evaluators.py">delete</a>(evaluator_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/evaluators/{evaluator_id}:getBuildLogEndpoint">client.accounts.evaluators.<a href="./src/fireworks_ai/resources/accounts/evaluators.py">get_build_log_endpoint</a>(evaluator_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluator_get_build_log_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/evaluator_get_build_log_endpoint_response.py">EvaluatorGetBuildLogEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/evaluators/{evaluator_id}:getUploadEndpoint">client.accounts.evaluators.<a href="./src/fireworks_ai/resources/accounts/evaluators.py">get_upload_endpoint</a>(evaluator_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluator_get_upload_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/evaluator_get_upload_endpoint_response.py">EvaluatorGetUploadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/evaluators/{evaluator_id}:validateUpload">client.accounts.evaluators.<a href="./src/fireworks_ai/resources/accounts/evaluators.py">validate_upload</a>(evaluator_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/evaluator_validate_upload_params.py">params</a>) -> object</code>

## IdentityProviders

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayIdentityProvider,
    GatewayIdentityProviderState,
    GatewayOidcConfig,
    GatewaySAMLConfig,
    IdentityProviderListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/identityProviders">client.accounts.identity_providers.<a href="./src/fireworks_ai/resources/accounts/identity_providers.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/identity_provider_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_identity_provider.py">GatewayIdentityProvider</a></code>
- <code title="get /v1/accounts/{account_id}/identityProviders/{identity_provider_id}">client.accounts.identity_providers.<a href="./src/fireworks_ai/resources/accounts/identity_providers.py">retrieve</a>(identity_provider_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/identity_provider_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_identity_provider.py">GatewayIdentityProvider</a></code>
- <code title="patch /v1/accounts/{account_id}/identityProviders/{identity_provider_id}">client.accounts.identity_providers.<a href="./src/fireworks_ai/resources/accounts/identity_providers.py">update</a>(identity_provider_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/identity_provider_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_identity_provider.py">GatewayIdentityProvider</a></code>
- <code title="get /v1/accounts/{account_id}/identityProviders">client.accounts.identity_providers.<a href="./src/fireworks_ai/resources/accounts/identity_providers.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/identity_provider_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/identity_provider_list_response.py">IdentityProviderListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/identityProviders/{identity_provider_id}">client.accounts.identity_providers.<a href="./src/fireworks_ai/resources/accounts/identity_providers.py">delete</a>(identity_provider_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/identity_provider_delete_params.py">params</a>) -> object</code>

## Leaderboards

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayLeaderboard,
    LeaderboardRetrieveResponse,
    LeaderboardListResponse,
    LeaderboardListEvaluationJobsResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/leaderboards">client.accounts.leaderboards.<a href="./src/fireworks_ai/resources/accounts/leaderboards.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/leaderboard_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_leaderboard.py">GatewayLeaderboard</a></code>
- <code title="get /v1/accounts/{account_id}/leaderboards/{leaderboard_id}">client.accounts.leaderboards.<a href="./src/fireworks_ai/resources/accounts/leaderboards.py">retrieve</a>(leaderboard_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/leaderboard_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/leaderboard_retrieve_response.py">LeaderboardRetrieveResponse</a></code>
- <code title="get /v1/accounts/{account_id}/leaderboards">client.accounts.leaderboards.<a href="./src/fireworks_ai/resources/accounts/leaderboards.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/leaderboard_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/leaderboard_list_response.py">LeaderboardListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/leaderboards/{leaderboard_id}">client.accounts.leaderboards.<a href="./src/fireworks_ai/resources/accounts/leaderboards.py">delete</a>(leaderboard_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/leaderboards/{leaderboard_id}:listEvaluationJobs">client.accounts.leaderboards.<a href="./src/fireworks_ai/resources/accounts/leaderboards.py">list_evaluation_jobs</a>(leaderboard_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/leaderboard_list_evaluation_jobs_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/leaderboard_list_evaluation_jobs_response.py">LeaderboardListEvaluationJobsResponse</a></code>

## McpServers

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayMcpServer,
    GatewayMcpServerState,
    McpServerAuthenticationType,
    McpServerListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/mcpServers">client.accounts.mcp_servers.<a href="./src/fireworks_ai/resources/accounts/mcp_servers.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/mcp_server_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_mcp_server.py">GatewayMcpServer</a></code>
- <code title="get /v1/accounts/{account_id}/mcpServers/{mcp_server_id}">client.accounts.mcp_servers.<a href="./src/fireworks_ai/resources/accounts/mcp_servers.py">retrieve</a>(mcp_server_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/mcp_server_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_mcp_server.py">GatewayMcpServer</a></code>
- <code title="patch /v1/accounts/{account_id}/mcpServers/{mcp_server_id}">client.accounts.mcp_servers.<a href="./src/fireworks_ai/resources/accounts/mcp_servers.py">update</a>(mcp_server_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/mcp_server_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_mcp_server.py">GatewayMcpServer</a></code>
- <code title="get /v1/accounts/{account_id}/mcpServers">client.accounts.mcp_servers.<a href="./src/fireworks_ai/resources/accounts/mcp_servers.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/mcp_server_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/mcp_server_list_response.py">McpServerListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/mcpServers/{mcp_server_id}">client.accounts.mcp_servers.<a href="./src/fireworks_ai/resources/accounts/mcp_servers.py">delete</a>(mcp_server_id, \*, account_id) -> object</code>

## Models

Types:

```python
from fireworks_ai.types.accounts import (
    BaseModelDetails,
    ConversationConfig,
    DateType,
    DeployedModelRef,
    Model,
    ModelKind,
    ModelSnapshot,
    ModelState,
    ModelVersion,
    PeftDetails,
    ModelListResponse,
    ModelCountVersionsResponse,
    ModelGetDownloadEndpointResponse,
    ModelGetUploadEndpointResponse,
    ModelImportResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/models">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/model.py">Model</a></code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">retrieve</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/model.py">Model</a></code>
- <code title="patch /v1/accounts/{account_id}/models/{model_id}">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">update</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/model.py">Model</a></code>
- <code title="get /v1/accounts/{account_id}/models">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/model_list_response.py">ModelListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/models/{model_id}">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">delete</a>(model_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}/versions:count">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">count_versions</a>(model_id, \*, account_id) -> <a href="./src/fireworks_ai/types/accounts/model_count_versions_response.py">ModelCountVersionsResponse</a></code>
- <code title="post /v1/accounts/{account_id}/models/{model_id}/versions">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">create_version</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_create_version_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/model_version.py">ModelVersion</a></code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}:getDownloadEndpoint">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">get_download_endpoint</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_get_download_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/model_get_download_endpoint_response.py">ModelGetDownloadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/models/{model_id}:getUploadEndpoint">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">get_upload_endpoint</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_get_upload_endpoint_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/model_get_upload_endpoint_response.py">ModelGetUploadEndpointResponse</a></code>
- <code title="post /v1/accounts/{account_id}/models/{model_id}:import">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">import\_</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_import_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/model_import_response.py">ModelImportResponse</a></code>
- <code title="post /v1/accounts/{account_id}/models/{model_id}:prepare">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">prepare</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_prepare_params.py">params</a>) -> object</code>
- <code title="get /v1/accounts/{account_id}/models/{model_id}:validateUpload">client.accounts.models.<a href="./src/fireworks_ai/resources/accounts/models.py">validate_upload</a>(model_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/model_validate_upload_params.py">params</a>) -> object</code>

## NodePoolBindings

Types:

```python
from fireworks_ai.types.accounts import GatewayNodePoolBinding, NodePoolBindingListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/nodePoolBindings">client.accounts.node_pool_bindings.<a href="./src/fireworks_ai/resources/accounts/node_pool_bindings.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/node_pool_binding_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_node_pool_binding.py">GatewayNodePoolBinding</a></code>
- <code title="get /v1/accounts/{account_id}/nodePoolBindings">client.accounts.node_pool_bindings.<a href="./src/fireworks_ai/resources/accounts/node_pool_bindings.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/node_pool_binding_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/node_pool_binding_list_response.py">NodePoolBindingListResponse</a></code>

## NodePools

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayEksNodePool,
    GatewayFakeNodePool,
    GatewayNodePool,
    GatewayNodePoolState,
    GatewayNodePoolStats,
    NodePoolRetrieveNodePoolsResponse,
)
```

Methods:

- <code title="get /v1/accounts/{account_id}/nodePools/{node_pool_id}">client.accounts.node_pools.<a href="./src/fireworks_ai/resources/accounts/node_pools.py">retrieve</a>(node_pool_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/node_pool_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_node_pool.py">GatewayNodePool</a></code>
- <code title="patch /v1/accounts/{account_id}/nodePools/{node_pool_id}">client.accounts.node_pools.<a href="./src/fireworks_ai/resources/accounts/node_pools.py">update</a>(node_pool_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/node_pool_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_node_pool.py">GatewayNodePool</a></code>
- <code title="delete /v1/accounts/{account_id}/nodePools/{node_pool_id}">client.accounts.node_pools.<a href="./src/fireworks_ai/resources/accounts/node_pools.py">delete</a>(node_pool_id, \*, account_id) -> object</code>
- <code title="post /v1/accounts/{account_id}/nodePools">client.accounts.node_pools.<a href="./src/fireworks_ai/resources/accounts/node_pools.py">node_pools</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/node_pool_node_pools_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_node_pool.py">GatewayNodePool</a></code>
- <code title="get /v1/accounts/{account_id}/nodePools/{node_pool_id}:getStats">client.accounts.node_pools.<a href="./src/fireworks_ai/resources/accounts/node_pools.py">retrieve_node_pool_id_get_stats</a>(node_pool_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/node_pool_retrieve_node_pool_id_get_stats_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_node_pool_stats.py">GatewayNodePoolStats</a></code>
- <code title="get /v1/accounts/{account_id}/nodePools">client.accounts.node_pools.<a href="./src/fireworks_ai/resources/accounts/node_pools.py">retrieve_node_pools</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/node_pool_retrieve_node_pools_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/node_pool_retrieve_node_pools_response.py">NodePoolRetrieveNodePoolsResponse</a></code>

## ReinforcementFineTuningJobs

Types:

```python
from fireworks_ai.types.accounts import (
    GatewayReinforcementFineTuningJob,
    GatewayWandbConfig,
    ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse,
    ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
)
```

Methods:

- <code title="get /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}">client.accounts.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/reinforcement_fine_tuning_jobs.py">retrieve</a>(reinforcement_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/reinforcement_fine_tuning_job_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_reinforcement_fine_tuning_job.py">GatewayReinforcementFineTuningJob</a></code>
- <code title="delete /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}">client.accounts.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/reinforcement_fine_tuning_jobs.py">delete</a>(reinforcement_fine_tuning_job_id, \*, account_id) -> object</code>
- <code title="post /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}:debug">client.accounts.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/reinforcement_fine_tuning_jobs.py">reinforcement_fine_tuning_job_id_debug</a>(reinforcement_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/reinforcement_fine_tuning_job_reinforcement_fine_tuning_job_id_debug_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/reinforcement_fine_tuning_job_reinforcement_fine_tuning_job_id_debug_response.py">ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse</a></code>
- <code title="post /v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}:resume">client.accounts.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/reinforcement_fine_tuning_jobs.py">reinforcement_fine_tuning_job_id_resume</a>(reinforcement_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/reinforcement_fine_tuning_job_reinforcement_fine_tuning_job_id_resume_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_reinforcement_fine_tuning_job.py">GatewayReinforcementFineTuningJob</a></code>
- <code title="post /v1/accounts/{account_id}/reinforcementFineTuningJobs">client.accounts.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/reinforcement_fine_tuning_jobs.py">reinforcement_fine_tuning_jobs</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/reinforcement_fine_tuning_job_reinforcement_fine_tuning_jobs_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_reinforcement_fine_tuning_job.py">GatewayReinforcementFineTuningJob</a></code>
- <code title="get /v1/accounts/{account_id}/reinforcementFineTuningJobs">client.accounts.reinforcement_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/reinforcement_fine_tuning_jobs.py">retrieve_reinforcement_fine_tuning_jobs</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/reinforcement_fine_tuning_job_retrieve_reinforcement_fine_tuning_jobs_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/reinforcement_fine_tuning_job_retrieve_reinforcement_fine_tuning_jobs_response.py">ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse</a></code>

## Routers

Types:

```python
from fireworks_ai.types.accounts import GatewayRouter, GatewayRouterState, RouterListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/routers">client.accounts.routers.<a href="./src/fireworks_ai/resources/accounts/routers.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/router_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_router.py">GatewayRouter</a></code>
- <code title="get /v1/accounts/{account_id}/routers/{router_id}">client.accounts.routers.<a href="./src/fireworks_ai/resources/accounts/routers.py">retrieve</a>(router_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/router_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_router.py">GatewayRouter</a></code>
- <code title="patch /v1/accounts/{account_id}/routers/{router_id}">client.accounts.routers.<a href="./src/fireworks_ai/resources/accounts/routers.py">update</a>(router_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/router_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_router.py">GatewayRouter</a></code>
- <code title="get /v1/accounts/{account_id}/routers">client.accounts.routers.<a href="./src/fireworks_ai/resources/accounts/routers.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/router_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/router_list_response.py">RouterListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/routers/{router_id}">client.accounts.routers.<a href="./src/fireworks_ai/resources/accounts/routers.py">delete</a>(router_id, \*, account_id) -> object</code>

## Secrets

Types:

```python
from fireworks_ai.types.accounts import GatewaySecret, SecretListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/secrets">client.accounts.secrets.<a href="./src/fireworks_ai/resources/accounts/secrets.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/secret_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_secret.py">GatewaySecret</a></code>
- <code title="get /v1/accounts/{account_id}/secrets/{secret_id}">client.accounts.secrets.<a href="./src/fireworks_ai/resources/accounts/secrets.py">retrieve</a>(secret_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/secret_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_secret.py">GatewaySecret</a></code>
- <code title="patch /v1/accounts/{account_id}/secrets/{secret_id}">client.accounts.secrets.<a href="./src/fireworks_ai/resources/accounts/secrets.py">update</a>(secret_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/secret_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_secret.py">GatewaySecret</a></code>
- <code title="get /v1/accounts/{account_id}/secrets">client.accounts.secrets.<a href="./src/fireworks_ai/resources/accounts/secrets.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/secret_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/secret_list_response.py">SecretListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/secrets/{secret_id}">client.accounts.secrets.<a href="./src/fireworks_ai/resources/accounts/secrets.py">delete</a>(secret_id, \*, account_id) -> object</code>

## Snapshots

Types:

```python
from fireworks_ai.types.accounts import GatewaySnapshot, SnapshotListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/snapshots">client.accounts.snapshots.<a href="./src/fireworks_ai/resources/accounts/snapshots.py">create</a>(account_id) -> <a href="./src/fireworks_ai/types/accounts/gateway_snapshot.py">GatewaySnapshot</a></code>
- <code title="get /v1/accounts/{account_id}/snapshots/{snapshot_id}">client.accounts.snapshots.<a href="./src/fireworks_ai/resources/accounts/snapshots.py">retrieve</a>(snapshot_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/snapshot_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_snapshot.py">GatewaySnapshot</a></code>
- <code title="get /v1/accounts/{account_id}/snapshots">client.accounts.snapshots.<a href="./src/fireworks_ai/resources/accounts/snapshots.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/snapshot_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/snapshot_list_response.py">SnapshotListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/snapshots/{snapshot_id}">client.accounts.snapshots.<a href="./src/fireworks_ai/resources/accounts/snapshots.py">delete</a>(snapshot_id, \*, account_id) -> object</code>

## SupervisedFineTuningJobs

Types:

```python
from fireworks_ai.types.accounts import (
    GatewaySupervisedFineTuningJob,
    SupervisedFineTuningJobRetrieveSupervisedFineTuningJobsResponse,
)
```

Methods:

- <code title="get /v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}">client.accounts.supervised_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/supervised_fine_tuning_jobs.py">retrieve</a>(supervised_fine_tuning_job_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/supervised_fine_tuning_job_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_supervised_fine_tuning_job.py">GatewaySupervisedFineTuningJob</a></code>
- <code title="delete /v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}">client.accounts.supervised_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/supervised_fine_tuning_jobs.py">delete</a>(supervised_fine_tuning_job_id, \*, account_id) -> object</code>
- <code title="get /v1/accounts/{account_id}/supervisedFineTuningJobs">client.accounts.supervised_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/supervised_fine_tuning_jobs.py">retrieve_supervised_fine_tuning_jobs</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/supervised_fine_tuning_job_retrieve_supervised_fine_tuning_jobs_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/supervised_fine_tuning_job_retrieve_supervised_fine_tuning_jobs_response.py">SupervisedFineTuningJobRetrieveSupervisedFineTuningJobsResponse</a></code>
- <code title="post /v1/accounts/{account_id}/supervisedFineTuningJobs">client.accounts.supervised_fine_tuning_jobs.<a href="./src/fireworks_ai/resources/accounts/supervised_fine_tuning_jobs.py">supervised_fine_tuning_jobs</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/supervised_fine_tuning_job_supervised_fine_tuning_jobs_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/gateway_supervised_fine_tuning_job.py">GatewaySupervisedFineTuningJob</a></code>

## Users

Types:

```python
from fireworks_ai.types.accounts import User, UserState, UserListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/users">client.accounts.users.<a href="./src/fireworks_ai/resources/accounts/users/users.py">create</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/user_create_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/user.py">User</a></code>
- <code title="get /v1/accounts/{account_id}/users/{user_id}">client.accounts.users.<a href="./src/fireworks_ai/resources/accounts/users/users.py">retrieve</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/user_retrieve_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/user.py">User</a></code>
- <code title="patch /v1/accounts/{account_id}/users/{user_id}">client.accounts.users.<a href="./src/fireworks_ai/resources/accounts/users/users.py">update</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/user_update_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/user.py">User</a></code>
- <code title="get /v1/accounts/{account_id}/users">client.accounts.users.<a href="./src/fireworks_ai/resources/accounts/users/users.py">list</a>(account_id, \*\*<a href="src/fireworks_ai/types/accounts/user_list_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/user_list_response.py">UserListResponse</a></code>
- <code title="post /v1/accounts/{account_id}/users/{user_id}/apiKeys:delete">client.accounts.users.<a href="./src/fireworks_ai/resources/accounts/users/users.py">api_keys_delete</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/user_api_keys_delete_params.py">params</a>) -> object</code>

### APIKeys

Types:

```python
from fireworks_ai.types.accounts.users import APIKey, APIKeyRetrieveAPIKeysResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/users/{user_id}/apiKeys">client.accounts.users.api_keys.<a href="./src/fireworks_ai/resources/accounts/users/api_keys.py">api_keys</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/users/api_key_api_keys_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/users/api_key.py">APIKey</a></code>
- <code title="get /v1/accounts/{account_id}/users/{user_id}/apiKeys">client.accounts.users.api_keys.<a href="./src/fireworks_ai/resources/accounts/users/api_keys.py">retrieve_api_keys</a>(user_id, \*, account_id, \*\*<a href="src/fireworks_ai/types/accounts/users/api_key_retrieve_api_keys_params.py">params</a>) -> <a href="./src/fireworks_ai/types/accounts/users/api_key_retrieve_api_keys_response.py">APIKeyRetrieveAPIKeysResponse</a></code>

# ValidateModelConfig

Methods:

- <code title="post /v1/validateModelConfig">client.validate_model_config.<a href="./src/fireworks_ai/resources/validate_model_config.py">validate</a>(\*\*<a href="src/fireworks_ai/types/validate_model_config_validate_params.py">params</a>) -> object</code>
