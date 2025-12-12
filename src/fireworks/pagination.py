# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Generic, TypeVar, Optional
from typing_extensions import override

from pydantic import Field as FieldInfo

from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = [
    "SyncCursorAccounts",
    "AsyncCursorAccounts",
    "SyncCursorAPIKeys",
    "AsyncCursorAPIKeys",
    "SyncCursorBatchInferenceJobs",
    "AsyncCursorBatchInferenceJobs",
    "SyncCursorDatasets",
    "AsyncCursorDatasets",
    "SyncCursorDeploymentShapeVersions",
    "AsyncCursorDeploymentShapeVersions",
    "SyncCursorDeployments",
    "AsyncCursorDeployments",
    "SyncCursorDpoJobs",
    "AsyncCursorDpoJobs",
    "SyncCursorEvaluationJobs",
    "AsyncCursorEvaluationJobs",
    "SyncCursorEvaluators",
    "AsyncCursorEvaluators",
    "SyncCursorLora",
    "AsyncCursorLora",
    "SyncCursorModels",
    "AsyncCursorModels",
    "SyncCursorReinforcementFineTuningJobs",
    "AsyncCursorReinforcementFineTuningJobs",
    "SyncCursorReinforcementFineTuningSteps",
    "AsyncCursorReinforcementFineTuningSteps",
    "SyncCursorSecrets",
    "AsyncCursorSecrets",
    "SyncCursorSupervisedFineTuningJobs",
    "AsyncCursorSupervisedFineTuningJobs",
    "SyncCursorUsers",
    "AsyncCursorUsers",
]

_T = TypeVar("_T")


class SyncCursorAccounts(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    accounts: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        accounts = self.accounts
        if not accounts:
            return []
        return accounts

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorAccounts(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    accounts: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        accounts = self.accounts
        if not accounts:
            return []
        return accounts

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorAPIKeys(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    api_keys: List[_T] = FieldInfo(alias="apiKeys")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        api_keys = self.api_keys
        if not api_keys:
            return []
        return api_keys

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorAPIKeys(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    api_keys: List[_T] = FieldInfo(alias="apiKeys")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        api_keys = self.api_keys
        if not api_keys:
            return []
        return api_keys

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorBatchInferenceJobs(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    batch_inference_jobs: List[_T] = FieldInfo(alias="batchInferenceJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        batch_inference_jobs = self.batch_inference_jobs
        if not batch_inference_jobs:
            return []
        return batch_inference_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorBatchInferenceJobs(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    batch_inference_jobs: List[_T] = FieldInfo(alias="batchInferenceJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        batch_inference_jobs = self.batch_inference_jobs
        if not batch_inference_jobs:
            return []
        return batch_inference_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorDatasets(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    datasets: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        datasets = self.datasets
        if not datasets:
            return []
        return datasets

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorDatasets(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    datasets: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        datasets = self.datasets
        if not datasets:
            return []
        return datasets

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorDeploymentShapeVersions(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    deployment_shape_versions: List[_T] = FieldInfo(alias="deploymentShapeVersions")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        deployment_shape_versions = self.deployment_shape_versions
        if not deployment_shape_versions:
            return []
        return deployment_shape_versions

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorDeploymentShapeVersions(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    deployment_shape_versions: List[_T] = FieldInfo(alias="deploymentShapeVersions")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        deployment_shape_versions = self.deployment_shape_versions
        if not deployment_shape_versions:
            return []
        return deployment_shape_versions

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorDeployments(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    deployments: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        deployments = self.deployments
        if not deployments:
            return []
        return deployments

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorDeployments(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    deployments: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        deployments = self.deployments
        if not deployments:
            return []
        return deployments

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorDpoJobs(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    dpo_jobs: List[_T] = FieldInfo(alias="dpoJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        dpo_jobs = self.dpo_jobs
        if not dpo_jobs:
            return []
        return dpo_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorDpoJobs(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    dpo_jobs: List[_T] = FieldInfo(alias="dpoJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        dpo_jobs = self.dpo_jobs
        if not dpo_jobs:
            return []
        return dpo_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorEvaluationJobs(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    evaluation_jobs: List[_T] = FieldInfo(alias="evaluationJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        evaluation_jobs = self.evaluation_jobs
        if not evaluation_jobs:
            return []
        return evaluation_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorEvaluationJobs(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    evaluation_jobs: List[_T] = FieldInfo(alias="evaluationJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        evaluation_jobs = self.evaluation_jobs
        if not evaluation_jobs:
            return []
        return evaluation_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorEvaluators(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    evaluators: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        evaluators = self.evaluators
        if not evaluators:
            return []
        return evaluators

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorEvaluators(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    evaluators: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        evaluators = self.evaluators
        if not evaluators:
            return []
        return evaluators

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorLora(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    deployed_models: List[_T] = FieldInfo(alias="deployedModels")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        deployed_models = self.deployed_models
        if not deployed_models:
            return []
        return deployed_models

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorLora(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    deployed_models: List[_T] = FieldInfo(alias="deployedModels")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        deployed_models = self.deployed_models
        if not deployed_models:
            return []
        return deployed_models

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorModels(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    models: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        models = self.models
        if not models:
            return []
        return models

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorModels(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    models: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        models = self.models
        if not models:
            return []
        return models

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorReinforcementFineTuningJobs(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    reinforcement_fine_tuning_jobs: List[_T] = FieldInfo(alias="reinforcementFineTuningJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        reinforcement_fine_tuning_jobs = self.reinforcement_fine_tuning_jobs
        if not reinforcement_fine_tuning_jobs:
            return []
        return reinforcement_fine_tuning_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorReinforcementFineTuningJobs(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    reinforcement_fine_tuning_jobs: List[_T] = FieldInfo(alias="reinforcementFineTuningJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        reinforcement_fine_tuning_jobs = self.reinforcement_fine_tuning_jobs
        if not reinforcement_fine_tuning_jobs:
            return []
        return reinforcement_fine_tuning_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorReinforcementFineTuningSteps(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    rlor_trainer_jobs: List[_T] = FieldInfo(alias="rlorTrainerJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        rlor_trainer_jobs = self.rlor_trainer_jobs
        if not rlor_trainer_jobs:
            return []
        return rlor_trainer_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorReinforcementFineTuningSteps(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    rlor_trainer_jobs: List[_T] = FieldInfo(alias="rlorTrainerJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        rlor_trainer_jobs = self.rlor_trainer_jobs
        if not rlor_trainer_jobs:
            return []
        return rlor_trainer_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorSecrets(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    secrets: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        secrets = self.secrets
        if not secrets:
            return []
        return secrets

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorSecrets(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    secrets: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        secrets = self.secrets
        if not secrets:
            return []
        return secrets

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorSupervisedFineTuningJobs(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    supervised_fine_tuning_jobs: List[_T] = FieldInfo(alias="supervisedFineTuningJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        supervised_fine_tuning_jobs = self.supervised_fine_tuning_jobs
        if not supervised_fine_tuning_jobs:
            return []
        return supervised_fine_tuning_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorSupervisedFineTuningJobs(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    supervised_fine_tuning_jobs: List[_T] = FieldInfo(alias="supervisedFineTuningJobs")
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        supervised_fine_tuning_jobs = self.supervised_fine_tuning_jobs
        if not supervised_fine_tuning_jobs:
            return []
        return supervised_fine_tuning_jobs

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class SyncCursorUsers(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    users: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        users = self.users
        if not users:
            return []
        return users

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})


class AsyncCursorUsers(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    users: List[_T]
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    @override
    def _get_page_items(self) -> List[_T]:
        users = self.users
        if not users:
            return []
        return users

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page_token = self.next_page_token
        if not next_page_token:
            return None

        return PageInfo(params={"pageToken": next_page_token})
