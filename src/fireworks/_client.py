# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, FireworksError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import (
        chat,
        lora,
        users,
        models,
        secrets,
        accounts,
        api_keys,
        datasets,
        dpo_jobs,
        evaluators,
        completions,
        deployments,
        evaluation_jobs,
        batch_inference_jobs,
        deployment_shape_versions,
        supervised_fine_tuning_jobs,
        reinforcement_fine_tuning_jobs,
        reinforcement_fine_tuning_steps,
    )
    from .resources.lora import LoraResource, AsyncLoraResource
    from .resources.users import UsersResource, AsyncUsersResource
    from .resources.models import ModelsResource, AsyncModelsResource
    from .resources.secrets import SecretsResource, AsyncSecretsResource
    from .resources.accounts import AccountsResource, AsyncAccountsResource
    from .resources.api_keys import APIKeysResource, AsyncAPIKeysResource
    from .resources.datasets import DatasetsResource, AsyncDatasetsResource
    from .resources.dpo_jobs import DpoJobsResource, AsyncDpoJobsResource
    from .resources.chat.chat import ChatResource, AsyncChatResource
    from .resources.evaluators import EvaluatorsResource, AsyncEvaluatorsResource
    from .resources.completions import CompletionsResource, AsyncCompletionsResource
    from .resources.deployments import DeploymentsResource, AsyncDeploymentsResource
    from .resources.evaluation_jobs import EvaluationJobsResource, AsyncEvaluationJobsResource
    from .resources.batch_inference_jobs import BatchInferenceJobsResource, AsyncBatchInferenceJobsResource
    from .resources.deployment_shape_versions import (
        DeploymentShapeVersionsResource,
        AsyncDeploymentShapeVersionsResource,
    )
    from .resources.supervised_fine_tuning_jobs import (
        SupervisedFineTuningJobsResource,
        AsyncSupervisedFineTuningJobsResource,
    )
    from .resources.reinforcement_fine_tuning_jobs import (
        ReinforcementFineTuningJobsResource,
        AsyncReinforcementFineTuningJobsResource,
    )
    from .resources.reinforcement_fine_tuning_steps import (
        ReinforcementFineTuningStepsResource,
        AsyncReinforcementFineTuningStepsResource,
    )

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Fireworks",
    "AsyncFireworks",
    "Client",
    "AsyncClient",
]


class Fireworks(SyncAPIClient):
    # client options
    api_key: str
    account_id: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        account_id: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Fireworks client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `FIREWORKS_API_KEY`
        - `account_id` from `FIREWORKS_ACCOUNT_ID`
        """
        if api_key is None:
            api_key = os.environ.get("FIREWORKS_API_KEY")
        if api_key is None:
            raise FireworksError(
                "The api_key client option must be set either by passing api_key to the client or by setting the FIREWORKS_API_KEY environment variable"
            )
        self.api_key = api_key

        if account_id is None:
            account_id = os.environ.get("FIREWORKS_ACCOUNT_ID")
        self.account_id = account_id

        if base_url is None:
            base_url = os.environ.get("FIREWORKS_BASE_URL")
        self._base_url_overridden = base_url is not None
        if base_url is None:
            base_url = f"https://api.fireworks.ai"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = Stream

    @cached_property
    def chat(self) -> ChatResource:
        from .resources.chat import ChatResource

        return ChatResource(self)

    @cached_property
    def completions(self) -> CompletionsResource:
        from .resources.completions import CompletionsResource

        return CompletionsResource(self)

    @cached_property
    def batch_inference_jobs(self) -> BatchInferenceJobsResource:
        from .resources.batch_inference_jobs import BatchInferenceJobsResource

        return BatchInferenceJobsResource(self)

    @cached_property
    def deployments(self) -> DeploymentsResource:
        from .resources.deployments import DeploymentsResource

        return DeploymentsResource(self)

    @cached_property
    def models(self) -> ModelsResource:
        from .resources.models import ModelsResource

        return ModelsResource(self)

    @cached_property
    def lora(self) -> LoraResource:
        from .resources.lora import LoraResource

        return LoraResource(self)

    @cached_property
    def deployment_shape_versions(self) -> DeploymentShapeVersionsResource:
        from .resources.deployment_shape_versions import DeploymentShapeVersionsResource

        return DeploymentShapeVersionsResource(self)

    @cached_property
    def datasets(self) -> DatasetsResource:
        from .resources.datasets import DatasetsResource

        return DatasetsResource(self)

    @cached_property
    def supervised_fine_tuning_jobs(self) -> SupervisedFineTuningJobsResource:
        from .resources.supervised_fine_tuning_jobs import SupervisedFineTuningJobsResource

        return SupervisedFineTuningJobsResource(self)

    @cached_property
    def reinforcement_fine_tuning_jobs(self) -> ReinforcementFineTuningJobsResource:
        from .resources.reinforcement_fine_tuning_jobs import ReinforcementFineTuningJobsResource

        return ReinforcementFineTuningJobsResource(self)

    @cached_property
    def reinforcement_fine_tuning_steps(self) -> ReinforcementFineTuningStepsResource:
        from .resources.reinforcement_fine_tuning_steps import ReinforcementFineTuningStepsResource

        return ReinforcementFineTuningStepsResource(self)

    @cached_property
    def dpo_jobs(self) -> DpoJobsResource:
        from .resources.dpo_jobs import DpoJobsResource

        return DpoJobsResource(self)

    @cached_property
    def evaluation_jobs(self) -> EvaluationJobsResource:
        from .resources.evaluation_jobs import EvaluationJobsResource

        return EvaluationJobsResource(self)

    @cached_property
    def evaluators(self) -> EvaluatorsResource:
        from .resources.evaluators import EvaluatorsResource

        return EvaluatorsResource(self)

    @cached_property
    def accounts(self) -> AccountsResource:
        from .resources.accounts import AccountsResource

        return AccountsResource(self)

    @cached_property
    def users(self) -> UsersResource:
        from .resources.users import UsersResource

        return UsersResource(self)

    @cached_property
    def api_keys(self) -> APIKeysResource:
        from .resources.api_keys import APIKeysResource

        return APIKeysResource(self)

    @cached_property
    def secrets(self) -> SecretsResource:
        from .resources.secrets import SecretsResource

        return SecretsResource(self)

    @cached_property
    def with_raw_response(self) -> FireworksWithRawResponse:
        return FireworksWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FireworksWithStreamedResponse:
        return FireworksWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        account_id: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        client = self.__class__(
            api_key=api_key or self.api_key,
            account_id=account_id or self.account_id,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )
        client._base_url_overridden = self._base_url_overridden or base_url is not None
        return client

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def _get_account_id_path_param(self) -> str:
        from_client = self.account_id
        if from_client is not None:
            return from_client

        raise ValueError(
            "Missing account_id argument; Please provide it at the client level, e.g. Fireworks(account_id='abcd') or per method."
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncFireworks(AsyncAPIClient):
    # client options
    api_key: str
    account_id: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        account_id: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncFireworks client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `FIREWORKS_API_KEY`
        - `account_id` from `FIREWORKS_ACCOUNT_ID`
        """
        if api_key is None:
            api_key = os.environ.get("FIREWORKS_API_KEY")
        if api_key is None:
            raise FireworksError(
                "The api_key client option must be set either by passing api_key to the client or by setting the FIREWORKS_API_KEY environment variable"
            )
        self.api_key = api_key

        if account_id is None:
            account_id = os.environ.get("FIREWORKS_ACCOUNT_ID")
        self.account_id = account_id

        if base_url is None:
            base_url = os.environ.get("FIREWORKS_BASE_URL")
        self._base_url_overridden = base_url is not None
        if base_url is None:
            base_url = f"https://api.fireworks.ai"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = AsyncStream

    @cached_property
    def chat(self) -> AsyncChatResource:
        from .resources.chat import AsyncChatResource

        return AsyncChatResource(self)

    @cached_property
    def completions(self) -> AsyncCompletionsResource:
        from .resources.completions import AsyncCompletionsResource

        return AsyncCompletionsResource(self)

    @cached_property
    def batch_inference_jobs(self) -> AsyncBatchInferenceJobsResource:
        from .resources.batch_inference_jobs import AsyncBatchInferenceJobsResource

        return AsyncBatchInferenceJobsResource(self)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResource:
        from .resources.deployments import AsyncDeploymentsResource

        return AsyncDeploymentsResource(self)

    @cached_property
    def models(self) -> AsyncModelsResource:
        from .resources.models import AsyncModelsResource

        return AsyncModelsResource(self)

    @cached_property
    def lora(self) -> AsyncLoraResource:
        from .resources.lora import AsyncLoraResource

        return AsyncLoraResource(self)

    @cached_property
    def deployment_shape_versions(self) -> AsyncDeploymentShapeVersionsResource:
        from .resources.deployment_shape_versions import AsyncDeploymentShapeVersionsResource

        return AsyncDeploymentShapeVersionsResource(self)

    @cached_property
    def datasets(self) -> AsyncDatasetsResource:
        from .resources.datasets import AsyncDatasetsResource

        return AsyncDatasetsResource(self)

    @cached_property
    def supervised_fine_tuning_jobs(self) -> AsyncSupervisedFineTuningJobsResource:
        from .resources.supervised_fine_tuning_jobs import AsyncSupervisedFineTuningJobsResource

        return AsyncSupervisedFineTuningJobsResource(self)

    @cached_property
    def reinforcement_fine_tuning_jobs(self) -> AsyncReinforcementFineTuningJobsResource:
        from .resources.reinforcement_fine_tuning_jobs import AsyncReinforcementFineTuningJobsResource

        return AsyncReinforcementFineTuningJobsResource(self)

    @cached_property
    def reinforcement_fine_tuning_steps(self) -> AsyncReinforcementFineTuningStepsResource:
        from .resources.reinforcement_fine_tuning_steps import AsyncReinforcementFineTuningStepsResource

        return AsyncReinforcementFineTuningStepsResource(self)

    @cached_property
    def dpo_jobs(self) -> AsyncDpoJobsResource:
        from .resources.dpo_jobs import AsyncDpoJobsResource

        return AsyncDpoJobsResource(self)

    @cached_property
    def evaluation_jobs(self) -> AsyncEvaluationJobsResource:
        from .resources.evaluation_jobs import AsyncEvaluationJobsResource

        return AsyncEvaluationJobsResource(self)

    @cached_property
    def evaluators(self) -> AsyncEvaluatorsResource:
        from .resources.evaluators import AsyncEvaluatorsResource

        return AsyncEvaluatorsResource(self)

    @cached_property
    def accounts(self) -> AsyncAccountsResource:
        from .resources.accounts import AsyncAccountsResource

        return AsyncAccountsResource(self)

    @cached_property
    def users(self) -> AsyncUsersResource:
        from .resources.users import AsyncUsersResource

        return AsyncUsersResource(self)

    @cached_property
    def api_keys(self) -> AsyncAPIKeysResource:
        from .resources.api_keys import AsyncAPIKeysResource

        return AsyncAPIKeysResource(self)

    @cached_property
    def secrets(self) -> AsyncSecretsResource:
        from .resources.secrets import AsyncSecretsResource

        return AsyncSecretsResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncFireworksWithRawResponse:
        return AsyncFireworksWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFireworksWithStreamedResponse:
        return AsyncFireworksWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        account_id: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        client = self.__class__(
            api_key=api_key or self.api_key,
            account_id=account_id or self.account_id,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )
        client._base_url_overridden = self._base_url_overridden or base_url is not None
        return client

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def _get_account_id_path_param(self) -> str:
        from_client = self.account_id
        if from_client is not None:
            return from_client

        raise ValueError(
            "Missing account_id argument; Please provide it at the client level, e.g. AsyncFireworks(account_id='abcd') or per method."
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class FireworksWithRawResponse:
    _client: Fireworks

    def __init__(self, client: Fireworks) -> None:
        self._client = client

    @cached_property
    def chat(self) -> chat.ChatResourceWithRawResponse:
        from .resources.chat import ChatResourceWithRawResponse

        return ChatResourceWithRawResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.CompletionsResourceWithRawResponse:
        from .resources.completions import CompletionsResourceWithRawResponse

        return CompletionsResourceWithRawResponse(self._client.completions)

    @cached_property
    def batch_inference_jobs(self) -> batch_inference_jobs.BatchInferenceJobsResourceWithRawResponse:
        from .resources.batch_inference_jobs import BatchInferenceJobsResourceWithRawResponse

        return BatchInferenceJobsResourceWithRawResponse(self._client.batch_inference_jobs)

    @cached_property
    def deployments(self) -> deployments.DeploymentsResourceWithRawResponse:
        from .resources.deployments import DeploymentsResourceWithRawResponse

        return DeploymentsResourceWithRawResponse(self._client.deployments)

    @cached_property
    def models(self) -> models.ModelsResourceWithRawResponse:
        from .resources.models import ModelsResourceWithRawResponse

        return ModelsResourceWithRawResponse(self._client.models)

    @cached_property
    def lora(self) -> lora.LoraResourceWithRawResponse:
        from .resources.lora import LoraResourceWithRawResponse

        return LoraResourceWithRawResponse(self._client.lora)

    @cached_property
    def deployment_shape_versions(self) -> deployment_shape_versions.DeploymentShapeVersionsResourceWithRawResponse:
        from .resources.deployment_shape_versions import DeploymentShapeVersionsResourceWithRawResponse

        return DeploymentShapeVersionsResourceWithRawResponse(self._client.deployment_shape_versions)

    @cached_property
    def datasets(self) -> datasets.DatasetsResourceWithRawResponse:
        from .resources.datasets import DatasetsResourceWithRawResponse

        return DatasetsResourceWithRawResponse(self._client.datasets)

    @cached_property
    def supervised_fine_tuning_jobs(
        self,
    ) -> supervised_fine_tuning_jobs.SupervisedFineTuningJobsResourceWithRawResponse:
        from .resources.supervised_fine_tuning_jobs import SupervisedFineTuningJobsResourceWithRawResponse

        return SupervisedFineTuningJobsResourceWithRawResponse(self._client.supervised_fine_tuning_jobs)

    @cached_property
    def reinforcement_fine_tuning_jobs(
        self,
    ) -> reinforcement_fine_tuning_jobs.ReinforcementFineTuningJobsResourceWithRawResponse:
        from .resources.reinforcement_fine_tuning_jobs import ReinforcementFineTuningJobsResourceWithRawResponse

        return ReinforcementFineTuningJobsResourceWithRawResponse(self._client.reinforcement_fine_tuning_jobs)

    @cached_property
    def reinforcement_fine_tuning_steps(
        self,
    ) -> reinforcement_fine_tuning_steps.ReinforcementFineTuningStepsResourceWithRawResponse:
        from .resources.reinforcement_fine_tuning_steps import ReinforcementFineTuningStepsResourceWithRawResponse

        return ReinforcementFineTuningStepsResourceWithRawResponse(self._client.reinforcement_fine_tuning_steps)

    @cached_property
    def dpo_jobs(self) -> dpo_jobs.DpoJobsResourceWithRawResponse:
        from .resources.dpo_jobs import DpoJobsResourceWithRawResponse

        return DpoJobsResourceWithRawResponse(self._client.dpo_jobs)

    @cached_property
    def evaluation_jobs(self) -> evaluation_jobs.EvaluationJobsResourceWithRawResponse:
        from .resources.evaluation_jobs import EvaluationJobsResourceWithRawResponse

        return EvaluationJobsResourceWithRawResponse(self._client.evaluation_jobs)

    @cached_property
    def evaluators(self) -> evaluators.EvaluatorsResourceWithRawResponse:
        from .resources.evaluators import EvaluatorsResourceWithRawResponse

        return EvaluatorsResourceWithRawResponse(self._client.evaluators)

    @cached_property
    def accounts(self) -> accounts.AccountsResourceWithRawResponse:
        from .resources.accounts import AccountsResourceWithRawResponse

        return AccountsResourceWithRawResponse(self._client.accounts)

    @cached_property
    def users(self) -> users.UsersResourceWithRawResponse:
        from .resources.users import UsersResourceWithRawResponse

        return UsersResourceWithRawResponse(self._client.users)

    @cached_property
    def api_keys(self) -> api_keys.APIKeysResourceWithRawResponse:
        from .resources.api_keys import APIKeysResourceWithRawResponse

        return APIKeysResourceWithRawResponse(self._client.api_keys)

    @cached_property
    def secrets(self) -> secrets.SecretsResourceWithRawResponse:
        from .resources.secrets import SecretsResourceWithRawResponse

        return SecretsResourceWithRawResponse(self._client.secrets)


class AsyncFireworksWithRawResponse:
    _client: AsyncFireworks

    def __init__(self, client: AsyncFireworks) -> None:
        self._client = client

    @cached_property
    def chat(self) -> chat.AsyncChatResourceWithRawResponse:
        from .resources.chat import AsyncChatResourceWithRawResponse

        return AsyncChatResourceWithRawResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.AsyncCompletionsResourceWithRawResponse:
        from .resources.completions import AsyncCompletionsResourceWithRawResponse

        return AsyncCompletionsResourceWithRawResponse(self._client.completions)

    @cached_property
    def batch_inference_jobs(self) -> batch_inference_jobs.AsyncBatchInferenceJobsResourceWithRawResponse:
        from .resources.batch_inference_jobs import AsyncBatchInferenceJobsResourceWithRawResponse

        return AsyncBatchInferenceJobsResourceWithRawResponse(self._client.batch_inference_jobs)

    @cached_property
    def deployments(self) -> deployments.AsyncDeploymentsResourceWithRawResponse:
        from .resources.deployments import AsyncDeploymentsResourceWithRawResponse

        return AsyncDeploymentsResourceWithRawResponse(self._client.deployments)

    @cached_property
    def models(self) -> models.AsyncModelsResourceWithRawResponse:
        from .resources.models import AsyncModelsResourceWithRawResponse

        return AsyncModelsResourceWithRawResponse(self._client.models)

    @cached_property
    def lora(self) -> lora.AsyncLoraResourceWithRawResponse:
        from .resources.lora import AsyncLoraResourceWithRawResponse

        return AsyncLoraResourceWithRawResponse(self._client.lora)

    @cached_property
    def deployment_shape_versions(
        self,
    ) -> deployment_shape_versions.AsyncDeploymentShapeVersionsResourceWithRawResponse:
        from .resources.deployment_shape_versions import AsyncDeploymentShapeVersionsResourceWithRawResponse

        return AsyncDeploymentShapeVersionsResourceWithRawResponse(self._client.deployment_shape_versions)

    @cached_property
    def datasets(self) -> datasets.AsyncDatasetsResourceWithRawResponse:
        from .resources.datasets import AsyncDatasetsResourceWithRawResponse

        return AsyncDatasetsResourceWithRawResponse(self._client.datasets)

    @cached_property
    def supervised_fine_tuning_jobs(
        self,
    ) -> supervised_fine_tuning_jobs.AsyncSupervisedFineTuningJobsResourceWithRawResponse:
        from .resources.supervised_fine_tuning_jobs import AsyncSupervisedFineTuningJobsResourceWithRawResponse

        return AsyncSupervisedFineTuningJobsResourceWithRawResponse(self._client.supervised_fine_tuning_jobs)

    @cached_property
    def reinforcement_fine_tuning_jobs(
        self,
    ) -> reinforcement_fine_tuning_jobs.AsyncReinforcementFineTuningJobsResourceWithRawResponse:
        from .resources.reinforcement_fine_tuning_jobs import AsyncReinforcementFineTuningJobsResourceWithRawResponse

        return AsyncReinforcementFineTuningJobsResourceWithRawResponse(self._client.reinforcement_fine_tuning_jobs)

    @cached_property
    def reinforcement_fine_tuning_steps(
        self,
    ) -> reinforcement_fine_tuning_steps.AsyncReinforcementFineTuningStepsResourceWithRawResponse:
        from .resources.reinforcement_fine_tuning_steps import AsyncReinforcementFineTuningStepsResourceWithRawResponse

        return AsyncReinforcementFineTuningStepsResourceWithRawResponse(self._client.reinforcement_fine_tuning_steps)

    @cached_property
    def dpo_jobs(self) -> dpo_jobs.AsyncDpoJobsResourceWithRawResponse:
        from .resources.dpo_jobs import AsyncDpoJobsResourceWithRawResponse

        return AsyncDpoJobsResourceWithRawResponse(self._client.dpo_jobs)

    @cached_property
    def evaluation_jobs(self) -> evaluation_jobs.AsyncEvaluationJobsResourceWithRawResponse:
        from .resources.evaluation_jobs import AsyncEvaluationJobsResourceWithRawResponse

        return AsyncEvaluationJobsResourceWithRawResponse(self._client.evaluation_jobs)

    @cached_property
    def evaluators(self) -> evaluators.AsyncEvaluatorsResourceWithRawResponse:
        from .resources.evaluators import AsyncEvaluatorsResourceWithRawResponse

        return AsyncEvaluatorsResourceWithRawResponse(self._client.evaluators)

    @cached_property
    def accounts(self) -> accounts.AsyncAccountsResourceWithRawResponse:
        from .resources.accounts import AsyncAccountsResourceWithRawResponse

        return AsyncAccountsResourceWithRawResponse(self._client.accounts)

    @cached_property
    def users(self) -> users.AsyncUsersResourceWithRawResponse:
        from .resources.users import AsyncUsersResourceWithRawResponse

        return AsyncUsersResourceWithRawResponse(self._client.users)

    @cached_property
    def api_keys(self) -> api_keys.AsyncAPIKeysResourceWithRawResponse:
        from .resources.api_keys import AsyncAPIKeysResourceWithRawResponse

        return AsyncAPIKeysResourceWithRawResponse(self._client.api_keys)

    @cached_property
    def secrets(self) -> secrets.AsyncSecretsResourceWithRawResponse:
        from .resources.secrets import AsyncSecretsResourceWithRawResponse

        return AsyncSecretsResourceWithRawResponse(self._client.secrets)


class FireworksWithStreamedResponse:
    _client: Fireworks

    def __init__(self, client: Fireworks) -> None:
        self._client = client

    @cached_property
    def chat(self) -> chat.ChatResourceWithStreamingResponse:
        from .resources.chat import ChatResourceWithStreamingResponse

        return ChatResourceWithStreamingResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.CompletionsResourceWithStreamingResponse:
        from .resources.completions import CompletionsResourceWithStreamingResponse

        return CompletionsResourceWithStreamingResponse(self._client.completions)

    @cached_property
    def batch_inference_jobs(self) -> batch_inference_jobs.BatchInferenceJobsResourceWithStreamingResponse:
        from .resources.batch_inference_jobs import BatchInferenceJobsResourceWithStreamingResponse

        return BatchInferenceJobsResourceWithStreamingResponse(self._client.batch_inference_jobs)

    @cached_property
    def deployments(self) -> deployments.DeploymentsResourceWithStreamingResponse:
        from .resources.deployments import DeploymentsResourceWithStreamingResponse

        return DeploymentsResourceWithStreamingResponse(self._client.deployments)

    @cached_property
    def models(self) -> models.ModelsResourceWithStreamingResponse:
        from .resources.models import ModelsResourceWithStreamingResponse

        return ModelsResourceWithStreamingResponse(self._client.models)

    @cached_property
    def lora(self) -> lora.LoraResourceWithStreamingResponse:
        from .resources.lora import LoraResourceWithStreamingResponse

        return LoraResourceWithStreamingResponse(self._client.lora)

    @cached_property
    def deployment_shape_versions(
        self,
    ) -> deployment_shape_versions.DeploymentShapeVersionsResourceWithStreamingResponse:
        from .resources.deployment_shape_versions import DeploymentShapeVersionsResourceWithStreamingResponse

        return DeploymentShapeVersionsResourceWithStreamingResponse(self._client.deployment_shape_versions)

    @cached_property
    def datasets(self) -> datasets.DatasetsResourceWithStreamingResponse:
        from .resources.datasets import DatasetsResourceWithStreamingResponse

        return DatasetsResourceWithStreamingResponse(self._client.datasets)

    @cached_property
    def supervised_fine_tuning_jobs(
        self,
    ) -> supervised_fine_tuning_jobs.SupervisedFineTuningJobsResourceWithStreamingResponse:
        from .resources.supervised_fine_tuning_jobs import SupervisedFineTuningJobsResourceWithStreamingResponse

        return SupervisedFineTuningJobsResourceWithStreamingResponse(self._client.supervised_fine_tuning_jobs)

    @cached_property
    def reinforcement_fine_tuning_jobs(
        self,
    ) -> reinforcement_fine_tuning_jobs.ReinforcementFineTuningJobsResourceWithStreamingResponse:
        from .resources.reinforcement_fine_tuning_jobs import ReinforcementFineTuningJobsResourceWithStreamingResponse

        return ReinforcementFineTuningJobsResourceWithStreamingResponse(self._client.reinforcement_fine_tuning_jobs)

    @cached_property
    def reinforcement_fine_tuning_steps(
        self,
    ) -> reinforcement_fine_tuning_steps.ReinforcementFineTuningStepsResourceWithStreamingResponse:
        from .resources.reinforcement_fine_tuning_steps import ReinforcementFineTuningStepsResourceWithStreamingResponse

        return ReinforcementFineTuningStepsResourceWithStreamingResponse(self._client.reinforcement_fine_tuning_steps)

    @cached_property
    def dpo_jobs(self) -> dpo_jobs.DpoJobsResourceWithStreamingResponse:
        from .resources.dpo_jobs import DpoJobsResourceWithStreamingResponse

        return DpoJobsResourceWithStreamingResponse(self._client.dpo_jobs)

    @cached_property
    def evaluation_jobs(self) -> evaluation_jobs.EvaluationJobsResourceWithStreamingResponse:
        from .resources.evaluation_jobs import EvaluationJobsResourceWithStreamingResponse

        return EvaluationJobsResourceWithStreamingResponse(self._client.evaluation_jobs)

    @cached_property
    def evaluators(self) -> evaluators.EvaluatorsResourceWithStreamingResponse:
        from .resources.evaluators import EvaluatorsResourceWithStreamingResponse

        return EvaluatorsResourceWithStreamingResponse(self._client.evaluators)

    @cached_property
    def accounts(self) -> accounts.AccountsResourceWithStreamingResponse:
        from .resources.accounts import AccountsResourceWithStreamingResponse

        return AccountsResourceWithStreamingResponse(self._client.accounts)

    @cached_property
    def users(self) -> users.UsersResourceWithStreamingResponse:
        from .resources.users import UsersResourceWithStreamingResponse

        return UsersResourceWithStreamingResponse(self._client.users)

    @cached_property
    def api_keys(self) -> api_keys.APIKeysResourceWithStreamingResponse:
        from .resources.api_keys import APIKeysResourceWithStreamingResponse

        return APIKeysResourceWithStreamingResponse(self._client.api_keys)

    @cached_property
    def secrets(self) -> secrets.SecretsResourceWithStreamingResponse:
        from .resources.secrets import SecretsResourceWithStreamingResponse

        return SecretsResourceWithStreamingResponse(self._client.secrets)


class AsyncFireworksWithStreamedResponse:
    _client: AsyncFireworks

    def __init__(self, client: AsyncFireworks) -> None:
        self._client = client

    @cached_property
    def chat(self) -> chat.AsyncChatResourceWithStreamingResponse:
        from .resources.chat import AsyncChatResourceWithStreamingResponse

        return AsyncChatResourceWithStreamingResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.AsyncCompletionsResourceWithStreamingResponse:
        from .resources.completions import AsyncCompletionsResourceWithStreamingResponse

        return AsyncCompletionsResourceWithStreamingResponse(self._client.completions)

    @cached_property
    def batch_inference_jobs(self) -> batch_inference_jobs.AsyncBatchInferenceJobsResourceWithStreamingResponse:
        from .resources.batch_inference_jobs import AsyncBatchInferenceJobsResourceWithStreamingResponse

        return AsyncBatchInferenceJobsResourceWithStreamingResponse(self._client.batch_inference_jobs)

    @cached_property
    def deployments(self) -> deployments.AsyncDeploymentsResourceWithStreamingResponse:
        from .resources.deployments import AsyncDeploymentsResourceWithStreamingResponse

        return AsyncDeploymentsResourceWithStreamingResponse(self._client.deployments)

    @cached_property
    def models(self) -> models.AsyncModelsResourceWithStreamingResponse:
        from .resources.models import AsyncModelsResourceWithStreamingResponse

        return AsyncModelsResourceWithStreamingResponse(self._client.models)

    @cached_property
    def lora(self) -> lora.AsyncLoraResourceWithStreamingResponse:
        from .resources.lora import AsyncLoraResourceWithStreamingResponse

        return AsyncLoraResourceWithStreamingResponse(self._client.lora)

    @cached_property
    def deployment_shape_versions(
        self,
    ) -> deployment_shape_versions.AsyncDeploymentShapeVersionsResourceWithStreamingResponse:
        from .resources.deployment_shape_versions import AsyncDeploymentShapeVersionsResourceWithStreamingResponse

        return AsyncDeploymentShapeVersionsResourceWithStreamingResponse(self._client.deployment_shape_versions)

    @cached_property
    def datasets(self) -> datasets.AsyncDatasetsResourceWithStreamingResponse:
        from .resources.datasets import AsyncDatasetsResourceWithStreamingResponse

        return AsyncDatasetsResourceWithStreamingResponse(self._client.datasets)

    @cached_property
    def supervised_fine_tuning_jobs(
        self,
    ) -> supervised_fine_tuning_jobs.AsyncSupervisedFineTuningJobsResourceWithStreamingResponse:
        from .resources.supervised_fine_tuning_jobs import AsyncSupervisedFineTuningJobsResourceWithStreamingResponse

        return AsyncSupervisedFineTuningJobsResourceWithStreamingResponse(self._client.supervised_fine_tuning_jobs)

    @cached_property
    def reinforcement_fine_tuning_jobs(
        self,
    ) -> reinforcement_fine_tuning_jobs.AsyncReinforcementFineTuningJobsResourceWithStreamingResponse:
        from .resources.reinforcement_fine_tuning_jobs import (
            AsyncReinforcementFineTuningJobsResourceWithStreamingResponse,
        )

        return AsyncReinforcementFineTuningJobsResourceWithStreamingResponse(
            self._client.reinforcement_fine_tuning_jobs
        )

    @cached_property
    def reinforcement_fine_tuning_steps(
        self,
    ) -> reinforcement_fine_tuning_steps.AsyncReinforcementFineTuningStepsResourceWithStreamingResponse:
        from .resources.reinforcement_fine_tuning_steps import (
            AsyncReinforcementFineTuningStepsResourceWithStreamingResponse,
        )

        return AsyncReinforcementFineTuningStepsResourceWithStreamingResponse(
            self._client.reinforcement_fine_tuning_steps
        )

    @cached_property
    def dpo_jobs(self) -> dpo_jobs.AsyncDpoJobsResourceWithStreamingResponse:
        from .resources.dpo_jobs import AsyncDpoJobsResourceWithStreamingResponse

        return AsyncDpoJobsResourceWithStreamingResponse(self._client.dpo_jobs)

    @cached_property
    def evaluation_jobs(self) -> evaluation_jobs.AsyncEvaluationJobsResourceWithStreamingResponse:
        from .resources.evaluation_jobs import AsyncEvaluationJobsResourceWithStreamingResponse

        return AsyncEvaluationJobsResourceWithStreamingResponse(self._client.evaluation_jobs)

    @cached_property
    def evaluators(self) -> evaluators.AsyncEvaluatorsResourceWithStreamingResponse:
        from .resources.evaluators import AsyncEvaluatorsResourceWithStreamingResponse

        return AsyncEvaluatorsResourceWithStreamingResponse(self._client.evaluators)

    @cached_property
    def accounts(self) -> accounts.AsyncAccountsResourceWithStreamingResponse:
        from .resources.accounts import AsyncAccountsResourceWithStreamingResponse

        return AsyncAccountsResourceWithStreamingResponse(self._client.accounts)

    @cached_property
    def users(self) -> users.AsyncUsersResourceWithStreamingResponse:
        from .resources.users import AsyncUsersResourceWithStreamingResponse

        return AsyncUsersResourceWithStreamingResponse(self._client.users)

    @cached_property
    def api_keys(self) -> api_keys.AsyncAPIKeysResourceWithStreamingResponse:
        from .resources.api_keys import AsyncAPIKeysResourceWithStreamingResponse

        return AsyncAPIKeysResourceWithStreamingResponse(self._client.api_keys)

    @cached_property
    def secrets(self) -> secrets.AsyncSecretsResourceWithStreamingResponse:
        from .resources.secrets import AsyncSecretsResourceWithStreamingResponse

        return AsyncSecretsResourceWithStreamingResponse(self._client.secrets)


Client = Fireworks

AsyncClient = AsyncFireworks
