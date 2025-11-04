# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types.accounts import (
    GatewayReinforcementFineTuningJob,
    ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse,
    ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestReinforcementFineTuningJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = client.accounts.reinforcement_fine_tuning_jobs.retrieve(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = client.accounts.reinforcement_fine_tuning_jobs.retrieve(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = response.parse()
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.retrieve(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = response.parse()
            assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received ''"
        ):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve(
                reinforcement_fine_tuning_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = client.accounts.reinforcement_fine_tuning_jobs.delete(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: FireworksAI) -> None:
        response = client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.delete(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = response.parse()
        assert_matches_type(object, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: FireworksAI) -> None:
        with client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.delete(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = response.parse()
            assert_matches_type(object, reinforcement_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.delete(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received ''"
        ):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.delete(
                reinforcement_fine_tuning_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reinforcement_fine_tuning_job_id_debug(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            client.accounts.reinforcement_fine_tuning_jobs.reinforcement_fine_tuning_job_id_debug(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="account_id",
                body={},
            )
        )
        assert_matches_type(
            ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reinforcement_fine_tuning_job_id_debug(self, client: FireworksAI) -> None:
        response = (
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_debug(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="account_id",
                body={},
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = response.parse()
        assert_matches_type(
            ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reinforcement_fine_tuning_job_id_debug(self, client: FireworksAI) -> None:
        with client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.reinforcement_fine_tuning_job_id_debug(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = response.parse()
            assert_matches_type(
                ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse,
                reinforcement_fine_tuning_job,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reinforcement_fine_tuning_job_id_debug(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_debug(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received ''"
        ):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_debug(
                reinforcement_fine_tuning_job_id="",
                account_id="account_id",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reinforcement_fine_tuning_job_id_resume(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            client.accounts.reinforcement_fine_tuning_jobs.reinforcement_fine_tuning_job_id_resume(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="account_id",
                body={},
            )
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reinforcement_fine_tuning_job_id_resume(self, client: FireworksAI) -> None:
        response = (
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_resume(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="account_id",
                body={},
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = response.parse()
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reinforcement_fine_tuning_job_id_resume(self, client: FireworksAI) -> None:
        with client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.reinforcement_fine_tuning_job_id_resume(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = response.parse()
            assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reinforcement_fine_tuning_job_id_resume(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_resume(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received ''"
        ):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_resume(
                reinforcement_fine_tuning_job_id="",
                account_id="account_id",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reinforcement_fine_tuning_jobs(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = client.accounts.reinforcement_fine_tuning_jobs.reinforcement_fine_tuning_jobs(
            account_id="account_id",
            dataset="dataset",
            evaluator="evaluator",
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reinforcement_fine_tuning_jobs_with_all_params(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = client.accounts.reinforcement_fine_tuning_jobs.reinforcement_fine_tuning_jobs(
            account_id="account_id",
            dataset="dataset",
            evaluator="evaluator",
            reinforcement_fine_tuning_job_id="reinforcementFineTuningJobId",
            display_name="displayName",
            eval_auto_carveout=True,
            evaluation_dataset="evaluationDataset",
            inference_parameters={
                "extra_body": "extraBody",
                "max_tokens": 0,
                "n": 0,
                "temperature": 0,
                "top_k": 0,
                "top_p": 0,
            },
            mcp_server="mcpServer",
            output_metrics="outputMetrics",
            output_stats="outputStats",
            training_config={
                "accelerator_count": 0,
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
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reinforcement_fine_tuning_jobs(self, client: FireworksAI) -> None:
        response = client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_jobs(
            account_id="account_id",
            dataset="dataset",
            evaluator="evaluator",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = response.parse()
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reinforcement_fine_tuning_jobs(self, client: FireworksAI) -> None:
        with client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.reinforcement_fine_tuning_jobs(
            account_id="account_id",
            dataset="dataset",
            evaluator="evaluator",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = response.parse()
            assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reinforcement_fine_tuning_jobs(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_jobs(
                account_id="",
                dataset="dataset",
                evaluator="evaluator",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_reinforcement_fine_tuning_jobs(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            client.accounts.reinforcement_fine_tuning_jobs.retrieve_reinforcement_fine_tuning_jobs(
                account_id="account_id",
            )
        )
        assert_matches_type(
            ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_reinforcement_fine_tuning_jobs_with_all_params(self, client: FireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            client.accounts.reinforcement_fine_tuning_jobs.retrieve_reinforcement_fine_tuning_jobs(
                account_id="account_id",
                filter="filter",
                order_by="orderBy",
                page_size=0,
                page_token="pageToken",
                read_mask="readMask",
            )
        )
        assert_matches_type(
            ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_reinforcement_fine_tuning_jobs(self, client: FireworksAI) -> None:
        response = (
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve_reinforcement_fine_tuning_jobs(
                account_id="account_id",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = response.parse()
        assert_matches_type(
            ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_reinforcement_fine_tuning_jobs(self, client: FireworksAI) -> None:
        with client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.retrieve_reinforcement_fine_tuning_jobs(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = response.parse()
            assert_matches_type(
                ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
                reinforcement_fine_tuning_job,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_reinforcement_fine_tuning_jobs(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve_reinforcement_fine_tuning_jobs(
                account_id="",
            )


class TestAsyncReinforcementFineTuningJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        reinforcement_fine_tuning_job = await async_client.accounts.reinforcement_fine_tuning_jobs.retrieve(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        reinforcement_fine_tuning_job = await async_client.accounts.reinforcement_fine_tuning_jobs.retrieve(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = await response.parse()
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.retrieve(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = await response.parse()
            assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received ''"
        ):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve(
                reinforcement_fine_tuning_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworksAI) -> None:
        reinforcement_fine_tuning_job = await async_client.accounts.reinforcement_fine_tuning_jobs.delete(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        )
        assert_matches_type(object, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.delete(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = await response.parse()
        assert_matches_type(object, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.delete(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = await response.parse()
            assert_matches_type(object, reinforcement_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.delete(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received ''"
        ):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.delete(
                reinforcement_fine_tuning_job_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reinforcement_fine_tuning_job_id_debug(self, async_client: AsyncFireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            await async_client.accounts.reinforcement_fine_tuning_jobs.reinforcement_fine_tuning_job_id_debug(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="account_id",
                body={},
            )
        )
        assert_matches_type(
            ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reinforcement_fine_tuning_job_id_debug(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_debug(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = await response.parse()
        assert_matches_type(
            ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reinforcement_fine_tuning_job_id_debug(
        self, async_client: AsyncFireworksAI
    ) -> None:
        async with async_client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.reinforcement_fine_tuning_job_id_debug(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = await response.parse()
            assert_matches_type(
                ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse,
                reinforcement_fine_tuning_job,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reinforcement_fine_tuning_job_id_debug(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_debug(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received ''"
        ):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_debug(
                reinforcement_fine_tuning_job_id="",
                account_id="account_id",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reinforcement_fine_tuning_job_id_resume(self, async_client: AsyncFireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            await async_client.accounts.reinforcement_fine_tuning_jobs.reinforcement_fine_tuning_job_id_resume(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="account_id",
                body={},
            )
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reinforcement_fine_tuning_job_id_resume(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_resume(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = await response.parse()
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reinforcement_fine_tuning_job_id_resume(
        self, async_client: AsyncFireworksAI
    ) -> None:
        async with async_client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.reinforcement_fine_tuning_job_id_resume(
            reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = await response.parse()
            assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reinforcement_fine_tuning_job_id_resume(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_resume(
                reinforcement_fine_tuning_job_id="reinforcement_fine_tuning_job_id",
                account_id="",
                body={},
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received ''"
        ):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_job_id_resume(
                reinforcement_fine_tuning_job_id="",
                account_id="account_id",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reinforcement_fine_tuning_jobs(self, async_client: AsyncFireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            await async_client.accounts.reinforcement_fine_tuning_jobs.reinforcement_fine_tuning_jobs(
                account_id="account_id",
                dataset="dataset",
                evaluator="evaluator",
            )
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reinforcement_fine_tuning_jobs_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            await async_client.accounts.reinforcement_fine_tuning_jobs.reinforcement_fine_tuning_jobs(
                account_id="account_id",
                dataset="dataset",
                evaluator="evaluator",
                reinforcement_fine_tuning_job_id="reinforcementFineTuningJobId",
                display_name="displayName",
                eval_auto_carveout=True,
                evaluation_dataset="evaluationDataset",
                inference_parameters={
                    "extra_body": "extraBody",
                    "max_tokens": 0,
                    "n": 0,
                    "temperature": 0,
                    "top_k": 0,
                    "top_p": 0,
                },
                mcp_server="mcpServer",
                output_metrics="outputMetrics",
                output_stats="outputStats",
                training_config={
                    "accelerator_count": 0,
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
        )
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reinforcement_fine_tuning_jobs(self, async_client: AsyncFireworksAI) -> None:
        response = (
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_jobs(
                account_id="account_id",
                dataset="dataset",
                evaluator="evaluator",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = await response.parse()
        assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reinforcement_fine_tuning_jobs(self, async_client: AsyncFireworksAI) -> None:
        async with (
            async_client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.reinforcement_fine_tuning_jobs(
                account_id="account_id",
                dataset="dataset",
                evaluator="evaluator",
            )
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = await response.parse()
            assert_matches_type(GatewayReinforcementFineTuningJob, reinforcement_fine_tuning_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reinforcement_fine_tuning_jobs(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.reinforcement_fine_tuning_jobs(
                account_id="",
                dataset="dataset",
                evaluator="evaluator",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_reinforcement_fine_tuning_jobs(self, async_client: AsyncFireworksAI) -> None:
        reinforcement_fine_tuning_job = (
            await async_client.accounts.reinforcement_fine_tuning_jobs.retrieve_reinforcement_fine_tuning_jobs(
                account_id="account_id",
            )
        )
        assert_matches_type(
            ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_reinforcement_fine_tuning_jobs_with_all_params(
        self, async_client: AsyncFireworksAI
    ) -> None:
        reinforcement_fine_tuning_job = (
            await async_client.accounts.reinforcement_fine_tuning_jobs.retrieve_reinforcement_fine_tuning_jobs(
                account_id="account_id",
                filter="filter",
                order_by="orderBy",
                page_size=0,
                page_token="pageToken",
                read_mask="readMask",
            )
        )
        assert_matches_type(
            ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_reinforcement_fine_tuning_jobs(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve_reinforcement_fine_tuning_jobs(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        reinforcement_fine_tuning_job = await response.parse()
        assert_matches_type(
            ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
            reinforcement_fine_tuning_job,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_reinforcement_fine_tuning_jobs(
        self, async_client: AsyncFireworksAI
    ) -> None:
        async with async_client.accounts.reinforcement_fine_tuning_jobs.with_streaming_response.retrieve_reinforcement_fine_tuning_jobs(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            reinforcement_fine_tuning_job = await response.parse()
            assert_matches_type(
                ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse,
                reinforcement_fine_tuning_job,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_reinforcement_fine_tuning_jobs(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.reinforcement_fine_tuning_jobs.with_raw_response.retrieve_reinforcement_fine_tuning_jobs(
                account_id="",
            )
