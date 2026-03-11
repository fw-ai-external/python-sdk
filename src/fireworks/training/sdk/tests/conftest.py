"""Shared pytest configuration for the SDK test suite."""

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(
            pytest.mark.filterwarnings(
                "ignore::pytest.PytestUnraisableExceptionWarning"
            )
        )
