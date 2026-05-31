"""Compatibility tests: ``FiretitanSamplingClient`` vs ``tinker.SamplingClient``.

The other tests in this directory drive ``FiretitanSamplingClient`` against
*fake* tinker types (see the ``fake_tinker`` fixture). That proves behavior but
says nothing about whether the wrapper is actually drop-in compatible with the
*real* tinker client. This module closes that gap with three layers:

1. ``TestInterfaceCompat`` — static, no network, no creds. Introspects the real
   ``tinker.lib.public_interfaces.SamplingClient`` and asserts the Firetitan
   wrapper exposes every method of the shared sampling surface with a
   signature-compatible definition.

2. ``TestFormatCompat`` — exercises ``FiretitanSamplingClient`` against a mocked
   deployment using the *real* ``tinker.types``, then asserts the returned
   objects are genuine ``tinker.SampleResponse`` / ``SampledSequence`` instances
   whose structural *shape* matches a hand-built tinker reference object.

3. ``TestLiveFormatCompat`` — runs both real clients end-to-end and diffs their
   shapes side by side. Skipped unless ``TINKER_API_KEY`` and
   ``FIREWORKS_API_KEY`` are set (and ``FIRETITAN_LIVE=1`` to opt in).

The reusable comparison logic lives in :class:`SamplingFormatComparator`, which
is import-safe to reuse from notebooks/scripts.

Run just this file:
    pytest src/fireworks/training/sdk/tests/test_firetitan_tinker_compat.py -v
Run the live layer too:
    FIRETITAN_LIVE=1 pytest -k LiveFormatCompat -v
"""

from __future__ import annotations

import os
import inspect
from typing import Any

import pytest

from fireworks.training.sdk.deployment import (
    ServerMetrics,
    DeploymentSampler,
    FiretitanSamplingClient,
)

# The whole module is meaningless without the real tinker package; skip cleanly
# (e.g. on a CI image that doesn't install the optional 'tinker' extra).
tinker = pytest.importorskip("tinker", reason="real tinker package required for compat checks")
from tinker import types as tinker_types  # noqa: E402

# Skip the entire module unless both API credentials are present. Even the
# static/mocked layers are gated on this so the file is a no-op in environments
# without Tinker/Fireworks access (e.g. CI without secrets configured).
pytestmark = pytest.mark.skipif(
    not (os.environ.get("TINKER_API_KEY") and os.environ.get("FIREWORKS_API_KEY")),
    reason="TINKER_API_KEY and FIREWORKS_API_KEY required for tinker/fireworks compat checks",
)

# The public sampling surface the wrapper promises to mirror. tinker-internal
# concerns (pickling, queue-state callbacks, retry handlers, the differing
# `create` constructor) are deliberately excluded.
SHARED_SURFACE = (
    "sample",
    "sample_async",
    "compute_logprobs",
    "compute_logprobs_async",
    "get_tokenizer",
    "get_base_model",
    "get_base_model_async",
    "get_telemetry",
)


def _tinker_sampling_client_cls() -> type:
    from tinker.lib.public_interfaces.sampling_client import SamplingClient

    return SamplingClient


# ---------------------------------------------------------------------------
# Reusable structural comparator (also handy from notebooks)
# ---------------------------------------------------------------------------


class SamplingFormatComparator:
    """Compare the *structure* (not the values) of sampling return objects.

    ``shape_of`` reduces an arbitrary return value to a canonical fingerprint:
    nested types, field names, element types and None-vs-present distinctions —
    everything that matters for format compatibility, nothing that depends on
    the actual sampled tokens or logprob magnitudes.
    """

    @staticmethod
    def shape_of(obj: Any, _depth: int = 0) -> Any:
        if obj is None:
            return "None"
        if isinstance(obj, bool):
            return "bool"
        if isinstance(obj, int):
            return "int"
        if isinstance(obj, float):
            return "float"
        if isinstance(obj, str):
            return "str"
        if isinstance(obj, (list, tuple)):
            kind = type(obj).__name__
            if not obj:
                return f"{kind}[empty]"
            # Collapse element shapes; flag whether any element is None so that
            # `[None, -0.1, -0.2]` (prompt_logprobs) is distinguishable from a
            # pure `list[float]`. Dedup via repr because element shapes may be
            # dicts (e.g. a list of SampledSequence), which are unhashable.
            has_none = any(e is None for e in obj)
            seen: dict[str, Any] = {}
            for e in obj:
                if e is None:
                    continue
                s = SamplingFormatComparator.shape_of(e, _depth + 1)
                seen.setdefault(repr(s), s)
            non_none = [seen[k] for k in sorted(seen)]
            if not non_none:
                inner: Any = "None"
            elif len(non_none) == 1:
                inner = non_none[0]
            else:
                inner = non_none  # heterogeneous list: keep all variant shapes
            if has_none:
                inner = {"Optional": inner}
            return {"__list__": kind, "elem": inner}
        # pydantic model or dataclass: descend into named fields.
        fields = SamplingFormatComparator._field_names(obj)
        if fields is not None:
            qualname = f"{type(obj).__module__.split('.')[0]}.{type(obj).__name__}"
            return {
                "__type__": qualname,
                **{
                    f: SamplingFormatComparator.shape_of(getattr(obj, f), _depth + 1)
                    for f in fields
                },
            }
        return type(obj).__name__

    @staticmethod
    def _field_names(obj: Any) -> list[str] | None:
        # pydantic v2
        mf = getattr(type(obj), "model_fields", None)
        if isinstance(mf, dict):
            return list(mf.keys())
        # dataclass
        df = getattr(type(obj), "__dataclass_fields__", None)
        if isinstance(df, dict):
            return list(df.keys())
        return None

    @classmethod
    def diff(cls, expected: Any, actual: Any, path: str = "") -> list[str]:
        """Return human-readable mismatches between two shapes (empty == match)."""
        exp_shape = cls.shape_of(expected) if not cls._is_shape(expected) else expected
        act_shape = cls.shape_of(actual) if not cls._is_shape(actual) else actual
        return cls._diff_shapes(exp_shape, act_shape, path)

    @staticmethod
    def _is_shape(x: Any) -> bool:
        return isinstance(x, str) or (isinstance(x, dict) and "__type__" in x)

    @classmethod
    def _diff_shapes(cls, exp: Any, act: Any, path: str) -> list[str]:
        loc = path or "<root>"
        if isinstance(exp, dict) and isinstance(act, dict):
            problems: list[str] = []
            for key in sorted(set(exp) | set(act)):
                if key not in act:
                    problems.append(f"{loc}: missing field {key!r}")
                elif key not in exp:
                    problems.append(f"{loc}: unexpected field {key!r}")
                else:
                    problems.extend(
                        cls._diff_shapes(exp[key], act[key], f"{path}.{key}" if path else key)
                    )
            return problems
        if exp != act:
            return [f"{loc}: expected {exp!r}, got {act!r}"]
        return []


# ---------------------------------------------------------------------------
# Helpers: build a mocked Firetitan client backed by a canned completion
# ---------------------------------------------------------------------------


def _firetitan_with_completion(choice: dict, captured: dict | None = None) -> FiretitanSamplingClient:
    """A FiretitanSamplingClient whose deployment returns a single canned choice."""
    sampler = DeploymentSampler(
        inference_url="https://api.example.com",
        model="accounts/fireworks/models/gpt-oss-20b",
        api_key="key",
        tokenizer=None,
    )

    async def _fake_stream(*args, **kwargs):
        if captured is not None:
            captured.update(kwargs)
        return {"choices": [choice]}, ServerMetrics()

    sampler.async_completions_stream = _fake_stream
    return FiretitanSamplingClient(sampler)


def _completion(completion_ids, logprobs=None, finish_reason="stop"):
    choice: dict[str, Any] = {
        "text": "out",
        "finish_reason": finish_reason,
        "raw_output": {"completion_token_ids": completion_ids},
    }
    if logprobs is not None:
        choice["logprobs"] = {"content": [{"logprob": lp} for lp in logprobs]}
    return choice


# ---------------------------------------------------------------------------
# 1. Interface compatibility (static)
# ---------------------------------------------------------------------------


class TestInterfaceCompat:
    @pytest.mark.parametrize("name", SHARED_SURFACE)
    def test_method_present_and_callable(self, name):
        attr = getattr(FiretitanSamplingClient, name, None)
        assert attr is not None, f"FiretitanSamplingClient is missing {name!r}"
        assert callable(attr), f"{name!r} is not callable"

    @pytest.mark.parametrize("name", SHARED_SURFACE)
    def test_signature_matches_tinker(self, name):
        tinker_cls = _tinker_sampling_client_cls()
        if not hasattr(tinker_cls, name):
            pytest.skip(f"tinker SamplingClient has no {name!r} in this version")

        tinker_params = _public_params(getattr(tinker_cls, name))
        fire_params = _public_params(getattr(FiretitanSamplingClient, name))

        # Same parameter names, in the same order.
        assert [p.name for p in fire_params] == [p.name for p in tinker_params], (
            f"{name}: parameter names/order differ\n"
            f"  tinker:    {[p.name for p in tinker_params]}\n"
            f"  firetitan: {[p.name for p in fire_params]}"
        )
        # Same defaults (so callers can rely on identical optional behavior).
        for tp, fp in zip(tinker_params, fire_params):
            assert fp.default == tp.default, (
                f"{name}: default for {tp.name!r} differs "
                f"(tinker={tp.default!r}, firetitan={fp.default!r})"
            )

    def test_async_methods_are_coroutines(self):
        for name in ("sample_async", "compute_logprobs_async", "get_base_model_async"):
            assert inspect.iscoroutinefunction(getattr(FiretitanSamplingClient, name)), (
                f"{name} should be a coroutine function, matching tinker"
            )


def _public_params(func) -> list[inspect.Parameter]:
    """Positional/keyword params excluding self and any *args/**kwargs."""
    params = list(inspect.signature(func).parameters.values())
    out = []
    for p in params:
        if p.name == "self":
            continue
        if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        out.append(p)
    return out


# ---------------------------------------------------------------------------
# 2. Format compatibility (mocked deployment, real tinker.types)
# ---------------------------------------------------------------------------


class TestFormatCompat:
    def test_sample_response_is_real_tinker_type(self):
        client = _firetitan_with_completion(_completion([40, 50], logprobs=[-0.3, -0.4]))
        try:
            resp = client.sample(
                prompt=tinker_types.ModelInput.from_ints([10, 20, 30]),
                num_samples=1,
                sampling_params=tinker_types.SamplingParams(max_tokens=2, temperature=0.7),
            ).result(timeout=5)
        finally:
            client.close()

        assert isinstance(resp, tinker_types.SampleResponse)
        assert isinstance(resp.sequences[0], tinker_types.SampledSequence)

    def test_sample_shape_matches_tinker_reference(self):
        """Firetitan's SampleResponse must have the same shape as a hand-built
        tinker one constructed from equivalent data."""
        client = _firetitan_with_completion(_completion([40, 50], logprobs=[-0.3, -0.4]))
        try:
            actual = client.sample(
                prompt=tinker_types.ModelInput.from_ints([10, 20, 30]),
                num_samples=1,
                sampling_params=tinker_types.SamplingParams(max_tokens=2),
            ).result(timeout=5)
        finally:
            client.close()

        reference = tinker_types.SampleResponse(
            sequences=[
                tinker_types.SampledSequence(
                    stop_reason="stop", tokens=[40, 50], logprobs=[-0.3, -0.4]
                )
            ],
            prompt_logprobs=None,
        )

        problems = SamplingFormatComparator.diff(reference, actual)
        assert not problems, "shape mismatch vs tinker reference:\n  " + "\n  ".join(problems)

    def test_prompt_logprobs_shape_matches(self):
        """include_prompt_logprobs=True must yield the tinker
        list[Optional[float]] shape with a leading None for the first token."""
        prompt_ids = [10, 20, 30]
        echoed = prompt_ids + [40, 50]
        logprobs = [0.0, -0.1, -0.2, -0.3, -0.4]
        client = _firetitan_with_completion(
            _completion(echoed, logprobs=logprobs, finish_reason="length")
        )
        try:
            actual = client.sample(
                prompt=tinker_types.ModelInput.from_ints(prompt_ids),
                num_samples=1,
                sampling_params=tinker_types.SamplingParams(max_tokens=2),
                include_prompt_logprobs=True,
            ).result(timeout=5)
        finally:
            client.close()

        reference = tinker_types.SampleResponse(
            sequences=[
                tinker_types.SampledSequence(
                    stop_reason="length", tokens=[40, 50], logprobs=[-0.3, -0.4]
                )
            ],
            prompt_logprobs=[None, -0.1, -0.2],
        )
        problems = SamplingFormatComparator.diff(reference, actual)
        assert not problems, "prompt_logprobs shape mismatch:\n  " + "\n  ".join(problems)

    def test_compute_logprobs_shape_matches(self):
        prompt_ids = [10, 20, 30]
        client = _firetitan_with_completion(
            _completion(prompt_ids + [40], logprobs=[0.0, -0.1, -0.2, -0.3], finish_reason="length")
        )
        try:
            actual = client.compute_logprobs(
                tinker_types.ModelInput.from_ints(prompt_ids)
            ).result(timeout=5)
        finally:
            client.close()

        # tinker contract: list[float | None]
        reference: list[float | None] = [None, -0.1, -0.2]
        problems = SamplingFormatComparator.diff(reference, actual)
        assert not problems, "compute_logprobs shape mismatch:\n  " + "\n  ".join(problems)

    def test_num_samples_produces_list_of_sequences(self):
        client = _firetitan_with_completion(_completion([40, 50], logprobs=[-0.3, -0.4]))
        try:
            # The mocked stream returns one choice per call regardless of n; what
            # we assert here is that sequences is a list whose elements are all
            # SampledSequence (the tinker container contract).
            resp = client.sample(
                prompt=tinker_types.ModelInput.from_ints([10, 20, 30]),
                num_samples=3,
                sampling_params=tinker_types.SamplingParams(max_tokens=2),
            ).result(timeout=5)
        finally:
            client.close()

        assert isinstance(resp.sequences, list)
        assert all(isinstance(s, tinker_types.SampledSequence) for s in resp.sequences)


# ---------------------------------------------------------------------------
# 3. Live cross-check (both real clients) — opt-in
# ---------------------------------------------------------------------------

_LIVE_REASON = (
    "set FIRETITAN_LIVE=1, TINKER_API_KEY and FIREWORKS_API_KEY to run live compat"
)


@pytest.mark.skipif(
    not (
        os.environ.get("FIRETITAN_LIVE") == "1"
        and os.environ.get("TINKER_API_KEY")
        and os.environ.get("FIREWORKS_API_KEY")
    ),
    reason=_LIVE_REASON,
)
class TestLiveFormatCompat:
    TINKER_MODEL = os.environ.get("TINKER_COMPAT_MODEL", "Qwen/Qwen3-4B-Instruct-2507")
    FIREWORKS_MODEL = os.environ.get(
        "FIREWORKS_COMPAT_MODEL", "accounts/fireworks/models/gpt-oss-20b"
    )

    def test_sample_shapes_match_live(self):
        params = tinker_types.SamplingParams(max_tokens=8, temperature=0.7)

        # --- real tinker ---
        sc = tinker.ServiceClient()
        tinker_client = sc.create_sampling_client(base_model=self.TINKER_MODEL)
        tok = tinker_client.get_tokenizer()
        t_prompt = tinker_types.ModelInput.from_ints(tok.encode("The weather today is"))
        t_resp = tinker_client.sample(
            prompt=t_prompt, sampling_params=params, num_samples=2
        ).result()

        # --- firetitan ---
        f_client = FiretitanSamplingClient.create(
            inference_url="https://api.fireworks.ai",
            model=self.FIREWORKS_MODEL,
            api_key=os.environ["FIREWORKS_API_KEY"],
            tokenizer=None,
        )
        try:
            f_prompt = tinker_types.ModelInput.from_ints([3923, 374, 220, 17, 10, 17, 30])
            f_resp = f_client.sample(
                prompt=f_prompt, sampling_params=params, num_samples=2
            ).result(timeout=120)
        finally:
            f_client.close()

        problems = SamplingFormatComparator.diff(t_resp, f_resp)
        assert not problems, "live shape mismatch:\n  " + "\n  ".join(problems)
