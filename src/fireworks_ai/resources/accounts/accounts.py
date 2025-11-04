# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime

import httpx

from .models import (
    ModelsResource,
    AsyncModelsResource,
    ModelsResourceWithRawResponse,
    AsyncModelsResourceWithRawResponse,
    ModelsResourceWithStreamingResponse,
    AsyncModelsResourceWithStreamingResponse,
)
from ...types import (
    account_list_params,
    account_retrieve_params,
    account_list_audit_logs_params,
    account_test_evaluation_params,
    account_preview_evaluator_params,
    account_create_evaluator_v2_params,
    account_batch_delete_batch_jobs_params,
    account_batch_delete_node_pools_params,
    account_delete_node_pool_binding_params,
    account_batch_delete_environments_params,
    account_delete_aws_iam_role_binding_params,
    account_validate_evaluation_assertions_params,
)
from .billing import (
    BillingResource,
    AsyncBillingResource,
    BillingResourceWithRawResponse,
    AsyncBillingResourceWithRawResponse,
    BillingResourceWithStreamingResponse,
    AsyncBillingResourceWithStreamingResponse,
)
from .routers import (
    RoutersResource,
    AsyncRoutersResource,
    RoutersResourceWithRawResponse,
    AsyncRoutersResourceWithRawResponse,
    RoutersResourceWithStreamingResponse,
    AsyncRoutersResourceWithStreamingResponse,
)
from .secrets import (
    SecretsResource,
    AsyncSecretsResource,
    SecretsResourceWithRawResponse,
    AsyncSecretsResourceWithRawResponse,
    SecretsResourceWithStreamingResponse,
    AsyncSecretsResourceWithStreamingResponse,
)
from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from .clusters import (
    ClustersResource,
    AsyncClustersResource,
    ClustersResourceWithRawResponse,
    AsyncClustersResourceWithRawResponse,
    ClustersResourceWithStreamingResponse,
    AsyncClustersResourceWithStreamingResponse,
)
from .datasets import (
    DatasetsResource,
    AsyncDatasetsResource,
    DatasetsResourceWithRawResponse,
    AsyncDatasetsResourceWithRawResponse,
    DatasetsResourceWithStreamingResponse,
    AsyncDatasetsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .snapshots import (
    SnapshotsResource,
    AsyncSnapshotsResource,
    SnapshotsResourceWithRawResponse,
    AsyncSnapshotsResourceWithRawResponse,
    SnapshotsResourceWithStreamingResponse,
    AsyncSnapshotsResourceWithStreamingResponse,
)
from .batch_jobs import (
    BatchJobsResource,
    AsyncBatchJobsResource,
    BatchJobsResourceWithRawResponse,
    AsyncBatchJobsResourceWithRawResponse,
    BatchJobsResourceWithStreamingResponse,
    AsyncBatchJobsResourceWithStreamingResponse,
)
from .evaluators import (
    EvaluatorsResource,
    AsyncEvaluatorsResource,
    EvaluatorsResourceWithRawResponse,
    AsyncEvaluatorsResourceWithRawResponse,
    EvaluatorsResourceWithStreamingResponse,
    AsyncEvaluatorsResourceWithStreamingResponse,
)
from .node_pools import (
    NodePoolsResource,
    AsyncNodePoolsResource,
    NodePoolsResourceWithRawResponse,
    AsyncNodePoolsResourceWithRawResponse,
    NodePoolsResourceWithStreamingResponse,
    AsyncNodePoolsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .evaluations import (
    EvaluationsResource,
    AsyncEvaluationsResource,
    EvaluationsResourceWithRawResponse,
    AsyncEvaluationsResourceWithRawResponse,
    EvaluationsResourceWithStreamingResponse,
    AsyncEvaluationsResourceWithStreamingResponse,
)
from .mcp_servers import (
    McpServersResource,
    AsyncMcpServersResource,
    McpServersResourceWithRawResponse,
    AsyncMcpServersResourceWithRawResponse,
    McpServersResourceWithStreamingResponse,
    AsyncMcpServersResourceWithStreamingResponse,
)
from .users.users import (
    UsersResource,
    AsyncUsersResource,
    UsersResourceWithRawResponse,
    AsyncUsersResourceWithRawResponse,
    UsersResourceWithStreamingResponse,
    AsyncUsersResourceWithStreamingResponse,
)
from .environments import (
    EnvironmentsResource,
    AsyncEnvironmentsResource,
    EnvironmentsResourceWithRawResponse,
    AsyncEnvironmentsResourceWithRawResponse,
    EnvironmentsResourceWithStreamingResponse,
    AsyncEnvironmentsResourceWithStreamingResponse,
)
from .leaderboards import (
    LeaderboardsResource,
    AsyncLeaderboardsResource,
    LeaderboardsResourceWithRawResponse,
    AsyncLeaderboardsResourceWithRawResponse,
    LeaderboardsResourceWithStreamingResponse,
    AsyncLeaderboardsResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from ...types.account import Account
from .deployed_models import (
    DeployedModelsResource,
    AsyncDeployedModelsResource,
    DeployedModelsResourceWithRawResponse,
    AsyncDeployedModelsResourceWithRawResponse,
    DeployedModelsResourceWithStreamingResponse,
    AsyncDeployedModelsResourceWithStreamingResponse,
)
from .evaluation_jobs import (
    EvaluationJobsResource,
    AsyncEvaluationJobsResource,
    EvaluationJobsResourceWithRawResponse,
    AsyncEvaluationJobsResourceWithRawResponse,
    EvaluationJobsResourceWithStreamingResponse,
    AsyncEvaluationJobsResourceWithStreamingResponse,
)
from .peft_merge_jobs import (
    PeftMergeJobsResource,
    AsyncPeftMergeJobsResource,
    PeftMergeJobsResourceWithRawResponse,
    AsyncPeftMergeJobsResourceWithRawResponse,
    PeftMergeJobsResourceWithStreamingResponse,
    AsyncPeftMergeJobsResourceWithStreamingResponse,
)
from ...types.accounts import GatewayEvaluator
from .identity_providers import (
    IdentityProvidersResource,
    AsyncIdentityProvidersResource,
    IdentityProvidersResourceWithRawResponse,
    AsyncIdentityProvidersResourceWithRawResponse,
    IdentityProvidersResourceWithStreamingResponse,
    AsyncIdentityProvidersResourceWithStreamingResponse,
)
from .node_pool_bindings import (
    NodePoolBindingsResource,
    AsyncNodePoolBindingsResource,
    NodePoolBindingsResourceWithRawResponse,
    AsyncNodePoolBindingsResourceWithRawResponse,
    NodePoolBindingsResourceWithStreamingResponse,
    AsyncNodePoolBindingsResourceWithStreamingResponse,
)
from .batch_inference_jobs import (
    BatchInferenceJobsResource,
    AsyncBatchInferenceJobsResource,
    BatchInferenceJobsResourceWithRawResponse,
    AsyncBatchInferenceJobsResourceWithRawResponse,
    BatchInferenceJobsResourceWithStreamingResponse,
    AsyncBatchInferenceJobsResourceWithStreamingResponse,
)
from .aws_iam_role_bindings import (
    AwsIamRoleBindingsResource,
    AsyncAwsIamRoleBindingsResource,
    AwsIamRoleBindingsResourceWithRawResponse,
    AsyncAwsIamRoleBindingsResourceWithRawResponse,
    AwsIamRoleBindingsResourceWithStreamingResponse,
    AsyncAwsIamRoleBindingsResourceWithStreamingResponse,
)
from .deployments.deployments import (
    DeploymentsResource,
    AsyncDeploymentsResource,
    DeploymentsResourceWithRawResponse,
    AsyncDeploymentsResourceWithRawResponse,
    DeploymentsResourceWithStreamingResponse,
    AsyncDeploymentsResourceWithStreamingResponse,
)
from .supervised_fine_tuning_jobs import (
    SupervisedFineTuningJobsResource,
    AsyncSupervisedFineTuningJobsResource,
    SupervisedFineTuningJobsResourceWithRawResponse,
    AsyncSupervisedFineTuningJobsResourceWithRawResponse,
    SupervisedFineTuningJobsResourceWithStreamingResponse,
    AsyncSupervisedFineTuningJobsResourceWithStreamingResponse,
)
from ...types.account_list_response import AccountListResponse
from .reinforcement_fine_tuning_jobs import (
    ReinforcementFineTuningJobsResource,
    AsyncReinforcementFineTuningJobsResource,
    ReinforcementFineTuningJobsResourceWithRawResponse,
    AsyncReinforcementFineTuningJobsResourceWithRawResponse,
    ReinforcementFineTuningJobsResourceWithStreamingResponse,
    AsyncReinforcementFineTuningJobsResourceWithStreamingResponse,
)
from ...types.accounts.assertion_param import AssertionParam
from ...types.accounts.evaluation_param import EvaluationParam
from ...types.accounts.gateway_evaluator import GatewayEvaluator
from .deployment_shapes.deployment_shapes import (
    DeploymentShapesResource,
    AsyncDeploymentShapesResource,
    DeploymentShapesResourceWithRawResponse,
    AsyncDeploymentShapesResourceWithRawResponse,
    DeploymentShapesResourceWithStreamingResponse,
    AsyncDeploymentShapesResourceWithStreamingResponse,
)
from ...types.account_list_audit_logs_response import AccountListAuditLogsResponse
from ...types.accounts.gateway_evaluator_param import GatewayEvaluatorParam
from ...types.account_preview_evaluator_response import AccountPreviewEvaluatorResponse
from ...types.accounts.preview_evaluation_response import PreviewEvaluationResponse
from ...types.account_validate_evaluation_assertions_response import AccountValidateEvaluationAssertionsResponse

__all__ = ["AccountsResource", "AsyncAccountsResource"]


class AccountsResource(SyncAPIResource):
    @cached_property
    def peft_merge_jobs(self) -> PeftMergeJobsResource:
        return PeftMergeJobsResource(self._client)

    @cached_property
    def aws_iam_role_bindings(self) -> AwsIamRoleBindingsResource:
        return AwsIamRoleBindingsResource(self._client)

    @cached_property
    def batch_inference_jobs(self) -> BatchInferenceJobsResource:
        return BatchInferenceJobsResource(self._client)

    @cached_property
    def batch_jobs(self) -> BatchJobsResource:
        return BatchJobsResource(self._client)

    @cached_property
    def billing(self) -> BillingResource:
        return BillingResource(self._client)

    @cached_property
    def clusters(self) -> ClustersResource:
        return ClustersResource(self._client)

    @cached_property
    def datasets(self) -> DatasetsResource:
        return DatasetsResource(self._client)

    @cached_property
    def deployed_models(self) -> DeployedModelsResource:
        return DeployedModelsResource(self._client)

    @cached_property
    def deployment_shapes(self) -> DeploymentShapesResource:
        return DeploymentShapesResource(self._client)

    @cached_property
    def deployments(self) -> DeploymentsResource:
        return DeploymentsResource(self._client)

    @cached_property
    def environments(self) -> EnvironmentsResource:
        return EnvironmentsResource(self._client)

    @cached_property
    def evaluation_jobs(self) -> EvaluationJobsResource:
        return EvaluationJobsResource(self._client)

    @cached_property
    def evaluations(self) -> EvaluationsResource:
        return EvaluationsResource(self._client)

    @cached_property
    def evaluators(self) -> EvaluatorsResource:
        return EvaluatorsResource(self._client)

    @cached_property
    def identity_providers(self) -> IdentityProvidersResource:
        return IdentityProvidersResource(self._client)

    @cached_property
    def leaderboards(self) -> LeaderboardsResource:
        return LeaderboardsResource(self._client)

    @cached_property
    def mcp_servers(self) -> McpServersResource:
        return McpServersResource(self._client)

    @cached_property
    def models(self) -> ModelsResource:
        return ModelsResource(self._client)

    @cached_property
    def node_pool_bindings(self) -> NodePoolBindingsResource:
        return NodePoolBindingsResource(self._client)

    @cached_property
    def node_pools(self) -> NodePoolsResource:
        return NodePoolsResource(self._client)

    @cached_property
    def reinforcement_fine_tuning_jobs(self) -> ReinforcementFineTuningJobsResource:
        return ReinforcementFineTuningJobsResource(self._client)

    @cached_property
    def routers(self) -> RoutersResource:
        return RoutersResource(self._client)

    @cached_property
    def secrets(self) -> SecretsResource:
        return SecretsResource(self._client)

    @cached_property
    def snapshots(self) -> SnapshotsResource:
        return SnapshotsResource(self._client)

    @cached_property
    def supervised_fine_tuning_jobs(self) -> SupervisedFineTuningJobsResource:
        return SupervisedFineTuningJobsResource(self._client)

    @cached_property
    def users(self) -> UsersResource:
        return UsersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AccountsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        account_id: str,
        *,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """Get Account

        Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, account_retrieve_params.AccountRetrieveParams),
            ),
            cast_to=Account,
        )

    def list(
        self,
        *,
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
    ) -> AccountListResponse:
        """
        List Accounts

        Args:
          filter: Only accounts satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: Not supported. Accounts will be returned ordered by `name`.

          page_size: The maximum number of accounts to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListAccounts call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListAccounts must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/accounts",
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
                    account_list_params.AccountListParams,
                ),
            ),
            cast_to=AccountListResponse,
        )

    def batch_delete_batch_jobs(
        self,
        account_id: str,
        *,
        names: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Batch Delete Batch Jobs

        Args:
          names: The resource names of the batch jobs to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/batchJobs:batchDelete",
            body=maybe_transform(
                {"names": names}, account_batch_delete_batch_jobs_params.AccountBatchDeleteBatchJobsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def batch_delete_environments(
        self,
        account_id: str,
        *,
        names: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Batch Delete Environments

        Args:
          names: The resource names of the environments to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/environments:batchDelete",
            body=maybe_transform(
                {"names": names}, account_batch_delete_environments_params.AccountBatchDeleteEnvironmentsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def batch_delete_node_pools(
        self,
        account_id: str,
        *,
        names: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Batch Delete Node Pools

        Args:
          names: The resource names of the node pools to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/nodePools:batchDelete",
            body=maybe_transform(
                {"names": names}, account_batch_delete_node_pools_params.AccountBatchDeleteNodePoolsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def create_evaluator_v2(
        self,
        account_id: str,
        *,
        evaluator: GatewayEvaluatorParam,
        evaluator_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluator:
        """
        V2 api for evaluator creation, this is for new eval protocol evaluators, where
        it will trigger an async template build process during the creation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluatorsV2",
            body=maybe_transform(
                {
                    "evaluator": evaluator,
                    "evaluator_id": evaluator_id,
                },
                account_create_evaluator_v2_params.AccountCreateEvaluatorV2Params,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayEvaluator,
        )

    def delete_aws_iam_role_binding(
        self,
        account_id: str,
        *,
        principal: str | Omit = omit,
        role: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Aws Iam Role Binding

        Args:
          principal: The principal that is allowed to assume the AWS IAM role. This must be the email
              address of the user.

          role: The AWS IAM role ARN that is allowed to be assumed by the principal.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/awsIamRoleBindings:delete",
            body=maybe_transform(
                {
                    "principal": principal,
                    "role": role,
                },
                account_delete_aws_iam_role_binding_params.AccountDeleteAwsIamRoleBindingParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def delete_node_pool_binding(
        self,
        account_id: str,
        *,
        principal: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Node Pool Binding

        Args:
          principal: The principal that is allowed use the node pool. This must be the email address
              of the user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/nodePoolBindings:delete",
            body=maybe_transform(
                {"principal": principal}, account_delete_node_pool_binding_params.AccountDeleteNodePoolBindingParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def list_audit_logs(
        self,
        account_id: str,
        *,
        email: str | Omit = omit,
        end_time: Union[str, datetime] | Omit = omit,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        start_time: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountListAuditLogsResponse:
        """List User Audit Logs

        Args:
          email: Optional.

        Filter audit logs for user email associated with the account.

          end_time: End time of the audit logs to retrieve. If unspecified, the default is the
              current time.

          filter: Unused but required to use existing ListRequest functionality.

          order_by: Unused but required to use existing ListRequest functionality.

          page_size: The maximum number of audit logs to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 10.

          page_token: A page token, received from a previous ListAuditLogs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListAuditLogs must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          start_time: Start time of the audit logs to retrieve. If unspecified, the default is 30 days
              before now.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/auditLogs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "email": email,
                        "end_time": end_time,
                        "filter": filter,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "read_mask": read_mask,
                        "start_time": start_time,
                    },
                    account_list_audit_logs_params.AccountListAuditLogsParams,
                ),
            ),
            cast_to=AccountListAuditLogsResponse,
        )

    def preview_evaluator(
        self,
        account_id: str,
        *,
        evaluator: GatewayEvaluatorParam,
        sample_data: SequenceNotStr[str],
        max_samples: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountPreviewEvaluatorResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluators:previewEvaluator",
            body=maybe_transform(
                {
                    "evaluator": evaluator,
                    "sample_data": sample_data,
                    "max_samples": max_samples,
                },
                account_preview_evaluator_params.AccountPreviewEvaluatorParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountPreviewEvaluatorResponse,
        )

    def test_evaluation(
        self,
        account_id: str,
        *,
        evaluation: EvaluationParam,
        sample_data: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PreviewEvaluationResponse:
        """
        Similar to preview evaluation, but no need to create the evaluation entry first.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}:testeval",
            body=maybe_transform(
                {
                    "evaluation": evaluation,
                    "sample_data": sample_data,
                },
                account_test_evaluation_params.AccountTestEvaluationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PreviewEvaluationResponse,
        )

    def validate_evaluation_assertions(
        self,
        account_id: str,
        *,
        assertions: Iterable[AssertionParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountValidateEvaluationAssertionsResponse:
        """
        Validate evaluation assertions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluations:validateAssertions",
            body=maybe_transform(
                {"assertions": assertions},
                account_validate_evaluation_assertions_params.AccountValidateEvaluationAssertionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountValidateEvaluationAssertionsResponse,
        )


class AsyncAccountsResource(AsyncAPIResource):
    @cached_property
    def peft_merge_jobs(self) -> AsyncPeftMergeJobsResource:
        return AsyncPeftMergeJobsResource(self._client)

    @cached_property
    def aws_iam_role_bindings(self) -> AsyncAwsIamRoleBindingsResource:
        return AsyncAwsIamRoleBindingsResource(self._client)

    @cached_property
    def batch_inference_jobs(self) -> AsyncBatchInferenceJobsResource:
        return AsyncBatchInferenceJobsResource(self._client)

    @cached_property
    def batch_jobs(self) -> AsyncBatchJobsResource:
        return AsyncBatchJobsResource(self._client)

    @cached_property
    def billing(self) -> AsyncBillingResource:
        return AsyncBillingResource(self._client)

    @cached_property
    def clusters(self) -> AsyncClustersResource:
        return AsyncClustersResource(self._client)

    @cached_property
    def datasets(self) -> AsyncDatasetsResource:
        return AsyncDatasetsResource(self._client)

    @cached_property
    def deployed_models(self) -> AsyncDeployedModelsResource:
        return AsyncDeployedModelsResource(self._client)

    @cached_property
    def deployment_shapes(self) -> AsyncDeploymentShapesResource:
        return AsyncDeploymentShapesResource(self._client)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResource:
        return AsyncDeploymentsResource(self._client)

    @cached_property
    def environments(self) -> AsyncEnvironmentsResource:
        return AsyncEnvironmentsResource(self._client)

    @cached_property
    def evaluation_jobs(self) -> AsyncEvaluationJobsResource:
        return AsyncEvaluationJobsResource(self._client)

    @cached_property
    def evaluations(self) -> AsyncEvaluationsResource:
        return AsyncEvaluationsResource(self._client)

    @cached_property
    def evaluators(self) -> AsyncEvaluatorsResource:
        return AsyncEvaluatorsResource(self._client)

    @cached_property
    def identity_providers(self) -> AsyncIdentityProvidersResource:
        return AsyncIdentityProvidersResource(self._client)

    @cached_property
    def leaderboards(self) -> AsyncLeaderboardsResource:
        return AsyncLeaderboardsResource(self._client)

    @cached_property
    def mcp_servers(self) -> AsyncMcpServersResource:
        return AsyncMcpServersResource(self._client)

    @cached_property
    def models(self) -> AsyncModelsResource:
        return AsyncModelsResource(self._client)

    @cached_property
    def node_pool_bindings(self) -> AsyncNodePoolBindingsResource:
        return AsyncNodePoolBindingsResource(self._client)

    @cached_property
    def node_pools(self) -> AsyncNodePoolsResource:
        return AsyncNodePoolsResource(self._client)

    @cached_property
    def reinforcement_fine_tuning_jobs(self) -> AsyncReinforcementFineTuningJobsResource:
        return AsyncReinforcementFineTuningJobsResource(self._client)

    @cached_property
    def routers(self) -> AsyncRoutersResource:
        return AsyncRoutersResource(self._client)

    @cached_property
    def secrets(self) -> AsyncSecretsResource:
        return AsyncSecretsResource(self._client)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResource:
        return AsyncSnapshotsResource(self._client)

    @cached_property
    def supervised_fine_tuning_jobs(self) -> AsyncSupervisedFineTuningJobsResource:
        return AsyncSupervisedFineTuningJobsResource(self._client)

    @cached_property
    def users(self) -> AsyncUsersResource:
        return AsyncUsersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AsyncAccountsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        account_id: str,
        *,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """Get Account

        Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, account_retrieve_params.AccountRetrieveParams
                ),
            ),
            cast_to=Account,
        )

    async def list(
        self,
        *,
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
    ) -> AccountListResponse:
        """
        List Accounts

        Args:
          filter: Only accounts satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: Not supported. Accounts will be returned ordered by `name`.

          page_size: The maximum number of accounts to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListAccounts call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListAccounts must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/accounts",
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
                    account_list_params.AccountListParams,
                ),
            ),
            cast_to=AccountListResponse,
        )

    async def batch_delete_batch_jobs(
        self,
        account_id: str,
        *,
        names: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Batch Delete Batch Jobs

        Args:
          names: The resource names of the batch jobs to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/batchJobs:batchDelete",
            body=await async_maybe_transform(
                {"names": names}, account_batch_delete_batch_jobs_params.AccountBatchDeleteBatchJobsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def batch_delete_environments(
        self,
        account_id: str,
        *,
        names: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Batch Delete Environments

        Args:
          names: The resource names of the environments to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/environments:batchDelete",
            body=await async_maybe_transform(
                {"names": names}, account_batch_delete_environments_params.AccountBatchDeleteEnvironmentsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def batch_delete_node_pools(
        self,
        account_id: str,
        *,
        names: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Batch Delete Node Pools

        Args:
          names: The resource names of the node pools to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/nodePools:batchDelete",
            body=await async_maybe_transform(
                {"names": names}, account_batch_delete_node_pools_params.AccountBatchDeleteNodePoolsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def create_evaluator_v2(
        self,
        account_id: str,
        *,
        evaluator: GatewayEvaluatorParam,
        evaluator_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluator:
        """
        V2 api for evaluator creation, this is for new eval protocol evaluators, where
        it will trigger an async template build process during the creation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluatorsV2",
            body=await async_maybe_transform(
                {
                    "evaluator": evaluator,
                    "evaluator_id": evaluator_id,
                },
                account_create_evaluator_v2_params.AccountCreateEvaluatorV2Params,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayEvaluator,
        )

    async def delete_aws_iam_role_binding(
        self,
        account_id: str,
        *,
        principal: str | Omit = omit,
        role: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Aws Iam Role Binding

        Args:
          principal: The principal that is allowed to assume the AWS IAM role. This must be the email
              address of the user.

          role: The AWS IAM role ARN that is allowed to be assumed by the principal.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/awsIamRoleBindings:delete",
            body=await async_maybe_transform(
                {
                    "principal": principal,
                    "role": role,
                },
                account_delete_aws_iam_role_binding_params.AccountDeleteAwsIamRoleBindingParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def delete_node_pool_binding(
        self,
        account_id: str,
        *,
        principal: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Node Pool Binding

        Args:
          principal: The principal that is allowed use the node pool. This must be the email address
              of the user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/nodePoolBindings:delete",
            body=await async_maybe_transform(
                {"principal": principal}, account_delete_node_pool_binding_params.AccountDeleteNodePoolBindingParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def list_audit_logs(
        self,
        account_id: str,
        *,
        email: str | Omit = omit,
        end_time: Union[str, datetime] | Omit = omit,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        start_time: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountListAuditLogsResponse:
        """List User Audit Logs

        Args:
          email: Optional.

        Filter audit logs for user email associated with the account.

          end_time: End time of the audit logs to retrieve. If unspecified, the default is the
              current time.

          filter: Unused but required to use existing ListRequest functionality.

          order_by: Unused but required to use existing ListRequest functionality.

          page_size: The maximum number of audit logs to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 10.

          page_token: A page token, received from a previous ListAuditLogs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListAuditLogs must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          start_time: Start time of the audit logs to retrieve. If unspecified, the default is 30 days
              before now.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/auditLogs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "email": email,
                        "end_time": end_time,
                        "filter": filter,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "read_mask": read_mask,
                        "start_time": start_time,
                    },
                    account_list_audit_logs_params.AccountListAuditLogsParams,
                ),
            ),
            cast_to=AccountListAuditLogsResponse,
        )

    async def preview_evaluator(
        self,
        account_id: str,
        *,
        evaluator: GatewayEvaluatorParam,
        sample_data: SequenceNotStr[str],
        max_samples: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountPreviewEvaluatorResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluators:previewEvaluator",
            body=await async_maybe_transform(
                {
                    "evaluator": evaluator,
                    "sample_data": sample_data,
                    "max_samples": max_samples,
                },
                account_preview_evaluator_params.AccountPreviewEvaluatorParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountPreviewEvaluatorResponse,
        )

    async def test_evaluation(
        self,
        account_id: str,
        *,
        evaluation: EvaluationParam,
        sample_data: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PreviewEvaluationResponse:
        """
        Similar to preview evaluation, but no need to create the evaluation entry first.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}:testeval",
            body=await async_maybe_transform(
                {
                    "evaluation": evaluation,
                    "sample_data": sample_data,
                },
                account_test_evaluation_params.AccountTestEvaluationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PreviewEvaluationResponse,
        )

    async def validate_evaluation_assertions(
        self,
        account_id: str,
        *,
        assertions: Iterable[AssertionParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountValidateEvaluationAssertionsResponse:
        """
        Validate evaluation assertions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluations:validateAssertions",
            body=await async_maybe_transform(
                {"assertions": assertions},
                account_validate_evaluation_assertions_params.AccountValidateEvaluationAssertionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountValidateEvaluationAssertionsResponse,
        )


class AccountsResourceWithRawResponse:
    def __init__(self, accounts: AccountsResource) -> None:
        self._accounts = accounts

        self.retrieve = to_raw_response_wrapper(
            accounts.retrieve,
        )
        self.list = to_raw_response_wrapper(
            accounts.list,
        )
        self.batch_delete_batch_jobs = to_raw_response_wrapper(
            accounts.batch_delete_batch_jobs,
        )
        self.batch_delete_environments = to_raw_response_wrapper(
            accounts.batch_delete_environments,
        )
        self.batch_delete_node_pools = to_raw_response_wrapper(
            accounts.batch_delete_node_pools,
        )
        self.create_evaluator_v2 = to_raw_response_wrapper(
            accounts.create_evaluator_v2,
        )
        self.delete_aws_iam_role_binding = to_raw_response_wrapper(
            accounts.delete_aws_iam_role_binding,
        )
        self.delete_node_pool_binding = to_raw_response_wrapper(
            accounts.delete_node_pool_binding,
        )
        self.list_audit_logs = to_raw_response_wrapper(
            accounts.list_audit_logs,
        )
        self.preview_evaluator = to_raw_response_wrapper(
            accounts.preview_evaluator,
        )
        self.test_evaluation = to_raw_response_wrapper(
            accounts.test_evaluation,
        )
        self.validate_evaluation_assertions = to_raw_response_wrapper(
            accounts.validate_evaluation_assertions,
        )

    @cached_property
    def peft_merge_jobs(self) -> PeftMergeJobsResourceWithRawResponse:
        return PeftMergeJobsResourceWithRawResponse(self._accounts.peft_merge_jobs)

    @cached_property
    def aws_iam_role_bindings(self) -> AwsIamRoleBindingsResourceWithRawResponse:
        return AwsIamRoleBindingsResourceWithRawResponse(self._accounts.aws_iam_role_bindings)

    @cached_property
    def batch_inference_jobs(self) -> BatchInferenceJobsResourceWithRawResponse:
        return BatchInferenceJobsResourceWithRawResponse(self._accounts.batch_inference_jobs)

    @cached_property
    def batch_jobs(self) -> BatchJobsResourceWithRawResponse:
        return BatchJobsResourceWithRawResponse(self._accounts.batch_jobs)

    @cached_property
    def billing(self) -> BillingResourceWithRawResponse:
        return BillingResourceWithRawResponse(self._accounts.billing)

    @cached_property
    def clusters(self) -> ClustersResourceWithRawResponse:
        return ClustersResourceWithRawResponse(self._accounts.clusters)

    @cached_property
    def datasets(self) -> DatasetsResourceWithRawResponse:
        return DatasetsResourceWithRawResponse(self._accounts.datasets)

    @cached_property
    def deployed_models(self) -> DeployedModelsResourceWithRawResponse:
        return DeployedModelsResourceWithRawResponse(self._accounts.deployed_models)

    @cached_property
    def deployment_shapes(self) -> DeploymentShapesResourceWithRawResponse:
        return DeploymentShapesResourceWithRawResponse(self._accounts.deployment_shapes)

    @cached_property
    def deployments(self) -> DeploymentsResourceWithRawResponse:
        return DeploymentsResourceWithRawResponse(self._accounts.deployments)

    @cached_property
    def environments(self) -> EnvironmentsResourceWithRawResponse:
        return EnvironmentsResourceWithRawResponse(self._accounts.environments)

    @cached_property
    def evaluation_jobs(self) -> EvaluationJobsResourceWithRawResponse:
        return EvaluationJobsResourceWithRawResponse(self._accounts.evaluation_jobs)

    @cached_property
    def evaluations(self) -> EvaluationsResourceWithRawResponse:
        return EvaluationsResourceWithRawResponse(self._accounts.evaluations)

    @cached_property
    def evaluators(self) -> EvaluatorsResourceWithRawResponse:
        return EvaluatorsResourceWithRawResponse(self._accounts.evaluators)

    @cached_property
    def identity_providers(self) -> IdentityProvidersResourceWithRawResponse:
        return IdentityProvidersResourceWithRawResponse(self._accounts.identity_providers)

    @cached_property
    def leaderboards(self) -> LeaderboardsResourceWithRawResponse:
        return LeaderboardsResourceWithRawResponse(self._accounts.leaderboards)

    @cached_property
    def mcp_servers(self) -> McpServersResourceWithRawResponse:
        return McpServersResourceWithRawResponse(self._accounts.mcp_servers)

    @cached_property
    def models(self) -> ModelsResourceWithRawResponse:
        return ModelsResourceWithRawResponse(self._accounts.models)

    @cached_property
    def node_pool_bindings(self) -> NodePoolBindingsResourceWithRawResponse:
        return NodePoolBindingsResourceWithRawResponse(self._accounts.node_pool_bindings)

    @cached_property
    def node_pools(self) -> NodePoolsResourceWithRawResponse:
        return NodePoolsResourceWithRawResponse(self._accounts.node_pools)

    @cached_property
    def reinforcement_fine_tuning_jobs(self) -> ReinforcementFineTuningJobsResourceWithRawResponse:
        return ReinforcementFineTuningJobsResourceWithRawResponse(self._accounts.reinforcement_fine_tuning_jobs)

    @cached_property
    def routers(self) -> RoutersResourceWithRawResponse:
        return RoutersResourceWithRawResponse(self._accounts.routers)

    @cached_property
    def secrets(self) -> SecretsResourceWithRawResponse:
        return SecretsResourceWithRawResponse(self._accounts.secrets)

    @cached_property
    def snapshots(self) -> SnapshotsResourceWithRawResponse:
        return SnapshotsResourceWithRawResponse(self._accounts.snapshots)

    @cached_property
    def supervised_fine_tuning_jobs(self) -> SupervisedFineTuningJobsResourceWithRawResponse:
        return SupervisedFineTuningJobsResourceWithRawResponse(self._accounts.supervised_fine_tuning_jobs)

    @cached_property
    def users(self) -> UsersResourceWithRawResponse:
        return UsersResourceWithRawResponse(self._accounts.users)


class AsyncAccountsResourceWithRawResponse:
    def __init__(self, accounts: AsyncAccountsResource) -> None:
        self._accounts = accounts

        self.retrieve = async_to_raw_response_wrapper(
            accounts.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            accounts.list,
        )
        self.batch_delete_batch_jobs = async_to_raw_response_wrapper(
            accounts.batch_delete_batch_jobs,
        )
        self.batch_delete_environments = async_to_raw_response_wrapper(
            accounts.batch_delete_environments,
        )
        self.batch_delete_node_pools = async_to_raw_response_wrapper(
            accounts.batch_delete_node_pools,
        )
        self.create_evaluator_v2 = async_to_raw_response_wrapper(
            accounts.create_evaluator_v2,
        )
        self.delete_aws_iam_role_binding = async_to_raw_response_wrapper(
            accounts.delete_aws_iam_role_binding,
        )
        self.delete_node_pool_binding = async_to_raw_response_wrapper(
            accounts.delete_node_pool_binding,
        )
        self.list_audit_logs = async_to_raw_response_wrapper(
            accounts.list_audit_logs,
        )
        self.preview_evaluator = async_to_raw_response_wrapper(
            accounts.preview_evaluator,
        )
        self.test_evaluation = async_to_raw_response_wrapper(
            accounts.test_evaluation,
        )
        self.validate_evaluation_assertions = async_to_raw_response_wrapper(
            accounts.validate_evaluation_assertions,
        )

    @cached_property
    def peft_merge_jobs(self) -> AsyncPeftMergeJobsResourceWithRawResponse:
        return AsyncPeftMergeJobsResourceWithRawResponse(self._accounts.peft_merge_jobs)

    @cached_property
    def aws_iam_role_bindings(self) -> AsyncAwsIamRoleBindingsResourceWithRawResponse:
        return AsyncAwsIamRoleBindingsResourceWithRawResponse(self._accounts.aws_iam_role_bindings)

    @cached_property
    def batch_inference_jobs(self) -> AsyncBatchInferenceJobsResourceWithRawResponse:
        return AsyncBatchInferenceJobsResourceWithRawResponse(self._accounts.batch_inference_jobs)

    @cached_property
    def batch_jobs(self) -> AsyncBatchJobsResourceWithRawResponse:
        return AsyncBatchJobsResourceWithRawResponse(self._accounts.batch_jobs)

    @cached_property
    def billing(self) -> AsyncBillingResourceWithRawResponse:
        return AsyncBillingResourceWithRawResponse(self._accounts.billing)

    @cached_property
    def clusters(self) -> AsyncClustersResourceWithRawResponse:
        return AsyncClustersResourceWithRawResponse(self._accounts.clusters)

    @cached_property
    def datasets(self) -> AsyncDatasetsResourceWithRawResponse:
        return AsyncDatasetsResourceWithRawResponse(self._accounts.datasets)

    @cached_property
    def deployed_models(self) -> AsyncDeployedModelsResourceWithRawResponse:
        return AsyncDeployedModelsResourceWithRawResponse(self._accounts.deployed_models)

    @cached_property
    def deployment_shapes(self) -> AsyncDeploymentShapesResourceWithRawResponse:
        return AsyncDeploymentShapesResourceWithRawResponse(self._accounts.deployment_shapes)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResourceWithRawResponse:
        return AsyncDeploymentsResourceWithRawResponse(self._accounts.deployments)

    @cached_property
    def environments(self) -> AsyncEnvironmentsResourceWithRawResponse:
        return AsyncEnvironmentsResourceWithRawResponse(self._accounts.environments)

    @cached_property
    def evaluation_jobs(self) -> AsyncEvaluationJobsResourceWithRawResponse:
        return AsyncEvaluationJobsResourceWithRawResponse(self._accounts.evaluation_jobs)

    @cached_property
    def evaluations(self) -> AsyncEvaluationsResourceWithRawResponse:
        return AsyncEvaluationsResourceWithRawResponse(self._accounts.evaluations)

    @cached_property
    def evaluators(self) -> AsyncEvaluatorsResourceWithRawResponse:
        return AsyncEvaluatorsResourceWithRawResponse(self._accounts.evaluators)

    @cached_property
    def identity_providers(self) -> AsyncIdentityProvidersResourceWithRawResponse:
        return AsyncIdentityProvidersResourceWithRawResponse(self._accounts.identity_providers)

    @cached_property
    def leaderboards(self) -> AsyncLeaderboardsResourceWithRawResponse:
        return AsyncLeaderboardsResourceWithRawResponse(self._accounts.leaderboards)

    @cached_property
    def mcp_servers(self) -> AsyncMcpServersResourceWithRawResponse:
        return AsyncMcpServersResourceWithRawResponse(self._accounts.mcp_servers)

    @cached_property
    def models(self) -> AsyncModelsResourceWithRawResponse:
        return AsyncModelsResourceWithRawResponse(self._accounts.models)

    @cached_property
    def node_pool_bindings(self) -> AsyncNodePoolBindingsResourceWithRawResponse:
        return AsyncNodePoolBindingsResourceWithRawResponse(self._accounts.node_pool_bindings)

    @cached_property
    def node_pools(self) -> AsyncNodePoolsResourceWithRawResponse:
        return AsyncNodePoolsResourceWithRawResponse(self._accounts.node_pools)

    @cached_property
    def reinforcement_fine_tuning_jobs(self) -> AsyncReinforcementFineTuningJobsResourceWithRawResponse:
        return AsyncReinforcementFineTuningJobsResourceWithRawResponse(self._accounts.reinforcement_fine_tuning_jobs)

    @cached_property
    def routers(self) -> AsyncRoutersResourceWithRawResponse:
        return AsyncRoutersResourceWithRawResponse(self._accounts.routers)

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithRawResponse:
        return AsyncSecretsResourceWithRawResponse(self._accounts.secrets)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResourceWithRawResponse:
        return AsyncSnapshotsResourceWithRawResponse(self._accounts.snapshots)

    @cached_property
    def supervised_fine_tuning_jobs(self) -> AsyncSupervisedFineTuningJobsResourceWithRawResponse:
        return AsyncSupervisedFineTuningJobsResourceWithRawResponse(self._accounts.supervised_fine_tuning_jobs)

    @cached_property
    def users(self) -> AsyncUsersResourceWithRawResponse:
        return AsyncUsersResourceWithRawResponse(self._accounts.users)


class AccountsResourceWithStreamingResponse:
    def __init__(self, accounts: AccountsResource) -> None:
        self._accounts = accounts

        self.retrieve = to_streamed_response_wrapper(
            accounts.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            accounts.list,
        )
        self.batch_delete_batch_jobs = to_streamed_response_wrapper(
            accounts.batch_delete_batch_jobs,
        )
        self.batch_delete_environments = to_streamed_response_wrapper(
            accounts.batch_delete_environments,
        )
        self.batch_delete_node_pools = to_streamed_response_wrapper(
            accounts.batch_delete_node_pools,
        )
        self.create_evaluator_v2 = to_streamed_response_wrapper(
            accounts.create_evaluator_v2,
        )
        self.delete_aws_iam_role_binding = to_streamed_response_wrapper(
            accounts.delete_aws_iam_role_binding,
        )
        self.delete_node_pool_binding = to_streamed_response_wrapper(
            accounts.delete_node_pool_binding,
        )
        self.list_audit_logs = to_streamed_response_wrapper(
            accounts.list_audit_logs,
        )
        self.preview_evaluator = to_streamed_response_wrapper(
            accounts.preview_evaluator,
        )
        self.test_evaluation = to_streamed_response_wrapper(
            accounts.test_evaluation,
        )
        self.validate_evaluation_assertions = to_streamed_response_wrapper(
            accounts.validate_evaluation_assertions,
        )

    @cached_property
    def peft_merge_jobs(self) -> PeftMergeJobsResourceWithStreamingResponse:
        return PeftMergeJobsResourceWithStreamingResponse(self._accounts.peft_merge_jobs)

    @cached_property
    def aws_iam_role_bindings(self) -> AwsIamRoleBindingsResourceWithStreamingResponse:
        return AwsIamRoleBindingsResourceWithStreamingResponse(self._accounts.aws_iam_role_bindings)

    @cached_property
    def batch_inference_jobs(self) -> BatchInferenceJobsResourceWithStreamingResponse:
        return BatchInferenceJobsResourceWithStreamingResponse(self._accounts.batch_inference_jobs)

    @cached_property
    def batch_jobs(self) -> BatchJobsResourceWithStreamingResponse:
        return BatchJobsResourceWithStreamingResponse(self._accounts.batch_jobs)

    @cached_property
    def billing(self) -> BillingResourceWithStreamingResponse:
        return BillingResourceWithStreamingResponse(self._accounts.billing)

    @cached_property
    def clusters(self) -> ClustersResourceWithStreamingResponse:
        return ClustersResourceWithStreamingResponse(self._accounts.clusters)

    @cached_property
    def datasets(self) -> DatasetsResourceWithStreamingResponse:
        return DatasetsResourceWithStreamingResponse(self._accounts.datasets)

    @cached_property
    def deployed_models(self) -> DeployedModelsResourceWithStreamingResponse:
        return DeployedModelsResourceWithStreamingResponse(self._accounts.deployed_models)

    @cached_property
    def deployment_shapes(self) -> DeploymentShapesResourceWithStreamingResponse:
        return DeploymentShapesResourceWithStreamingResponse(self._accounts.deployment_shapes)

    @cached_property
    def deployments(self) -> DeploymentsResourceWithStreamingResponse:
        return DeploymentsResourceWithStreamingResponse(self._accounts.deployments)

    @cached_property
    def environments(self) -> EnvironmentsResourceWithStreamingResponse:
        return EnvironmentsResourceWithStreamingResponse(self._accounts.environments)

    @cached_property
    def evaluation_jobs(self) -> EvaluationJobsResourceWithStreamingResponse:
        return EvaluationJobsResourceWithStreamingResponse(self._accounts.evaluation_jobs)

    @cached_property
    def evaluations(self) -> EvaluationsResourceWithStreamingResponse:
        return EvaluationsResourceWithStreamingResponse(self._accounts.evaluations)

    @cached_property
    def evaluators(self) -> EvaluatorsResourceWithStreamingResponse:
        return EvaluatorsResourceWithStreamingResponse(self._accounts.evaluators)

    @cached_property
    def identity_providers(self) -> IdentityProvidersResourceWithStreamingResponse:
        return IdentityProvidersResourceWithStreamingResponse(self._accounts.identity_providers)

    @cached_property
    def leaderboards(self) -> LeaderboardsResourceWithStreamingResponse:
        return LeaderboardsResourceWithStreamingResponse(self._accounts.leaderboards)

    @cached_property
    def mcp_servers(self) -> McpServersResourceWithStreamingResponse:
        return McpServersResourceWithStreamingResponse(self._accounts.mcp_servers)

    @cached_property
    def models(self) -> ModelsResourceWithStreamingResponse:
        return ModelsResourceWithStreamingResponse(self._accounts.models)

    @cached_property
    def node_pool_bindings(self) -> NodePoolBindingsResourceWithStreamingResponse:
        return NodePoolBindingsResourceWithStreamingResponse(self._accounts.node_pool_bindings)

    @cached_property
    def node_pools(self) -> NodePoolsResourceWithStreamingResponse:
        return NodePoolsResourceWithStreamingResponse(self._accounts.node_pools)

    @cached_property
    def reinforcement_fine_tuning_jobs(self) -> ReinforcementFineTuningJobsResourceWithStreamingResponse:
        return ReinforcementFineTuningJobsResourceWithStreamingResponse(self._accounts.reinforcement_fine_tuning_jobs)

    @cached_property
    def routers(self) -> RoutersResourceWithStreamingResponse:
        return RoutersResourceWithStreamingResponse(self._accounts.routers)

    @cached_property
    def secrets(self) -> SecretsResourceWithStreamingResponse:
        return SecretsResourceWithStreamingResponse(self._accounts.secrets)

    @cached_property
    def snapshots(self) -> SnapshotsResourceWithStreamingResponse:
        return SnapshotsResourceWithStreamingResponse(self._accounts.snapshots)

    @cached_property
    def supervised_fine_tuning_jobs(self) -> SupervisedFineTuningJobsResourceWithStreamingResponse:
        return SupervisedFineTuningJobsResourceWithStreamingResponse(self._accounts.supervised_fine_tuning_jobs)

    @cached_property
    def users(self) -> UsersResourceWithStreamingResponse:
        return UsersResourceWithStreamingResponse(self._accounts.users)


class AsyncAccountsResourceWithStreamingResponse:
    def __init__(self, accounts: AsyncAccountsResource) -> None:
        self._accounts = accounts

        self.retrieve = async_to_streamed_response_wrapper(
            accounts.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            accounts.list,
        )
        self.batch_delete_batch_jobs = async_to_streamed_response_wrapper(
            accounts.batch_delete_batch_jobs,
        )
        self.batch_delete_environments = async_to_streamed_response_wrapper(
            accounts.batch_delete_environments,
        )
        self.batch_delete_node_pools = async_to_streamed_response_wrapper(
            accounts.batch_delete_node_pools,
        )
        self.create_evaluator_v2 = async_to_streamed_response_wrapper(
            accounts.create_evaluator_v2,
        )
        self.delete_aws_iam_role_binding = async_to_streamed_response_wrapper(
            accounts.delete_aws_iam_role_binding,
        )
        self.delete_node_pool_binding = async_to_streamed_response_wrapper(
            accounts.delete_node_pool_binding,
        )
        self.list_audit_logs = async_to_streamed_response_wrapper(
            accounts.list_audit_logs,
        )
        self.preview_evaluator = async_to_streamed_response_wrapper(
            accounts.preview_evaluator,
        )
        self.test_evaluation = async_to_streamed_response_wrapper(
            accounts.test_evaluation,
        )
        self.validate_evaluation_assertions = async_to_streamed_response_wrapper(
            accounts.validate_evaluation_assertions,
        )

    @cached_property
    def peft_merge_jobs(self) -> AsyncPeftMergeJobsResourceWithStreamingResponse:
        return AsyncPeftMergeJobsResourceWithStreamingResponse(self._accounts.peft_merge_jobs)

    @cached_property
    def aws_iam_role_bindings(self) -> AsyncAwsIamRoleBindingsResourceWithStreamingResponse:
        return AsyncAwsIamRoleBindingsResourceWithStreamingResponse(self._accounts.aws_iam_role_bindings)

    @cached_property
    def batch_inference_jobs(self) -> AsyncBatchInferenceJobsResourceWithStreamingResponse:
        return AsyncBatchInferenceJobsResourceWithStreamingResponse(self._accounts.batch_inference_jobs)

    @cached_property
    def batch_jobs(self) -> AsyncBatchJobsResourceWithStreamingResponse:
        return AsyncBatchJobsResourceWithStreamingResponse(self._accounts.batch_jobs)

    @cached_property
    def billing(self) -> AsyncBillingResourceWithStreamingResponse:
        return AsyncBillingResourceWithStreamingResponse(self._accounts.billing)

    @cached_property
    def clusters(self) -> AsyncClustersResourceWithStreamingResponse:
        return AsyncClustersResourceWithStreamingResponse(self._accounts.clusters)

    @cached_property
    def datasets(self) -> AsyncDatasetsResourceWithStreamingResponse:
        return AsyncDatasetsResourceWithStreamingResponse(self._accounts.datasets)

    @cached_property
    def deployed_models(self) -> AsyncDeployedModelsResourceWithStreamingResponse:
        return AsyncDeployedModelsResourceWithStreamingResponse(self._accounts.deployed_models)

    @cached_property
    def deployment_shapes(self) -> AsyncDeploymentShapesResourceWithStreamingResponse:
        return AsyncDeploymentShapesResourceWithStreamingResponse(self._accounts.deployment_shapes)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResourceWithStreamingResponse:
        return AsyncDeploymentsResourceWithStreamingResponse(self._accounts.deployments)

    @cached_property
    def environments(self) -> AsyncEnvironmentsResourceWithStreamingResponse:
        return AsyncEnvironmentsResourceWithStreamingResponse(self._accounts.environments)

    @cached_property
    def evaluation_jobs(self) -> AsyncEvaluationJobsResourceWithStreamingResponse:
        return AsyncEvaluationJobsResourceWithStreamingResponse(self._accounts.evaluation_jobs)

    @cached_property
    def evaluations(self) -> AsyncEvaluationsResourceWithStreamingResponse:
        return AsyncEvaluationsResourceWithStreamingResponse(self._accounts.evaluations)

    @cached_property
    def evaluators(self) -> AsyncEvaluatorsResourceWithStreamingResponse:
        return AsyncEvaluatorsResourceWithStreamingResponse(self._accounts.evaluators)

    @cached_property
    def identity_providers(self) -> AsyncIdentityProvidersResourceWithStreamingResponse:
        return AsyncIdentityProvidersResourceWithStreamingResponse(self._accounts.identity_providers)

    @cached_property
    def leaderboards(self) -> AsyncLeaderboardsResourceWithStreamingResponse:
        return AsyncLeaderboardsResourceWithStreamingResponse(self._accounts.leaderboards)

    @cached_property
    def mcp_servers(self) -> AsyncMcpServersResourceWithStreamingResponse:
        return AsyncMcpServersResourceWithStreamingResponse(self._accounts.mcp_servers)

    @cached_property
    def models(self) -> AsyncModelsResourceWithStreamingResponse:
        return AsyncModelsResourceWithStreamingResponse(self._accounts.models)

    @cached_property
    def node_pool_bindings(self) -> AsyncNodePoolBindingsResourceWithStreamingResponse:
        return AsyncNodePoolBindingsResourceWithStreamingResponse(self._accounts.node_pool_bindings)

    @cached_property
    def node_pools(self) -> AsyncNodePoolsResourceWithStreamingResponse:
        return AsyncNodePoolsResourceWithStreamingResponse(self._accounts.node_pools)

    @cached_property
    def reinforcement_fine_tuning_jobs(self) -> AsyncReinforcementFineTuningJobsResourceWithStreamingResponse:
        return AsyncReinforcementFineTuningJobsResourceWithStreamingResponse(
            self._accounts.reinforcement_fine_tuning_jobs
        )

    @cached_property
    def routers(self) -> AsyncRoutersResourceWithStreamingResponse:
        return AsyncRoutersResourceWithStreamingResponse(self._accounts.routers)

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithStreamingResponse:
        return AsyncSecretsResourceWithStreamingResponse(self._accounts.secrets)

    @cached_property
    def snapshots(self) -> AsyncSnapshotsResourceWithStreamingResponse:
        return AsyncSnapshotsResourceWithStreamingResponse(self._accounts.snapshots)

    @cached_property
    def supervised_fine_tuning_jobs(self) -> AsyncSupervisedFineTuningJobsResourceWithStreamingResponse:
        return AsyncSupervisedFineTuningJobsResourceWithStreamingResponse(self._accounts.supervised_fine_tuning_jobs)

    @cached_property
    def users(self) -> AsyncUsersResourceWithStreamingResponse:
        return AsyncUsersResourceWithStreamingResponse(self._accounts.users)
