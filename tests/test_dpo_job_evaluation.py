from __future__ import annotations

import json

import httpx

from fireworks import Fireworks
from fireworks.types.dpo_job import DpoJob


def test_dpo_job_create_sends_evaluation_settings() -> None:
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

    client.dpo_jobs.create(
        account_id="test",
        dataset="dpo-data",
        evaluation_dataset="accounts/test/datasets/held-out",
    )
    client.dpo_jobs.create(account_id="test", dataset="dpo-data", eval_auto_carveout=True)
    client.dpo_jobs.create(account_id="test", dataset="dpo-data")

    assert payloads[0]["evaluationDataset"] == "accounts/test/datasets/held-out"
    assert payloads[1]["evalAutoCarveout"] is True
    assert "evaluationDataset" not in payloads[2]
    assert "evalAutoCarveout" not in payloads[2]


def test_dpo_job_response_exposes_evaluation_settings() -> None:
    job = DpoJob(dataset="dataset", evaluationDataset="accounts/test/datasets/held-out", evalAutoCarveout=False)

    assert job.evaluation_dataset == "accounts/test/datasets/held-out"
    assert job.eval_auto_carveout is False
