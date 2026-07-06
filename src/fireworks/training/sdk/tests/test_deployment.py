"""Tests for fireworks.training.sdk.deployment — DeploymentManager + DeploymentSampler."""

from __future__ import annotations

import sys
import types as pytypes
import asyncio
import logging
from dataclasses import replace
from urllib.parse import parse_qs, urlparse
from unittest.mock import MagicMock

import httpx
import pytest

from fireworks.training.sdk.client import FiretitanSamplingClient
from fireworks.training.sdk.deployment import (
    ServerMetrics,
    DeploymentInfo,
    DeploymentConfig,
    DeploymentManager,
    DeploymentSampler,
    FixedConcurrencyController,
    AdaptiveConcurrencyController,
    DeploymentSamplerTimeoutError,
    _SSETruncationError,
    _deployment_hot_load_trainer_job,
)
from fireworks.training.sdk._rest_client import _should_verify_ssl


@pytest.fixture
def mgr():
    manager = DeploymentManager(
        api_key="test-key",
        base_url="https://api.example.com",
        inference_url="https://inference.example.com",
        hotload_api_url="https://hotload.example.com",
        additional_headers={"X-Secret": "s"},
    )
    manager._account_id = "test-acct"
    yield manager
    manager.close()


@pytest.fixture
def deploy_config():
    return DeploymentConfig(
        deployment_id="dep-1",
        base_model="accounts/test/models/qwen3-1p7b",
        region="US_OHIO_1",
    )


def _make_mock_tokenizer(return_ids=None):
    tok = MagicMock()
    tok.apply_chat_template.return_value = return_ids or [1, 2, 3]
    # Integer stop IDs are converted to strings via decode for the completions
    # API (token-in, string-stop). Map id -> "<id>" so tests can assert on it.
    def _decode(ids, **_kwargs):
        return f"<{ids[0]}>"

    tok.decode.side_effect = _decode
    return tok


def _make_sampler(**kwargs):
    defaults = dict(
        inference_url="https://api.example.com",
        model="m",
        api_key="key",
        tokenizer=_make_mock_tokenizer(),
    )
    defaults.update(kwargs)
    return DeploymentSampler(**defaults)


def _query_params(path: str) -> dict[str, list[str]]:
    return parse_qs(urlparse(path).query)


def _mock_async_completions_stream(sampler, return_value):
    """Patch async_completions_stream to return a value without hitting the network."""
    async def _fake(*args, **kwargs):
        return return_value, ServerMetrics()
    sampler.async_completions_stream = _fake


def _sample_with_firetitan_client(
    sampler,
    fake_tinker,
    prompt_ids,
    *,
    num_samples=1,
    sampling_params=None,
    include_prompt_logprobs=False,
):
    client = FiretitanSamplingClient(sampler)
    try:
        return client.sample(
            prompt=fake_tinker.ModelInput.from_ints(prompt_ids),
            num_samples=num_samples,
            sampling_params=sampling_params or fake_tinker.SamplingParams(),
            include_prompt_logprobs=include_prompt_logprobs,
        ).result(timeout=5)
    finally:
        client.close()


class _FakeModelInput:
    def __init__(self, tokens):
        self._tokens = list(tokens)

    @classmethod
    def from_ints(cls, tokens):
        return cls(tokens)

    def to_ints(self):
        return list(self._tokens)


class _FakeSamplingParams:
    def __init__(
        self,
        max_tokens=None,
        seed=None,
        stop=None,
        temperature=1,
        top_k=-1,
        top_p=1,
    ):
        self.max_tokens = max_tokens
        self.seed = seed
        self.stop = stop
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p


class _FakeSampledSequence:
    def __init__(
        self,
        stop_reason,
        tokens=None,
        logprobs=None,
        _tokens_list=None,
        _logprobs_list=None,
    ):
        self.stop_reason = stop_reason
        self.tokens = tokens if tokens is not None else _tokens_list
        self.logprobs = logprobs if logprobs is not None else _logprobs_list


class _FakeSampleResponse:
    def __init__(self, sequences, prompt_logprobs=None, _prompt_logprobs_list=None):
        self.sequences = sequences
        self.prompt_logprobs = (
            prompt_logprobs
            if prompt_logprobs is not None
            else _prompt_logprobs_list
        )


@pytest.fixture
def fake_tinker(monkeypatch):
    fake_types = pytypes.SimpleNamespace(
        ModelInput=_FakeModelInput,
        SamplingParams=_FakeSamplingParams,
        SampledSequence=_FakeSampledSequence,
        SampleResponse=_FakeSampleResponse,
    )
    monkeypatch.setitem(sys.modules, "tinker", pytypes.SimpleNamespace(types=fake_types))
    return fake_types


# ---------------------------------------------------------------------------
# _should_verify_ssl
# ---------------------------------------------------------------------------


class TestShouldVerifySsl:
    def test_https_domain(self):
        assert _should_verify_ssl("https://api.fireworks.ai") is True

    def test_http_no_verify(self):
        assert _should_verify_ssl("http://203.0.113.10:8083") is False

    def test_https_ip_no_verify(self):
        assert _should_verify_ssl("https://203.0.113.10:8083") is False

    def test_https_localhost(self):
        assert _should_verify_ssl("https://127.0.0.1:8080") is False

    def test_https_real_domain(self):
        assert _should_verify_ssl("https://example.com") is True


# ---------------------------------------------------------------------------
# _parse_deployment_info
# ---------------------------------------------------------------------------


class TestParseDeploymentInfo:
    def test_all_fields_present(self, mgr):
        data = {
            "name": "accounts/a/deployments/d",
            "state": "READY",
            "deploymentShape": "accounts/a/deploymentShapes/s/versions/v",
        }
        info = mgr._parse_deployment_info("d", data)
        assert info.deployment_id == "d"
        assert info.state == "READY"
        assert info.deployment_shape_version == "accounts/a/deploymentShapes/s/versions/v"

    def test_missing_shape(self, mgr):
        data = {"name": "accounts/a/deployments/d", "state": "CREATING"}
        info = mgr._parse_deployment_info("d", data)
        assert info.deployment_shape_version is None

    def test_state_override_preserves_other_metadata(self, mgr):
        data = {
            "name": "accounts/a/deployments/d",
            "state": "CREATING",
            "deploymentShape": "accounts/a/deploymentShapes/s/versions/v",
        }

        info = mgr._parse_deployment_info("d", data, state="READY")

        assert info.state == "READY"
        assert info.name == "accounts/a/deployments/d"
        assert info.deployment_shape_version == "accounts/a/deploymentShapes/s/versions/v"


# ---------------------------------------------------------------------------
# Deployment creation
# ---------------------------------------------------------------------------


class TestCreateDeployment:
    def test_create_posts_correct_path(self, mgr, deploy_config):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {
            "name": "accounts/test-acct/deployments/dep-1",
            "state": "CREATING",
        }
        mgr._post = MagicMock(return_value=resp)
        mgr._create_deployment(deploy_config)
        path = mgr._post.call_args[0][0]
        body = mgr._post.call_args[1]["json"]
        assert "/deployments" in path
        assert body["description"] == "Fireworks training deployment"
        assert body["forTraining"] is False
        assert body["enableHotLoad"] is True

    def test_create_can_mark_deployment_as_training_owned(self, deploy_config):
        body = DeploymentManager._build_deployment_body(
            replace(deploy_config, for_training=True)
        )

        assert body["forTraining"] is True
        assert body["enableHotLoad"] is True

    def test_create_can_disable_hotload(self, mgr, deploy_config):
        body = DeploymentManager._build_deployment_body(
            replace(deploy_config, enable_hot_load=False)
        )

        assert body["enableHotLoad"] is False
        assert body["forTraining"] is False

    def test_create_omits_placement_when_region_unset(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {
            "name": "accounts/test-acct/deployments/dep-1",
            "state": "CREATING",
        }
        mgr._post = MagicMock(return_value=resp)

        mgr._create_deployment(
            DeploymentConfig(
                deployment_id="dep-1",
                base_model="accounts/test/models/qwen3-1p7b",
            )
        )

        body = mgr._post.call_args[1]["json"]
        assert "placement" not in body

    def _create_resp(self):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {
            "name": "accounts/test-acct/deployments/dep-1",
            "state": "CREATING",
        }
        return resp

    def test_hotload_trainer_job_does_not_resolve_region_client_side(self, mgr):
        mgr._get = MagicMock(side_effect=AssertionError("trainer region should be resolved by control plane"))
        mgr._post = MagicMock(return_value=self._create_resp())

        mgr._create_deployment(
            DeploymentConfig(
                deployment_id="dep-1",
                base_model="accounts/test/models/qwen3-1p7b",
                hot_load_trainer_job="accounts/test-acct/rlorTrainerJobs/job-1",
            )
        )

        mgr._get.assert_not_called()
        body = mgr._post.call_args[1]["json"]
        assert "placement" not in body

    def test_hotload_explicit_region_is_sent_for_server_validation(self, mgr):
        mgr._get = MagicMock(side_effect=AssertionError("trainer region should be resolved by control plane"))
        mgr._post = MagicMock(return_value=self._create_resp())

        mgr._create_deployment(
            DeploymentConfig(
                deployment_id="dep-1",
                base_model="accounts/test/models/qwen3-1p7b",
                region="US_VIRGINIA_1",
                hot_load_trainer_job="accounts/test-acct/rlorTrainerJobs/job-1",
            )
        )

        mgr._get.assert_not_called()
        body = mgr._post.call_args[1]["json"]
        assert body["placement"] == {"region": "US_VIRGINIA_1"}

    def test_create_includes_annotations(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {
            "name": "accounts/test-acct/deployments/dep-1",
            "state": "CREATING",
        }
        mgr._post = MagicMock(return_value=resp)

        mgr._create_deployment(
            DeploymentConfig(
                deployment_id="dep-1",
                base_model="accounts/test/models/qwen3-1p7b",
                annotations={"purpose": "test"},
            )
        )

        body = mgr._post.call_args[1]["json"]
        assert body["annotations"] == {"purpose": "test"}

    def test_409_is_not_raised(self, mgr, deploy_config):
        resp = MagicMock()
        resp.status_code = 409
        resp.is_success = False
        resp.json.return_value = {"error": "already exists"}
        mgr._post = MagicMock(return_value=resp)
        # On 409, _create_deployment fetches the existing deployment instead of
        # raising; mock that follow-up GET so it doesn't hit the network.
        mgr._get_deployment = MagicMock(return_value={"name": "dep-1", "state": "READY"})
        mgr._create_deployment(deploy_config)

    def test_create_or_get_retry_reuses_deployment_id_after_conflict(
        self, mgr, deploy_config, monkeypatch
    ):
        """E2E-style retry stack test: same SDK call, same deployment ID."""
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if (
                request.method == "GET"
                and request.url.path == "/v1/accounts/test-acct/deployments/dep-1"
            ):
                get_count = sum(req.method == "GET" for req in requests)
                if get_count == 1:
                    return httpx.Response(
                        404, json={"error": "not found"}, request=request
                    )
                return httpx.Response(
                    200,
                    json={
                        "name": "accounts/test-acct/deployments/dep-1",
                        "state": "READY",
                    },
                    request=request,
                )
            if (
                request.method == "POST"
                and request.url.path == "/v1/accounts/test-acct/deployments"
            ):
                post_count = sum(req.method == "POST" for req in requests)
                if post_count == 1:
                    return httpx.Response(
                        503,
                        json={"error": {"message": "transient"}},
                        request=request,
                    )
                return httpx.Response(
                    409,
                    json={"error": {"message": "deployment ID already exists"}},
                    request=request,
                )
            return httpx.Response(404, json={"error": "not found"}, request=request)

        monkeypatch.setattr(
            "fireworks.training.sdk.errors._backoff_delay",
            lambda *_args, **_kwargs: 0.0,
        )
        monkeypatch.setattr(
            "fireworks.training.sdk.errors.time.sleep", lambda _delay: None
        )
        mgr._sync_client.close()
        mgr._sync_client = httpx.Client(transport=httpx.MockTransport(handler))

        result = mgr.create_or_get(deploy_config)

        post_requests = [req for req in requests if req.method == "POST"]
        get_requests = [req for req in requests if req.method == "GET"]
        post_deployment_ids = [
            _query_params(str(req.url))["deploymentId"][0] for req in post_requests
        ]

        assert result == DeploymentInfo(
            deployment_id="dep-1",
            name="accounts/test-acct/deployments/dep-1",
            state="READY",
            inference_model="accounts/test-acct/deployments/dep-1",
        )
        assert post_deployment_ids == ["dep-1", "dep-1"]
        assert [req.url.path for req in get_requests] == [
            "/v1/accounts/test-acct/deployments/dep-1",
            "/v1/accounts/test-acct/deployments/dep-1",
        ]


# ---------------------------------------------------------------------------
# Deployment readiness
# ---------------------------------------------------------------------------


class TestWaitForReady:
    def test_serving_creating_deployment_returns_ready_state(self, mgr):
        mgr._get_deployment = MagicMock(
            return_value={
                "name": "accounts/test-acct/deployments/dep-1",
                "state": "CREATING",
                "deploymentShape": "accounts/test-acct/deploymentShapes/s/versions/v",
            }
        )
        mgr._probe_inference = MagicMock(return_value=True)

        result = mgr.wait_for_ready(
            "dep-1",
            timeout_s=1,
            poll_interval_s=0.01,
        )

        assert result.state == "READY"
        assert result.deployment_id == "dep-1"
        assert result.name == "accounts/test-acct/deployments/dep-1"
        assert (
            result.deployment_shape_version
            == "accounts/test-acct/deploymentShapes/s/versions/v"
        )
        mgr._probe_inference.assert_called_once_with(
            "accounts/test-acct/deployments/dep-1"
        )


# ---------------------------------------------------------------------------
# Trainer reattach
# ---------------------------------------------------------------------------


class TestReattachTrainer:
    def test_deployment_hot_load_trainer_job_reads_parsed_info(self):
        deployment = DeploymentInfo(
            deployment_id="dep-1",
            name="accounts/test-acct/deployments/dep-1",
            state="READY",
            hot_load_trainer_job="accounts/test-acct/rlorTrainerJobs/job-1",
        )

        assert _deployment_hot_load_trainer_job(deployment) == "accounts/test-acct/rlorTrainerJobs/job-1"

    def test_already_attached_returns_existing(self, mgr):
        existing = DeploymentInfo(
            deployment_id="dep-1",
            name="accounts/test-acct/deployments/dep-1",
            state="READY",
            hot_load_trainer_job="accounts/test-acct/rlorTrainerJobs/job-1",
        )
        mgr.update = MagicMock()
        mgr.hotload_check_status = MagicMock()

        result = mgr.reattach_trainer(
            existing,
            base_model="accounts/test-acct/models/base",
            trainer_job_name="accounts/test-acct/rlorTrainerJobs/job-1",
            timeout_s=5,
            poll_interval_s=0.01,
        )

        assert result is existing
        mgr.update.assert_not_called()
        mgr.hotload_check_status.assert_not_called()

    def test_patch_and_waits_for_new_replica(self, mgr, monkeypatch):
        existing = DeploymentInfo(
            deployment_id="dep-1",
            name="accounts/test-acct/deployments/dep-1",
            state="READY",
            hot_load_trainer_job="accounts/test-acct/rlorTrainerJobs/old-job",
        )
        updated = DeploymentInfo(
            deployment_id="dep-1",
            name="accounts/test-acct/deployments/dep-1",
            state="READY",
            hot_load_trainer_job="accounts/test-acct/rlorTrainerJobs/job-1",
        )
        mgr.update = MagicMock(return_value=updated)
        mgr.hotload_check_status = MagicMock(
            side_effect=[
                {"replicas": [{"current_snapshot_identity": "old-pod"}]},
                {"replicas": []},
                {"replicas": [{"current_snapshot_identity": "new-pod"}]},
            ]
        )
        monkeypatch.setattr("fireworks.training.sdk.deployment.time.sleep", lambda _seconds: None)

        result = mgr.reattach_trainer(
            existing,
            base_model="accounts/test-acct/models/base",
            trainer_job_name="accounts/test-acct/rlorTrainerJobs/job-1",
            timeout_s=5,
            poll_interval_s=0.01,
        )

        assert result is updated
        mgr.update.assert_called_once_with(
            "dep-1",
            body={"hotLoadTrainerJob": "accounts/test-acct/rlorTrainerJobs/job-1"},
            update_mask="hot_load_trainer_job",
        )


# ---------------------------------------------------------------------------
# Hotload
# ---------------------------------------------------------------------------


class TestHotload:
    @staticmethod
    def _response(status_code: int, payload: dict | None = None, text: str = ""):
        resp = MagicMock()
        resp.status_code = status_code
        resp.is_success = 200 <= status_code < 300
        resp.json.return_value = payload or {}
        resp.text = text
        return resp

    def test_hotload_sends_identity(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {}
        mgr._sync_request = MagicMock(return_value=resp)

        mgr.hotload("dep-1", "accounts/test/models/m", "snap-123")
        call_kwargs = mgr._sync_request.call_args[1]
        assert call_kwargs["json"]["identity"] == "snap-123"

    def test_hotload_headers_include_additional_headers(self, mgr):
        headers = mgr._hotload_headers("dep-1", "accounts/test/models/m")
        assert headers.get("X-Secret") == "s"
        assert "Authorization" in headers
        assert "fireworks-model" in headers

    def test_hotload_incremental_metadata(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {}
        mgr._sync_request = MagicMock(return_value=resp)

        mgr.hotload(
            "dep-1", "accounts/test/models/m", "snap-2",
            incremental_snapshot_metadata={"previous_snapshot_identity": "snap-1"},
        )
        payload = mgr._sync_request.call_args[1]["json"]
        assert payload["incremental_snapshot_metadata"]["previous_snapshot_identity"] == "snap-1"

    def test_hotload_log_describes_non_delta_snapshot_with_context(self, mgr, caplog):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {}
        mgr._sync_request = MagicMock(return_value=resp)

        caplog.set_level(logging.INFO, logger="fireworks.training.sdk.deployment")
        mgr.hotload(
            "dep-1",
            "accounts/test/models/m",
            "snap-123",
        )

        assert (
            "Hotloading BASE (non-delta) snapshot 'snap-123' to deployment 'dep-1'"
            in caplog.text
        )
        assert "FULL snapshot" not in caplog.text

    def test_hotload_retries_without_reset_prompt_cache_when_rejected(self, mgr):
        unsupported = self._response(
            400,
            {"error": {"message": "Extra inputs are not permitted, field: 'reset_prompt_cache', value: True"}},
            text="Extra inputs are not permitted, field: 'reset_prompt_cache', value: True",
        )
        success = self._response(200, {})
        mgr._sync_request = MagicMock(side_effect=[unsupported, success, success])

        mgr.hotload("dep-1", "accounts/test/models/m", "snap-123")
        mgr.hotload("dep-1", "accounts/test/models/m", "snap-456")

        first_payload = mgr._sync_request.call_args_list[0].kwargs["json"]
        retry_payload = mgr._sync_request.call_args_list[1].kwargs["json"]
        second_call_payload = mgr._sync_request.call_args_list[2].kwargs["json"]

        assert first_payload["reset_prompt_cache"] is True
        assert "reset_prompt_cache" not in retry_payload
        assert "reset_prompt_cache" not in second_call_payload
        assert mgr._hotload_reset_prompt_cache_supported is False

    def test_hotload_path_sent_as_header_not_body(self, mgr):
        # ``path`` rides the ``x-fireworks-hot-load-source-url`` header so
        # the request body stays a fixed shape across serving backends
        # (some of which 400 on unknown body fields).
        resp = self._response(200)
        mgr._sync_request = MagicMock(return_value=resp)

        mgr.hotload(
            "dep-1",
            "accounts/test/models/m",
            "snap-123",
            path="gs://my-bucket/snapshots/snap-123/",
        )
        call_kwargs = mgr._sync_request.call_args[1]
        body = call_kwargs["json"]
        headers = call_kwargs["headers"]

        assert "path" not in body
        assert headers.get("x-fireworks-hot-load-source-url") == "gs://my-bucket/snapshots/snap-123/"

    def test_hotload_omits_source_url_header_when_no_path(self, mgr):
        resp = self._response(200)
        mgr._sync_request = MagicMock(return_value=resp)

        mgr.hotload("dep-1", "accounts/test/models/m", "snap-123")
        headers = mgr._sync_request.call_args[1]["headers"]
        assert "x-fireworks-hot-load-source-url" not in headers

    def test_hotload_and_wait_forwards_path(self, mgr):
        resp = self._response(200)
        mgr._sync_request = MagicMock(return_value=resp)
        mgr.wait_for_hotload = MagicMock(return_value=True)

        ok = mgr.hotload_and_wait(
            "dep-1",
            "accounts/test/models/m",
            "snap-123",
            path="gs://my-bucket/snapshots/snap-123/",
        )
        assert ok is True
        headers = mgr._sync_request.call_args[1]["headers"]
        assert headers.get("x-fireworks-hot-load-source-url") == "gs://my-bucket/snapshots/snap-123/"


# ---------------------------------------------------------------------------
# wait_for_hotload
# ---------------------------------------------------------------------------


class TestWaitForHotload:
    def test_immediate_success(self, mgr):
        mgr.hotload_check_status = MagicMock(return_value={
            "replicas": [{
                "current_snapshot_identity": "snap-1",
                "loading_state": {"stage": "idle"},
                "readiness": True,
            }]
        })
        result = mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5, poll_interval=0)
        assert result is True

    def test_timeout_returns_false(self, mgr):
        mgr.hotload_check_status = MagicMock(return_value={
            "replicas": [{
                "identity": None,
                "stage": "downloading",
                "ready": False,
            }]
        })
        result = mgr.wait_for_hotload("dep-1", "m", "snap-x", timeout_seconds=0.01, poll_interval=0.005)
        assert result is False

    def test_loaded_adapters_status_loaded_signals_completion(self, mgr):
        # Some serving backends report multi-adapter completion via a
        # per-adapter ``loaded_adapters`` array rather than a single
        # ``current_snapshot_identity``. Both shapes must be accepted.
        mgr.hotload_check_status = MagicMock(return_value={
            "replicas": [{
                "current_snapshot_identity": None,
                "readiness": True,
                "loading_state": {"stage": "idle"},
                "loaded_adapters": [
                    {"identity": "snap-1", "status": "loaded"},
                ],
            }]
        })
        result = mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5, poll_interval=0)
        assert result is True

    def test_loaded_adapters_non_loaded_status_does_not_complete(self, mgr):
        # A non-``loaded`` status (e.g. ``loading``, ``failed``) must NOT
        # terminate the wait — the SDK keeps polling until either
        # ``status: loaded`` shows up or the timeout fires.
        mgr.hotload_check_status = MagicMock(return_value={
            "replicas": [{
                "current_snapshot_identity": None,
                "readiness": True,
                "loading_state": {"stage": "downloading"},
                "loaded_adapters": [
                    {"identity": "snap-1", "status": "loading"},
                ],
            }]
        })
        result = mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=0.01, poll_interval=0.005)
        assert result is False

    def test_error_status_records_client_snapshot_state(self, mgr):
        mgr.hotload_check_status = MagicMock(return_value={
            "replicas": [{
                "current_snapshot_identity": "old-snap",
                "readiness": False,
                "loading_state": {
                    "stage": "error",
                    "target_snapshot_identity": "snap-1",
                },
            }]
        })

        result = mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5, poll_interval=0)

        assert result is False
        assert mgr.last_hotload_error_message is not None
        assert "reported an error for the requested snapshot" in mgr.last_hotload_error_message
        assert "Expected client snapshot: snap-1" in mgr.last_hotload_error_message
        assert "current deployment snapshot: old-snap" in mgr.last_hotload_error_message
        assert "Use the Fireworks training cookbook skill's hotload recovery self-check" in mgr.last_hotload_error_message
        assert "reattach or recreate a stale deployment" in mgr.last_hotload_error_message
        assert "full-parameter training" in mgr.last_hotload_error_message
        assert "for LoRA, fix deployment attachment" in mgr.last_hotload_error_message
        assert "First search the Fireworks training cookbook skill" in mgr.last_hotload_error_message
        assert "https://github.com/fw-ai/cookbook" in mgr.last_hotload_error_message


# ---------------------------------------------------------------------------
# _extract_logprobs
# ---------------------------------------------------------------------------


class TestExtractLogprobs:
    def test_modern_structured_format(self):
        choice = {
            "logprobs": {
                "content": [
                    {"logprob": -0.5, "sampling_logprob": -0.6},
                    {"logprob": -1.2, "sampling_logprob": -1.3},
                ]
            }
        }
        lps = DeploymentSampler._extract_logprobs(choice)
        assert lps == [-0.5, -1.2]
        sampling_lps = DeploymentSampler._extract_logprobs(
            choice, field="sampling_logprob",
        )
        assert sampling_lps == [-0.6, -1.3]

    def test_none_field_is_missing_unless_allowed(self):
        choice = {"logprobs": {"content": [{"logprob": None}]}}
        assert DeploymentSampler._extract_logprobs(choice) is None
        assert DeploymentSampler._extract_logprobs(
            choice, allow_none=True,
        ) == [None]

    def test_none_if_absent(self):
        assert DeploymentSampler._extract_logprobs({}) is None
        assert DeploymentSampler._extract_logprobs({"logprobs": None}) is None
        assert DeploymentSampler._extract_logprobs({"logprobs": {}}) is None

    def test_empty_content(self):
        assert DeploymentSampler._extract_logprobs({"logprobs": {"content": []}}) is None



# ---------------------------------------------------------------------------
# DeploymentManager.warmup — token-in warmup payload
# ---------------------------------------------------------------------------


class TestWarmup:
    def test_uses_token_prompt(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        mgr._sync_request = MagicMock(return_value=resp)

        assert mgr.warmup("accounts/test/deployments/dep-1", max_retries=1) is True
        payload = mgr._sync_request.call_args[1]["json"]
        assert isinstance(payload["prompt"], list)
        assert all(isinstance(tok, int) for tok in payload["prompt"])

    def test_warmup_headers_include_additional(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        mgr._sync_request = MagicMock(return_value=resp)

        mgr.warmup("accounts/test/deployments/dep-1", max_retries=1)
        headers = mgr._sync_request.call_args[1]["headers"]
        assert headers.get("X-Secret") == "s"


# ---------------------------------------------------------------------------
# DeploymentSampler.sample_with_tokens — client-side tokenization
# ---------------------------------------------------------------------------


class TestSampleWithTokens:
    def test_basic_sample(self):
        prompt_ids = [1, 100, 200]
        completion_ids = [400, 500]

        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "hello world",
                "finish_reason": "stop",
                "raw_output": {"completion_token_ids": completion_ids},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}],
        ))

        assert len(results) == 1
        c = results[0]
        assert c.text == "hello world"
        assert c.full_tokens == prompt_ids + completion_ids
        assert c.prompt_len == len(prompt_ids)
        assert c.completion_len == len(completion_ids)
        assert c.finish_reason == "stop"
        sampler.close()

    def test_tokenizer_called_with_messages(self):
        tok = _make_mock_tokenizer([1, 2, 3])
        sampler = _make_sampler(tokenizer=tok)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "ok", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
            }]
        })

        messages = [{"role": "user", "content": "test"}]
        asyncio.run(sampler.sample_with_tokens(messages=messages))
        tok.apply_chat_template.assert_called_once_with(
            messages, tokenize=True, add_generation_prompt=True, return_dict=False,
        )
        sampler.close()

    def test_missing_completion_token_ids_raises(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2, 3]))
        _mock_async_completions_stream(sampler, {
            "choices": [{"text": "ok", "finish_reason": "stop", "raw_output": {}}]
        })

        with pytest.raises(RuntimeError, match="missing completion_token_ids"):
            asyncio.run(sampler.sample_with_tokens(
                messages=[{"role": "user", "content": "hi"}],
            ))
        sampler.close()

    def test_echo_strips_verified_prefix(self):
        prompt_ids = [1, 100, 200]
        echoed_completion_ids = [1, 100, 200, 400, 500]

        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "gen", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": echoed_completion_ids},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}], echo=True,
        ))

        assert len(results) == 1
        c = results[0]
        assert c.full_tokens == prompt_ids + [400, 500]
        assert c.completion_len == 2
        assert c.logprobs_echoed is False
        sampler.close()

    def test_echo_logprobs_aligned(self):
        prompt_ids = [1, 100, 200]
        echoed_ids = [1, 100, 200, 400, 500]

        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "gen", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": echoed_ids},
                "logprobs": {"content": [
                    {"logprob": 0.0, "sampling_logprob": None},
                    {"logprob": -0.1, "sampling_logprob": -0.11},
                    {"logprob": -0.2, "sampling_logprob": -0.21},
                    {"logprob": -0.3, "sampling_logprob": -0.31},
                    {"logprob": -0.4, "sampling_logprob": -0.41},
                ]},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}],
            echo=True, logprobs=True,
        ))

        c = results[0]
        assert c.logprobs_echoed is True
        assert c.inference_logprobs == [-0.1, -0.2, -0.3, -0.4]
        assert c.sampling_logprobs == [-0.11, -0.21, -0.31, -0.41]
        sampler.close()

    def test_max_seq_len_pre_filter(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2, 3, 4, 5]))
        _mock_async_completions_stream(sampler, {"choices": []})

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}], max_seq_len=5,
        ))
        assert results == []
        sampler.close()

    def test_max_seq_len_post_filter(self):
        prompt_ids = [1, 2]
        long_completion = list(range(100, 200))

        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "long", "finish_reason": "length",
                "raw_output": {"completion_token_ids": long_completion},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}], max_seq_len=50,
        ))
        assert len(results) == 0
        sampler.close()

    def test_logprobs_extracted(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2]))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "hi", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {
                    "content": [{"logprob": -1.5, "sampling_logprob": -1.6}]
                },
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "x"}], logprobs=True,
        ))
        assert results[0].inference_logprobs == [-1.5]
        assert results[0].sampling_logprobs == [-1.6]
        sampler.close()

    def test_legacy_logprobs_fall_back_to_raw_for_full_distribution_sampling(self, caplog):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2]))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "hi", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {"content": [{"logprob": -1.5}]},
            }]
        })

        with caplog.at_level(logging.WARNING):
            results = asyncio.run(sampler.sample_with_tokens(
                messages=[{"role": "user", "content": "x"}], logprobs=True,
            ))
        assert results[0].inference_logprobs == [-1.5]
        assert results[0].sampling_logprobs == [-1.5]
        assert "omitted logprobs.content[].sampling_logprob" in caplog.text
        assert "temperature=1, top_p=1, top_k=0" in caplog.text
        assert "temperature, top_p, or top_k change the sampling distribution" in caplog.text
        assert "train/inference logprob drift" in caplog.text
        sampler.close()

    def test_legacy_logprobs_do_not_fall_back_when_sampling_distribution_changes(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2]))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "hi", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {"content": [{"logprob": -1.5}]},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "x"}],
            logprobs=True,
            temperature=0.7,
        ))
        assert results[0].inference_logprobs == [-1.5]
        assert results[0].sampling_logprobs == [None]
        sampler.close()

    def test_routing_matrices_extracted(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2]))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "hi", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {"content": [{"logprob": -0.5, "routing_matrix": "AQID"}]},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "x"}],
            include_routing_matrix=True,
        ))
        assert results[0].routing_matrices == ["AQID"]
        sampler.close()


# ---------------------------------------------------------------------------
# Default parameter values
# ---------------------------------------------------------------------------


class TestDefaultValues:
    def test_default_temperature_is_1(self):
        import inspect
        sig = inspect.signature(DeploymentSampler.async_completions_stream)
        assert sig.parameters["temperature"].default == 1.0
        sig2 = inspect.signature(DeploymentSampler.sample_with_tokens)
        assert sig2.parameters["temperature"].default == 1.0
        sig3 = inspect.signature(DeploymentSampler.sample_with_prompt_tokens)
        assert sig3.parameters["temperature"].default == 1.0


# ---------------------------------------------------------------------------
# DeploymentSampler.sample_with_prompt_tokens — pre-tokenized prompt entry point
# ---------------------------------------------------------------------------


class TestSampleWithPromptTokens:
    def test_basic_sample(self, fake_tinker):
        prompt_ids = [10, 20, 30]
        completion_ids = [40, 50]

        sampler = _make_sampler(tokenizer=None)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "out",
                "finish_reason": "stop",
                "raw_output": {"completion_token_ids": completion_ids},
            }]
        })

        results = asyncio.run(sampler.sample_with_prompt_tokens(prompt_ids))

        assert len(results) == 1
        c = results[0]
        assert c.full_tokens[: len(prompt_ids)] == prompt_ids
        assert c.full_tokens[len(prompt_ids) :] == completion_ids
        assert c.prompt_len == len(prompt_ids)
        assert c.finish_reason == "stop"
        sampler.close()

        sampler = _make_sampler(tokenizer=None)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "out",
                "finish_reason": "stop",
                "raw_output": {"completion_token_ids": completion_ids},
                "logprobs": {"content": [
                    {"logprob": -0.4, "sampling_logprob": -0.41},
                    {"logprob": -0.5, "sampling_logprob": -0.51},
                ]},
            }]
        })
        response = _sample_with_firetitan_client(
            sampler,
            fake_tinker,
            prompt_ids,
            sampling_params=fake_tinker.SamplingParams(max_tokens=1024),
        )
        assert len(response.sequences) == 1
        assert response.sequences[0].tokens == completion_ids
        assert response.sequences[0].stop_reason == "stop"
        assert response.prompt_logprobs is None

    def test_does_not_call_apply_chat_template(self, fake_tinker):
        tok = MagicMock()
        sampler = _make_sampler(tokenizer=tok)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "out", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
            }]
        })

        asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        tok.apply_chat_template.assert_not_called()
        sampler.close()

        tok = MagicMock()
        sampler = _make_sampler(tokenizer=tok)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "out", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {"content": [{"logprob": -0.7, "sampling_logprob": -0.8}]},
            }]
        })
        _sample_with_firetitan_client(
            sampler,
            fake_tinker,
            [1, 2, 3],
            sampling_params=fake_tinker.SamplingParams(max_tokens=1),
        )
        tok.apply_chat_template.assert_not_called()

    def test_stop_str_shape_preserved(self, fake_tinker):
        sampler = _make_sampler(tokenizer=None)
        captured: dict[str, object] = {}

        async def _fake_stream(*args, **kwargs):
            captured["stop"] = kwargs.get("stop")
            return {
                "choices": [{
                    "text": "out", "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": [99]},
                    "logprobs": {"content": [{"logprob": -0.7, "sampling_logprob": -0.8}]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake_stream

        stop_strs = ["</answer>", "<|end|>"]
        asyncio.run(sampler.sample_with_prompt_tokens([1, 2], stop=stop_strs))
        assert captured["stop"] == stop_strs
        assert all(isinstance(s, str) for s in captured["stop"])  # type: ignore[arg-type]
        sampler.close()

        sampler = _make_sampler(tokenizer=None)
        captured = {}
        sampler.async_completions_stream = _fake_stream
        _sample_with_firetitan_client(
            sampler,
            fake_tinker,
            [1, 2],
            sampling_params=fake_tinker.SamplingParams(stop=stop_strs),
        )
        assert captured["stop"] == stop_strs
        assert all(isinstance(s, str) for s in captured["stop"])  # type: ignore[arg-type]

    def test_stop_int_converted_to_strings_via_tokenizer(self, fake_tinker):
        # The completions API takes string stop sequences, so integer stop IDs
        # are decoded to strings client-side before the request.
        sampler = _make_sampler()
        captured: dict[str, object] = {}

        async def _fake_stream(*args, **kwargs):
            captured["stop"] = kwargs.get("stop")
            return {
                "choices": [{
                    "text": "out", "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": [99]},
                    "logprobs": {"content": [{"logprob": -0.7, "sampling_logprob": -0.8}]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake_stream

        asyncio.run(sampler.sample_with_prompt_tokens([1, 2], stop=[13, 42]))
        assert captured["stop"] == ["<13>", "<42>"]
        assert all(isinstance(s, str) for s in captured["stop"])  # type: ignore[arg-type]
        sampler.close()

        sampler = _make_sampler()
        captured = {}
        sampler.async_completions_stream = _fake_stream
        _sample_with_firetitan_client(
            sampler,
            fake_tinker,
            [1, 2],
            sampling_params=fake_tinker.SamplingParams(stop=[13, 42]),
        )
        assert captured["stop"] == ["<13>", "<42>"]
        assert all(isinstance(s, str) for s in captured["stop"])  # type: ignore[arg-type]

    def test_max_seq_len_pre_filter(self):
        sampler = _make_sampler(tokenizer=None)
        _mock_async_completions_stream(sampler, {"choices": []})

        results = asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3, 4, 5], max_seq_len=5))
        assert results == []
        sampler.close()

    def test_logprobs_extracted(self, fake_tinker):
        sampler = _make_sampler(tokenizer=None)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "x", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {
                    "content": [{"logprob": -0.7, "sampling_logprob": -0.8}]
                },
            }]
        })

        results = asyncio.run(sampler.sample_with_prompt_tokens([1, 2], logprobs=True))
        assert results[0].inference_logprobs == [-0.7]
        assert results[0].sampling_logprobs == [-0.8]
        sampler.close()

        sampler = _make_sampler(tokenizer=None)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "x", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {"content": [{"logprob": -0.7, "sampling_logprob": -0.8}]},
            }]
        })
        response = _sample_with_firetitan_client(
            sampler,
            fake_tinker,
            [1, 2],
            sampling_params=fake_tinker.SamplingParams(max_tokens=1),
        )
        assert response.sequences[0].logprobs == [-0.8]

    def test_sample_falls_back_to_raw_logprobs_for_compatible_legacy_response(self, fake_tinker):
        sampler = _make_sampler(tokenizer=None)

        async def _fake_stream(*args, **kwargs):
            return {
                "choices": [{
                    "text": "x",
                    "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": [99]},
                    "logprobs": {"content": [{"logprob": -0.7}]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake_stream
        client = FiretitanSamplingClient(sampler)
        try:
            response = client.sample(
                prompt=fake_tinker.ModelInput.from_ints([1, 2]),
                num_samples=1,
                sampling_params=fake_tinker.SamplingParams(max_tokens=1),
            ).result(timeout=5)
            assert response.sequences[0].logprobs == [-0.7]
        finally:
            client.close()

    def test_sample_requires_sampling_logprobs_when_sampling_distribution_changes(self, fake_tinker):
        sampler = _make_sampler(tokenizer=None)

        async def _fake_stream(*args, **kwargs):
            return {
                "choices": [{
                    "text": "x",
                    "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": [99]},
                    "logprobs": {"content": [{"logprob": -0.7}]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake_stream
        client = FiretitanSamplingClient(sampler)
        try:
            with pytest.raises(RuntimeError, match="sampling_logprob"):
                client.sample(
                    prompt=fake_tinker.ModelInput.from_ints([1, 2]),
                    num_samples=1,
                    sampling_params=fake_tinker.SamplingParams(max_tokens=1, temperature=0.7),
                ).result(timeout=5)
        finally:
            client.close()

    def test_n_concurrent_calls(self, fake_tinker):
        sampler = _make_sampler(tokenizer=None)
        call_count = {"n": 0}

        async def _fake_stream(*args, **kwargs):
            call_count["n"] += 1
            return {
                "choices": [{
                    "text": "x", "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": [99]},
                    "logprobs": {"content": [{"logprob": -0.7, "sampling_logprob": -0.8}]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake_stream

        results = asyncio.run(sampler.sample_with_prompt_tokens([1, 2], n=4))
        assert call_count["n"] == 4
        assert len(results) == 4
        sampler.close()

        sampler = _make_sampler(tokenizer=None)
        call_count = {"n": 0}
        sampler.async_completions_stream = _fake_stream
        response = _sample_with_firetitan_client(
            sampler,
            fake_tinker,
            [1, 2],
            num_samples=4,
            sampling_params=fake_tinker.SamplingParams(max_tokens=1),
        )
        assert call_count["n"] == 4
        assert len(response.sequences) == 4


class TestFiretitanSamplingClient:
    def test_extends_tinker_sampling_client(self):
        tinker = pytest.importorskip("tinker")
        sampler = _make_sampler(tokenizer=None)
        client = FiretitanSamplingClient(sampler)
        try:
            assert issubclass(FiretitanSamplingClient, tinker.SamplingClient)
            assert isinstance(client, tinker.SamplingClient)
        finally:
            client.close()

    def test_sample_returns_tinker_response(self, fake_tinker):
        prompt_ids = [10, 20, 30]
        completion_ids = [40, 50]
        sampler = _make_sampler()
        captured = {}

        async def _fake_stream(*args, **kwargs):
            captured.update(kwargs)
            return {
                "choices": [{
                    "text": "out",
                    "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": completion_ids},
                    "logprobs": {"content": [
                        {"logprob": -0.3, "sampling_logprob": -0.31},
                        {"logprob": -0.4, "sampling_logprob": -0.41},
                    ]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake_stream
        client = FiretitanSamplingClient(sampler)
        try:
            response = client.sample(
                prompt=fake_tinker.ModelInput.from_ints(prompt_ids),
                num_samples=1,
                sampling_params=fake_tinker.SamplingParams(
                    max_tokens=2,
                    stop=[99],
                    temperature=0.7,
                    top_p=0.9,
                    top_k=10,
                    seed=123,
                ),
            ).result(timeout=5)
        finally:
            client.close()

        assert len(response.sequences) == 1
        assert response.sequences[0].tokens == completion_ids
        assert response.sequences[0].logprobs == [-0.31, -0.41]
        assert response.sequences[0].stop_reason == "stop"
        assert response.prompt_logprobs is None
        assert captured["prompt"] == prompt_ids
        assert captured["max_tokens"] == 2
        assert captured["temperature"] == 0.7
        assert captured["stop"] == ["<99>"]
        assert captured["top_p"] == 0.9
        assert captured["top_k"] == 10
        assert captured["seed"] == 123
        assert captured["logprobs"] is True

    def test_sample_splits_echo_prompt_logprobs(self, fake_tinker):
        prompt_ids = [10, 20, 30]
        completion_ids = [40, 50]
        sampler = _make_sampler(tokenizer=None)
        captured = {}

        async def _fake_stream(*args, **kwargs):
            captured.update(kwargs)
            return {
                "choices": [{
                    "text": "out",
                    "finish_reason": "length",
                    "raw_output": {"completion_token_ids": prompt_ids + completion_ids},
                    "logprobs": {"content": [
                        {"logprob": 0.0, "sampling_logprob": None},
                        {"logprob": -0.1, "sampling_logprob": None},
                        {"logprob": -0.2, "sampling_logprob": None},
                        {"logprob": -0.3, "sampling_logprob": -0.33},
                        {"logprob": -0.4, "sampling_logprob": -0.44},
                    ]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake_stream
        client = FiretitanSamplingClient(sampler)
        try:
            response = client.sample(
                prompt=fake_tinker.ModelInput.from_ints(prompt_ids),
                num_samples=1,
                sampling_params=fake_tinker.SamplingParams(max_tokens=2),
                include_prompt_logprobs=True,
            ).result(timeout=5)
        finally:
            client.close()

        assert captured["echo"] is True
        assert response.prompt_logprobs == [None, -0.1, -0.2]
        assert response.sequences[0].tokens == completion_ids
        assert response.sequences[0].logprobs == [-0.33, -0.44]
        assert response.sequences[0].stop_reason == "length"

    def test_compute_logprobs_uses_prompt_logprobs(self, fake_tinker):
        prompt_ids = [10, 20, 30]
        sampler = _make_sampler(tokenizer=None)

        async def _fake_stream(*args, **kwargs):
            return {
                "choices": [{
                    "text": "x",
                    "finish_reason": "length",
                    "raw_output": {"completion_token_ids": prompt_ids + [40]},
                    "logprobs": {"content": [
                        {"logprob": 0.0, "sampling_logprob": None},
                        {"logprob": -0.1, "sampling_logprob": None},
                        {"logprob": -0.2, "sampling_logprob": None},
                        {"logprob": -0.3, "sampling_logprob": -0.33},
                    ]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake_stream
        client = FiretitanSamplingClient(sampler)
        try:
            with pytest.warns(UserWarning, match="training_client.forward"):
                logprobs = client.compute_logprobs(
                    fake_tinker.ModelInput.from_ints(prompt_ids)
                ).result(timeout=5)
        finally:
            client.close()

        assert logprobs == [None, -0.1, -0.2]

    def test_topk_prompt_logprobs_is_explicitly_unsupported(self, fake_tinker):
        sampler = _make_sampler(tokenizer=None)
        client = FiretitanSamplingClient(sampler)
        try:
            with pytest.raises(NotImplementedError, match="topk_prompt_logprobs"):
                client.sample(
                    prompt=fake_tinker.ModelInput.from_ints([1, 2]),
                    num_samples=1,
                    sampling_params=fake_tinker.SamplingParams(max_tokens=1),
                    topk_prompt_logprobs=1,
                )
        finally:
            client.close()

    def test_topk_prompt_logprobs_async_is_explicitly_unsupported(self, fake_tinker):
        sampler = _make_sampler(tokenizer=None)
        client = FiretitanSamplingClient(sampler)
        try:
            with pytest.raises(NotImplementedError, match="topk_prompt_logprobs"):
                asyncio.run(
                    client.sample_async(
                        prompt=fake_tinker.ModelInput.from_ints([1, 2]),
                        num_samples=1,
                        sampling_params=fake_tinker.SamplingParams(max_tokens=1),
                        topk_prompt_logprobs=1,
                    )
                )
        finally:
            client.close()

    def test_close_does_not_close_loop_if_thread_join_times_out(self, monkeypatch):
        sampler = _make_sampler(tokenizer=None)
        client = FiretitanSamplingClient(sampler)

        class _FakeLoop:
            closed = False

            def is_running(self):
                return True

            def call_soon_threadsafe(self, callback, *args):
                return None

            def stop(self):
                return None

            def close(self):
                self.closed = True
                raise RuntimeError("Cannot close a running event loop")

        class _FakeThread:
            joined = False

            def is_alive(self):
                return True

            def join(self, timeout=None):
                self.joined = True

        class _FakeFuture:
            def result(self, timeout=None):
                raise TimeoutError

        def _run_coroutine_threadsafe(coro, loop):
            coro.close()
            return _FakeFuture()

        fake_loop = _FakeLoop()
        fake_thread = _FakeThread()
        client._loop = fake_loop
        client._loop_thread = fake_thread
        monkeypatch.setattr(asyncio, "run_coroutine_threadsafe", _run_coroutine_threadsafe)

        client.close()

        assert fake_thread.joined is True
        assert fake_loop.closed is False


# ---------------------------------------------------------------------------
# Regression: legacy sample_with_tokens(messages=...) still calls apply_chat_template
# ---------------------------------------------------------------------------


class TestSampleWithTokensLegacyRegression:
    def test_legacy_path_still_renders_via_chat_template(self):
        tok = _make_mock_tokenizer([7, 8, 9])
        sampler = _make_sampler(tokenizer=tok)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "ok", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [11]},
            }]
        })

        messages = [{"role": "user", "content": "hi"}]
        asyncio.run(sampler.sample_with_tokens(messages=messages))
        tok.apply_chat_template.assert_called_once_with(
            messages, tokenize=True, add_generation_prompt=True, return_dict=False,
        )
        sampler.close()


# ---------------------------------------------------------------------------
# Deployment CRUD — REST method wrappers
# ---------------------------------------------------------------------------


class TestDeploymentCrud:
    def test_get_deployment_calls_rest_get(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {"name": "n", "state": "READY"}
        mgr._get = MagicMock(return_value=resp)

        result = mgr._get_deployment("dep-1")
        path = mgr._get.call_args[0][0]
        assert "/deployments/dep-1" in path
        assert result is not None

    def test_get_deployment_returns_none_on_404(self, mgr):
        resp = MagicMock()
        resp.status_code = 404
        mgr._get = MagicMock(return_value=resp)

        result = mgr._get_deployment("dep-1")
        assert result is None

    def test_scale_to_zero_calls_rest_patch(self, mgr):
        resp = MagicMock()
        resp.is_success = True
        mgr._patch = MagicMock(return_value=resp)

        mgr.scale_to_zero("dep-1")
        path = mgr._patch.call_args[0][0]
        assert "/deployments/dep-1" in path
        body = mgr._patch.call_args[1]["json"]
        assert body["maxReplicaCount"] == 0
        assert body["minReplicaCount"] == 0


# ---------------------------------------------------------------------------
# ServerMetrics
# ---------------------------------------------------------------------------


class TestServerMetrics:
    def test_from_headers_full(self):
        headers = {
            "num-concurrent-requests": "12",
            "prefill-queue-duration": "0.250",
            "generation-queue-duration": "1.100",
            "server-time-to-first-token": "0.350",
            "cached-prompt-tokens": "128",
            "prompt-tokens": "256",
            "server-processing-time": "2.500",
        }
        m = ServerMetrics.from_headers(headers, client_ttft=0.4)
        assert m.num_concurrent_requests == 12
        assert m.prefill_queue_duration == pytest.approx(0.25)
        assert m.generation_queue_duration == pytest.approx(1.1)
        assert m.server_ttft == pytest.approx(0.35)
        assert m.cached_prompt_tokens == 128
        assert m.prompt_tokens == 256
        assert m.server_processing_time == pytest.approx(2.5)
        assert m.client_ttft == pytest.approx(0.4)

    def test_from_headers_empty(self):
        m = ServerMetrics.from_headers({})
        assert m.num_concurrent_requests is None
        assert m.prefill_queue_duration is None
        assert m.client_ttft is None

    def test_from_headers_invalid_values(self):
        headers = {"num-concurrent-requests": "bad", "prefill-queue-duration": "bad"}
        m = ServerMetrics.from_headers(headers)
        assert m.num_concurrent_requests is None
        assert m.prefill_queue_duration is None


# ---------------------------------------------------------------------------
# AdaptiveConcurrencyController
# ---------------------------------------------------------------------------


class TestAdaptiveConcurrencyController:
    def test_initial_window(self):
        ctrl = AdaptiveConcurrencyController(initial_window=16)
        assert ctrl.window_size == 16

    def test_acquire_release_basic(self):
        ctrl = AdaptiveConcurrencyController(initial_window=2)

        async def _test():
            await ctrl.acquire()
            await ctrl.acquire()
            assert ctrl._semaphore._value == 0
            ctrl.release()
            ctrl.release()
            assert ctrl._semaphore._value == 2

        asyncio.run(_test())

    def test_release_collects_but_does_not_adjust(self):
        """release() collects metrics but does NOT change the window."""
        ctrl = AdaptiveConcurrencyController(initial_window=10, ema_alpha=1.0)
        ctrl.release(ServerMetrics(prefill_queue_duration=5.0))
        assert ctrl.window_size == 10  # unchanged until step_completed()

    def test_step_completed_decrease_on_high_pq(self):
        ctrl = AdaptiveConcurrencyController(
            initial_window=10, prefill_queue_target=0.5,
            multiplicative_decrease=0.5, ema_alpha=1.0,
        )
        # Simulate a step with high prefill queue.
        for _ in range(8):
            ctrl.release(ServerMetrics(prefill_queue_duration=2.0))
        summary = ctrl.step_completed()
        assert ctrl.window_size < 10
        assert summary["avg_pq"] == pytest.approx(2.0)

    def test_step_completed_increase_on_low_pq(self):
        ctrl = AdaptiveConcurrencyController(
            initial_window=4, prefill_queue_target=1.0,
            additive_increase=2.0, ema_alpha=1.0,
        )
        for _ in range(8):
            ctrl.release(ServerMetrics(prefill_queue_duration=0.1))
        ctrl.step_completed()
        assert ctrl._window > 4.0

    def test_no_change_without_metrics(self):
        ctrl = AdaptiveConcurrencyController(initial_window=8)
        ctrl.release(None)
        ctrl.step_completed()
        assert ctrl.window_size == 8
        assert ctrl.ema_prefill_queue is None

    def test_ema_smoothing_across_steps(self):
        ctrl = AdaptiveConcurrencyController(initial_window=10, ema_alpha=0.5, prefill_queue_target=1.0)
        # Step 1: avg_pq = 0.4
        ctrl.release(ServerMetrics(prefill_queue_duration=0.4))
        ctrl.step_completed()
        assert ctrl.ema_prefill_queue == pytest.approx(0.4)
        # Step 2: avg_pq = 0.8
        ctrl.release(ServerMetrics(prefill_queue_duration=0.8))
        ctrl.step_completed()
        assert ctrl.ema_prefill_queue == pytest.approx(0.5 * 0.8 + 0.5 * 0.4)

    def test_repeated_congestion_floors_at_min(self):
        ctrl = AdaptiveConcurrencyController(
            initial_window=16, min_window=2, prefill_queue_target=0.1,
            multiplicative_decrease=0.5, ema_alpha=1.0,
        )
        for _ in range(20):
            ctrl.release(ServerMetrics(prefill_queue_duration=5.0))
            ctrl.step_completed()
        assert ctrl.window_size == 2

    def test_repeated_good_metrics_caps_at_max(self):
        ctrl = AdaptiveConcurrencyController(
            initial_window=4, max_window=16, prefill_queue_target=1.0,
            additive_increase=5.0, ema_alpha=1.0,
        )
        for _ in range(100):
            ctrl.release(ServerMetrics(prefill_queue_duration=0.01))
            ctrl.step_completed()
        assert ctrl.window_size == 16

    def test_step_completed_resets_accumulators(self):
        ctrl = AdaptiveConcurrencyController(initial_window=8)
        ctrl.release(ServerMetrics(prefill_queue_duration=0.3, cached_prompt_tokens=10, prompt_tokens=100))
        ctrl.release(ServerMetrics(prefill_queue_duration=0.5, cached_prompt_tokens=20, prompt_tokens=100))
        summary = ctrl.step_completed()
        assert summary["requests"] == 2
        assert summary["avg_pq"] == pytest.approx(0.4)
        assert summary["cache_hit_rate"] == pytest.approx(30 / 200)
        # After step_completed, accumulators are reset.
        summary2 = ctrl.step_completed()
        assert summary2["requests"] == 0
        assert "avg_pq" not in summary2


# ---------------------------------------------------------------------------
# Streaming completions
# ---------------------------------------------------------------------------


class TestStreamingCompletions:
    def test_streaming_with_adaptive_controller(self):
        import json as _json
        prompt_ids = [1, 2, 3]
        completion_ids = [400, 500]
        ctrl = AdaptiveConcurrencyController(initial_window=8, ema_alpha=1.0)
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids), concurrency_controller=ctrl)

        chunk_data = {
            "choices": [{
                "text": "hello",
                "raw_output": {"completion_token_ids": completion_ids},
                "finish_reason": "stop",
            }],
            "perf_metrics": {"prefill-queue-duration": "0.1"},
        }
        # SSE wire format: "data: {json}\n\n" per event
        raw_bytes = (
            f"data: {_json.dumps(chunk_data)}\n\n"
            f"data: [DONE]\n\n"
        ).encode()

        async def mock_post(*args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            resp.headers = {}

            async def aiter_bytes():
                yield raw_bytes
            resp.aiter_bytes = aiter_bytes
            return resp

        sampler._get_async_client = MagicMock()
        sampler._get_async_client.return_value.post = mock_post

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}],
        ))
        assert len(results) == 1
        assert results[0].full_tokens == prompt_ids + completion_ids
        # Metrics collected but window not adjusted yet.
        assert ctrl.ema_prefill_queue is None
        # Trigger step-level adjustment.
        summary = ctrl.step_completed()
        assert ctrl.ema_prefill_queue == pytest.approx(0.1)
        assert summary["avg_pq"] == pytest.approx(0.1)
        sampler.close()


class TestSseTruncationRetry:
    """Contract: only :class:`_SSETruncationError` triggers retry; other
    ``RuntimeError`` subclasses propagate unchanged."""

    def test_truncation_then_success_recovers(self, monkeypatch):
        """First attempt raises _SSETruncationError, second attempt succeeds."""
        import random as _random

        # Pin jitter to a deterministic minimum sleep.
        monkeypatch.setattr(_random, "random", lambda: 0.0)
        # Drop the first-attempt sleep to keep the test fast.
        async def _no_sleep(_s):
            return None
        monkeypatch.setattr(asyncio, "sleep", _no_sleep)

        sampler = _make_sampler(tokenizer=None)
        attempts = {"n": 0}

        async def _fake(*args, **kwargs):
            attempts["n"] += 1
            if attempts["n"] == 1:
                raise _SSETruncationError("truncated")
            return {
                "choices": [{
                    "text": "ok", "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": [7]},
                }]
            }, ServerMetrics()

        sampler.async_completions_stream = _fake
        results = asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert attempts["n"] == 2
        assert len(results) == 1
        assert results[0].finish_reason == "stop"
        sampler.close()

    def test_non_truncation_runtime_error_propagates(self):
        """A generic RuntimeError must NOT trigger retry — it propagates immediately."""
        sampler = _make_sampler(tokenizer=None)
        attempts = {"n": 0}

        async def _fake(*args, **kwargs):
            attempts["n"] += 1
            raise RuntimeError("Exhausted hotload retries in streaming mode")

        sampler.async_completions_stream = _fake
        with pytest.raises(RuntimeError, match="hotload"):
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert attempts["n"] == 1, "non-truncation RuntimeError must not be retried"
        sampler.close()

    def test_truncation_exhausts_after_max_attempts(self, monkeypatch):
        """After _RETRY_MAX_ATTEMPTS truncations, the error surfaces."""
        import random as _random

        monkeypatch.setattr(_random, "random", lambda: 0.0)
        async def _no_sleep(_s):
            return None
        monkeypatch.setattr(asyncio, "sleep", _no_sleep)

        sampler = _make_sampler(tokenizer=None)
        attempts = {"n": 0}

        async def _fake(*args, **kwargs):
            attempts["n"] += 1
            raise _SSETruncationError("truncated")

        sampler.async_completions_stream = _fake
        with pytest.raises(_SSETruncationError):
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert attempts["n"] == DeploymentSampler._RETRY_MAX_ATTEMPTS
        sampler.close()


class TestSamplerTimeoutDiagnostics:
    """Timeout-like transient failures get deployment sampler diagnostics."""

    @staticmethod
    def _http_status_error(status_code: int) -> httpx.HTTPStatusError:
        request = httpx.Request(
            "POST",
            "https://api.example.com/inference/v1/completions",
        )
        response = httpx.Response(status_code, request=request)
        return httpx.HTTPStatusError(
            f"Server error '{status_code}'",
            request=request,
            response=response,
        )

    @pytest.mark.parametrize(
        ("workload", "recipe"),
        [
            ("async_rl_rollout", "async_rl_loop"),
            ("rl_rollout", "rl_loop"),
        ],
    )
    def test_http_504_exhaustion_raises_sampler_timeout_diagnostic(
        self,
        workload,
        recipe,
        monkeypatch,
        caplog,
    ):
        import random as _random

        monkeypatch.setattr(_random, "random", lambda: 0.0)

        async def _no_sleep(_s):
            return None

        monkeypatch.setattr(asyncio, "sleep", _no_sleep)

        sampler = _make_sampler(
            tokenizer=None,
            model="accounts/figma/deployments/qwen3p6-27b-1780660798",
            concurrency_controller=FixedConcurrencyController(16),
        )
        sampler._recent_metrics = [
            ServerMetrics(
                prefill_queue_duration=590.0,
                generation_queue_duration=591.0,
                client_ttft=599.0,
                num_concurrent_requests=16,
            )
        ]
        attempts = {"n": 0}

        async def _fake(*args, **kwargs):
            attempts["n"] += 1
            assert "timeout_diagnostic_context" not in kwargs
            raise self._http_status_error(504)

        sampler.async_completions_stream = _fake
        caplog.set_level(logging.WARNING)

        with pytest.raises(DeploymentSamplerTimeoutError) as exc_info:
            asyncio.run(
                sampler.sample_with_prompt_tokens(
                    [1, 2, 3],
                    max_tokens=40000,
                    http_timeout=1200,
                    timeout_diagnostic_context={
                        "workload": workload,
                        "recipe": recipe,
                        "completions_per_prompt": 4,
                        "max_concurrency_rollout_sample": 16,
                        "prompt_groups_per_step": 1,
                    },
                )
            )

        msg = str(exc_info.value)
        assert attempts["n"] == DeploymentSampler._RETRY_MAX_ATTEMPTS
        assert "DeploymentSampler request failed after exhausting retries" in msg
        assert "on a timeout-like error" in msg
        assert "RL rollout context detected" in msg
        assert "If recent queue/TTFT metrics are high" in msg
        assert "rollout sampling may be exceeding sampler capacity" in msg
        assert "raw_error=HTTP 504" in msg
        assert "prompt_tokens=3" in msg
        assert "max_tokens=40000" in msg
        assert "http_timeout=1200s" in msg
        assert "sampler_concurrency_window=16" in msg
        assert f"workload={workload}" in msg
        assert f"recipe={recipe}" in msg
        assert "completions_per_prompt=4" in msg
        assert "max_concurrency_rollout_sample=16" in msg
        assert "prompt_groups_per_step=1" in msg
        assert "recent_prefill_queue_p95=590.0s" in msg
        assert "recent_generation_queue_p95=591.0s" in msg
        assert "recent_client_ttft_p95=599.0s" in msg
        assert "If they are elevated, reduce rollout concurrency" in msg
        assert "otherwise investigate gateway, network, or client timeout limits" in msg
        assert "DeploymentSampler request hit a timeout-like transient" in caplog.text
        sampler.close()

    def test_read_timeout_exhaustion_raises_generic_sampler_timeout_diagnostic(self, monkeypatch):
        import random as _random

        monkeypatch.setattr(_random, "random", lambda: 0.0)

        async def _no_sleep(_s):
            return None

        monkeypatch.setattr(asyncio, "sleep", _no_sleep)

        sampler = _make_sampler(tokenizer=None)
        attempts = {"n": 0}

        async def _fake(*args, **kwargs):
            attempts["n"] += 1
            raise httpx.ReadTimeout("read timed out")

        sampler.async_completions_stream = _fake

        with pytest.raises(DeploymentSamplerTimeoutError) as exc_info:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        msg = str(exc_info.value)
        assert attempts["n"] == DeploymentSampler._RETRY_MAX_ATTEMPTS
        assert "DeploymentSampler request failed after exhausting retries" in msg
        assert "raw_error=ReadTimeout" in msg
        assert "Check serving queue/TTFT metrics" in msg
        assert "gateway timeout limits" in msg
        assert "async RL" not in msg
        assert "max_concurrency_rollout_sample" not in msg
        sampler.close()

    @pytest.mark.parametrize("entrypoint", ["prompt_tokens", "messages"])
    def test_parallel_n_preserves_timeout_diagnostic_context_for_each_completion(self, entrypoint):
        context = {
            "workload": "rl_rollout",
            "recipe": "rl_loop",
            "max_concurrency_rollout_sample": 16,
        }
        tokenizer = _make_mock_tokenizer([1, 2, 3]) if entrypoint == "messages" else None
        sampler = _make_sampler(tokenizer=tokenizer)
        seen_contexts: list[dict] = []

        async def _fake_do_one_completion(*args, **kwargs):
            seen_contexts.append(kwargs.pop("timeout_diagnostic_context", None))
            return []

        sampler._do_one_completion = _fake_do_one_completion

        if entrypoint == "messages":
            asyncio.run(
                sampler.sample_with_tokens(
                    [{"role": "user", "content": "hi"}],
                    n=3,
                    timeout_diagnostic_context=context,
                )
            )
        else:
            asyncio.run(
                sampler.sample_with_prompt_tokens(
                    [1, 2, 3],
                    n=3,
                    timeout_diagnostic_context=context,
                )
            )

        assert seen_contexts == [context, context, context]
        sampler.close()
