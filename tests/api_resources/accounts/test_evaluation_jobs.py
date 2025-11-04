# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai.types.accounts import (
    GatewayEvaluationJob,
    EvaluationJobListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluationJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        evaluation_job = client.accounts.evaluation_jobs.create(
            account_id="account_id",
            evaluation_job={
                "evaluator": "evaluator",
                "input_dataset": "inputDataset",
                "output_dataset": "outputDataset",
            },
        )
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        evaluation_job = client.accounts.evaluation_jobs.create(
            account_id="account_id",
            evaluation_job={
                "evaluator": "evaluator",
                "input_dataset": "inputDataset",
                "output_dataset": "outputDataset",
                "display_name": "displayName",
                "output_stats": "outputStats",
            },
            evaluation_job_id="evaluationJobId",
            leaderboard_ids=["string"],
        )
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.accounts.evaluation_jobs.with_raw_response.create(
            account_id="account_id",
            evaluation_job={
                "evaluator": "evaluator",
                "input_dataset": "inputDataset",
                "output_dataset": "outputDataset",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_job = response.parse()
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.accounts.evaluation_jobs.with_streaming_response.create(
            account_id="account_id",
            evaluation_job={
                "evaluator": "evaluator",
                "input_dataset": "inputDataset",
                "output_dataset": "outputDataset",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_job = response.parse()
            assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluation_jobs.with_raw_response.create(
                account_id="",
                evaluation_job={
                    "evaluator": "evaluator",
                    "input_dataset": "inputDataset",
                    "output_dataset": "outputDataset",
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Fireworks) -> None:
        evaluation_job = client.accounts.evaluation_jobs.retrieve(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Fireworks) -> None:
        evaluation_job = client.accounts.evaluation_jobs.retrieve(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Fireworks) -> None:
        response = client.accounts.evaluation_jobs.with_raw_response.retrieve(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_job = response.parse()
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Fireworks) -> None:
        with client.accounts.evaluation_jobs.with_streaming_response.retrieve(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_job = response.parse()
            assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluation_jobs.with_raw_response.retrieve(
                evaluation_job_id="evaluation_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_job_id` but received ''"):
            client.accounts.evaluation_jobs.with_raw_response.retrieve(
                evaluation_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        evaluation_job = client.accounts.evaluation_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(EvaluationJobListResponse, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        evaluation_job = client.accounts.evaluation_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(EvaluationJobListResponse, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.accounts.evaluation_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_job = response.parse()
        assert_matches_type(EvaluationJobListResponse, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.accounts.evaluation_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_job = response.parse()
            assert_matches_type(EvaluationJobListResponse, evaluation_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluation_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        evaluation_job = client.accounts.evaluation_jobs.delete(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.accounts.evaluation_jobs.with_raw_response.delete(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_job = response.parse()
        assert_matches_type(object, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.accounts.evaluation_jobs.with_streaming_response.delete(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_job = response.parse()
            assert_matches_type(object, evaluation_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluation_jobs.with_raw_response.delete(
                evaluation_job_id="evaluation_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_job_id` but received ''"):
            client.accounts.evaluation_jobs.with_raw_response.delete(
                evaluation_job_id="",
                account_id="account_id",
            )


class TestAsyncEvaluationJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        evaluation_job = await async_client.accounts.evaluation_jobs.create(
            account_id="account_id",
            evaluation_job={
                "evaluator": "evaluator",
                "input_dataset": "inputDataset",
                "output_dataset": "outputDataset",
            },
        )
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluation_job = await async_client.accounts.evaluation_jobs.create(
            account_id="account_id",
            evaluation_job={
                "evaluator": "evaluator",
                "input_dataset": "inputDataset",
                "output_dataset": "outputDataset",
                "display_name": "displayName",
                "output_stats": "outputStats",
            },
            evaluation_job_id="evaluationJobId",
            leaderboard_ids=["string"],
        )
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluation_jobs.with_raw_response.create(
            account_id="account_id",
            evaluation_job={
                "evaluator": "evaluator",
                "input_dataset": "inputDataset",
                "output_dataset": "outputDataset",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_job = await response.parse()
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluation_jobs.with_streaming_response.create(
            account_id="account_id",
            evaluation_job={
                "evaluator": "evaluator",
                "input_dataset": "inputDataset",
                "output_dataset": "outputDataset",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_job = await response.parse()
            assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluation_jobs.with_raw_response.create(
                account_id="",
                evaluation_job={
                    "evaluator": "evaluator",
                    "input_dataset": "inputDataset",
                    "output_dataset": "outputDataset",
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworks) -> None:
        evaluation_job = await async_client.accounts.evaluation_jobs.retrieve(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluation_job = await async_client.accounts.evaluation_jobs.retrieve(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluation_jobs.with_raw_response.retrieve(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_job = await response.parse()
        assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluation_jobs.with_streaming_response.retrieve(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_job = await response.parse()
            assert_matches_type(GatewayEvaluationJob, evaluation_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluation_jobs.with_raw_response.retrieve(
                evaluation_job_id="evaluation_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_job_id` but received ''"):
            await async_client.accounts.evaluation_jobs.with_raw_response.retrieve(
                evaluation_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        evaluation_job = await async_client.accounts.evaluation_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(EvaluationJobListResponse, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluation_job = await async_client.accounts.evaluation_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(EvaluationJobListResponse, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluation_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_job = await response.parse()
        assert_matches_type(EvaluationJobListResponse, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluation_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_job = await response.parse()
            assert_matches_type(EvaluationJobListResponse, evaluation_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluation_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        evaluation_job = await async_client.accounts.evaluation_jobs.delete(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluation_jobs.with_raw_response.delete(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_job = await response.parse()
        assert_matches_type(object, evaluation_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluation_jobs.with_streaming_response.delete(
            evaluation_job_id="evaluation_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_job = await response.parse()
            assert_matches_type(object, evaluation_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluation_jobs.with_raw_response.delete(
                evaluation_job_id="evaluation_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluation_job_id` but received ''"):
            await async_client.accounts.evaluation_jobs.with_raw_response.delete(
                evaluation_job_id="",
                account_id="account_id",
            )
