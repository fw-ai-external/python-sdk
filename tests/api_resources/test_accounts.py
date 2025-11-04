# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types import (
    Account,
    AccountListResponse,
    AccountListAuditLogsResponse,
    AccountPreviewEvaluatorResponse,
    AccountValidateEvaluationAssertionsResponse,
)
from fireworks_ai._utils import parse_datetime
from fireworks_ai.types.accounts import GatewayEvaluator, PreviewEvaluationResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAccounts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        account = client.accounts.retrieve(
            account_id="account_id",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        account = client.accounts.retrieve(
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.retrieve(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.retrieve(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(Account, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.retrieve(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FireworksAI) -> None:
        account = client.accounts.list()
        assert_matches_type(AccountListResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FireworksAI) -> None:
        account = client.accounts.list(
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AccountListResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountListResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountListResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_delete_batch_jobs(self, client: FireworksAI) -> None:
        account = client.accounts.batch_delete_batch_jobs(
            account_id="account_id",
            names=["string"],
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_delete_batch_jobs(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.batch_delete_batch_jobs(
            account_id="account_id",
            names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_delete_batch_jobs(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.batch_delete_batch_jobs(
            account_id="account_id",
            names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_delete_batch_jobs(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.batch_delete_batch_jobs(
                account_id="",
                names=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_delete_environments(self, client: FireworksAI) -> None:
        account = client.accounts.batch_delete_environments(
            account_id="account_id",
            names=["string"],
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_delete_environments(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.batch_delete_environments(
            account_id="account_id",
            names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_delete_environments(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.batch_delete_environments(
            account_id="account_id",
            names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_delete_environments(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.batch_delete_environments(
                account_id="",
                names=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_delete_node_pools(self, client: FireworksAI) -> None:
        account = client.accounts.batch_delete_node_pools(
            account_id="account_id",
            names=["string"],
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_delete_node_pools(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.batch_delete_node_pools(
            account_id="account_id",
            names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_delete_node_pools(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.batch_delete_node_pools(
            account_id="account_id",
            names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_delete_node_pools(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.batch_delete_node_pools(
                account_id="",
                names=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_evaluator_v2(self, client: FireworksAI) -> None:
        account = client.accounts.create_evaluator_v2(
            account_id="account_id",
            evaluator={},
        )
        assert_matches_type(GatewayEvaluator, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_evaluator_v2_with_all_params(self, client: FireworksAI) -> None:
        account = client.accounts.create_evaluator_v2(
            account_id="account_id",
            evaluator={
                "commit_hash": "commitHash",
                "criteria": [
                    {
                        "code_snippets": {
                            "entry_file": "entryFile",
                            "entry_func": "entryFunc",
                            "file_contents": {"foo": "string"},
                            "language": "language",
                        },
                        "description": "description",
                        "name": "name",
                        "type": "TYPE_UNSPECIFIED",
                    }
                ],
                "description": "description",
                "display_name": "displayName",
                "entry_point": "entryPoint",
                "multi_metrics": True,
                "requirements": "requirements",
                "rollup_settings": {
                    "criteria_weights": {"foo": 0},
                    "python_code": "pythonCode",
                    "skip_rollup": True,
                    "success_threshold": 0,
                },
            },
            evaluator_id="evaluatorId",
        )
        assert_matches_type(GatewayEvaluator, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_evaluator_v2(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.create_evaluator_v2(
            account_id="account_id",
            evaluator={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(GatewayEvaluator, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_evaluator_v2(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.create_evaluator_v2(
            account_id="account_id",
            evaluator={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(GatewayEvaluator, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_evaluator_v2(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.create_evaluator_v2(
                account_id="",
                evaluator={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_aws_iam_role_binding(self, client: FireworksAI) -> None:
        account = client.accounts.delete_aws_iam_role_binding(
            account_id="account_id",
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_aws_iam_role_binding_with_all_params(self, client: FireworksAI) -> None:
        account = client.accounts.delete_aws_iam_role_binding(
            account_id="account_id",
            principal="principal",
            role="role",
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_aws_iam_role_binding(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.delete_aws_iam_role_binding(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_aws_iam_role_binding(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.delete_aws_iam_role_binding(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_aws_iam_role_binding(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.delete_aws_iam_role_binding(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_node_pool_binding(self, client: FireworksAI) -> None:
        account = client.accounts.delete_node_pool_binding(
            account_id="account_id",
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_node_pool_binding_with_all_params(self, client: FireworksAI) -> None:
        account = client.accounts.delete_node_pool_binding(
            account_id="account_id",
            principal="principal",
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_node_pool_binding(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.delete_node_pool_binding(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_node_pool_binding(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.delete_node_pool_binding(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_node_pool_binding(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.delete_node_pool_binding(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_audit_logs(self, client: FireworksAI) -> None:
        account = client.accounts.list_audit_logs(
            account_id="account_id",
        )
        assert_matches_type(AccountListAuditLogsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_audit_logs_with_all_params(self, client: FireworksAI) -> None:
        account = client.accounts.list_audit_logs(
            account_id="account_id",
            email="email",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(AccountListAuditLogsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_audit_logs(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.list_audit_logs(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountListAuditLogsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_audit_logs(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.list_audit_logs(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountListAuditLogsResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_audit_logs(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.list_audit_logs(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_preview_evaluator(self, client: FireworksAI) -> None:
        account = client.accounts.preview_evaluator(
            account_id="account_id",
            evaluator={},
            sample_data=["string"],
        )
        assert_matches_type(AccountPreviewEvaluatorResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_preview_evaluator_with_all_params(self, client: FireworksAI) -> None:
        account = client.accounts.preview_evaluator(
            account_id="account_id",
            evaluator={
                "commit_hash": "commitHash",
                "criteria": [
                    {
                        "code_snippets": {
                            "entry_file": "entryFile",
                            "entry_func": "entryFunc",
                            "file_contents": {"foo": "string"},
                            "language": "language",
                        },
                        "description": "description",
                        "name": "name",
                        "type": "TYPE_UNSPECIFIED",
                    }
                ],
                "description": "description",
                "display_name": "displayName",
                "entry_point": "entryPoint",
                "multi_metrics": True,
                "requirements": "requirements",
                "rollup_settings": {
                    "criteria_weights": {"foo": 0},
                    "python_code": "pythonCode",
                    "skip_rollup": True,
                    "success_threshold": 0,
                },
            },
            sample_data=["string"],
            max_samples=0,
        )
        assert_matches_type(AccountPreviewEvaluatorResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_preview_evaluator(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.preview_evaluator(
            account_id="account_id",
            evaluator={},
            sample_data=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountPreviewEvaluatorResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_preview_evaluator(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.preview_evaluator(
            account_id="account_id",
            evaluator={},
            sample_data=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountPreviewEvaluatorResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_preview_evaluator(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.preview_evaluator(
                account_id="",
                evaluator={},
                sample_data=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_test_evaluation(self, client: FireworksAI) -> None:
        account = client.accounts.test_evaluation(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
            sample_data="sampleData",
        )
        assert_matches_type(PreviewEvaluationResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_test_evaluation_with_all_params(self, client: FireworksAI) -> None:
        account = client.accounts.test_evaluation(
            account_id="account_id",
            evaluation={
                "assertions": [
                    {
                        "assertion_type": "ASSERTION_TYPE_UNSPECIFIED",
                        "code_assertion": {
                            "code": "code",
                            "language": "language",
                            "expected_output": "expectedOutput",
                            "options": {
                                "env_vars": {"foo": "string"},
                                "memory_limit_mb": 0,
                                "timeout_ms": 0,
                            },
                        },
                        "llm_assertion": {
                            "prompts": ["string"],
                            "providers": [
                                {
                                    "id": "id",
                                    "config": {"foo": "string"},
                                    "label": "label",
                                }
                            ],
                            "evaluate_options": {
                                "delay": 0,
                                "max_concurrency": 0,
                                "repeat": 0,
                            },
                            "llm_evaluator_prompt": "llmEvaluatorPrompt",
                        },
                        "metric_name": "metricName",
                    }
                ],
                "evaluation_type": "evaluationType",
                "providers": [
                    {
                        "id": "id",
                        "config": {"foo": "string"},
                        "label": "label",
                    }
                ],
                "description": "description",
            },
            sample_data="sampleData",
        )
        assert_matches_type(PreviewEvaluationResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_test_evaluation(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.test_evaluation(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
            sample_data="sampleData",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(PreviewEvaluationResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_test_evaluation(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.test_evaluation(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
            sample_data="sampleData",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(PreviewEvaluationResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_test_evaluation(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.test_evaluation(
                account_id="",
                evaluation={
                    "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                    "evaluation_type": "evaluationType",
                    "providers": [{}],
                },
                sample_data="sampleData",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_evaluation_assertions(self, client: FireworksAI) -> None:
        account = client.accounts.validate_evaluation_assertions(
            account_id="account_id",
            assertions=[{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
        )
        assert_matches_type(AccountValidateEvaluationAssertionsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_validate_evaluation_assertions(self, client: FireworksAI) -> None:
        response = client.accounts.with_raw_response.validate_evaluation_assertions(
            account_id="account_id",
            assertions=[{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountValidateEvaluationAssertionsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_validate_evaluation_assertions(self, client: FireworksAI) -> None:
        with client.accounts.with_streaming_response.validate_evaluation_assertions(
            account_id="account_id",
            assertions=[{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountValidateEvaluationAssertionsResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_validate_evaluation_assertions(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.validate_evaluation_assertions(
                account_id="",
                assertions=[{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
            )


class TestAsyncAccounts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.retrieve(
            account_id="account_id",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.retrieve(
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.retrieve(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.retrieve(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(Account, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.retrieve(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.list()
        assert_matches_type(AccountListResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.list(
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AccountListResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountListResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountListResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_delete_batch_jobs(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.batch_delete_batch_jobs(
            account_id="account_id",
            names=["string"],
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_delete_batch_jobs(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.batch_delete_batch_jobs(
            account_id="account_id",
            names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_delete_batch_jobs(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.batch_delete_batch_jobs(
            account_id="account_id",
            names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_delete_batch_jobs(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.batch_delete_batch_jobs(
                account_id="",
                names=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_delete_environments(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.batch_delete_environments(
            account_id="account_id",
            names=["string"],
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_delete_environments(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.batch_delete_environments(
            account_id="account_id",
            names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_delete_environments(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.batch_delete_environments(
            account_id="account_id",
            names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_delete_environments(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.batch_delete_environments(
                account_id="",
                names=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_delete_node_pools(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.batch_delete_node_pools(
            account_id="account_id",
            names=["string"],
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_delete_node_pools(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.batch_delete_node_pools(
            account_id="account_id",
            names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_delete_node_pools(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.batch_delete_node_pools(
            account_id="account_id",
            names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_delete_node_pools(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.batch_delete_node_pools(
                account_id="",
                names=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_evaluator_v2(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.create_evaluator_v2(
            account_id="account_id",
            evaluator={},
        )
        assert_matches_type(GatewayEvaluator, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_evaluator_v2_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.create_evaluator_v2(
            account_id="account_id",
            evaluator={
                "commit_hash": "commitHash",
                "criteria": [
                    {
                        "code_snippets": {
                            "entry_file": "entryFile",
                            "entry_func": "entryFunc",
                            "file_contents": {"foo": "string"},
                            "language": "language",
                        },
                        "description": "description",
                        "name": "name",
                        "type": "TYPE_UNSPECIFIED",
                    }
                ],
                "description": "description",
                "display_name": "displayName",
                "entry_point": "entryPoint",
                "multi_metrics": True,
                "requirements": "requirements",
                "rollup_settings": {
                    "criteria_weights": {"foo": 0},
                    "python_code": "pythonCode",
                    "skip_rollup": True,
                    "success_threshold": 0,
                },
            },
            evaluator_id="evaluatorId",
        )
        assert_matches_type(GatewayEvaluator, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_evaluator_v2(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.create_evaluator_v2(
            account_id="account_id",
            evaluator={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(GatewayEvaluator, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_evaluator_v2(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.create_evaluator_v2(
            account_id="account_id",
            evaluator={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(GatewayEvaluator, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_evaluator_v2(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.create_evaluator_v2(
                account_id="",
                evaluator={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_aws_iam_role_binding(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.delete_aws_iam_role_binding(
            account_id="account_id",
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_aws_iam_role_binding_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.delete_aws_iam_role_binding(
            account_id="account_id",
            principal="principal",
            role="role",
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_aws_iam_role_binding(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.delete_aws_iam_role_binding(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_aws_iam_role_binding(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.delete_aws_iam_role_binding(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_aws_iam_role_binding(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.delete_aws_iam_role_binding(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_node_pool_binding(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.delete_node_pool_binding(
            account_id="account_id",
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_node_pool_binding_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.delete_node_pool_binding(
            account_id="account_id",
            principal="principal",
        )
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_node_pool_binding(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.delete_node_pool_binding(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(object, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_node_pool_binding(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.delete_node_pool_binding(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(object, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_node_pool_binding(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.delete_node_pool_binding(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_audit_logs(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.list_audit_logs(
            account_id="account_id",
        )
        assert_matches_type(AccountListAuditLogsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_audit_logs_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.list_audit_logs(
            account_id="account_id",
            email="email",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(AccountListAuditLogsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_audit_logs(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.list_audit_logs(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountListAuditLogsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_audit_logs(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.list_audit_logs(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountListAuditLogsResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_audit_logs(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.list_audit_logs(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_preview_evaluator(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.preview_evaluator(
            account_id="account_id",
            evaluator={},
            sample_data=["string"],
        )
        assert_matches_type(AccountPreviewEvaluatorResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_preview_evaluator_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.preview_evaluator(
            account_id="account_id",
            evaluator={
                "commit_hash": "commitHash",
                "criteria": [
                    {
                        "code_snippets": {
                            "entry_file": "entryFile",
                            "entry_func": "entryFunc",
                            "file_contents": {"foo": "string"},
                            "language": "language",
                        },
                        "description": "description",
                        "name": "name",
                        "type": "TYPE_UNSPECIFIED",
                    }
                ],
                "description": "description",
                "display_name": "displayName",
                "entry_point": "entryPoint",
                "multi_metrics": True,
                "requirements": "requirements",
                "rollup_settings": {
                    "criteria_weights": {"foo": 0},
                    "python_code": "pythonCode",
                    "skip_rollup": True,
                    "success_threshold": 0,
                },
            },
            sample_data=["string"],
            max_samples=0,
        )
        assert_matches_type(AccountPreviewEvaluatorResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_preview_evaluator(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.preview_evaluator(
            account_id="account_id",
            evaluator={},
            sample_data=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountPreviewEvaluatorResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_preview_evaluator(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.preview_evaluator(
            account_id="account_id",
            evaluator={},
            sample_data=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountPreviewEvaluatorResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_preview_evaluator(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.preview_evaluator(
                account_id="",
                evaluator={},
                sample_data=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_test_evaluation(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.test_evaluation(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
            sample_data="sampleData",
        )
        assert_matches_type(PreviewEvaluationResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_test_evaluation_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.test_evaluation(
            account_id="account_id",
            evaluation={
                "assertions": [
                    {
                        "assertion_type": "ASSERTION_TYPE_UNSPECIFIED",
                        "code_assertion": {
                            "code": "code",
                            "language": "language",
                            "expected_output": "expectedOutput",
                            "options": {
                                "env_vars": {"foo": "string"},
                                "memory_limit_mb": 0,
                                "timeout_ms": 0,
                            },
                        },
                        "llm_assertion": {
                            "prompts": ["string"],
                            "providers": [
                                {
                                    "id": "id",
                                    "config": {"foo": "string"},
                                    "label": "label",
                                }
                            ],
                            "evaluate_options": {
                                "delay": 0,
                                "max_concurrency": 0,
                                "repeat": 0,
                            },
                            "llm_evaluator_prompt": "llmEvaluatorPrompt",
                        },
                        "metric_name": "metricName",
                    }
                ],
                "evaluation_type": "evaluationType",
                "providers": [
                    {
                        "id": "id",
                        "config": {"foo": "string"},
                        "label": "label",
                    }
                ],
                "description": "description",
            },
            sample_data="sampleData",
        )
        assert_matches_type(PreviewEvaluationResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_test_evaluation(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.test_evaluation(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
            sample_data="sampleData",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(PreviewEvaluationResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_test_evaluation(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.test_evaluation(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
            sample_data="sampleData",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(PreviewEvaluationResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_test_evaluation(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.test_evaluation(
                account_id="",
                evaluation={
                    "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                    "evaluation_type": "evaluationType",
                    "providers": [{}],
                },
                sample_data="sampleData",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_evaluation_assertions(self, async_client: AsyncFireworksAI) -> None:
        account = await async_client.accounts.validate_evaluation_assertions(
            account_id="account_id",
            assertions=[{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
        )
        assert_matches_type(AccountValidateEvaluationAssertionsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_validate_evaluation_assertions(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.with_raw_response.validate_evaluation_assertions(
            account_id="account_id",
            assertions=[{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountValidateEvaluationAssertionsResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_validate_evaluation_assertions(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.with_streaming_response.validate_evaluation_assertions(
            account_id="account_id",
            assertions=[{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountValidateEvaluationAssertionsResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_validate_evaluation_assertions(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.validate_evaluation_assertions(
                account_id="",
                assertions=[{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
            )
