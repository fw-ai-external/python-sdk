# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Mapping
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
from ._version import __version__
from .resources import (
    lora,
    users,
    models,
    accounts,
    api_keys,
    datasets,
    dpo_jobs,
    deployments,
    batch_inference_jobs,
    supervised_fine_tuning_jobs,
    reinforcement_fine_tuning_jobs,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, FireworksError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
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
    accounts: accounts.AccountsResource
    batch_inference_jobs: batch_inference_jobs.BatchInferenceJobsResource
    datasets: datasets.DatasetsResource
    deployments: deployments.DeploymentsResource
    models: models.ModelsResource
    reinforcement_fine_tuning_jobs: reinforcement_fine_tuning_jobs.ReinforcementFineTuningJobsResource
    supervised_fine_tuning_jobs: supervised_fine_tuning_jobs.SupervisedFineTuningJobsResource
    users: users.UsersResource
    api_keys: api_keys.APIKeysResource
    lora: lora.LoraResource
    dpo_jobs: dpo_jobs.DpoJobsResource
    with_raw_response: FireworksWithRawResponse
    with_streaming_response: FireworksWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
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

        This automatically infers the `api_key` argument from the `FIREWORKS_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("FIREWORKS_API_KEY")
        if api_key is None:
            raise FireworksError(
                "The api_key client option must be set either by passing api_key to the client or by setting the FIREWORKS_API_KEY environment variable"
            )
        self.api_key = api_key

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

        self.accounts = accounts.AccountsResource(self)
        self.batch_inference_jobs = batch_inference_jobs.BatchInferenceJobsResource(self)
        self.datasets = datasets.DatasetsResource(self)
        self.deployments = deployments.DeploymentsResource(self)
        self.models = models.ModelsResource(self)
        self.reinforcement_fine_tuning_jobs = reinforcement_fine_tuning_jobs.ReinforcementFineTuningJobsResource(self)
        self.supervised_fine_tuning_jobs = supervised_fine_tuning_jobs.SupervisedFineTuningJobsResource(self)
        self.users = users.UsersResource(self)
        self.api_keys = api_keys.APIKeysResource(self)
        self.lora = lora.LoraResource(self)
        self.dpo_jobs = dpo_jobs.DpoJobsResource(self)
        self.with_raw_response = FireworksWithRawResponse(self)
        self.with_streaming_response = FireworksWithStreamedResponse(self)

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
    accounts: accounts.AsyncAccountsResource
    batch_inference_jobs: batch_inference_jobs.AsyncBatchInferenceJobsResource
    datasets: datasets.AsyncDatasetsResource
    deployments: deployments.AsyncDeploymentsResource
    models: models.AsyncModelsResource
    reinforcement_fine_tuning_jobs: reinforcement_fine_tuning_jobs.AsyncReinforcementFineTuningJobsResource
    supervised_fine_tuning_jobs: supervised_fine_tuning_jobs.AsyncSupervisedFineTuningJobsResource
    users: users.AsyncUsersResource
    api_keys: api_keys.AsyncAPIKeysResource
    lora: lora.AsyncLoraResource
    dpo_jobs: dpo_jobs.AsyncDpoJobsResource
    with_raw_response: AsyncFireworksWithRawResponse
    with_streaming_response: AsyncFireworksWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
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

        This automatically infers the `api_key` argument from the `FIREWORKS_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("FIREWORKS_API_KEY")
        if api_key is None:
            raise FireworksError(
                "The api_key client option must be set either by passing api_key to the client or by setting the FIREWORKS_API_KEY environment variable"
            )
        self.api_key = api_key

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

        self.accounts = accounts.AsyncAccountsResource(self)
        self.batch_inference_jobs = batch_inference_jobs.AsyncBatchInferenceJobsResource(self)
        self.datasets = datasets.AsyncDatasetsResource(self)
        self.deployments = deployments.AsyncDeploymentsResource(self)
        self.models = models.AsyncModelsResource(self)
        self.reinforcement_fine_tuning_jobs = reinforcement_fine_tuning_jobs.AsyncReinforcementFineTuningJobsResource(
            self
        )
        self.supervised_fine_tuning_jobs = supervised_fine_tuning_jobs.AsyncSupervisedFineTuningJobsResource(self)
        self.users = users.AsyncUsersResource(self)
        self.api_keys = api_keys.AsyncAPIKeysResource(self)
        self.lora = lora.AsyncLoraResource(self)
        self.dpo_jobs = dpo_jobs.AsyncDpoJobsResource(self)
        self.with_raw_response = AsyncFireworksWithRawResponse(self)
        self.with_streaming_response = AsyncFireworksWithStreamedResponse(self)

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
    def __init__(self, client: Fireworks) -> None:
        self.accounts = accounts.AccountsResourceWithRawResponse(client.accounts)
        self.batch_inference_jobs = batch_inference_jobs.BatchInferenceJobsResourceWithRawResponse(
            client.batch_inference_jobs
        )
        self.datasets = datasets.DatasetsResourceWithRawResponse(client.datasets)
        self.deployments = deployments.DeploymentsResourceWithRawResponse(client.deployments)
        self.models = models.ModelsResourceWithRawResponse(client.models)
        self.reinforcement_fine_tuning_jobs = (
            reinforcement_fine_tuning_jobs.ReinforcementFineTuningJobsResourceWithRawResponse(
                client.reinforcement_fine_tuning_jobs
            )
        )
        self.supervised_fine_tuning_jobs = supervised_fine_tuning_jobs.SupervisedFineTuningJobsResourceWithRawResponse(
            client.supervised_fine_tuning_jobs
        )
        self.users = users.UsersResourceWithRawResponse(client.users)
        self.api_keys = api_keys.APIKeysResourceWithRawResponse(client.api_keys)
        self.lora = lora.LoraResourceWithRawResponse(client.lora)
        self.dpo_jobs = dpo_jobs.DpoJobsResourceWithRawResponse(client.dpo_jobs)


class AsyncFireworksWithRawResponse:
    def __init__(self, client: AsyncFireworks) -> None:
        self.accounts = accounts.AsyncAccountsResourceWithRawResponse(client.accounts)
        self.batch_inference_jobs = batch_inference_jobs.AsyncBatchInferenceJobsResourceWithRawResponse(
            client.batch_inference_jobs
        )
        self.datasets = datasets.AsyncDatasetsResourceWithRawResponse(client.datasets)
        self.deployments = deployments.AsyncDeploymentsResourceWithRawResponse(client.deployments)
        self.models = models.AsyncModelsResourceWithRawResponse(client.models)
        self.reinforcement_fine_tuning_jobs = (
            reinforcement_fine_tuning_jobs.AsyncReinforcementFineTuningJobsResourceWithRawResponse(
                client.reinforcement_fine_tuning_jobs
            )
        )
        self.supervised_fine_tuning_jobs = (
            supervised_fine_tuning_jobs.AsyncSupervisedFineTuningJobsResourceWithRawResponse(
                client.supervised_fine_tuning_jobs
            )
        )
        self.users = users.AsyncUsersResourceWithRawResponse(client.users)
        self.api_keys = api_keys.AsyncAPIKeysResourceWithRawResponse(client.api_keys)
        self.lora = lora.AsyncLoraResourceWithRawResponse(client.lora)
        self.dpo_jobs = dpo_jobs.AsyncDpoJobsResourceWithRawResponse(client.dpo_jobs)


class FireworksWithStreamedResponse:
    def __init__(self, client: Fireworks) -> None:
        self.accounts = accounts.AccountsResourceWithStreamingResponse(client.accounts)
        self.batch_inference_jobs = batch_inference_jobs.BatchInferenceJobsResourceWithStreamingResponse(
            client.batch_inference_jobs
        )
        self.datasets = datasets.DatasetsResourceWithStreamingResponse(client.datasets)
        self.deployments = deployments.DeploymentsResourceWithStreamingResponse(client.deployments)
        self.models = models.ModelsResourceWithStreamingResponse(client.models)
        self.reinforcement_fine_tuning_jobs = (
            reinforcement_fine_tuning_jobs.ReinforcementFineTuningJobsResourceWithStreamingResponse(
                client.reinforcement_fine_tuning_jobs
            )
        )
        self.supervised_fine_tuning_jobs = (
            supervised_fine_tuning_jobs.SupervisedFineTuningJobsResourceWithStreamingResponse(
                client.supervised_fine_tuning_jobs
            )
        )
        self.users = users.UsersResourceWithStreamingResponse(client.users)
        self.api_keys = api_keys.APIKeysResourceWithStreamingResponse(client.api_keys)
        self.lora = lora.LoraResourceWithStreamingResponse(client.lora)
        self.dpo_jobs = dpo_jobs.DpoJobsResourceWithStreamingResponse(client.dpo_jobs)


class AsyncFireworksWithStreamedResponse:
    def __init__(self, client: AsyncFireworks) -> None:
        self.accounts = accounts.AsyncAccountsResourceWithStreamingResponse(client.accounts)
        self.batch_inference_jobs = batch_inference_jobs.AsyncBatchInferenceJobsResourceWithStreamingResponse(
            client.batch_inference_jobs
        )
        self.datasets = datasets.AsyncDatasetsResourceWithStreamingResponse(client.datasets)
        self.deployments = deployments.AsyncDeploymentsResourceWithStreamingResponse(client.deployments)
        self.models = models.AsyncModelsResourceWithStreamingResponse(client.models)
        self.reinforcement_fine_tuning_jobs = (
            reinforcement_fine_tuning_jobs.AsyncReinforcementFineTuningJobsResourceWithStreamingResponse(
                client.reinforcement_fine_tuning_jobs
            )
        )
        self.supervised_fine_tuning_jobs = (
            supervised_fine_tuning_jobs.AsyncSupervisedFineTuningJobsResourceWithStreamingResponse(
                client.supervised_fine_tuning_jobs
            )
        )
        self.users = users.AsyncUsersResourceWithStreamingResponse(client.users)
        self.api_keys = api_keys.AsyncAPIKeysResourceWithStreamingResponse(client.api_keys)
        self.lora = lora.AsyncLoraResourceWithStreamingResponse(client.lora)
        self.dpo_jobs = dpo_jobs.AsyncDpoJobsResourceWithStreamingResponse(client.dpo_jobs)


Client = Fireworks

AsyncClient = AsyncFireworks
