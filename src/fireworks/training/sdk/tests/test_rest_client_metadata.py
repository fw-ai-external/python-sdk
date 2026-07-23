from fireworks.training.sdk._rest_client import _RestClient


def test_headers_inherit_valid_skill_metadata(monkeypatch):
    monkeypatch.setenv("FIREWORKS_CLIENT_SOURCE", "fireworks-training-skill/2.0.0")
    monkeypatch.setenv("FIREWORKS_SESSION_ID", "8c6f765a-1e2d-4cdd-a010-3a7a0f7daf42")
    client = _RestClient("key", verify_ssl=False)
    try:
        headers = client._headers()
        assert headers["X-Fireworks-Client-Source"] == "fireworks-training-skill/2.0.0"
        assert headers["X-Fireworks-Session-Id"] == ("8c6f765a-1e2d-4cdd-a010-3a7a0f7daf42")
    finally:
        client.close()


def test_headers_ignore_invalid_or_missing_skill_metadata(monkeypatch):
    monkeypatch.setenv("FIREWORKS_CLIENT_SOURCE", "untrusted/source")
    monkeypatch.setenv("FIREWORKS_SESSION_ID", "not-a-uuid")
    client = _RestClient("key", verify_ssl=False)
    try:
        headers = client._headers()
        assert "X-Fireworks-Client-Source" not in headers
        assert "X-Fireworks-Session-Id" not in headers
    finally:
        client.close()


def test_explicit_headers_override_environment_case_insensitively(monkeypatch):
    monkeypatch.setenv("FIREWORKS_CLIENT_SOURCE", "fireworks-training-skill/2.0.0")
    monkeypatch.setenv("FIREWORKS_SESSION_ID", "8c6f765a-1e2d-4cdd-a010-3a7a0f7daf42")
    client = _RestClient(
        "key",
        additional_headers={
            "x-fireworks-client-source": "caller/source",
            "x-fireworks-session-id": "caller-session",
        },
        verify_ssl=False,
    )
    try:
        headers = client._headers()
        assert headers["x-fireworks-client-source"] == "caller/source"
        assert headers["x-fireworks-session-id"] == "caller-session"
        assert "X-Fireworks-Client-Source" not in headers
        assert "X-Fireworks-Session-Id" not in headers
    finally:
        client.close()
