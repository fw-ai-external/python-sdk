# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal

import httpx

from ..types import (
    Model,
    model_get_params,
    model_list_params,
    model_create_params,
    model_update_params,
    model_prepare_params,
    model_validate_upload_params,
    model_get_upload_endpoint_params,
    model_get_download_endpoint_params,
)
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..types.model import Model
from .._base_client import make_request_options
from ..types.model_param import ModelParam
from ..types.type_date_param import TypeDateParam
from ..types.peft_details_param import PeftDetailsParam
from ..types.model_list_response import ModelListResponse
from ..types.base_model_details_param import BaseModelDetailsParam
from ..types.conversation_config_param import ConversationConfigParam
from ..types.model_get_upload_endpoint_response import ModelGetUploadEndpointResponse
from ..types.model_get_download_endpoint_response import ModelGetDownloadEndpointResponse

__all__ = ["ModelsResource", "AsyncModelsResource"]


class ModelsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return ModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return ModelsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str | None = None,
        model_id: str,
        cluster: str | Omit = omit,
        model: ModelParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """
        Create Model

        Args:
          model_id: ID of the model.

          cluster: The resource name of the BYOC cluster to which this model belongs. e.g.
              accounts/my-account/clusters/my-cluster. Empty if it belongs to a Fireworks
              cluster.

          model: The properties of the Model being created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/models"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models",
            body=maybe_transform(
                {
                    "model_id": model_id,
                    "cluster": cluster,
                    "model": model,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    def update(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        base_model_details: BaseModelDetailsParam | Omit = omit,
        context_length: int | Omit = omit,
        conversation_config: ConversationConfigParam | Omit = omit,
        default_draft_model: str | Omit = omit,
        default_draft_token_count: int | Omit = omit,
        deprecation_date: TypeDateParam | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        github_url: str | Omit = omit,
        hugging_face_url: str | Omit = omit,
        kind: Literal[
            "KIND_UNSPECIFIED",
            "HF_BASE_MODEL",
            "HF_PEFT_ADDON",
            "HF_TEFT_ADDON",
            "FLUMINA_BASE_MODEL",
            "FLUMINA_ADDON",
            "DRAFT_ADDON",
            "FIRE_AGENT",
            "LIVE_MERGE",
            "CUSTOM_MODEL",
            "EMBEDDING_MODEL",
            "SNAPSHOT_MODEL",
        ]
        | Omit = omit,
        peft_details: PeftDetailsParam | Omit = omit,
        public: bool | Omit = omit,
        snapshot_type: Literal["FULL_SNAPSHOT", "INCREMENTAL_SNAPSHOT"] | Omit = omit,
        supports_image_input: bool | Omit = omit,
        supports_lora: bool | Omit = omit,
        supports_tools: bool | Omit = omit,
        teft_details: object | Omit = omit,
        training_context_length: int | Omit = omit,
        use_hf_apply_chat_template: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """Update Model

        Args:
          base_model_details: Base model details.

        Required if kind is HF_BASE_MODEL. Must not be set
              otherwise.

          context_length: The maximum context length supported by the model.

          conversation_config: If set, the Chat Completions API will be enabled for this model.

          default_draft_model: The default draft model to use when creating a deployment. If empty, speculative
              decoding is disabled by default.

          default_draft_token_count: The default draft token count to use when creating a deployment. Must be
              specified if default_draft_model is specified.

          deprecation_date: If specified, this is the date when the serverless deployment of the model will
              be taken down.

          description: The description of the model. Must be fewer than 1000 characters long.

          display_name: Human-readable display name of the model. e.g. "My Model" Must be fewer than 64
              characters long.

          github_url: The URL to GitHub repository of the model.

          hugging_face_url: The URL to the Hugging Face model.

          kind: The kind of model. If not specified, the default is HF_PEFT_ADDON.

          peft_details: PEFT addon details. Required if kind is HF_PEFT_ADDON or HF_TEFT_ADDON.

          public: If true, the model will be publicly readable.

          supports_image_input: If set, images can be provided as input to the model.

          supports_lora: Whether this model supports LoRA.

          supports_tools: If set, tools (i.e. functions) can be provided as input to the model, and the
              model may respond with one or more tool calls.

          teft_details: TEFT addon details. Required if kind is HF_TEFT_ADDON. Must not be set
              otherwise.

          training_context_length: The maximum context length supported by the model.

          use_hf_apply_chat_template: If true, the model will use the Hugging Face apply_chat_template API to apply
              the chat template.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/models/{model_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}",
            body=maybe_transform(
                {
                    "base_model_details": base_model_details,
                    "context_length": context_length,
                    "conversation_config": conversation_config,
                    "default_draft_model": default_draft_model,
                    "default_draft_token_count": default_draft_token_count,
                    "deprecation_date": deprecation_date,
                    "description": description,
                    "display_name": display_name,
                    "github_url": github_url,
                    "hugging_face_url": hugging_face_url,
                    "kind": kind,
                    "peft_details": peft_details,
                    "public": public,
                    "snapshot_type": snapshot_type,
                    "supports_image_input": supports_image_input,
                    "supports_lora": supports_lora,
                    "supports_tools": supports_tools,
                    "teft_details": teft_details,
                    "training_context_length": training_context_length,
                    "use_hf_apply_chat_template": use_hf_apply_chat_template,
                },
                model_update_params.ModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    def list(
        self,
        *,
        account_id: str | None = None,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListResponse:
        """
        List Models

        Args:
          filter: Only model satisfying the provided filter (if specified) will be returned. See
              https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of models to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListModels call. Provide this to retrieve
              the subsequent page. When paginating, all other parameters provided to
              ListModels must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/models"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "read_mask": read_mask,
                    },
                    model_list_params.ModelListParams,
                ),
            ),
            cast_to=ModelListResponse,
        )

    def delete(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Model

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/models/{model_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """Get Model

        Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/models/{model_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, model_get_params.ModelGetParams),
            ),
            cast_to=Model,
        )

    def get_download_endpoint(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelGetDownloadEndpointResponse:
        """
        Get Model Download Endpoint

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/models/{model_id}:getDownloadEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:getDownloadEndpoint",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, model_get_download_endpoint_params.ModelGetDownloadEndpointParams
                ),
            ),
            cast_to=ModelGetDownloadEndpointResponse,
        )

    def get_upload_endpoint(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        filename_to_size: Dict[str, str],
        enable_resumable_upload: bool | Omit = omit,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelGetUploadEndpointResponse:
        """
        Get Model Upload Endpoint

        Args:
          filename_to_size: A mapping from the file name to its size in bytes.

          enable_resumable_upload: If true, enable resumable upload instead of PUT.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/models/{model_id}:getUploadEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:getUploadEndpoint",
            body=maybe_transform(
                {
                    "filename_to_size": filename_to_size,
                    "enable_resumable_upload": enable_resumable_upload,
                    "read_mask": read_mask,
                },
                model_get_upload_endpoint_params.ModelGetUploadEndpointParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelGetUploadEndpointResponse,
        )

    def prepare(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        precision: Literal[
            "PRECISION_UNSPECIFIED",
            "FP16",
            "FP8",
            "FP8_MM",
            "FP8_AR",
            "FP8_MM_KV_ATTN",
            "FP8_KV",
            "FP8_MM_V2",
            "FP8_V2",
            "FP8_MM_KV_ATTN_V2",
            "NF4",
            "FP4",
            "BF16",
            "FP4_BLOCKSCALED_MM",
            "FP4_MX_MOE",
        ]
        | Omit = omit,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Prepare Model for different precisions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/models/{model_id}:prepare"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:prepare",
            body=maybe_transform(
                {
                    "precision": precision,
                    "read_mask": read_mask,
                },
                model_prepare_params.ModelPrepareParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def validate_upload(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        config_only: bool | Omit = omit,
        skip_hf_config_validation: bool | Omit = omit,
        trust_remote_code: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Validate Model Upload

        Args:
          config_only: If true, skip tokenizer and parameter name validation.

          skip_hf_config_validation: If true, skip the Hugging Face config validation.

          trust_remote_code: If true, trusts remote code when validating the Hugging Face config.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/models/{model_id}:validateUpload"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:validateUpload",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "config_only": config_only,
                        "skip_hf_config_validation": skip_hf_config_validation,
                        "trust_remote_code": trust_remote_code,
                    },
                    model_validate_upload_params.ModelValidateUploadParams,
                ),
            ),
            cast_to=object,
        )


class AsyncModelsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncModelsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str | None = None,
        model_id: str,
        cluster: str | Omit = omit,
        model: ModelParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """
        Create Model

        Args:
          model_id: ID of the model.

          cluster: The resource name of the BYOC cluster to which this model belongs. e.g.
              accounts/my-account/clusters/my-cluster. Empty if it belongs to a Fireworks
              cluster.

          model: The properties of the Model being created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/models"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models",
            body=await async_maybe_transform(
                {
                    "model_id": model_id,
                    "cluster": cluster,
                    "model": model,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    async def update(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        base_model_details: BaseModelDetailsParam | Omit = omit,
        context_length: int | Omit = omit,
        conversation_config: ConversationConfigParam | Omit = omit,
        default_draft_model: str | Omit = omit,
        default_draft_token_count: int | Omit = omit,
        deprecation_date: TypeDateParam | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        github_url: str | Omit = omit,
        hugging_face_url: str | Omit = omit,
        kind: Literal[
            "KIND_UNSPECIFIED",
            "HF_BASE_MODEL",
            "HF_PEFT_ADDON",
            "HF_TEFT_ADDON",
            "FLUMINA_BASE_MODEL",
            "FLUMINA_ADDON",
            "DRAFT_ADDON",
            "FIRE_AGENT",
            "LIVE_MERGE",
            "CUSTOM_MODEL",
            "EMBEDDING_MODEL",
            "SNAPSHOT_MODEL",
        ]
        | Omit = omit,
        peft_details: PeftDetailsParam | Omit = omit,
        public: bool | Omit = omit,
        snapshot_type: Literal["FULL_SNAPSHOT", "INCREMENTAL_SNAPSHOT"] | Omit = omit,
        supports_image_input: bool | Omit = omit,
        supports_lora: bool | Omit = omit,
        supports_tools: bool | Omit = omit,
        teft_details: object | Omit = omit,
        training_context_length: int | Omit = omit,
        use_hf_apply_chat_template: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """Update Model

        Args:
          base_model_details: Base model details.

        Required if kind is HF_BASE_MODEL. Must not be set
              otherwise.

          context_length: The maximum context length supported by the model.

          conversation_config: If set, the Chat Completions API will be enabled for this model.

          default_draft_model: The default draft model to use when creating a deployment. If empty, speculative
              decoding is disabled by default.

          default_draft_token_count: The default draft token count to use when creating a deployment. Must be
              specified if default_draft_model is specified.

          deprecation_date: If specified, this is the date when the serverless deployment of the model will
              be taken down.

          description: The description of the model. Must be fewer than 1000 characters long.

          display_name: Human-readable display name of the model. e.g. "My Model" Must be fewer than 64
              characters long.

          github_url: The URL to GitHub repository of the model.

          hugging_face_url: The URL to the Hugging Face model.

          kind: The kind of model. If not specified, the default is HF_PEFT_ADDON.

          peft_details: PEFT addon details. Required if kind is HF_PEFT_ADDON or HF_TEFT_ADDON.

          public: If true, the model will be publicly readable.

          supports_image_input: If set, images can be provided as input to the model.

          supports_lora: Whether this model supports LoRA.

          supports_tools: If set, tools (i.e. functions) can be provided as input to the model, and the
              model may respond with one or more tool calls.

          teft_details: TEFT addon details. Required if kind is HF_TEFT_ADDON. Must not be set
              otherwise.

          training_context_length: The maximum context length supported by the model.

          use_hf_apply_chat_template: If true, the model will use the Hugging Face apply_chat_template API to apply
              the chat template.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/models/{model_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}",
            body=await async_maybe_transform(
                {
                    "base_model_details": base_model_details,
                    "context_length": context_length,
                    "conversation_config": conversation_config,
                    "default_draft_model": default_draft_model,
                    "default_draft_token_count": default_draft_token_count,
                    "deprecation_date": deprecation_date,
                    "description": description,
                    "display_name": display_name,
                    "github_url": github_url,
                    "hugging_face_url": hugging_face_url,
                    "kind": kind,
                    "peft_details": peft_details,
                    "public": public,
                    "snapshot_type": snapshot_type,
                    "supports_image_input": supports_image_input,
                    "supports_lora": supports_lora,
                    "supports_tools": supports_tools,
                    "teft_details": teft_details,
                    "training_context_length": training_context_length,
                    "use_hf_apply_chat_template": use_hf_apply_chat_template,
                },
                model_update_params.ModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    async def list(
        self,
        *,
        account_id: str | None = None,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListResponse:
        """
        List Models

        Args:
          filter: Only model satisfying the provided filter (if specified) will be returned. See
              https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of models to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListModels call. Provide this to retrieve
              the subsequent page. When paginating, all other parameters provided to
              ListModels must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/models"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "read_mask": read_mask,
                    },
                    model_list_params.ModelListParams,
                ),
            ),
            cast_to=ModelListResponse,
        )

    async def delete(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Model

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/models/{model_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """Get Model

        Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/models/{model_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"read_mask": read_mask}, model_get_params.ModelGetParams),
            ),
            cast_to=Model,
        )

    async def get_download_endpoint(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelGetDownloadEndpointResponse:
        """
        Get Model Download Endpoint

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/models/{model_id}:getDownloadEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:getDownloadEndpoint",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, model_get_download_endpoint_params.ModelGetDownloadEndpointParams
                ),
            ),
            cast_to=ModelGetDownloadEndpointResponse,
        )

    async def get_upload_endpoint(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        filename_to_size: Dict[str, str],
        enable_resumable_upload: bool | Omit = omit,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelGetUploadEndpointResponse:
        """
        Get Model Upload Endpoint

        Args:
          filename_to_size: A mapping from the file name to its size in bytes.

          enable_resumable_upload: If true, enable resumable upload instead of PUT.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/models/{model_id}:getUploadEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:getUploadEndpoint",
            body=await async_maybe_transform(
                {
                    "filename_to_size": filename_to_size,
                    "enable_resumable_upload": enable_resumable_upload,
                    "read_mask": read_mask,
                },
                model_get_upload_endpoint_params.ModelGetUploadEndpointParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelGetUploadEndpointResponse,
        )

    async def prepare(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        precision: Literal[
            "PRECISION_UNSPECIFIED",
            "FP16",
            "FP8",
            "FP8_MM",
            "FP8_AR",
            "FP8_MM_KV_ATTN",
            "FP8_KV",
            "FP8_MM_V2",
            "FP8_V2",
            "FP8_MM_KV_ATTN_V2",
            "NF4",
            "FP4",
            "BF16",
            "FP4_BLOCKSCALED_MM",
            "FP4_MX_MOE",
        ]
        | Omit = omit,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Prepare Model for different precisions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/models/{model_id}:prepare"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:prepare",
            body=await async_maybe_transform(
                {
                    "precision": precision,
                    "read_mask": read_mask,
                },
                model_prepare_params.ModelPrepareParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def validate_upload(
        self,
        model_id: str,
        *,
        account_id: str | None = None,
        config_only: bool | Omit = omit,
        skip_hf_config_validation: bool | Omit = omit,
        trust_remote_code: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Validate Model Upload

        Args:
          config_only: If true, skip tokenizer and parameter name validation.

          skip_hf_config_validation: If true, skip the Hugging Face config validation.

          trust_remote_code: If true, trusts remote code when validating the Hugging Face config.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not model_id:
            raise ValueError(f"Expected a non-empty value for `model_id` but received {model_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/models/{model_id}:validateUpload"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:validateUpload",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "config_only": config_only,
                        "skip_hf_config_validation": skip_hf_config_validation,
                        "trust_remote_code": trust_remote_code,
                    },
                    model_validate_upload_params.ModelValidateUploadParams,
                ),
            ),
            cast_to=object,
        )


class ModelsResourceWithRawResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_raw_response_wrapper(
            models.create,
        )
        self.update = to_raw_response_wrapper(
            models.update,
        )
        self.list = to_raw_response_wrapper(
            models.list,
        )
        self.delete = to_raw_response_wrapper(
            models.delete,
        )
        self.get = to_raw_response_wrapper(
            models.get,
        )
        self.get_download_endpoint = to_raw_response_wrapper(
            models.get_download_endpoint,
        )
        self.get_upload_endpoint = to_raw_response_wrapper(
            models.get_upload_endpoint,
        )
        self.prepare = to_raw_response_wrapper(
            models.prepare,
        )
        self.validate_upload = to_raw_response_wrapper(
            models.validate_upload,
        )


class AsyncModelsResourceWithRawResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_raw_response_wrapper(
            models.create,
        )
        self.update = async_to_raw_response_wrapper(
            models.update,
        )
        self.list = async_to_raw_response_wrapper(
            models.list,
        )
        self.delete = async_to_raw_response_wrapper(
            models.delete,
        )
        self.get = async_to_raw_response_wrapper(
            models.get,
        )
        self.get_download_endpoint = async_to_raw_response_wrapper(
            models.get_download_endpoint,
        )
        self.get_upload_endpoint = async_to_raw_response_wrapper(
            models.get_upload_endpoint,
        )
        self.prepare = async_to_raw_response_wrapper(
            models.prepare,
        )
        self.validate_upload = async_to_raw_response_wrapper(
            models.validate_upload,
        )


class ModelsResourceWithStreamingResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_streamed_response_wrapper(
            models.create,
        )
        self.update = to_streamed_response_wrapper(
            models.update,
        )
        self.list = to_streamed_response_wrapper(
            models.list,
        )
        self.delete = to_streamed_response_wrapper(
            models.delete,
        )
        self.get = to_streamed_response_wrapper(
            models.get,
        )
        self.get_download_endpoint = to_streamed_response_wrapper(
            models.get_download_endpoint,
        )
        self.get_upload_endpoint = to_streamed_response_wrapper(
            models.get_upload_endpoint,
        )
        self.prepare = to_streamed_response_wrapper(
            models.prepare,
        )
        self.validate_upload = to_streamed_response_wrapper(
            models.validate_upload,
        )


class AsyncModelsResourceWithStreamingResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_streamed_response_wrapper(
            models.create,
        )
        self.update = async_to_streamed_response_wrapper(
            models.update,
        )
        self.list = async_to_streamed_response_wrapper(
            models.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            models.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            models.get,
        )
        self.get_download_endpoint = async_to_streamed_response_wrapper(
            models.get_download_endpoint,
        )
        self.get_upload_endpoint = async_to_streamed_response_wrapper(
            models.get_upload_endpoint,
        )
        self.prepare = async_to_streamed_response_wrapper(
            models.prepare,
        )
        self.validate_upload = async_to_streamed_response_wrapper(
            models.validate_upload,
        )
