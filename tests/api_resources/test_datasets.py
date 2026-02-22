# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import (
    Dataset,
    DatasetUploadResponse,
    DatasetGetUploadEndpointResponse,
    DatasetGetDownloadEndpointResponse,
)
from fireworks.pagination import SyncCursorDatasets, AsyncCursorDatasets

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDatasets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        dataset = client.datasets.create(
            account_id="account_id",
            dataset={},
            dataset_id="datasetId",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        dataset = client.datasets.create(
            account_id="account_id",
            dataset={
                "display_name": "displayName",
                "eval_protocol": {},
                "evaluation_result": {"evaluation_job_id": "evaluationJobId"},
                "example_count": "exampleCount",
                "external_url": "externalUrl",
                "format": "FORMAT_UNSPECIFIED",
                "source_job_name": "sourceJobName",
                "splitted": {"source_dataset_id": "sourceDatasetId"},
                "transformed": {
                    "source_dataset_id": "sourceDatasetId",
                    "filter": "filter",
                    "original_format": "FORMAT_UNSPECIFIED",
                },
                "user_uploaded": {},
            },
            dataset_id="datasetId",
            filter="filter",
            source_dataset_id="sourceDatasetId",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.create(
            account_id="account_id",
            dataset={},
            dataset_id="datasetId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.create(
            account_id="account_id",
            dataset={},
            dataset_id="datasetId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(Dataset, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.create(
                account_id="",
                dataset={},
                dataset_id="datasetId",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        dataset = client.datasets.update(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        dataset = client.datasets.update(
            dataset_id="dataset_id",
            account_id="account_id",
            display_name="displayName",
            eval_protocol={},
            evaluation_result={"evaluation_job_id": "evaluationJobId"},
            example_count="exampleCount",
            external_url="externalUrl",
            format="FORMAT_UNSPECIFIED",
            source_job_name="sourceJobName",
            splitted={"source_dataset_id": "sourceDatasetId"},
            transformed={
                "source_dataset_id": "sourceDatasetId",
                "filter": "filter",
                "original_format": "FORMAT_UNSPECIFIED",
            },
            user_uploaded={},
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.update(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.update(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(Dataset, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.update(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.update(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        dataset = client.datasets.list(
            account_id="account_id",
        )
        assert_matches_type(SyncCursorDatasets[Dataset], dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        dataset = client.datasets.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SyncCursorDatasets[Dataset], dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(SyncCursorDatasets[Dataset], dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(SyncCursorDatasets[Dataset], dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        dataset = client.datasets.delete(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.delete(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.delete(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.delete(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.delete(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        dataset = client.datasets.get(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        dataset = client.datasets.get(
            dataset_id="dataset_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.get(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.get(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(Dataset, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.get(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.get(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_download_endpoint(self, client: Fireworks) -> None:
        dataset = client.datasets.get_download_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(DatasetGetDownloadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_download_endpoint_with_all_params(self, client: Fireworks) -> None:
        dataset = client.datasets.get_download_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            download_lineage=True,
            read_mask="readMask",
        )
        assert_matches_type(DatasetGetDownloadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_get_download_endpoint(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.get_download_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetGetDownloadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_get_download_endpoint(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.get_download_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetGetDownloadEndpointResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_get_download_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.get_download_endpoint(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.get_download_endpoint(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint(self, client: Fireworks) -> None:
        dataset = client.datasets.get_upload_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(DatasetGetUploadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint_with_all_params(self, client: Fireworks) -> None:
        dataset = client.datasets.get_upload_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
            read_mask="readMask",
        )
        assert_matches_type(DatasetGetUploadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_get_upload_endpoint(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.get_upload_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetGetUploadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_get_upload_endpoint(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.get_upload_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetGetUploadEndpointResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_get_upload_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.get_upload_endpoint(
                dataset_id="dataset_id",
                account_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.get_upload_endpoint(
                dataset_id="",
                account_id="account_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_upload(self, client: Fireworks) -> None:
        dataset = client.datasets.upload(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(DatasetUploadResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_upload_with_all_params(self, client: Fireworks) -> None:
        dataset = client.datasets.upload(
            dataset_id="dataset_id",
            account_id="account_id",
            file=b"raw file contents",
        )
        assert_matches_type(DatasetUploadResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_upload(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.upload(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetUploadResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_upload(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.upload(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetUploadResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_upload(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.upload(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.upload(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_validate_upload(self, client: Fireworks) -> None:
        dataset = client.datasets.validate_upload(
            dataset_id="dataset_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_validate_upload(self, client: Fireworks) -> None:
        response = client.datasets.with_raw_response.validate_upload(
            dataset_id="dataset_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_validate_upload(self, client: Fireworks) -> None:
        with client.datasets.with_streaming_response.validate_upload(
            dataset_id="dataset_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_validate_upload(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.datasets.with_raw_response.validate_upload(
                dataset_id="dataset_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.validate_upload(
                dataset_id="",
                account_id="account_id",
                body={},
            )


class TestAsyncDatasets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.create(
            account_id="account_id",
            dataset={},
            dataset_id="datasetId",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.create(
            account_id="account_id",
            dataset={
                "display_name": "displayName",
                "eval_protocol": {},
                "evaluation_result": {"evaluation_job_id": "evaluationJobId"},
                "example_count": "exampleCount",
                "external_url": "externalUrl",
                "format": "FORMAT_UNSPECIFIED",
                "source_job_name": "sourceJobName",
                "splitted": {"source_dataset_id": "sourceDatasetId"},
                "transformed": {
                    "source_dataset_id": "sourceDatasetId",
                    "filter": "filter",
                    "original_format": "FORMAT_UNSPECIFIED",
                },
                "user_uploaded": {},
            },
            dataset_id="datasetId",
            filter="filter",
            source_dataset_id="sourceDatasetId",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.create(
            account_id="account_id",
            dataset={},
            dataset_id="datasetId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.create(
            account_id="account_id",
            dataset={},
            dataset_id="datasetId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(Dataset, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.create(
                account_id="",
                dataset={},
                dataset_id="datasetId",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.update(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.update(
            dataset_id="dataset_id",
            account_id="account_id",
            display_name="displayName",
            eval_protocol={},
            evaluation_result={"evaluation_job_id": "evaluationJobId"},
            example_count="exampleCount",
            external_url="externalUrl",
            format="FORMAT_UNSPECIFIED",
            source_job_name="sourceJobName",
            splitted={"source_dataset_id": "sourceDatasetId"},
            transformed={
                "source_dataset_id": "sourceDatasetId",
                "filter": "filter",
                "original_format": "FORMAT_UNSPECIFIED",
            },
            user_uploaded={},
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.update(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.update(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(Dataset, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.update(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.update(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.list(
            account_id="account_id",
        )
        assert_matches_type(AsyncCursorDatasets[Dataset], dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AsyncCursorDatasets[Dataset], dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(AsyncCursorDatasets[Dataset], dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(AsyncCursorDatasets[Dataset], dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.delete(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.delete(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.delete(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.delete(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.delete(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.get(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.get(
            dataset_id="dataset_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.get(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(Dataset, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.get(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(Dataset, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.get(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.get(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_download_endpoint(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.get_download_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(DatasetGetDownloadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_download_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.get_download_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            download_lineage=True,
            read_mask="readMask",
        )
        assert_matches_type(DatasetGetDownloadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_get_download_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.get_download_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetGetDownloadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_get_download_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.get_download_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetGetDownloadEndpointResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_get_download_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.get_download_endpoint(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.get_download_endpoint(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.get_upload_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(DatasetGetUploadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.get_upload_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
            read_mask="readMask",
        )
        assert_matches_type(DatasetGetUploadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.get_upload_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetGetUploadEndpointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.get_upload_endpoint(
            dataset_id="dataset_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetGetUploadEndpointResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.get_upload_endpoint(
                dataset_id="dataset_id",
                account_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.get_upload_endpoint(
                dataset_id="",
                account_id="account_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_upload(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.upload(
            dataset_id="dataset_id",
            account_id="account_id",
        )
        assert_matches_type(DatasetUploadResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_upload_with_all_params(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.upload(
            dataset_id="dataset_id",
            account_id="account_id",
            file=b"raw file contents",
        )
        assert_matches_type(DatasetUploadResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.upload(
            dataset_id="dataset_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetUploadResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.upload(
            dataset_id="dataset_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetUploadResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_upload(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.upload(
                dataset_id="dataset_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.upload(
                dataset_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_validate_upload(self, async_client: AsyncFireworks) -> None:
        dataset = await async_client.datasets.validate_upload(
            dataset_id="dataset_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        response = await async_client.datasets.with_raw_response.validate_upload(
            dataset_id="dataset_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        async with async_client.datasets.with_streaming_response.validate_upload(
            dataset_id="dataset_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_validate_upload(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.datasets.with_raw_response.validate_upload(
                dataset_id="dataset_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.validate_upload(
                dataset_id="",
                account_id="account_id",
                body={},
            )
