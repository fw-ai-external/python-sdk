from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Union, Mapping
from collections.abc import Mapping
from typing_extensions import Self, override

import httpx

from fireworks.training.sdk._core import _exceptions
from fireworks.training.sdk.errors import (
    _is_serverless_gateway_url,
    _attach_training_error_source,
    _serverless_gateway_source_error,
)
from fireworks.training.sdk._core._qs import Querystring
from fireworks.training.sdk._core._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from fireworks.training.sdk._core._utils import is_given, get_async_library
from fireworks.training.sdk._core._compat import cached_property
from fireworks.training.sdk._core._version import PROTOCOL_CLIENT_VERSION, __version__
from fireworks.training.sdk._core._streaming import AsyncStream as AsyncStream
from fireworks.training.sdk._core._exceptions import APIStatusError
from fireworks.training.sdk._core._base_client import DEFAULT_MAX_RETRIES, AsyncAPIClient
from fireworks.training.sdk.types.client_config_response import ClientConfigResponse
from fireworks.training.sdk._core.lib._auth_token_provider import AuthTokenProvider, ApiKeyAuthProvider

if TYPE_CHECKING:
    from fireworks.training.sdk._core.resources import futures, telemetry
    from fireworks.training.sdk._core.resources.models import AsyncModelsResource
    from fireworks.training.sdk._core.resources.futures import AsyncFuturesResource
    from fireworks.training.sdk._core.resources.service import AsyncServiceResource
    from fireworks.training.sdk._core.resources.weights import AsyncWeightsResource
    from fireworks.training.sdk._core.resources.sampling import AsyncSamplingResource
    from fireworks.training.sdk._core.resources.training import AsyncTrainingResource
    from fireworks.training.sdk._core.resources.telemetry import AsyncTelemetryResource

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "AsyncTrainingHTTPClient",
]


_DEFAULT_CLIENT_CONFIG = ClientConfigResponse()


def resolve_training_base_url(base_url: str | httpx.URL | None) -> str | httpx.URL:
    if base_url is None:
        base_url = os.environ.get("TINKER_BASE_URL")
    return base_url or "https://api.fireworks.ai/training/v1/serverless"


class AsyncTrainingHTTPClient(AsyncAPIClient):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
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
        _auth: AuthTokenProvider | None = None,
        # Internal: server-resolved feature flags. Set by InternalClientHolder
        # after the one-off /client/config fetch.
        _client_config: ClientConfigResponse = _DEFAULT_CLIENT_CONFIG,
    ) -> None:
        """Construct an async Fireworks training HTTP client.

        This automatically infers the `api_key` argument from the `FIREWORKS_API_KEY` environment variable if it is not provided.
        """
        if _auth is not None:
            self._auth = _auth
        else:
            self._auth = ApiKeyAuthProvider(api_key=api_key)

        base_url = resolve_training_base_url(base_url)

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            use_pyqwest=_client_config.use_pyqwest_transport,
            _strict_response_validation=_strict_response_validation,
        )

        self._client_config = _client_config

        self._idempotency_header = "X-Idempotency-Key"

    @cached_property
    def service(self) -> AsyncServiceResource:
        from fireworks.training.sdk._core.resources.service import AsyncServiceResource

        return AsyncServiceResource(self)

    @cached_property
    def training(self) -> AsyncTrainingResource:
        from fireworks.training.sdk._core.resources.training import AsyncTrainingResource

        return AsyncTrainingResource(self)

    @cached_property
    def models(self) -> AsyncModelsResource:
        from fireworks.training.sdk._core.resources.models import AsyncModelsResource

        return AsyncModelsResource(self)

    @cached_property
    def weights(self) -> AsyncWeightsResource:
        from fireworks.training.sdk._core.resources.weights import AsyncWeightsResource

        return AsyncWeightsResource(self)

    @cached_property
    def sampling(self) -> AsyncSamplingResource:
        from fireworks.training.sdk._core.resources.sampling import AsyncSamplingResource

        return AsyncSamplingResource(self)

    @cached_property
    def futures(self) -> AsyncFuturesResource:
        from fireworks.training.sdk._core.resources.futures import AsyncFuturesResource

        return AsyncFuturesResource(self)

    @cached_property
    def telemetry(self) -> AsyncTelemetryResource:
        from fireworks.training.sdk._core.resources.telemetry import AsyncTelemetryResource

        return AsyncTelemetryResource(self)

    @property
    @override
    def user_agent(self) -> str:
        # Reliability reporting recognizes this training protocol identifier.
        return f"AsyncTinker/Python {PROTOCOL_CLIENT_VERSION}"

    @cached_property
    def with_raw_response(self) -> AsyncTrainingHTTPClientWithRawResponse:
        return AsyncTrainingHTTPClientWithRawResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def custom_auth(self) -> AuthTokenProvider:
        return self._auth

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
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
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
        return self.__class__(
            _auth=self._auth,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(self, err_msg: str, *, body: object, response: httpx.Response) -> APIStatusError:
        exc = self._make_status_error_unclassified(err_msg, body=body, response=response)
        try:
            if _is_serverless_gateway_url(response.request.url):
                candidate = body if isinstance(body, Mapping) else response.json()
                _attach_training_error_source(exc, _serverless_gateway_source_error(candidate))
        except Exception:
            pass
        return exc

    def _make_status_error_unclassified(
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


class AsyncTrainingHTTPClientWithRawResponse:
    _client: AsyncTrainingHTTPClient

    def __init__(self, client: AsyncTrainingHTTPClient) -> None:
        self._client = client

    @cached_property
    def futures(self) -> futures.AsyncFuturesResourceWithRawResponse:
        from fireworks.training.sdk._core.resources.futures import AsyncFuturesResourceWithRawResponse

        return AsyncFuturesResourceWithRawResponse(self._client.futures)

    @cached_property
    def telemetry(self) -> telemetry.AsyncTelemetryResourceWithRawResponse:
        from fireworks.training.sdk._core.resources.telemetry import AsyncTelemetryResourceWithRawResponse

        return AsyncTelemetryResourceWithRawResponse(self._client.telemetry)
