"""Authentication credential management for the native training SDK.

Provides composable credential providers that plug into httpx's async auth flow:
- AuthTokenProvider: abstract base (httpx.Auth) — subclasses implement get_token()
- ApiKeyAuthProvider: resolves from api_key arg or FIREWORKS_API_KEY env var
- CredentialCmdAuthProvider: runs a command on every call for fresh credentials
- resolve_auth_provider(): factory that picks the right provider
"""

from __future__ import annotations

import os
import abc
import asyncio
from collections.abc import AsyncGenerator

import httpx

from fireworks.training.sdk._core._exceptions import TrainingError


class AuthTokenProvider(httpx.Auth):
    """Abstract base auth provider. Subclasses implement get_token()."""

    @abc.abstractmethod
    async def get_token(self) -> str | None: ...

    async def async_auth_flow(self, request: httpx.Request) -> AsyncGenerator[httpx.Request, httpx.Response]:
        token = await self.get_token()
        if token:
            request.headers["X-API-Key"] = token
        yield request


def resolve_api_key(api_key: str | None = None) -> str | None:
    """Resolve a caller's key before creating providers, headers or workers."""
    return api_key or os.environ.get("FIREWORKS_API_KEY")


class ApiKeyAuthProvider(AuthTokenProvider):
    """Resolves api_key from constructor arg or FIREWORKS_API_KEY env var."""

    def __init__(self, api_key: str | None = None) -> None:
        resolved = resolve_api_key(api_key)
        if not resolved:
            raise TrainingError(
                "The api_key client option must be set either by passing api_key to the client"
                " or by setting the FIREWORKS_API_KEY environment variable"
            )
        self._token = resolved

    async def get_token(self) -> str | None:
        return self._token


class CredentialCmdAuthProvider(AuthTokenProvider):
    """Runs FIREWORKS_CREDENTIAL_CMD on every get_token() call.

    Always produces a fresh credential (e.g. short-lived bearer tokens).
    Uses async subprocess to avoid blocking the event loop.
    """

    def __init__(self, cmd: str) -> None:
        if not cmd:
            raise TrainingError(
                "Your organization requires dynamic credentials — set FIREWORKS_CREDENTIAL_CMD"
                " to a command that prints a valid credential."
            )
        self._cmd = cmd

    async def get_token(self) -> str | None:
        proc = await asyncio.create_subprocess_shell(
            self._cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        credential = stdout.decode().strip()
        if not credential:
            raise TrainingError("FIREWORKS_CREDENTIAL_CMD returned an empty credential.")
        return credential


def resolve_auth_provider(api_key: str | None, enforce_cmd: bool) -> AuthTokenProvider:
    """Construct the appropriate auth provider based on available credentials.

    - enforce_cmd=True: uses FIREWORKS_CREDENTIAL_CMD, unless the api_key is
      already a JWT (dynamic credential) — in which case it's used directly.
    - enforce_cmd=False: uses api_key or FIREWORKS_API_KEY; never runs a command
    """
    credential_cmd = os.environ.get("FIREWORKS_CREDENTIAL_CMD", "")

    # A JWT passed as api_key is already a dynamic credential — use it
    # directly even when credential_cmd is enforced.
    resolved = resolve_api_key(api_key)
    if resolved and resolved.startswith("eyJ"):
        return ApiKeyAuthProvider(api_key=resolved)

    if enforce_cmd:
        return CredentialCmdAuthProvider(credential_cmd)

    return ApiKeyAuthProvider(api_key=api_key)
