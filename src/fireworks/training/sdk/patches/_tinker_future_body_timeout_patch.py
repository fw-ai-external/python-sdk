"""Bound Tinker future response-body reads for Fireworks training clients.

Tinker 0.22.7 passes a 45-second timeout to pyqwest, but pyqwest stops that
timer when response headers arrive. A stalled result body can therefore keep
``APIFuture`` blocked until an infrastructure timeout closes the connection.

This downstream compatibility patch reads the complete retrieve response with
separate header and body deadlines. Body timeout and transport failures enter
Tinker's existing same-future retry path, so the original forward operation is
not replayed. Remove this patch when the pinned Tinker version has equivalent
native behavior.
"""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any, cast

import httpx
import orjson
import tinker
import tinker.lib.api_future_impl as api_future_impl
from tinker._response import async_to_streamed_response_wrapper

_HEADER_TIMEOUT_SECONDS = 45.0
_BODY_TIMEOUT_SECONDS = 45.0


def _make_fetch_via_rest(*, header_timeout_seconds: float, body_timeout_seconds: float):
    if header_timeout_seconds <= 0 or body_timeout_seconds <= 0:
        raise ValueError("Tinker future retrieve timeouts must be positive")

    async def _fetch_via_rest(self, state, iteration):
        headers = {
            "X-Tinker-Request-Iteration": str(iteration),
            "X-Tinker-Request-Type": self.request_type,
        }
        if self.model_cls in api_future_impl.PROTO_SUPPORTED_TYPES:
            headers["Accept"] = "application/x-protobuf, application/json"
        if iteration == 0:
            headers["X-Tinker-Create-Promise-Roundtrip-Time"] = str(self.request_queue_roundtrip_time)

        async def _retrieve_response():
            with self.holder.aclient(api_future_impl.ClientConnectionPoolType.RETRIEVE_PROMISE) as client:
                retrieve_streaming = async_to_streamed_response_wrapper(client.futures.retrieve)
                async with retrieve_streaming(
                    request=api_future_impl.FutureRetrieveRequest(
                        request_id=self.request_id,
                        allow_metadata_only=state.allow_metadata_only,
                    ),
                    timeout=header_timeout_seconds,
                    extra_headers=headers,
                    max_retries=0,
                ) as response:
                    body = await asyncio.wait_for(response.read(), timeout=body_timeout_seconds)
                    if "application/x-protobuf" in response.headers.get("content-type", ""):
                        return api_future_impl._SuccessProto(proto_bytes=body)
                    return cast(dict[str, Any], orjson.loads(body))

        try:
            # The generated client may consume a non-2xx body before yielding
            # the streaming response, so retain a combined outer safety bound.
            result = await asyncio.wait_for(
                _retrieve_response(),
                timeout=header_timeout_seconds + body_timeout_seconds,
            )
        except tinker.APIStatusError as exc:
            return api_future_impl._rest_status_error_to_transport_error(exc)
        except tinker.APIConnectionError as exc:
            return api_future_impl._TransportError(
                kind=api_future_impl._TransportErrorKind.RETRY_WITH_BACKOFF,
                status_code=0,
                detail=str(exc),
                exception=exc,
                event_name="connection_error",
            )
        except (asyncio.TimeoutError, httpx.TransportError) as exc:
            return api_future_impl._TransportError(
                kind=api_future_impl._TransportErrorKind.RETRY_WITH_BACKOFF,
                status_code=0,
                detail=(
                    "Timed out or lost the connection while retrieving future "
                    f"{self.request_id}: {type(exc).__name__}: {exc}"
                ),
                exception=exc,
                event_name="connection_error",
            )

        if isinstance(result, api_future_impl._SuccessProto):
            return result
        result_dict: Any = result

        if result_dict.get("type") == "try_again":
            queue_state = result_dict.get("queue_state") or ""
            return api_future_impl._TryAgain(
                queue_state=api_future_impl._rest_queue_state_to_enum(queue_state),
                queue_state_reason=result_dict.get("queue_state_reason"),
            )
        if result_dict.get("status") == "complete_metadata":
            return api_future_impl._MetadataOnly(payload_size=result_dict.get("response_payload_size") or 0)
        if "error" in result_dict:
            error_category = api_future_impl.RequestErrorCategory.Unknown
            with contextlib.suppress(Exception):
                error_category = api_future_impl.RequestErrorCategory(result_dict.get("category"))
            return api_future_impl._Failed(
                error_message=result_dict["error"],
                error_category=error_category,
            )
        return api_future_impl._SuccessJson(result_dict=result_dict)

    _fetch_via_rest._fireworks_body_timeout_patch = True
    return _fetch_via_rest


def _apply_tinker_future_body_timeout_patch() -> bool:
    current = api_future_impl._APIFuture._fetch_via_rest
    if getattr(current, "_fireworks_body_timeout_patch", False):
        return False
    if hasattr(api_future_impl, "_RETRIEVE_FUTURE_BODY_TIMEOUT_SECONDS"):
        # A future pinned Tinker may carry the native implementation. Do not
        # replace it with the downstream compatibility patch.
        return False
    api_future_impl._APIFuture._fetch_via_rest = _make_fetch_via_rest(
        header_timeout_seconds=_HEADER_TIMEOUT_SECONDS,
        body_timeout_seconds=_BODY_TIMEOUT_SECONDS,
    )
    return True


_apply_tinker_future_body_timeout_patch()
