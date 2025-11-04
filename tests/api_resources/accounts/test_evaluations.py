# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types.accounts import (
    Evaluation,
    EvaluationListResponse,
    PreviewEvaluationResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.create(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
        )
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.create(
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
            evaluation_id="evaluationId",
        )
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: FireworksAI) -> None:
        response = client.accounts.evaluations.with_raw_response.create(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: FireworksAI) -> None:
        with client.accounts.evaluations.with_streaming_response.create(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(Evaluation, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluations.with_raw_response.create(
                account_id="",
                evaluation={
                    "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                    "evaluation_type": "evaluationType",
                    "providers": [{}],
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.retrieve(
            evaluation_id="evaluation_id",
            account_id="account_id",
        )
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.retrieve(
            evaluation_id="evaluation_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.evaluations.with_raw_response.retrieve(
            evaluation_id="evaluation_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.evaluations.with_streaming_response.retrieve(
            evaluation_id="evaluation_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(Evaluation, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluations.with_raw_response.retrieve(
                evaluation_id="evaluation_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            client.accounts.evaluations.with_raw_response.retrieve(
                evaluation_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.list(
            account_id="account_id",
        )
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FireworksAI) -> None:
        response = client.accounts.evaluations.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FireworksAI) -> None:
        with client.accounts.evaluations.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluations.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.delete(
            evaluation_id="evaluation_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: FireworksAI) -> None:
        response = client.accounts.evaluations.with_raw_response.delete(
            evaluation_id="evaluation_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(object, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: FireworksAI) -> None:
        with client.accounts.evaluations.with_streaming_response.delete(
            evaluation_id="evaluation_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(object, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluations.with_raw_response.delete(
                evaluation_id="evaluation_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            client.accounts.evaluations.with_raw_response.delete(
                evaluation_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_preview(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.preview(
            evaluation_id="evaluation_id",
            account_id="account_id",
            sample_data="sampleData",
        )
        assert_matches_type(PreviewEvaluationResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_preview_with_all_params(self, client: FireworksAI) -> None:
        evaluation = client.accounts.evaluations.preview(
            evaluation_id="evaluation_id",
            account_id="account_id",
            sample_data="sampleData",
            max_samples=0,
        )
        assert_matches_type(PreviewEvaluationResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_preview(self, client: FireworksAI) -> None:
        response = client.accounts.evaluations.with_raw_response.preview(
            evaluation_id="evaluation_id",
            account_id="account_id",
            sample_data="sampleData",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(PreviewEvaluationResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_preview(self, client: FireworksAI) -> None:
        with client.accounts.evaluations.with_streaming_response.preview(
            evaluation_id="evaluation_id",
            account_id="account_id",
            sample_data="sampleData",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(PreviewEvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_preview(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluations.with_raw_response.preview(
                evaluation_id="evaluation_id",
                account_id="",
                sample_data="sampleData",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            client.accounts.evaluations.with_raw_response.preview(
                evaluation_id="",
                account_id="account_id",
                sample_data="sampleData",
            )


class TestAsyncEvaluations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.create(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
        )
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.create(
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
            evaluation_id="evaluationId",
        )
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.evaluations.with_raw_response.create(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.evaluations.with_streaming_response.create(
            account_id="account_id",
            evaluation={
                "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                "evaluation_type": "evaluationType",
                "providers": [{}],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(Evaluation, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluations.with_raw_response.create(
                account_id="",
                evaluation={
                    "assertions": [{"assertion_type": "ASSERTION_TYPE_UNSPECIFIED"}],
                    "evaluation_type": "evaluationType",
                    "providers": [{}],
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.retrieve(
            evaluation_id="evaluation_id",
            account_id="account_id",
        )
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.retrieve(
            evaluation_id="evaluation_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.evaluations.with_raw_response.retrieve(
            evaluation_id="evaluation_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(Evaluation, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.evaluations.with_streaming_response.retrieve(
            evaluation_id="evaluation_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(Evaluation, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluations.with_raw_response.retrieve(
                evaluation_id="evaluation_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            await async_client.accounts.evaluations.with_raw_response.retrieve(
                evaluation_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.list(
            account_id="account_id",
        )
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.evaluations.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.evaluations.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluations.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.delete(
            evaluation_id="evaluation_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.evaluations.with_raw_response.delete(
            evaluation_id="evaluation_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(object, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.evaluations.with_streaming_response.delete(
            evaluation_id="evaluation_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(object, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluations.with_raw_response.delete(
                evaluation_id="evaluation_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            await async_client.accounts.evaluations.with_raw_response.delete(
                evaluation_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_preview(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.preview(
            evaluation_id="evaluation_id",
            account_id="account_id",
            sample_data="sampleData",
        )
        assert_matches_type(PreviewEvaluationResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_preview_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        evaluation = await async_client.accounts.evaluations.preview(
            evaluation_id="evaluation_id",
            account_id="account_id",
            sample_data="sampleData",
            max_samples=0,
        )
        assert_matches_type(PreviewEvaluationResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_preview(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.evaluations.with_raw_response.preview(
            evaluation_id="evaluation_id",
            account_id="account_id",
            sample_data="sampleData",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(PreviewEvaluationResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_preview(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.evaluations.with_streaming_response.preview(
            evaluation_id="evaluation_id",
            account_id="account_id",
            sample_data="sampleData",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(PreviewEvaluationResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_preview(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluations.with_raw_response.preview(
                evaluation_id="evaluation_id",
                account_id="",
                sample_data="sampleData",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_id` but received ''"):
            await async_client.accounts.evaluations.with_raw_response.preview(
                evaluation_id="",
                account_id="account_id",
                sample_data="sampleData",
            )
