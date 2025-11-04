# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai._utils import parse_datetime
from fireworks_ai.types.accounts import BillingGetSummaryResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBilling:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_summary(self, client: Fireworks) -> None:
        billing = client.accounts.billing.get_summary(
            account_id="account_id",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(BillingGetSummaryResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_summary(self, client: Fireworks) -> None:
        response = client.accounts.billing.with_raw_response.get_summary(
            account_id="account_id",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        billing = response.parse()
        assert_matches_type(BillingGetSummaryResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_summary(self, client: Fireworks) -> None:
        with client.accounts.billing.with_streaming_response.get_summary(
            account_id="account_id",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            billing = response.parse()
            assert_matches_type(BillingGetSummaryResponse, billing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_summary(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.billing.with_raw_response.get_summary(
                account_id="",
                end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
                start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            )


class TestAsyncBilling:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_summary(self, async_client: AsyncFireworks) -> None:
        billing = await async_client.accounts.billing.get_summary(
            account_id="account_id",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(BillingGetSummaryResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_summary(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.billing.with_raw_response.get_summary(
            account_id="account_id",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        billing = await response.parse()
        assert_matches_type(BillingGetSummaryResponse, billing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_summary(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.billing.with_streaming_response.get_summary(
            account_id="account_id",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            billing = await response.parse()
            assert_matches_type(BillingGetSummaryResponse, billing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_summary(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.billing.with_raw_response.get_summary(
                account_id="",
                end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
                start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            )
