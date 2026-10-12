from __future__ import annotations

from typing import Any

import tinker._base_client as tinker_base_client

from fireworks.training.sdk.patches import _tinker_pyqwest_transport_patch as patch


def test_transport_includes_system_tls_roots(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    class FakeHTTPTransport:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)

    class FakeAsyncPyqwestTransport:
        def __init__(self, *, transport: Any) -> None:
            self.transport = transport

    monkeypatch.setattr(patch.pyqwest, "HTTPTransport", FakeHTTPTransport)
    monkeypatch.setattr(patch, "AsyncPyqwestTransport", FakeAsyncPyqwestTransport)

    transport = tinker_base_client._default_pyqwest_transport()

    assert isinstance(transport, FakeAsyncPyqwestTransport)
    assert captured == {"tls_include_system_certs": True}
