"""Request-local activation for the optimized Fireworks training client."""

from typing import Literal
from contextlib import contextmanager
from contextvars import ContextVar
from collections.abc import Iterator

Comms = Literal["v1", "v2"]
_request_comms: ContextVar[Comms] = ContextVar("fireworks_request_comms", default="v1")


def get_comms() -> Comms:
    return _request_comms.get()


@contextmanager
def comms_context(comms: Comms) -> Iterator[None]:
    """Restore the caller's mode after success, failure or cancellation."""
    token = _request_comms.set(comms)
    try:
        yield
    finally:
        _request_comms.reset(token)
