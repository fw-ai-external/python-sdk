# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import EvaluatorGetResponse, EvaluatorListResponse
from fireworks.pagination import SyncCursorEvaluators, AsyncCursorEvaluators

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluators:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        evaluator = client.evaluators.list(
            account_id="account_id",
        )
        assert_matches_type(SyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(SyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.evaluators.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(SyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluators.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        evaluator = client.evaluators.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.evaluators.with_streaming_response.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(object, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluators.with_raw_response.delete(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.delete(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.evaluators.with_streaming_response.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluators.with_raw_response.get(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.get(
                evaluator_id="",
                account_id="account_id",
            )


class TestAsyncEvaluators:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.list(
            account_id="account_id",
        )
        assert_matches_type(AsyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AsyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(AsyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluators.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(AsyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluators.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluators.with_streaming_response.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(object, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluators.with_raw_response.delete(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.delete(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluators.with_streaming_response.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluators.with_raw_response.get(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.get(
                evaluator_id="",
                account_id="account_id",
            )
