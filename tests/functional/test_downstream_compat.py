"""Downstream compatibility tests.

Verify that the SDK's public API surface remains compatible with known
downstream consumers. These tests do NOT require network access — they only
check that import paths and class interfaces exist.

Run with: pytest tests/functional/test_downstream_compat.py -v
"""

from __future__ import annotations

import warnings

import pytest


class TestBackwardsCompatImportPaths:
    """Verify that old ``fireworks.client`` import paths still work.

    Downstream packages like langchain-fireworks, instructor, and many
    internal services use ``from fireworks.client import Fireworks``.
    """

    def test_fireworks_client_import(self) -> None:
        from fireworks.client import Fireworks

        assert Fireworks is not None

    def test_async_fireworks_client_import(self) -> None:
        from fireworks.client import AsyncFireworks

        assert AsyncFireworks is not None

    def test_version_from_client(self) -> None:
        from fireworks.client import __version__

        assert __version__

    def test_deprecation_warning_emitted(self) -> None:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Force reimport by removing from cache
            import sys

            sys.modules.pop("fireworks.client", None)
            from fireworks.client import Fireworks  # noqa: F811, F401  # pyright: ignore[reportUnusedImport]

            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1
            assert "fireworks.client" in str(deprecation_warnings[0].message)


class TestNewImportPaths:
    """Verify the canonical 1.x import paths work."""

    def test_top_level_fireworks(self) -> None:
        from fireworks import Fireworks

        assert Fireworks is not None

    def test_top_level_async(self) -> None:
        from fireworks import AsyncFireworks

        assert AsyncFireworks is not None

    def test_types_module(self) -> None:
        from fireworks import types

        assert types is not None

    def test_exceptions(self) -> None:
        from fireworks import (
            APIError,
            NotFoundError,
            RateLimitError,
            BadRequestError,
            AuthenticationError,
        )

        assert all([APIError, AuthenticationError, BadRequestError, NotFoundError, RateLimitError])

    def test_version(self) -> None:
        from fireworks import __version__

        assert __version__
        assert __version__.startswith("1.")


class TestClientInterface:
    """Verify the client class has the interface downstream consumers expect.

    These are the methods/attributes that langchain-fireworks, instructor,
    and other integrations rely on.
    """

    def test_fireworks_has_chat_completions(self) -> None:
        from fireworks import Fireworks

        client = Fireworks(api_key="test", base_url="http://localhost:9999")
        assert hasattr(client, "chat")
        assert hasattr(client.chat, "completions")
        assert hasattr(client.chat.completions, "create")

    def test_fireworks_has_completions(self) -> None:
        from fireworks import Fireworks

        client = Fireworks(api_key="test", base_url="http://localhost:9999")
        assert hasattr(client, "completions")
        assert hasattr(client.completions, "create")

    def test_fireworks_has_models(self) -> None:
        from fireworks import Fireworks

        client = Fireworks(api_key="test", base_url="http://localhost:9999")
        assert hasattr(client, "models")

    def test_async_fireworks_has_chat_completions(self) -> None:
        from fireworks import AsyncFireworks

        client = AsyncFireworks(api_key="test", base_url="http://localhost:9999")
        assert hasattr(client, "chat")
        assert hasattr(client.chat, "completions")
        assert hasattr(client.chat.completions, "create")

    def test_client_accepts_api_key(self) -> None:
        from fireworks import Fireworks

        client = Fireworks(api_key="test-key", base_url="http://localhost:9999")
        assert client is not None

    def test_client_accepts_base_url(self) -> None:
        from fireworks import Fireworks

        client = Fireworks(api_key="test", base_url="http://custom.api.example.com")
        assert client is not None


class TestAcreateCompat:
    """Verify the ``acreate()`` backwards-compat alias exists.

    langchain-fireworks and instructor call ``client.chat.completions.acreate()``.
    The new SDK only has ``create()`` (which is async-native). We patch in
    ``acreate`` as a deprecated alias.
    """

    def test_chat_completions_acreate_exists(self) -> None:
        from fireworks import AsyncFireworks

        client = AsyncFireworks(api_key="test", base_url="http://localhost:9999")
        assert hasattr(client.chat.completions, "acreate"), "acreate alias missing on chat.completions"
        assert callable(client.chat.completions.acreate)  # type: ignore[attr-defined]

    def test_completions_acreate_exists(self) -> None:
        from fireworks import AsyncFireworks

        client = AsyncFireworks(api_key="test", base_url="http://localhost:9999")
        assert hasattr(client.completions, "acreate"), "acreate alias missing on completions"
        assert callable(client.completions.acreate)  # type: ignore[attr-defined]

    def test_acreate_emits_deprecation_warning(self) -> None:
        """Calling acreate should emit a DeprecationWarning."""
        import asyncio

        from fireworks import AsyncFireworks

        async def _check() -> None:
            client = AsyncFireworks(api_key="test", base_url="http://localhost:9999")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                try:
                    await client.chat.completions.acreate(  # type: ignore[attr-defined]
                        model="test",
                        messages=[{"role": "user", "content": "hi"}],
                    )
                except Exception:
                    pass  # Connection refused is expected — we just want the warning
                deprecations = [x for x in w if issubclass(x.category, DeprecationWarning)]
                assert any("acreate" in str(d.message) for d in deprecations), (
                    f"Expected DeprecationWarning about acreate, got: {[str(d.message) for d in deprecations]}"
                )

        asyncio.run(_check())


class TestTrainingSdkExtras:
    """Verify training-sdk extras install correctly without heavy deps."""

    def test_training_sdk_import(self) -> None:
        """Training SDK should import with only tinker+requests.

        Note: tinker transitively imports torch (via tinker.types.tensor_data),
        so torch is still required at runtime. The training-sdk extra removes
        the *other* heavy deps (transformers, datasets, tiktoken, wandb,
        tinker-cookbook) that the SDK never imports.
        """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from fireworks.training import sdk

            assert sdk is not None
        except ImportError:
            pytest.skip("training-sdk extras not installed")
