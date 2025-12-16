# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import (
    DpoJob,
    DpoJobGetMetricsFileEndpointResponse,
)
from fireworks.pagination import SyncCursorDpoJobs, AsyncCursorDpoJobs

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDpoJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.create(
            account_id="account_id",
            dataset="dataset",
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.create(
            account_id="account_id",
            dataset="dataset",
            dpo_job_id="dpoJobId",
            display_name="displayName",
            training_config={
                "base_model": "baseModel",
                "batch_size": 0,
                "epochs": 0,
                "gradient_accumulation_steps": 0,
                "jinja_template": "jinjaTemplate",
                "learning_rate": 0,
                "learning_rate_warmup_steps": 0,
                "lora_rank": 0,
                "max_context_length": 0,
                "output_model": "outputModel",
                "region": "REGION_UNSPECIFIED",
                "warm_start_from": "warmStartFrom",
            },
            wandb_config={
                "api_key": "apiKey",
                "enabled": True,
                "entity": "entity",
                "project": "project",
                "run_id": "runId",
            },
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.dpo_jobs.with_raw_response.create(
            account_id="account_id",
            dataset="dataset",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = response.parse()
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.dpo_jobs.with_streaming_response.create(
            account_id="account_id",
            dataset="dataset",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = response.parse()
            assert_matches_type(DpoJob, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.dpo_jobs.with_raw_response.create(
                account_id="",
                dataset="dataset",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(SyncCursorDpoJobs[DpoJob], dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SyncCursorDpoJobs[DpoJob], dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.dpo_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = response.parse()
        assert_matches_type(SyncCursorDpoJobs[DpoJob], dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.dpo_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = response.parse()
            assert_matches_type(SyncCursorDpoJobs[DpoJob], dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.dpo_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.delete(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.dpo_jobs.with_raw_response.delete(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = response.parse()
        assert_matches_type(object, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.dpo_jobs.with_streaming_response.delete(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = response.parse()
            assert_matches_type(object, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.dpo_jobs.with_raw_response.delete(
                dpo_job_id="dpo_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dpo_job_id` but received ''"):
            client.dpo_jobs.with_raw_response.delete(
                dpo_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.get(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.get(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.dpo_jobs.with_raw_response.get(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = response.parse()
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.dpo_jobs.with_streaming_response.get(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = response.parse()
            assert_matches_type(DpoJob, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.dpo_jobs.with_raw_response.get(
                dpo_job_id="dpo_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dpo_job_id` but received ''"):
            client.dpo_jobs.with_raw_response.get(
                dpo_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_metrics_file_endpoint(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.get_metrics_file_endpoint(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )
        assert_matches_type(DpoJobGetMetricsFileEndpointResponse, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_metrics_file_endpoint(self, client: Fireworks) -> None:
        response = client.dpo_jobs.with_raw_response.get_metrics_file_endpoint(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = response.parse()
        assert_matches_type(DpoJobGetMetricsFileEndpointResponse, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_metrics_file_endpoint(self, client: Fireworks) -> None:
        with client.dpo_jobs.with_streaming_response.get_metrics_file_endpoint(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = response.parse()
            assert_matches_type(DpoJobGetMetricsFileEndpointResponse, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_metrics_file_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.dpo_jobs.with_raw_response.get_metrics_file_endpoint(
                dpo_job_id="dpo_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dpo_job_id` but received ''"):
            client.dpo_jobs.with_raw_response.get_metrics_file_endpoint(
                dpo_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resume(self, client: Fireworks) -> None:
        dpo_job = client.dpo_jobs.resume(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_resume(self, client: Fireworks) -> None:
        response = client.dpo_jobs.with_raw_response.resume(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = response.parse()
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_resume(self, client: Fireworks) -> None:
        with client.dpo_jobs.with_streaming_response.resume(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = response.parse()
            assert_matches_type(DpoJob, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_resume(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.dpo_jobs.with_raw_response.resume(
                dpo_job_id="dpo_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dpo_job_id` but received ''"):
            client.dpo_jobs.with_raw_response.resume(
                dpo_job_id="",
                account_id="account_id",
                body={},
            )


class TestAsyncDpoJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.create(
            account_id="account_id",
            dataset="dataset",
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.create(
            account_id="account_id",
            dataset="dataset",
            dpo_job_id="dpoJobId",
            display_name="displayName",
            training_config={
                "base_model": "baseModel",
                "batch_size": 0,
                "epochs": 0,
                "gradient_accumulation_steps": 0,
                "jinja_template": "jinjaTemplate",
                "learning_rate": 0,
                "learning_rate_warmup_steps": 0,
                "lora_rank": 0,
                "max_context_length": 0,
                "output_model": "outputModel",
                "region": "REGION_UNSPECIFIED",
                "warm_start_from": "warmStartFrom",
            },
            wandb_config={
                "api_key": "apiKey",
                "enabled": True,
                "entity": "entity",
                "project": "project",
                "run_id": "runId",
            },
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.dpo_jobs.with_raw_response.create(
            account_id="account_id",
            dataset="dataset",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = await response.parse()
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.dpo_jobs.with_streaming_response.create(
            account_id="account_id",
            dataset="dataset",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = await response.parse()
            assert_matches_type(DpoJob, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.create(
                account_id="",
                dataset="dataset",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(AsyncCursorDpoJobs[DpoJob], dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AsyncCursorDpoJobs[DpoJob], dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.dpo_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = await response.parse()
        assert_matches_type(AsyncCursorDpoJobs[DpoJob], dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.dpo_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = await response.parse()
            assert_matches_type(AsyncCursorDpoJobs[DpoJob], dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.delete(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.dpo_jobs.with_raw_response.delete(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = await response.parse()
        assert_matches_type(object, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.dpo_jobs.with_streaming_response.delete(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = await response.parse()
            assert_matches_type(object, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.delete(
                dpo_job_id="dpo_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dpo_job_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.delete(
                dpo_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.get(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.get(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.dpo_jobs.with_raw_response.get(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = await response.parse()
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.dpo_jobs.with_streaming_response.get(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = await response.parse()
            assert_matches_type(DpoJob, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.get(
                dpo_job_id="dpo_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dpo_job_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.get(
                dpo_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_metrics_file_endpoint(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.get_metrics_file_endpoint(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )
        assert_matches_type(DpoJobGetMetricsFileEndpointResponse, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_metrics_file_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.dpo_jobs.with_raw_response.get_metrics_file_endpoint(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = await response.parse()
        assert_matches_type(DpoJobGetMetricsFileEndpointResponse, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_metrics_file_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.dpo_jobs.with_streaming_response.get_metrics_file_endpoint(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = await response.parse()
            assert_matches_type(DpoJobGetMetricsFileEndpointResponse, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_metrics_file_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.get_metrics_file_endpoint(
                dpo_job_id="dpo_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dpo_job_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.get_metrics_file_endpoint(
                dpo_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resume(self, async_client: AsyncFireworks) -> None:
        dpo_job = await async_client.dpo_jobs.resume(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_resume(self, async_client: AsyncFireworks) -> None:
        response = await async_client.dpo_jobs.with_raw_response.resume(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dpo_job = await response.parse()
        assert_matches_type(DpoJob, dpo_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_resume(self, async_client: AsyncFireworks) -> None:
        async with async_client.dpo_jobs.with_streaming_response.resume(
            dpo_job_id="dpo_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dpo_job = await response.parse()
            assert_matches_type(DpoJob, dpo_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_resume(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.resume(
                dpo_job_id="dpo_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dpo_job_id` but received ''"):
            await async_client.dpo_jobs.with_raw_response.resume(
                dpo_job_id="",
                account_id="account_id",
                body={},
            )
