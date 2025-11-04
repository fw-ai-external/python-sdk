# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types.accounts import (
    GatewayBatchInferenceJob,
    BatchInferenceJobListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBatchInferenceJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: FireworksAI) -> None:
        batch_inference_job = client.accounts.batch_inference_jobs.create(
            account_id="account_id",
        )
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: FireworksAI) -> None:
        batch_inference_job = client.accounts.batch_inference_jobs.create(
            account_id="account_id",
            batch_inference_job_id="batchInferenceJobId",
            continued_from_job_name="continuedFromJobName",
            display_name="displayName",
            inference_parameters={
                "extra_body": "extraBody",
                "max_tokens": 0,
                "n": 0,
                "temperature": 0,
                "top_k": 0,
                "top_p": 0,
            },
            input_dataset_id="inputDatasetId",
            model="model",
            output_dataset_id="outputDatasetId",
            precision="PRECISION_UNSPECIFIED",
        )
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: FireworksAI) -> None:
        response = client.accounts.batch_inference_jobs.with_raw_response.create(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_inference_job = response.parse()
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: FireworksAI) -> None:
        with client.accounts.batch_inference_jobs.with_streaming_response.create(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_inference_job = response.parse()
            assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_inference_jobs.with_raw_response.create(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        batch_inference_job = client.accounts.batch_inference_jobs.retrieve(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        batch_inference_job = client.accounts.batch_inference_jobs.retrieve(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.batch_inference_jobs.with_raw_response.retrieve(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_inference_job = response.parse()
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.batch_inference_jobs.with_streaming_response.retrieve(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_inference_job = response.parse()
            assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_inference_jobs.with_raw_response.retrieve(
                batch_inference_job_id="batch_inference_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `batch_inference_job_id` but received ''"
        ):
            client.accounts.batch_inference_jobs.with_raw_response.retrieve(
                batch_inference_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FireworksAI) -> None:
        batch_inference_job = client.accounts.batch_inference_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(BatchInferenceJobListResponse, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FireworksAI) -> None:
        batch_inference_job = client.accounts.batch_inference_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(BatchInferenceJobListResponse, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FireworksAI) -> None:
        response = client.accounts.batch_inference_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_inference_job = response.parse()
        assert_matches_type(BatchInferenceJobListResponse, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FireworksAI) -> None:
        with client.accounts.batch_inference_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_inference_job = response.parse()
            assert_matches_type(BatchInferenceJobListResponse, batch_inference_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_inference_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: FireworksAI) -> None:
        batch_inference_job = client.accounts.batch_inference_jobs.delete(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: FireworksAI) -> None:
        response = client.accounts.batch_inference_jobs.with_raw_response.delete(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_inference_job = response.parse()
        assert_matches_type(object, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: FireworksAI) -> None:
        with client.accounts.batch_inference_jobs.with_streaming_response.delete(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_inference_job = response.parse()
            assert_matches_type(object, batch_inference_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_inference_jobs.with_raw_response.delete(
                batch_inference_job_id="batch_inference_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `batch_inference_job_id` but received ''"
        ):
            client.accounts.batch_inference_jobs.with_raw_response.delete(
                batch_inference_job_id="",
                account_id="account_id",
            )


class TestAsyncBatchInferenceJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworksAI) -> None:
        batch_inference_job = await async_client.accounts.batch_inference_jobs.create(
            account_id="account_id",
        )
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        batch_inference_job = await async_client.accounts.batch_inference_jobs.create(
            account_id="account_id",
            batch_inference_job_id="batchInferenceJobId",
            continued_from_job_name="continuedFromJobName",
            display_name="displayName",
            inference_parameters={
                "extra_body": "extraBody",
                "max_tokens": 0,
                "n": 0,
                "temperature": 0,
                "top_k": 0,
                "top_p": 0,
            },
            input_dataset_id="inputDatasetId",
            model="model",
            output_dataset_id="outputDatasetId",
            precision="PRECISION_UNSPECIFIED",
        )
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.batch_inference_jobs.with_raw_response.create(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_inference_job = await response.parse()
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.batch_inference_jobs.with_streaming_response.create(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_inference_job = await response.parse()
            assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_inference_jobs.with_raw_response.create(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        batch_inference_job = await async_client.accounts.batch_inference_jobs.retrieve(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        batch_inference_job = await async_client.accounts.batch_inference_jobs.retrieve(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.batch_inference_jobs.with_raw_response.retrieve(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_inference_job = await response.parse()
        assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.batch_inference_jobs.with_streaming_response.retrieve(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_inference_job = await response.parse()
            assert_matches_type(GatewayBatchInferenceJob, batch_inference_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_inference_jobs.with_raw_response.retrieve(
                batch_inference_job_id="batch_inference_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `batch_inference_job_id` but received ''"
        ):
            await async_client.accounts.batch_inference_jobs.with_raw_response.retrieve(
                batch_inference_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworksAI) -> None:
        batch_inference_job = await async_client.accounts.batch_inference_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(BatchInferenceJobListResponse, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        batch_inference_job = await async_client.accounts.batch_inference_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(BatchInferenceJobListResponse, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.batch_inference_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_inference_job = await response.parse()
        assert_matches_type(BatchInferenceJobListResponse, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.batch_inference_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_inference_job = await response.parse()
            assert_matches_type(BatchInferenceJobListResponse, batch_inference_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_inference_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworksAI) -> None:
        batch_inference_job = await async_client.accounts.batch_inference_jobs.delete(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.batch_inference_jobs.with_raw_response.delete(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_inference_job = await response.parse()
        assert_matches_type(object, batch_inference_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.batch_inference_jobs.with_streaming_response.delete(
            batch_inference_job_id="batch_inference_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_inference_job = await response.parse()
            assert_matches_type(object, batch_inference_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_inference_jobs.with_raw_response.delete(
                batch_inference_job_id="batch_inference_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `batch_inference_job_id` but received ''"
        ):
            await async_client.accounts.batch_inference_jobs.with_raw_response.delete(
                batch_inference_job_id="",
                account_id="account_id",
            )
