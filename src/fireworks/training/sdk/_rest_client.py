"""Shared REST client base class for Fireworks SDK HTTP clients.

Provides session management, SSL verification, header construction,
and convenience methods for GET/POST/DELETE/PATCH with automatic retries.
"""

from __future__ import annotations

import logging
import ipaddress
from urllib.parse import urlparse

import urllib3
import requests

from fireworks.training.sdk.errors import request_with_retries

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


def _should_verify_ssl(url: str) -> bool:
    """Verify SSL for https URLs with real domain names; skip for http or IPs."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    try:
        ipaddress.ip_address(parsed.hostname)
        return False
    except (ValueError, TypeError):
        return True


class _RestClient:
    """Base class for Fireworks REST API clients.

    Manages a ``requests.Session``, SSL verification, default headers,
    and convenience wrappers around ``request_with_retries`` for the
    standard HTTP verbs.

    Subclasses get ``_get``, ``_post``, ``_delete``, ``_patch`` methods
    that automatically prepend ``base_url``, inject default headers and
    SSL settings, and retry on transient failures.
    """

    def __init__(
        self,
        api_key: str,
        account_id: str | None = None,
        base_url: str = "https://api.fireworks.ai",
        additional_headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
    ):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url.rstrip("/")
        self.additional_headers = additional_headers
        self._verify_ssl = (
            verify_ssl if verify_ssl is not None else _should_verify_ssl(base_url)
        )
        self._session = requests.Session()

    def _headers(self, **extra: str) -> dict[str, str]:
        """Build default request headers, merged with *extra* overrides."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }
        if self.additional_headers:
            headers.update(self.additional_headers)
        if extra:
            headers.update(extra)
        return headers

    # -- Convenience HTTP verbs ------------------------------------------------

    def _get(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("verify", self._verify_ssl)
        kwargs.setdefault("timeout", 30)
        return request_with_retries(self._session.get, url, **kwargs)

    def _post(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("verify", self._verify_ssl)
        kwargs.setdefault("timeout", 60)
        return request_with_retries(self._session.post, url, **kwargs)

    def _delete(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("verify", self._verify_ssl)
        kwargs.setdefault("timeout", 60)
        return request_with_retries(self._session.delete, url, **kwargs)

    def _patch(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("verify", self._verify_ssl)
        kwargs.setdefault("timeout", 60)
        return request_with_retries(self._session.patch, url, **kwargs)

    # -- Lifecycle -------------------------------------------------------------

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
