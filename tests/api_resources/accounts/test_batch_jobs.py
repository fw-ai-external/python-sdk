# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai._utils import parse_datetime
from fireworks_ai.types.accounts import (
    GatewayBatchJob,
    BatchJobListResponse,
    BatchJobGetLogsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBatchJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.create(
            account_id="account_id",
            node_pool_id="nodePoolId",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.create(
            account_id="account_id",
            node_pool_id="nodePoolId",
            annotations={"foo": "string"},
            display_name="displayName",
            environment_id="environmentId",
            env_vars={"foo": "string"},
            image_ref="imageRef",
            notebook_executor={"notebook_filename": "notebookFilename"},
            num_ranks=0,
            python_executor={
                "target": "target",
                "target_type": "TARGET_TYPE_UNSPECIFIED",
                "args": ["string"],
            },
            role="role",
            shared=True,
            shell_executor={"command": "command"},
            snapshot_id="snapshotId",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.accounts.batch_jobs.with_raw_response.create(
            account_id="account_id",
            node_pool_id="nodePoolId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = response.parse()
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.accounts.batch_jobs.with_streaming_response.create(
            account_id="account_id",
            node_pool_id="nodePoolId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = response.parse()
            assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.create(
                account_id="",
                node_pool_id="nodePoolId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.retrieve(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.retrieve(
            batch_job_id="batch_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Fireworks) -> None:
        response = client.accounts.batch_jobs.with_raw_response.retrieve(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = response.parse()
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Fireworks) -> None:
        with client.accounts.batch_jobs.with_streaming_response.retrieve(
            batch_job_id="batch_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = response.parse()
            assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.retrieve(
                batch_job_id="batch_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.retrieve(
                batch_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.update(
            batch_job_id="batch_job_id",
            account_id="account_id",
            node_pool_id="nodePoolId",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.update(
            batch_job_id="batch_job_id",
            account_id="account_id",
            node_pool_id="nodePoolId",
            annotations={"foo": "string"},
            display_name="displayName",
            environment_id="environmentId",
            env_vars={"foo": "string"},
            image_ref="imageRef",
            notebook_executor={"notebook_filename": "notebookFilename"},
            num_ranks=0,
            python_executor={
                "target": "target",
                "target_type": "TARGET_TYPE_UNSPECIFIED",
                "args": ["string"],
            },
            role="role",
            shared=True,
            shell_executor={"command": "command"},
            snapshot_id="snapshotId",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.accounts.batch_jobs.with_raw_response.update(
            batch_job_id="batch_job_id",
            account_id="account_id",
            node_pool_id="nodePoolId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = response.parse()
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.accounts.batch_jobs.with_streaming_response.update(
            batch_job_id="batch_job_id",
            account_id="account_id",
            node_pool_id="nodePoolId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = response.parse()
            assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.update(
                batch_job_id="batch_job_id",
                account_id="",
                node_pool_id="nodePoolId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.update(
                batch_job_id="",
                account_id="account_id",
                node_pool_id="nodePoolId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(BatchJobListResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(BatchJobListResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.accounts.batch_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = response.parse()
        assert_matches_type(BatchJobListResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.accounts.batch_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = response.parse()
            assert_matches_type(BatchJobListResponse, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.delete(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.accounts.batch_jobs.with_raw_response.delete(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = response.parse()
        assert_matches_type(object, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.accounts.batch_jobs.with_streaming_response.delete(
            batch_job_id="batch_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = response.parse()
            assert_matches_type(object, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.delete(
                batch_job_id="batch_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.delete(
                batch_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.cancel(
            batch_job_id="batch_job_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(object, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: Fireworks) -> None:
        response = client.accounts.batch_jobs.with_raw_response.cancel(
            batch_job_id="batch_job_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = response.parse()
        assert_matches_type(object, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: Fireworks) -> None:
        with client.accounts.batch_jobs.with_streaming_response.cancel(
            batch_job_id="batch_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = response.parse()
            assert_matches_type(object, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_cancel(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.cancel(
                batch_job_id="batch_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.cancel(
                batch_job_id="",
                account_id="account_id",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_logs(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.get_logs(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )
        assert_matches_type(BatchJobGetLogsResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_logs_with_all_params(self, client: Fireworks) -> None:
        batch_job = client.accounts.batch_jobs.get_logs(
            batch_job_id="batch_job_id",
            account_id="account_id",
            filter="filter",
            page_size=0,
            page_token="pageToken",
            ranks=[0],
            read_mask="readMask",
            start_from_head=True,
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(BatchJobGetLogsResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_logs(self, client: Fireworks) -> None:
        response = client.accounts.batch_jobs.with_raw_response.get_logs(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = response.parse()
        assert_matches_type(BatchJobGetLogsResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_logs(self, client: Fireworks) -> None:
        with client.accounts.batch_jobs.with_streaming_response.get_logs(
            batch_job_id="batch_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = response.parse()
            assert_matches_type(BatchJobGetLogsResponse, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_logs(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.get_logs(
                batch_job_id="batch_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            client.accounts.batch_jobs.with_raw_response.get_logs(
                batch_job_id="",
                account_id="account_id",
            )


class TestAsyncBatchJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.create(
            account_id="account_id",
            node_pool_id="nodePoolId",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.create(
            account_id="account_id",
            node_pool_id="nodePoolId",
            annotations={"foo": "string"},
            display_name="displayName",
            environment_id="environmentId",
            env_vars={"foo": "string"},
            image_ref="imageRef",
            notebook_executor={"notebook_filename": "notebookFilename"},
            num_ranks=0,
            python_executor={
                "target": "target",
                "target_type": "TARGET_TYPE_UNSPECIFIED",
                "args": ["string"],
            },
            role="role",
            shared=True,
            shell_executor={"command": "command"},
            snapshot_id="snapshotId",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.batch_jobs.with_raw_response.create(
            account_id="account_id",
            node_pool_id="nodePoolId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = await response.parse()
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.batch_jobs.with_streaming_response.create(
            account_id="account_id",
            node_pool_id="nodePoolId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = await response.parse()
            assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.create(
                account_id="",
                node_pool_id="nodePoolId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.retrieve(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.retrieve(
            batch_job_id="batch_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.batch_jobs.with_raw_response.retrieve(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = await response.parse()
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.batch_jobs.with_streaming_response.retrieve(
            batch_job_id="batch_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = await response.parse()
            assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.retrieve(
                batch_job_id="batch_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.retrieve(
                batch_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.update(
            batch_job_id="batch_job_id",
            account_id="account_id",
            node_pool_id="nodePoolId",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.update(
            batch_job_id="batch_job_id",
            account_id="account_id",
            node_pool_id="nodePoolId",
            annotations={"foo": "string"},
            display_name="displayName",
            environment_id="environmentId",
            env_vars={"foo": "string"},
            image_ref="imageRef",
            notebook_executor={"notebook_filename": "notebookFilename"},
            num_ranks=0,
            python_executor={
                "target": "target",
                "target_type": "TARGET_TYPE_UNSPECIFIED",
                "args": ["string"],
            },
            role="role",
            shared=True,
            shell_executor={"command": "command"},
            snapshot_id="snapshotId",
        )
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.batch_jobs.with_raw_response.update(
            batch_job_id="batch_job_id",
            account_id="account_id",
            node_pool_id="nodePoolId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = await response.parse()
        assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.batch_jobs.with_streaming_response.update(
            batch_job_id="batch_job_id",
            account_id="account_id",
            node_pool_id="nodePoolId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = await response.parse()
            assert_matches_type(GatewayBatchJob, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.update(
                batch_job_id="batch_job_id",
                account_id="",
                node_pool_id="nodePoolId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.update(
                batch_job_id="",
                account_id="account_id",
                node_pool_id="nodePoolId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(BatchJobListResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(BatchJobListResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.batch_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = await response.parse()
        assert_matches_type(BatchJobListResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.batch_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = await response.parse()
            assert_matches_type(BatchJobListResponse, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.delete(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.batch_jobs.with_raw_response.delete(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = await response.parse()
        assert_matches_type(object, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.batch_jobs.with_streaming_response.delete(
            batch_job_id="batch_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = await response.parse()
            assert_matches_type(object, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.delete(
                batch_job_id="batch_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.delete(
                batch_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.cancel(
            batch_job_id="batch_job_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(object, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.batch_jobs.with_raw_response.cancel(
            batch_job_id="batch_job_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = await response.parse()
        assert_matches_type(object, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.batch_jobs.with_streaming_response.cancel(
            batch_job_id="batch_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = await response.parse()
            assert_matches_type(object, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.cancel(
                batch_job_id="batch_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.cancel(
                batch_job_id="",
                account_id="account_id",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_logs(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.get_logs(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )
        assert_matches_type(BatchJobGetLogsResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_logs_with_all_params(self, async_client: AsyncFireworks) -> None:
        batch_job = await async_client.accounts.batch_jobs.get_logs(
            batch_job_id="batch_job_id",
            account_id="account_id",
            filter="filter",
            page_size=0,
            page_token="pageToken",
            ranks=[0],
            read_mask="readMask",
            start_from_head=True,
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(BatchJobGetLogsResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_logs(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.batch_jobs.with_raw_response.get_logs(
            batch_job_id="batch_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_job = await response.parse()
        assert_matches_type(BatchJobGetLogsResponse, batch_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_logs(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.batch_jobs.with_streaming_response.get_logs(
            batch_job_id="batch_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_job = await response.parse()
            assert_matches_type(BatchJobGetLogsResponse, batch_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_logs(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.get_logs(
                batch_job_id="batch_job_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_job_id` but received ''"):
            await async_client.accounts.batch_jobs.with_raw_response.get_logs(
                batch_job_id="",
                account_id="account_id",
            )
