import json

import httpx

from fireworks import Fireworks


def test_create_watermark_detection() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/inference/v1/watermark/detect"
        assert json.loads(request.content) == {"text": "hello"}
        return httpx.Response(
            200,
            json={
                "id": "wmdet_test",
                "object": "watermark.detection",
                "detector_version": "detector-v1",
                "result": "not_detected",
                "scored_tokens": 400,
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Fireworks(api_key="test", http_client=http_client)
        result = client.watermark_detections.create(text="hello")
    assert result.id == "wmdet_test"
    assert result.result == "not_detected"
    assert result.scored_tokens == 400


def test_create_watermark_detection_with_overridden_base_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/watermark/detect"
        return httpx.Response(
            200,
            json={
                "id": "wmdet_test",
                "object": "watermark.detection",
                "detector_version": "detector-v1",
                "result": "uncertain",
                "scored_tokens": 20,
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Fireworks(
            api_key="test",
            base_url="http://detector.example.com",
            http_client=http_client,
        )
        result = client.watermark_detections.create(text="hello")
    assert result.result == "uncertain"
