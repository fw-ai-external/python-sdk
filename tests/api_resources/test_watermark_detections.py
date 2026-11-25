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
            json={"object": "watermark.detection", "result": "not_detected"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Fireworks(api_key="test", http_client=http_client)
        result = client.watermark_detections.create(text="hello")
    assert result.object == "watermark.detection"
    assert result.result == "not_detected"


def test_create_watermark_detection_with_overridden_base_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/watermark/detect"
        return httpx.Response(
            200,
            json={"object": "watermark.detection", "result": "detected"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Fireworks(
            api_key="test",
            base_url="http://detector.example.com",
            http_client=http_client,
        )
        result = client.watermark_detections.create(text="hello")
    assert result.result == "detected"
