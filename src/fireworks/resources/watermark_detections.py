# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import watermark_detection_create_params
from .._types import Body, Query, Headers, NotGiven, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.watermark_detection import WatermarkDetection

__all__ = ["WatermarkDetectionsResource", "AsyncWatermarkDetectionsResource"]


class WatermarkDetectionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WatermarkDetectionsResourceWithRawResponse:
        return WatermarkDetectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(
        self,
    ) -> WatermarkDetectionsResourceWithStreamingResponse:
        return WatermarkDetectionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        text: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WatermarkDetection:
        """Check whether text contains the Fireworks watermark."""
        return self._post(
            (
                "/v1/watermark/detect"
                if self._client._base_url_overridden
                else "https://api.fireworks.ai/inference/v1/watermark/detect"
            ),
            body=maybe_transform(
                {"text": text},
                watermark_detection_create_params.WatermarkDetectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=WatermarkDetection,
        )


class AsyncWatermarkDetectionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWatermarkDetectionsResourceWithRawResponse:
        return AsyncWatermarkDetectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(
        self,
    ) -> AsyncWatermarkDetectionsResourceWithStreamingResponse:
        return AsyncWatermarkDetectionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        text: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WatermarkDetection:
        """Check whether text contains the Fireworks watermark."""
        return await self._post(
            (
                "/v1/watermark/detect"
                if self._client._base_url_overridden
                else "https://api.fireworks.ai/inference/v1/watermark/detect"
            ),
            body=await async_maybe_transform(
                {"text": text},
                watermark_detection_create_params.WatermarkDetectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=WatermarkDetection,
        )


class WatermarkDetectionsResourceWithRawResponse:
    def __init__(self, watermark_detections: WatermarkDetectionsResource) -> None:
        self._watermark_detections = watermark_detections
        self.create = to_raw_response_wrapper(watermark_detections.create)


class AsyncWatermarkDetectionsResourceWithRawResponse:
    def __init__(self, watermark_detections: AsyncWatermarkDetectionsResource) -> None:
        self._watermark_detections = watermark_detections
        self.create = async_to_raw_response_wrapper(watermark_detections.create)


class WatermarkDetectionsResourceWithStreamingResponse:
    def __init__(self, watermark_detections: WatermarkDetectionsResource) -> None:
        self._watermark_detections = watermark_detections
        self.create = to_streamed_response_wrapper(watermark_detections.create)


class AsyncWatermarkDetectionsResourceWithStreamingResponse:
    def __init__(self, watermark_detections: AsyncWatermarkDetectionsResource) -> None:
        self._watermark_detections = watermark_detections
        self.create = async_to_streamed_response_wrapper(watermark_detections.create)
