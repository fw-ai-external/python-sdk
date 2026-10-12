"""Shared pytest configuration for the SDK test suite."""

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(
            pytest.mark.filterwarnings(
                "ignore::pytest.PytestUnraisableExceptionWarning"
            )
        )


@pytest.fixture(autouse=True)
def _fail_fast_http_retries(request, monkeypatch):
    """Disable HTTP retry backoff in unit tests so the suite stays fast.

    ``request_with_retries`` retries connection errors and retryable statuses
    with exponential backoff up to ``MAX_WAIT_TIME`` (5 minutes). A unit test
    that does not fully mock the HTTP boundary (e.g. mocks ``_post`` but lets
    the follow-up ``_get`` hit the unreachable test host) would otherwise spend
    minutes of real ``time.sleep`` in that loop.

    Forcing ``_backoff_delay`` to ``None`` makes both the sync and async retry
    loops do exactly one attempt — failures surface immediately instead of
    looping. ``test_errors`` is exempt because it exercises the retry/backoff
    logic itself.

    The functions bind ``MAX_WAIT_TIME`` as a default argument, so patching the
    module constant would not take effect; ``_backoff_delay`` is looked up as a
    module global at call time, so patching it does.
    """
    if request.module.__name__.rsplit(".", 1)[-1] == "test_errors":
        return
    import fireworks.training.sdk.errors as errors

    def _no_backoff_delay(*_args, **_kwargs):
        return None

    monkeypatch.setattr(errors, "_backoff_delay", _no_backoff_delay)
