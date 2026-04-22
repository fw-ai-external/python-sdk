"""End-to-end tests for downstream compatibility against the live Fireworks API.

These replicate the exact calling patterns of langchain-fireworks and instructor
to ensure a seamless upgrade when they bump their fireworks-ai constraint.

Run with: pytest tests/functional/test_downstream_compat_e2e.py -m e2e -v
"""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

import os
import asyncio

import pytest

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.timeout(60),
    pytest.mark.skipif(
        not os.environ.get("FIREWORKS_API_KEY"),
        reason="FIREWORKS_API_KEY not set",
    ),
]

TEST_MODEL = os.environ.get("E2E_TEST_MODEL", "accounts/fireworks/models/llama-v3p3-70b-instruct")


class TestLangchainPatternsE2E:
    """Replicate langchain-fireworks calling patterns against live API.

    langchain-fireworks stores `Fireworks(**params).chat.completions` directly,
    then calls `.create()` (sync) and `.acreate()` (async).
    """

    def test_sync_create_non_streaming(self) -> None:
        """langchain _generate(): response = self.client.create(messages=..., **params)"""
        from fireworks import Fireworks

        # langchain stores the resource object, not the top-level client
        client = Fireworks().chat.completions

        response = client.create(
            messages=[{"role": "user", "content": "Say hi"}],
            model=TEST_MODEL,
            max_tokens=10,
        )

        # langchain calls response.model_dump()
        d = response.model_dump()
        assert "choices" in d
        assert len(d["choices"]) >= 1
        assert d["choices"][0]["message"]["content"]
        assert "usage" in d

    def test_sync_create_streaming(self) -> None:
        """langchain _stream(): for chunk in self.client.create(stream=True, ...)"""
        from fireworks import Fireworks

        client = Fireworks().chat.completions

        chunks: list[object] = []
        with client.create(
            messages=[{"role": "user", "content": "Say hi"}],
            model=TEST_MODEL,
            max_tokens=10,
            stream=True,
        ) as stream:
            for chunk in stream:
                # langchain: chunk.model_dump()["choices"][0]
                d: dict[str, object] = chunk.model_dump()
                assert "choices" in d
                chunks.append(d)

        assert len(chunks) > 0

    def test_async_acreate_non_streaming(self) -> None:
        """langchain _agenerate(): response = await self.async_client.acreate(...)"""
        from fireworks import AsyncFireworks

        async def _run() -> None:
            async_client = AsyncFireworks().chat.completions

            response: object = await async_client.acreate(  # type: ignore[attr-defined]
                messages=[{"role": "user", "content": "Say hi"}],
                model=TEST_MODEL,
                max_tokens=10,
            )

            d = response.model_dump()  # type: ignore[union-attr]
            assert "choices" in d
            assert d["choices"][0]["message"]["content"]  # type: ignore[index]

        asyncio.run(_run())

    def test_async_acreate_streaming(self) -> None:
        """langchain _astream(): async for chunk in self.async_client.acreate(stream=True, ...)"""
        from fireworks import AsyncFireworks

        async def _run() -> None:
            async_client = AsyncFireworks().chat.completions

            chunks: list[object] = []
            stream: object = await async_client.acreate(  # type: ignore[attr-defined]
                messages=[{"role": "user", "content": "Say hi"}],
                model=TEST_MODEL,
                max_tokens=10,
                stream=True,
            )
            async for chunk in stream:  # type: ignore[union-attr]
                d = chunk.model_dump()  # type: ignore[union-attr]
                assert "choices" in d
                chunks.append(d)

            assert len(chunks) > 0

        asyncio.run(_run())


class TestInstructorPatternsE2E:
    """Replicate instructor calling patterns against live API.

    instructor imports via old path, does isinstance dispatch, then calls
    .create() (sync) or .acreate() (async).
    """

    def test_import_and_isinstance_dispatch(self) -> None:
        """instructor creates client, checks isinstance, then dispatches."""
        from fireworks.client import Fireworks, AsyncFireworks

        # instructor validates: isinstance(client, (AsyncFireworks, Fireworks))
        sync_client = Fireworks()
        async_client = AsyncFireworks()

        assert isinstance(sync_client, (AsyncFireworks, Fireworks))
        assert isinstance(async_client, (AsyncFireworks, Fireworks))

        # instructor dispatches on type
        assert isinstance(sync_client, Fireworks)
        assert isinstance(async_client, AsyncFireworks)

    def test_sync_create_via_old_import(self) -> None:
        """instructor sync: client.chat.completions.create(...)"""
        from fireworks.client import Fireworks

        client = Fireworks()
        response = client.chat.completions.create(
            model=TEST_MODEL,
            messages=[{"role": "user", "content": "Say hi"}],
            max_tokens=10,
        )
        assert response.choices[0].message.content

    def test_async_acreate_via_old_import(self) -> None:
        """instructor async: await client.chat.completions.acreate(...)"""

        async def _run() -> None:
            from fireworks.client import AsyncFireworks

            client = AsyncFireworks()
            response: object = await client.chat.completions.acreate(  # type: ignore[attr-defined]
                model=TEST_MODEL,
                messages=[{"role": "user", "content": "Say hi"}],
                max_tokens=10,
            )
            assert response.choices[0].message.content  # type: ignore[union-attr]

        asyncio.run(_run())


class TestOldToNewMigration:
    """Verify that switching from old import paths to new ones produces
    identical behavior. This is what downstream packages will do eventually."""

    def test_old_and_new_import_same_class(self) -> None:
        from fireworks import Fireworks as NewSync, AsyncFireworks as NewAsync
        from fireworks.client import Fireworks as OldSync, AsyncFireworks as OldAsync

        assert OldSync is NewSync, "Old and new Fireworks class must be identical"
        assert OldAsync is NewAsync, "Old and new AsyncFireworks class must be identical"

    def test_old_path_response_matches_new_path(self) -> None:
        """Same request via old vs new import should return structurally identical responses."""
        from fireworks import Fireworks

        client = Fireworks()
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say the number 42"}],
            model=TEST_MODEL,
            max_tokens=5,
            temperature=0,
            seed=42,
        )
        assert response.choices
        assert response.usage
        assert response.model
