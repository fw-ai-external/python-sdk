# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai.types.accounts import (
    GatewayAwsIamRoleBinding,
    AwsIamRoleBindingListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAwsIamRoleBindings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        aws_iam_role_binding = client.accounts.aws_iam_role_bindings.create(
            account_id="account_id",
            principal="principal",
            role="role",
        )
        assert_matches_type(GatewayAwsIamRoleBinding, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.accounts.aws_iam_role_bindings.with_raw_response.create(
            account_id="account_id",
            principal="principal",
            role="role",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        aws_iam_role_binding = response.parse()
        assert_matches_type(GatewayAwsIamRoleBinding, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.accounts.aws_iam_role_bindings.with_streaming_response.create(
            account_id="account_id",
            principal="principal",
            role="role",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            aws_iam_role_binding = response.parse()
            assert_matches_type(GatewayAwsIamRoleBinding, aws_iam_role_binding, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.aws_iam_role_bindings.with_raw_response.create(
                account_id="",
                principal="principal",
                role="role",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        aws_iam_role_binding = client.accounts.aws_iam_role_bindings.list(
            account_id="account_id",
        )
        assert_matches_type(AwsIamRoleBindingListResponse, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        aws_iam_role_binding = client.accounts.aws_iam_role_bindings.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AwsIamRoleBindingListResponse, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.accounts.aws_iam_role_bindings.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        aws_iam_role_binding = response.parse()
        assert_matches_type(AwsIamRoleBindingListResponse, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.accounts.aws_iam_role_bindings.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            aws_iam_role_binding = response.parse()
            assert_matches_type(AwsIamRoleBindingListResponse, aws_iam_role_binding, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.aws_iam_role_bindings.with_raw_response.list(
                account_id="",
            )


class TestAsyncAwsIamRoleBindings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        aws_iam_role_binding = await async_client.accounts.aws_iam_role_bindings.create(
            account_id="account_id",
            principal="principal",
            role="role",
        )
        assert_matches_type(GatewayAwsIamRoleBinding, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.aws_iam_role_bindings.with_raw_response.create(
            account_id="account_id",
            principal="principal",
            role="role",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        aws_iam_role_binding = await response.parse()
        assert_matches_type(GatewayAwsIamRoleBinding, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.aws_iam_role_bindings.with_streaming_response.create(
            account_id="account_id",
            principal="principal",
            role="role",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            aws_iam_role_binding = await response.parse()
            assert_matches_type(GatewayAwsIamRoleBinding, aws_iam_role_binding, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.aws_iam_role_bindings.with_raw_response.create(
                account_id="",
                principal="principal",
                role="role",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        aws_iam_role_binding = await async_client.accounts.aws_iam_role_bindings.list(
            account_id="account_id",
        )
        assert_matches_type(AwsIamRoleBindingListResponse, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        aws_iam_role_binding = await async_client.accounts.aws_iam_role_bindings.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AwsIamRoleBindingListResponse, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.aws_iam_role_bindings.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        aws_iam_role_binding = await response.parse()
        assert_matches_type(AwsIamRoleBindingListResponse, aws_iam_role_binding, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.aws_iam_role_bindings.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            aws_iam_role_binding = await response.parse()
            assert_matches_type(AwsIamRoleBindingListResponse, aws_iam_role_binding, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.aws_iam_role_bindings.with_raw_response.list(
                account_id="",
            )
