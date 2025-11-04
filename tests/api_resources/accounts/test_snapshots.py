# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types.accounts import (
    GatewaySnapshot,
    SnapshotListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSnapshots:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: FireworksAI) -> None:
        snapshot = client.accounts.snapshots.create(
            "account_id",
        )
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: FireworksAI) -> None:
        response = client.accounts.snapshots.with_raw_response.create(
            "account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = response.parse()
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: FireworksAI) -> None:
        with client.accounts.snapshots.with_streaming_response.create(
            "account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = response.parse()
            assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.snapshots.with_raw_response.create(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        snapshot = client.accounts.snapshots.retrieve(
            snapshot_id="snapshot_id",
            account_id="account_id",
        )
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        snapshot = client.accounts.snapshots.retrieve(
            snapshot_id="snapshot_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.snapshots.with_raw_response.retrieve(
            snapshot_id="snapshot_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = response.parse()
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.snapshots.with_streaming_response.retrieve(
            snapshot_id="snapshot_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = response.parse()
            assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.snapshots.with_raw_response.retrieve(
                snapshot_id="snapshot_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `snapshot_id` but received ''"):
            client.accounts.snapshots.with_raw_response.retrieve(
                snapshot_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FireworksAI) -> None:
        snapshot = client.accounts.snapshots.list(
            account_id="account_id",
        )
        assert_matches_type(SnapshotListResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FireworksAI) -> None:
        snapshot = client.accounts.snapshots.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SnapshotListResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FireworksAI) -> None:
        response = client.accounts.snapshots.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = response.parse()
        assert_matches_type(SnapshotListResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FireworksAI) -> None:
        with client.accounts.snapshots.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = response.parse()
            assert_matches_type(SnapshotListResponse, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.snapshots.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: FireworksAI) -> None:
        snapshot = client.accounts.snapshots.delete(
            snapshot_id="snapshot_id",
            account_id="account_id",
        )
        assert_matches_type(object, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: FireworksAI) -> None:
        response = client.accounts.snapshots.with_raw_response.delete(
            snapshot_id="snapshot_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = response.parse()
        assert_matches_type(object, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: FireworksAI) -> None:
        with client.accounts.snapshots.with_streaming_response.delete(
            snapshot_id="snapshot_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = response.parse()
            assert_matches_type(object, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.snapshots.with_raw_response.delete(
                snapshot_id="snapshot_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `snapshot_id` but received ''"):
            client.accounts.snapshots.with_raw_response.delete(
                snapshot_id="",
                account_id="account_id",
            )


class TestAsyncSnapshots:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworksAI) -> None:
        snapshot = await async_client.accounts.snapshots.create(
            "account_id",
        )
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.snapshots.with_raw_response.create(
            "account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = await response.parse()
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.snapshots.with_streaming_response.create(
            "account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = await response.parse()
            assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.snapshots.with_raw_response.create(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        snapshot = await async_client.accounts.snapshots.retrieve(
            snapshot_id="snapshot_id",
            account_id="account_id",
        )
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        snapshot = await async_client.accounts.snapshots.retrieve(
            snapshot_id="snapshot_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.snapshots.with_raw_response.retrieve(
            snapshot_id="snapshot_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = await response.parse()
        assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.snapshots.with_streaming_response.retrieve(
            snapshot_id="snapshot_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = await response.parse()
            assert_matches_type(GatewaySnapshot, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.snapshots.with_raw_response.retrieve(
                snapshot_id="snapshot_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `snapshot_id` but received ''"):
            await async_client.accounts.snapshots.with_raw_response.retrieve(
                snapshot_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworksAI) -> None:
        snapshot = await async_client.accounts.snapshots.list(
            account_id="account_id",
        )
        assert_matches_type(SnapshotListResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        snapshot = await async_client.accounts.snapshots.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SnapshotListResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.snapshots.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = await response.parse()
        assert_matches_type(SnapshotListResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.snapshots.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = await response.parse()
            assert_matches_type(SnapshotListResponse, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.snapshots.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworksAI) -> None:
        snapshot = await async_client.accounts.snapshots.delete(
            snapshot_id="snapshot_id",
            account_id="account_id",
        )
        assert_matches_type(object, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.snapshots.with_raw_response.delete(
            snapshot_id="snapshot_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = await response.parse()
        assert_matches_type(object, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.snapshots.with_streaming_response.delete(
            snapshot_id="snapshot_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = await response.parse()
            assert_matches_type(object, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.snapshots.with_raw_response.delete(
                snapshot_id="snapshot_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `snapshot_id` but received ''"):
            await async_client.accounts.snapshots.with_raw_response.delete(
                snapshot_id="",
                account_id="account_id",
            )
