# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai._utils import parse_datetime
from fireworks_ai.types.accounts import (
    GatewayLeaderboard,
    LeaderboardListResponse,
    LeaderboardRetrieveResponse,
    LeaderboardListEvaluationJobsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLeaderboards:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.create(
            account_id="account_id",
            leaderboard={},
        )
        assert_matches_type(GatewayLeaderboard, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.create(
            account_id="account_id",
            leaderboard={
                "description": "description",
                "display_name": "displayName",
                "source": {
                    "datasets": [{"dataset": "dataset"}],
                    "evaluator": "evaluator",
                    "last_duration": "lastDuration",
                    "time_interval": {
                        "end_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                        "start_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                    },
                    "time_window": "timeWindow",
                },
            },
            leaderboard_id="leaderboardId",
        )
        assert_matches_type(GatewayLeaderboard, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: FireworksAI) -> None:
        response = client.accounts.leaderboards.with_raw_response.create(
            account_id="account_id",
            leaderboard={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = response.parse()
        assert_matches_type(GatewayLeaderboard, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: FireworksAI) -> None:
        with client.accounts.leaderboards.with_streaming_response.create(
            account_id="account_id",
            leaderboard={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = response.parse()
            assert_matches_type(GatewayLeaderboard, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.leaderboards.with_raw_response.create(
                account_id="",
                leaderboard={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.retrieve(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )
        assert_matches_type(LeaderboardRetrieveResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.retrieve(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(LeaderboardRetrieveResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.leaderboards.with_raw_response.retrieve(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = response.parse()
        assert_matches_type(LeaderboardRetrieveResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.leaderboards.with_streaming_response.retrieve(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = response.parse()
            assert_matches_type(LeaderboardRetrieveResponse, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.leaderboards.with_raw_response.retrieve(
                leaderboard_id="leaderboard_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `leaderboard_id` but received ''"):
            client.accounts.leaderboards.with_raw_response.retrieve(
                leaderboard_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.list(
            account_id="account_id",
        )
        assert_matches_type(LeaderboardListResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(LeaderboardListResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FireworksAI) -> None:
        response = client.accounts.leaderboards.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = response.parse()
        assert_matches_type(LeaderboardListResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FireworksAI) -> None:
        with client.accounts.leaderboards.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = response.parse()
            assert_matches_type(LeaderboardListResponse, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.leaderboards.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.delete(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )
        assert_matches_type(object, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: FireworksAI) -> None:
        response = client.accounts.leaderboards.with_raw_response.delete(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = response.parse()
        assert_matches_type(object, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: FireworksAI) -> None:
        with client.accounts.leaderboards.with_streaming_response.delete(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = response.parse()
            assert_matches_type(object, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.leaderboards.with_raw_response.delete(
                leaderboard_id="leaderboard_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `leaderboard_id` but received ''"):
            client.accounts.leaderboards.with_raw_response.delete(
                leaderboard_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_evaluation_jobs(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.list_evaluation_jobs(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )
        assert_matches_type(LeaderboardListEvaluationJobsResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_evaluation_jobs_with_all_params(self, client: FireworksAI) -> None:
        leaderboard = client.accounts.leaderboards.list_evaluation_jobs(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(LeaderboardListEvaluationJobsResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_evaluation_jobs(self, client: FireworksAI) -> None:
        response = client.accounts.leaderboards.with_raw_response.list_evaluation_jobs(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = response.parse()
        assert_matches_type(LeaderboardListEvaluationJobsResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_evaluation_jobs(self, client: FireworksAI) -> None:
        with client.accounts.leaderboards.with_streaming_response.list_evaluation_jobs(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = response.parse()
            assert_matches_type(LeaderboardListEvaluationJobsResponse, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_evaluation_jobs(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.leaderboards.with_raw_response.list_evaluation_jobs(
                leaderboard_id="leaderboard_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `leaderboard_id` but received ''"):
            client.accounts.leaderboards.with_raw_response.list_evaluation_jobs(
                leaderboard_id="",
                account_id="account_id",
            )


class TestAsyncLeaderboards:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.create(
            account_id="account_id",
            leaderboard={},
        )
        assert_matches_type(GatewayLeaderboard, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.create(
            account_id="account_id",
            leaderboard={
                "description": "description",
                "display_name": "displayName",
                "source": {
                    "datasets": [{"dataset": "dataset"}],
                    "evaluator": "evaluator",
                    "last_duration": "lastDuration",
                    "time_interval": {
                        "end_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                        "start_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                    },
                    "time_window": "timeWindow",
                },
            },
            leaderboard_id="leaderboardId",
        )
        assert_matches_type(GatewayLeaderboard, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.leaderboards.with_raw_response.create(
            account_id="account_id",
            leaderboard={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = await response.parse()
        assert_matches_type(GatewayLeaderboard, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.leaderboards.with_streaming_response.create(
            account_id="account_id",
            leaderboard={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = await response.parse()
            assert_matches_type(GatewayLeaderboard, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.leaderboards.with_raw_response.create(
                account_id="",
                leaderboard={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.retrieve(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )
        assert_matches_type(LeaderboardRetrieveResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.retrieve(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(LeaderboardRetrieveResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.leaderboards.with_raw_response.retrieve(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = await response.parse()
        assert_matches_type(LeaderboardRetrieveResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.leaderboards.with_streaming_response.retrieve(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = await response.parse()
            assert_matches_type(LeaderboardRetrieveResponse, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.leaderboards.with_raw_response.retrieve(
                leaderboard_id="leaderboard_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `leaderboard_id` but received ''"):
            await async_client.accounts.leaderboards.with_raw_response.retrieve(
                leaderboard_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.list(
            account_id="account_id",
        )
        assert_matches_type(LeaderboardListResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(LeaderboardListResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.leaderboards.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = await response.parse()
        assert_matches_type(LeaderboardListResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.leaderboards.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = await response.parse()
            assert_matches_type(LeaderboardListResponse, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.leaderboards.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.delete(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )
        assert_matches_type(object, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.leaderboards.with_raw_response.delete(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = await response.parse()
        assert_matches_type(object, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.leaderboards.with_streaming_response.delete(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = await response.parse()
            assert_matches_type(object, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.leaderboards.with_raw_response.delete(
                leaderboard_id="leaderboard_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `leaderboard_id` but received ''"):
            await async_client.accounts.leaderboards.with_raw_response.delete(
                leaderboard_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_evaluation_jobs(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.list_evaluation_jobs(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )
        assert_matches_type(LeaderboardListEvaluationJobsResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_evaluation_jobs_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        leaderboard = await async_client.accounts.leaderboards.list_evaluation_jobs(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(LeaderboardListEvaluationJobsResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_evaluation_jobs(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.leaderboards.with_raw_response.list_evaluation_jobs(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        leaderboard = await response.parse()
        assert_matches_type(LeaderboardListEvaluationJobsResponse, leaderboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_evaluation_jobs(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.leaderboards.with_streaming_response.list_evaluation_jobs(
            leaderboard_id="leaderboard_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            leaderboard = await response.parse()
            assert_matches_type(LeaderboardListEvaluationJobsResponse, leaderboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_evaluation_jobs(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.leaderboards.with_raw_response.list_evaluation_jobs(
                leaderboard_id="leaderboard_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `leaderboard_id` but received ''"):
            await async_client.accounts.leaderboards.with_raw_response.list_evaluation_jobs(
                leaderboard_id="",
                account_id="account_id",
            )
