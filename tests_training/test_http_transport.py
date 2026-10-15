from __future__ import annotations

from typing import Any

import pyqwest
import pyqwest.httpx

import fireworks.training.sdk._core._base_client as training_base_client


def test_transport_includes_system_tls_roots(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    class FakeHTTPTransport:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)

    class FakeAsyncPyqwestTransport:
        def __init__(self, *, transport: Any) -> None:
            self.transport = transport

    monkeypatch.setattr(pyqwest, "HTTPTransport", FakeHTTPTransport)
    monkeypatch.setattr(pyqwest.httpx, "AsyncPyqwestTransport", FakeAsyncPyqwestTransport)

    transport = training_base_client._default_pyqwest_transport()

    assert isinstance(transport, FakeAsyncPyqwestTransport)
    assert captured == {"tls_include_system_certs": True}
