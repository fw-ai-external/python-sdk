from __future__ import annotations

import json

import httpx

from fireworks import Fireworks
from fireworks._utils import transform
from fireworks.types.dpo_job import DpoJob
from fireworks.types.dpo_job_create_params import DpoJobCreateParams
from fireworks.types.supervised_fine_tuning_job import SupervisedFineTuningJob
from fireworks.types.supervised_fine_tuning_job_create_params import SupervisedFineTuningJobCreateParams


def test_sft_use_reservation_uses_rest_alias() -> None:
    assert transform(
        {"dataset": "dataset", "use_reservation": True},
        expected_type=SupervisedFineTuningJobCreateParams,
    ) == {"dataset": "dataset", "useReservation": True}


def test_dpo_use_reservation_uses_rest_alias() -> None:
    assert transform(
        {"dataset": "dataset", "use_reservation": True},
        expected_type=DpoJobCreateParams,
    ) == {"dataset": "dataset", "useReservation": True}


def test_job_response_models_expose_use_reservation() -> None:
    assert DpoJob(dataset="dataset", useReservation=True).use_reservation is True
    assert SupervisedFineTuningJob(dataset="dataset", useReservation=True).use_reservation is True


def test_managed_job_create_payload_only_sends_explicit_use_reservation() -> None:
    payloads: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        payloads.append(payload)
        return httpx.Response(200, json=payload)

    client = Fireworks(
        api_key="test-key",
        base_url="http://test.local",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.supervised_fine_tuning_jobs.create(account_id="test", dataset="sft-data")
    client.dpo_jobs.create(account_id="test", dataset="dpo-data", use_reservation=True)

    assert "useReservation" not in payloads[0]
    assert payloads[1]["useReservation"] is True
