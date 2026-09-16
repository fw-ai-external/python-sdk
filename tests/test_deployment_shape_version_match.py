# Tests for the hand-written match methods on DeploymentShapeVersionsResource.
# Request/response shape is pinned against
# POST /v1/accounts/{account_id}/deploymentShapeVersions:match (PR #47681).
#
# These methods are hand-written in generated style (Stainless codegen is
# currently unwired, PR #26426). match_for_model() has no OpenAPI counterpart,
# so if generator-driven regeneration is ever restored it must be re-added by
# hand along with its tests; see the module top note in
# src/fireworks/resources/deployment_shape_versions.py.

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from fireworks import Fireworks, AsyncFireworks
from fireworks.types import DeploymentShapeVersionMatchResponse

MATCH_PATH = "/v1/accounts/test-account/deploymentShapeVersions:match"


def _make_client(handler: Any) -> Fireworks:
    return Fireworks(
        api_key="test-key",
        base_url="http://test.local",
        account_id="test-account",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def _make_async_client(handler: Any) -> AsyncFireworks:
    return AsyncFireworks(
        api_key="test-key",
        base_url="http://test.local",
        account_id="test-account",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )


def _match_response() -> dict[str, Any]:
    return {
        "deploymentShapeVersions": [
            {
                "name": "accounts/fireworks/deploymentShapes/g4-31b-a100/versions/3",
                "validated": True,
                "latestValidated": True,
                "snapshot": {
                    "name": "accounts/fireworks/deploymentShapes/g4-31b-a100",
                    "baseModel": "accounts/fireworks/models/gemma-4-31b-it",
                    "acceleratorType": "NVIDIA_A100_80GB",
                    "acceleratorCount": 4,
                },
            }
        ],
        "totalSize": 1,
    }


class TestMatch:
    def test_method_match_request_shape(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json=_match_response())

        client = _make_client(handler)
        response = client.deployment_shape_versions.match(
            create_deployment_request={
                "parent": "accounts/test-account",
                "deployment": {
                    "base_model": "accounts/fireworks/models/gemma-4-31b-it",
                    "enable_addons": True,
                },
            },
        )

        assert requests[0].method == "POST"
        assert requests[0].url.path == MATCH_PATH
        assert json.loads(requests[0].content) == {
            "createDeploymentRequest": {
                "parent": "accounts/test-account",
                "deployment": {
                    "baseModel": "accounts/fireworks/models/gemma-4-31b-it",
                    "enableAddons": True,
                },
            }
        }
        assert isinstance(response, DeploymentShapeVersionMatchResponse)
        assert response.total_size == 1
        assert response.deployment_shape_versions is not None
        version = response.deployment_shape_versions[0]
        assert version.name == "accounts/fireworks/deploymentShapes/g4-31b-a100/versions/3"
        assert version.snapshot is not None
        assert version.snapshot.base_model == "accounts/fireworks/models/gemma-4-31b-it"
        assert version.snapshot.accelerator_count == 4

    def test_method_match_requires_account_id(self) -> None:
        client = Fireworks(api_key="test-key", base_url="http://test.local")
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id`"):
            client.deployment_shape_versions.match(
                create_deployment_request={
                    "parent": "accounts/test-account",
                    "deployment": {"base_model": "accounts/fireworks/models/gemma-4-31b-it"},
                },
                account_id="",
            )

    def test_method_match_account_id_client_level_fallback(self) -> None:
        # No account_id on the client either: the default-resolution path must
        # raise rather than send an empty path segment.
        client = Fireworks(api_key="test-key", base_url="http://test.local")
        with pytest.raises(ValueError, match=r"account_id"):
            client.deployment_shape_versions.match(
                create_deployment_request={
                    "parent": "accounts/test-account",
                    "deployment": {"base_model": "accounts/fireworks/models/gemma-4-31b-it"},
                },
            )

    def test_method_match_tolerates_extra_response_fields(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            # A future server field addition must not break parsing.
            return httpx.Response(
                200,
                json={
                    "deploymentShapeVersions": [],
                    "totalSize": 0,
                    "someFutureField": {"nested": True},
                },
            )

        client = _make_client(handler)
        response = client.deployment_shape_versions.match(
            create_deployment_request={
                "parent": "accounts/test-account",
                "deployment": {"base_model": "accounts/fireworks/models/gemma-4-31b-it"},
            },
        )

        assert response.deployment_shape_versions == []
        assert response.total_size == 0

    def test_raw_response_match(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_match_response())

        client = _make_client(handler)
        response = client.deployment_shape_versions.with_raw_response.match(
            create_deployment_request={
                "parent": "accounts/test-account",
                "deployment": {"base_model": "accounts/fireworks/models/gemma-4-31b-it"},
            },
        )

        assert response.is_closed is True
        parsed = response.parse()
        assert isinstance(parsed, DeploymentShapeVersionMatchResponse)
        assert parsed.total_size == 1


class TestMatchForModel:
    def test_request_construction_base_model(self) -> None:
        payloads: list[dict[str, Any]] = []
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            payloads.append(json.loads(request.content))
            return httpx.Response(200, json=_match_response())

        client = _make_client(handler)
        response = client.deployment_shape_versions.match_for_model("accounts/fireworks/models/gemma-4-31b-it")

        assert requests[0].url.path == MATCH_PATH
        # enable_addons defaults to False and is still sent so the server
        # sees an explicit, match-relevant value.
        assert payloads[0] == {
            "createDeploymentRequest": {
                "parent": "accounts/test-account",
                "deployment": {
                    "baseModel": "accounts/fireworks/models/gemma-4-31b-it",
                    "enableAddons": False,
                },
            }
        }
        assert isinstance(response, DeploymentShapeVersionMatchResponse)
        assert response.deployment_shape_versions is not None

    def test_peft_addon_name_passed_through_untouched(self) -> None:
        payloads: list[dict[str, Any]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            payloads.append(json.loads(request.content))
            return httpx.Response(200, json=_match_response())

        client = _make_client(handler)
        addon = "accounts/palo-alto-networks/models/sft-gemma-4-31b-it-clickfix"
        client.deployment_shape_versions.match_for_model(addon, enable_addons=True)

        # The server resolves PEFT bases; the client must not rewrite the name.
        assert payloads[0]["createDeploymentRequest"]["deployment"]["baseModel"] == addon
        assert payloads[0]["createDeploymentRequest"]["deployment"]["enableAddons"] is True

    def test_zero_match_result(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"deploymentShapeVersions": [], "totalSize": 0})

        client = _make_client(handler)
        response = client.deployment_shape_versions.match_for_model("accounts/fireworks/models/gemma-4-31b-it")

        assert isinstance(response, DeploymentShapeVersionMatchResponse)
        assert response.deployment_shape_versions == []
        assert response.total_size == 0


class TestAsyncMatch:
    async def test_method_match_request_shape(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json=_match_response())

        async_client = _make_async_client(handler)
        response = await async_client.deployment_shape_versions.match(
            create_deployment_request={
                "parent": "accounts/test-account",
                "deployment": {"base_model": "accounts/fireworks/models/gemma-4-31b-it"},
            },
        )

        assert requests[0].method == "POST"
        assert requests[0].url.path == MATCH_PATH
        assert json.loads(requests[0].content) == {
            "createDeploymentRequest": {
                "parent": "accounts/test-account",
                "deployment": {"baseModel": "accounts/fireworks/models/gemma-4-31b-it"},
            }
        }
        assert isinstance(response, DeploymentShapeVersionMatchResponse)
        assert response.total_size == 1

    async def test_match_for_model_request_construction(self) -> None:
        payloads: list[dict[str, Any]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            payloads.append(json.loads(request.content))
            return httpx.Response(200, json=_match_response())

        async_client = _make_async_client(handler)
        response = await async_client.deployment_shape_versions.match_for_model(
            "accounts/fireworks/models/gemma-4-31b-it", enable_addons=True
        )

        assert payloads[0] == {
            "createDeploymentRequest": {
                "parent": "accounts/test-account",
                "deployment": {
                    "baseModel": "accounts/fireworks/models/gemma-4-31b-it",
                    "enableAddons": True,
                },
            }
        }
        assert isinstance(response, DeploymentShapeVersionMatchResponse)

    async def test_zero_match_result(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"deploymentShapeVersions": [], "totalSize": 0})

        async_client = _make_async_client(handler)
        response = await async_client.deployment_shape_versions.match_for_model(
            "accounts/fireworks/models/gemma-4-31b-it"
        )

        assert response.deployment_shape_versions == []
        assert response.total_size == 0

    async def test_raw_response_match(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_match_response())

        async_client = _make_async_client(handler)
        response = await async_client.deployment_shape_versions.with_raw_response.match(
            create_deployment_request={
                "parent": "accounts/test-account",
                "deployment": {"base_model": "accounts/fireworks/models/gemma-4-31b-it"},
            },
        )

        assert response.is_closed is True
        parsed = await response.parse()
        assert isinstance(parsed, DeploymentShapeVersionMatchResponse)
        assert parsed.total_size == 1
