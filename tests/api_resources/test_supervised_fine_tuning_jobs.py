# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import (
    SupervisedFineTuningJob,
)
from fireworks.pagination import SyncCursorSupervisedFineTuningJobs, AsyncCursorSupervisedFineTuningJobs

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSupervisedFineTuningJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        supervised_fine_tuning_job = client.supervised_fine_tuning_jobs.create(
            account_id="account_id",
            dataset="dataset",
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        supervised_fine_tuning_job = client.supervised_fine_tuning_jobs.create(
            account_id="account_id",
            dataset="dataset",
            supervised_fine_tuning_job_id="supervisedFineTuningJobId",
            aws_s3_config={
                "credentials_secret": "credentialsSecret",
                "iam_role_arn": "iamRoleArn",
            },
            base_model="baseModel",
            batch_size=0,
            batch_size_samples=0,
            display_name="displayName",
            early_stop=True,
            epochs=0,
            eval_auto_carveout=True,
            evaluation_dataset="evaluationDataset",
            gradient_accumulation_steps=0,
            is_turbo=True,
            jinja_template="jinjaTemplate",
            learning_rate=0,
            learning_rate_warmup_steps=0,
            lora_rank=0,
            max_context_length=0,
            metrics_file_signed_url="metricsFileSignedUrl",
            mtp_enabled=True,
            mtp_freeze_base_model=True,
            mtp_num_draft_tokens=0,
            nodes=0,
            optimizer_weight_decay=0,
            output_model="outputModel",
            region="REGION_UNSPECIFIED",
            use_purpose="usePurpose",
            wandb_config={
                "api_key": "apiKey",
                "enabled": True,
                "entity": "entity",
                "project": "project",
                "run_id": "runId",
            },
            warm_start_from="warmStartFrom",
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.supervised_fine_tuning_jobs.with_raw_response.create(
            account_id="account_id",
            dataset="dataset",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = response.parse()
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.supervised_fine_tuning_jobs.with_streaming_response.create(
            account_id="account_id",
            dataset="dataset",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = response.parse()
            assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.supervised_fine_tuning_jobs.with_raw_response.create(
                account_id="",
                dataset="dataset",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        supervised_fine_tuning_job = client.supervised_fine_tuning_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(
            SyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob], supervised_fine_tuning_job, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        supervised_fine_tuning_job = client.supervised_fine_tuning_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(
            SyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob], supervised_fine_tuning_job, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.supervised_fine_tuning_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = response.parse()
        assert_matches_type(
            SyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob], supervised_fine_tuning_job, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.supervised_fine_tuning_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = response.parse()
            assert_matches_type(
                SyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob],
                supervised_fine_tuning_job,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.supervised_fine_tuning_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        supervised_fine_tuning_job = client.supervised_fine_tuning_jobs.delete(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.supervised_fine_tuning_jobs.with_raw_response.delete(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = response.parse()
        assert_matches_type(object, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.supervised_fine_tuning_jobs.with_streaming_response.delete(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = response.parse()
            assert_matches_type(object, supervised_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.supervised_fine_tuning_jobs.with_raw_response.delete(
                supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `supervised_fine_tuning_job_id` but received ''"
        ):
            client.supervised_fine_tuning_jobs.with_raw_response.delete(
                supervised_fine_tuning_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        supervised_fine_tuning_job = client.supervised_fine_tuning_jobs.get(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        supervised_fine_tuning_job = client.supervised_fine_tuning_jobs.get(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.supervised_fine_tuning_jobs.with_raw_response.get(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = response.parse()
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.supervised_fine_tuning_jobs.with_streaming_response.get(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = response.parse()
            assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.supervised_fine_tuning_jobs.with_raw_response.get(
                supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `supervised_fine_tuning_job_id` but received ''"
        ):
            client.supervised_fine_tuning_jobs.with_raw_response.get(
                supervised_fine_tuning_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resume(self, client: Fireworks) -> None:
        supervised_fine_tuning_job = client.supervised_fine_tuning_jobs.resume(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_resume(self, client: Fireworks) -> None:
        response = client.supervised_fine_tuning_jobs.with_raw_response.resume(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = response.parse()
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_resume(self, client: Fireworks) -> None:
        with client.supervised_fine_tuning_jobs.with_streaming_response.resume(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = response.parse()
            assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_resume(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.supervised_fine_tuning_jobs.with_raw_response.resume(
                supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `supervised_fine_tuning_job_id` but received ''"
        ):
            client.supervised_fine_tuning_jobs.with_raw_response.resume(
                supervised_fine_tuning_job_id="",
                account_id="account_id",
                body={},
            )


class TestAsyncSupervisedFineTuningJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        supervised_fine_tuning_job = await async_client.supervised_fine_tuning_jobs.create(
            account_id="account_id",
            dataset="dataset",
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        supervised_fine_tuning_job = await async_client.supervised_fine_tuning_jobs.create(
            account_id="account_id",
            dataset="dataset",
            supervised_fine_tuning_job_id="supervisedFineTuningJobId",
            aws_s3_config={
                "credentials_secret": "credentialsSecret",
                "iam_role_arn": "iamRoleArn",
            },
            base_model="baseModel",
            batch_size=0,
            batch_size_samples=0,
            display_name="displayName",
            early_stop=True,
            epochs=0,
            eval_auto_carveout=True,
            evaluation_dataset="evaluationDataset",
            gradient_accumulation_steps=0,
            is_turbo=True,
            jinja_template="jinjaTemplate",
            learning_rate=0,
            learning_rate_warmup_steps=0,
            lora_rank=0,
            max_context_length=0,
            metrics_file_signed_url="metricsFileSignedUrl",
            mtp_enabled=True,
            mtp_freeze_base_model=True,
            mtp_num_draft_tokens=0,
            nodes=0,
            optimizer_weight_decay=0,
            output_model="outputModel",
            region="REGION_UNSPECIFIED",
            use_purpose="usePurpose",
            wandb_config={
                "api_key": "apiKey",
                "enabled": True,
                "entity": "entity",
                "project": "project",
                "run_id": "runId",
            },
            warm_start_from="warmStartFrom",
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.supervised_fine_tuning_jobs.with_raw_response.create(
            account_id="account_id",
            dataset="dataset",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = await response.parse()
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.supervised_fine_tuning_jobs.with_streaming_response.create(
            account_id="account_id",
            dataset="dataset",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = await response.parse()
            assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.supervised_fine_tuning_jobs.with_raw_response.create(
                account_id="",
                dataset="dataset",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        supervised_fine_tuning_job = await async_client.supervised_fine_tuning_jobs.list(
            account_id="account_id",
        )
        assert_matches_type(
            AsyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob], supervised_fine_tuning_job, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        supervised_fine_tuning_job = await async_client.supervised_fine_tuning_jobs.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(
            AsyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob], supervised_fine_tuning_job, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.supervised_fine_tuning_jobs.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = await response.parse()
        assert_matches_type(
            AsyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob], supervised_fine_tuning_job, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.supervised_fine_tuning_jobs.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = await response.parse()
            assert_matches_type(
                AsyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob],
                supervised_fine_tuning_job,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.supervised_fine_tuning_jobs.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        supervised_fine_tuning_job = await async_client.supervised_fine_tuning_jobs.delete(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.supervised_fine_tuning_jobs.with_raw_response.delete(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = await response.parse()
        assert_matches_type(object, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.supervised_fine_tuning_jobs.with_streaming_response.delete(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = await response.parse()
            assert_matches_type(object, supervised_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.supervised_fine_tuning_jobs.with_raw_response.delete(
                supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `supervised_fine_tuning_job_id` but received ''"
        ):
            await async_client.supervised_fine_tuning_jobs.with_raw_response.delete(
                supervised_fine_tuning_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        supervised_fine_tuning_job = await async_client.supervised_fine_tuning_jobs.get(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        supervised_fine_tuning_job = await async_client.supervised_fine_tuning_jobs.get(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.supervised_fine_tuning_jobs.with_raw_response.get(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = await response.parse()
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.supervised_fine_tuning_jobs.with_streaming_response.get(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = await response.parse()
            assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.supervised_fine_tuning_jobs.with_raw_response.get(
                supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `supervised_fine_tuning_job_id` but received ''"
        ):
            await async_client.supervised_fine_tuning_jobs.with_raw_response.get(
                supervised_fine_tuning_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resume(self, async_client: AsyncFireworks) -> None:
        supervised_fine_tuning_job = await async_client.supervised_fine_tuning_jobs.resume(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_resume(self, async_client: AsyncFireworks) -> None:
        response = await async_client.supervised_fine_tuning_jobs.with_raw_response.resume(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supervised_fine_tuning_job = await response.parse()
        assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_resume(self, async_client: AsyncFireworks) -> None:
        async with async_client.supervised_fine_tuning_jobs.with_streaming_response.resume(
            supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supervised_fine_tuning_job = await response.parse()
            assert_matches_type(SupervisedFineTuningJob, supervised_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_resume(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.supervised_fine_tuning_jobs.with_raw_response.resume(
                supervised_fine_tuning_job_id="supervised_fine_tuning_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `supervised_fine_tuning_job_id` but received ''"
        ):
            await async_client.supervised_fine_tuning_jobs.with_raw_response.resume(
                supervised_fine_tuning_job_id="",
                account_id="account_id",
                body={},
            )
