"""Shared REST client base class for Fireworks SDK HTTP clients.

Two transport layers:
  - Sync ``httpx.Client`` for control-plane operations (deployment CRUD,
    hotload, trainer management, warmup probes).
  - Async ``httpx.AsyncClient`` for high-concurrency sampling (completions).

Each URL's SSL verification is computed independently so mixed-endpoint
setups (control-plane + gateway + hotload at different URLs) get the
correct TLS policy.
"""

from __future__ import annotations

import logging
import ipaddress
from urllib.parse import urlparse

import httpx
import urllib3

from fireworks.training.sdk.errors import request_with_retries

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

logging.getLogger("tinker.lib.api_future_impl").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def _should_verify_ssl(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    try:
        ipaddress.ip_address(parsed.hostname)
        return False
    except (ValueError, TypeError):
        return True


def _make_sync_client(verify: bool) -> httpx.Client:
    return httpx.Client(verify=verify, timeout=httpx.Timeout(60.0))


def _make_async_client(verify: bool) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        verify=verify,
        timeout=httpx.Timeout(connect=30.0, read=600.0, write=30.0, pool=30.0),
        limits=httpx.Limits(
            max_connections=200,
            max_keepalive_connections=0,  # no keep-alive: fresh connection per request (like requests.post bare)
        ),
    )


class _RestClient:
    """Base class for Fireworks REST API clients.

    Sync ``httpx.Client`` for control-plane ops; lazy ``httpx.AsyncClient``
    for async sampling.  SSL verification computed per-URL.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.fireworks.ai",
        additional_headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
    ):
        self.api_key = api_key
        self._account_id: str | None = None
        self.base_url = base_url.rstrip("/")
        self.additional_headers = additional_headers
        self._verify_ssl_override = verify_ssl
        self._base_verify = (
            verify_ssl if verify_ssl is not None else _should_verify_ssl(base_url)
        )
        self._sync_client = _make_sync_client(self._base_verify)
        self._async_client: httpx.AsyncClient | None = None

    @property
    def account_id(self) -> str:
        """The Fireworks account ID, auto-resolved from the API key on first access."""
        if self._account_id is None:
            self._account_id = self._resolve_account_id()
        return self._account_id

    def _resolve_account_id(self) -> str:
        """Resolve account ID by calling GET /v1/accounts with the current API key."""
        resp = self._get("/v1/accounts?pageSize=2")
        resp.raise_for_status()
        data = resp.json()
        accounts = data.get("accounts", []) or []
        if not accounts:
            raise ValueError(
                "API key is not associated with any Fireworks account. "
                "Verify your API key is valid at: https://fireworks.ai/account/api-keys"
            )
        if len(accounts) > 1:
            ids = [a.get("name", "").removeprefix("accounts/") for a in accounts]
            raise ValueError(
                f"API key has access to multiple accounts: {ids}. "
                "This is not supported for firetitan training."
            )
        name = accounts[0].get("name", "")
        account_id = name.removeprefix("accounts/")
        if not account_id:
            raise ValueError(
                "Could not parse account ID from API response. "
                f"Got account name: '{name}'"
            )
        logger.info("Auto-resolved account ID: %s", account_id)
        return account_id

    def _verify_for_url(self, url: str) -> bool:
        if self._verify_ssl_override is not None:
            return self._verify_ssl_override
        return _should_verify_ssl(url)

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = _make_async_client(self._base_verify)
        return self._async_client

    def _sync_request(self, url: str, **kwargs) -> httpx.Response:
        """Make a sync request, using a per-URL client if SSL differs from base."""
        verify = self._verify_for_url(url)
        if verify != self._base_verify:
            with httpx.Client(verify=verify) as client:
                return request_with_retries(client.request, kwargs.pop("method", "GET"), url, **kwargs)
        return request_with_retries(self._sync_client.request, kwargs.pop("method", "GET"), url, **kwargs)

    def _headers(self, **extra: str) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }
        if self.additional_headers:
            headers.update(self.additional_headers)
        if extra:
            headers.update(extra)
        return headers

    # -- Sync HTTP verbs (control-plane) ---------------------------------------

    def _get(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", 30)
        return request_with_retries(self._sync_client.get, url, **kwargs)

    def _post(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", 60)
        return request_with_retries(self._sync_client.post, url, **kwargs)

    def _delete(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", 60)
        return request_with_retries(self._sync_client.delete, url, **kwargs)

    def _patch(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", 60)
        return request_with_retries(self._sync_client.patch, url, **kwargs)

    # -- Lifecycle -------------------------------------------------------------

    def close(self):
        self._sync_client.close()
        ac = self._async_client
        self._async_client = None
        if ac and not ac.is_closed:
            try:
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                if loop and loop.is_running():
                    loop.create_task(ac.aclose())
                else:
                    new_loop = asyncio.new_event_loop()
                    try:
                        new_loop.run_until_complete(ac.aclose())
                    finally:
                        new_loop.close()
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
