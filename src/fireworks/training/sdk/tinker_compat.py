"""Helpers for running Tinker cookbook code on FireTitan SDK-managed infra."""

from __future__ import annotations

from typing import Any, Iterator
from contextlib import contextmanager
from collections.abc import Callable

from fireworks.training.sdk.client import FiretitanServiceClient


def install_tinker_service_client(**managed_config_kwargs: Any) -> Callable[..., Any]:
    """Patch ``tinker.ServiceClient`` to create SDK-managed FireTitan clients."""
    import tinker

    original = tinker.ServiceClient

    def _firetitan_service_client(
        user_metadata: dict[str, str] | None = None,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> FiretitanServiceClient:
        base_url = kwargs.pop("base_url", None)
        api_key = kwargs.pop("api_key", None)
        default_headers = kwargs.pop("default_headers", None)
        if kwargs:
            unsupported = ", ".join(sorted(kwargs))
            raise TypeError(f"Unsupported tinker.ServiceClient keyword(s) for FireTitan compatibility: {unsupported}")
        return FiretitanServiceClient.from_firetitan_config(
            api_key=api_key,
            base_url=base_url,
            additional_headers=default_headers,
            user_metadata=user_metadata,
            project_id=project_id,
            **managed_config_kwargs,
        )

    tinker.ServiceClient = _firetitan_service_client
    return original


def restore_tinker_service_client(original: Callable[..., Any]) -> None:
    """Restore a ``tinker.ServiceClient`` value returned by install."""
    import tinker

    tinker.ServiceClient = original


@contextmanager
def patched_tinker_service_client(**managed_config_kwargs: Any) -> Iterator[None]:
    """Context manager variant of :func:`install_tinker_service_client`."""
    import tinker

    original = install_tinker_service_client(**managed_config_kwargs)
    try:
        yield
    finally:
        restore_tinker_service_client(original)
        assert tinker.ServiceClient is original
