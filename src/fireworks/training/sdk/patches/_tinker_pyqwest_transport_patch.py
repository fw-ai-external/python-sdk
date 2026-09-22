"""Keep Tinker's pyqwest transport on system TLS roots.

Tinker 0.23 constructs ``pyqwest.HTTPTransport`` without TLS options.
Pyqwest 0.7 and newer require callers to opt into system CA certificates, so
the unmodified factory cannot reach HTTPS trainer endpoints.

Remove this patch when the pinned Tinker version configures system roots
natively.
"""

from __future__ import annotations

import pyqwest
import tinker._base_client as tinker_base_client
from pyqwest.httpx import AsyncPyqwestTransport


def _default_pyqwest_transport() -> AsyncPyqwestTransport:
    return AsyncPyqwestTransport(
        transport=pyqwest.HTTPTransport(tls_include_system_certs=True),
    )


tinker_base_client._default_pyqwest_transport = _default_pyqwest_transport
