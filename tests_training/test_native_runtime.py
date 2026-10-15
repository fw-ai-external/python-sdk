"""Installation, import and transport contracts of the independent runtime."""

from __future__ import annotations

import ast
import sys
import asyncio
import subprocess
import importlib.metadata
from pathlib import Path

import httpx
import pytest

from fireworks.training import sdk
from fireworks.training.sdk.types import ClientConfigResponse
from fireworks.training.sdk._core._client import AsyncTrainingHTTPClient
from fireworks.training.sdk._core._version import __version__
from fireworks.training.sdk._core.lib._auth_token_provider import resolve_auth_provider
from fireworks.training.sdk._core.lib.internal_client_holder import InternalClientHolder


@pytest.mark.parametrize("version", [(3, 9), (3, 10)])
def test_training_python_floor_fails_before_optional_runtime_imports(version) -> None:
    script = f"""
import sys
import fireworks.training
sys.version_info = {version!r}
try:
    import fireworks.training.sdk
except ImportError as error:
    assert 'requires Python 3.11 or newer' in str(error)
else:
    raise AssertionError('Unsupported training Python version was accepted')
assert 'numpy' not in sys.modules
assert 'pyqwest' not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_native_imports_do_not_load_external_sdk_or_optional_ml_packages() -> None:
    script = """
import importlib.abc
import sys

class BlockExternal(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "tinker" or fullname.startswith("tinker."):
            raise AssertionError("Native SDK imported " + fullname)
        if fullname.split(".")[0] in {"torch", "transformers", "tml_tokenizers"}:
            raise ModuleNotFoundError(fullname)

sys.meta_path.insert(0, BlockExternal())
from fireworks.training import sdk
from fireworks.training.sdk import types
for name in sdk.__all__:
    getattr(sdk, name)
datum = types.Datum(model_input=types.ModelInput.from_ints([1, 2]),
                    loss_fn_inputs={"target_tokens": [2, 3], "weights": [1.0, 0.5]})
assert datum.loss_fn_inputs["weights"].tolist() == [1.0, 0.5]
assert not any(name == "tinker" or name.startswith("tinker.") for name in sys.modules)
"""
    result = subprocess.run([sys.executable, "-c", script], check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_native_source_and_install_metadata_do_not_require_tinker() -> None:
    root = Path(sdk.__file__).parent
    for path in root.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue
            assert not any(module == "tinker" or module.startswith("tinker.") for module in modules), path


@pytest.mark.parametrize(
    "module",
    ["telemetry", "async_client_provider", "api_future_impl", "public_interfaces.api_future"],
)
def test_native_runtime_modules_can_be_imported_first(module: str) -> None:
    script = (
        "import importlib, sys\n"
        f"importlib.import_module('fireworks.training.sdk._core.lib.{module}')\n"
        "from fireworks.training.sdk import FiretitanServiceClient\n"
        "assert 'tinker' not in sys.modules\n"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    requirements = importlib.metadata.requires("fireworks-ai") or []
    assert not any(requirement.lower().startswith("tinker") for requirement in requirements)
    assert __version__ == importlib.metadata.version("fireworks-ai")


def test_concurrent_native_clients_keep_their_own_fireworks_authentication() -> None:
    async def run() -> None:
        observed = []

        def receive(request: httpx.Request) -> httpx.Response:
            observed.append((request.url.path, request.headers["X-API-Key"]))
            return httpx.Response(200, json={"ok": True})

        http_clients = [httpx.AsyncClient(transport=httpx.MockTransport(receive)) for _ in range(2)]
        clients = [
            AsyncTrainingHTTPClient(
                api_key=key,
                base_url="https://trainer.test",
                http_client=http_client,
                _client_config=ClientConfigResponse(use_pyqwest_transport=False),
            )
            for key, http_client in zip(("fw-first", "fw-second"), http_clients)
        ]
        try:
            await asyncio.gather(
                clients[0].get("/first", cast_to=dict[str, bool]),
                clients[1].get("/second", cast_to=dict[str, bool]),
            )
        finally:
            await asyncio.gather(*(client.close() for client in clients))
        assert sorted(observed) == [("/first", "fw-first"), ("/second", "fw-second")]

    asyncio.run(run())


@pytest.mark.parametrize("explicit", [None, "eyJ.explicit.signature"])
@pytest.mark.parametrize("enforce_cmd", [False, True])
def test_native_auth_resolves_fireworks_env_and_jwt_consistently(
    monkeypatch: pytest.MonkeyPatch, explicit: str | None, enforce_cmd: bool
) -> None:
    env_key = "eyJ.mock-jwt.signature"
    monkeypatch.setenv("FIREWORKS_API_KEY", env_key)
    monkeypatch.setenv("TINKER_API_KEY", "unrelated-legacy-key")
    monkeypatch.delenv("TINKER_CREDENTIAL_CMD", raising=False)
    key = explicit or env_key
    # A resolved JWT bypasses the credential command even when enforced.
    provider = resolve_auth_provider(explicit, enforce_cmd=enforce_cmd)
    assert asyncio.run(provider.get_token()) == key

    async def probe() -> None:
        seen = []

        def receive(request: httpx.Request) -> httpx.Response:
            seen.append(request.headers["X-API-Key"])
            return httpx.Response(200, json={})

        client = AsyncTrainingHTTPClient(
            api_key=explicit,
            _auth=provider,
            base_url="https://trainer.test",
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(receive)),
            _client_config=ClientConfigResponse(use_pyqwest_transport=False),
        )
        try:
            await client.get("/probe", cast_to=dict[str, bool])
        finally:
            await client.close()
        assert seen == [key]

    asyncio.run(probe())
    holder = InternalClientHolder(api_key=explicit, _client_config={}, _skip_session=True)
    try:
        assert holder.shadow_kwargs["api_key"] == key
        monkeypatch.setenv("FIREWORKS_API_KEY", "fw-changed-after-construction")
        assert asyncio.run(holder._default_auth.get_token()) == key
        assert holder.shadow_kwargs["api_key"] == key
    finally:
        holder.close()


def test_source_only_runtime_does_not_require_distribution_metadata() -> None:
    script = """
import importlib.metadata
original = importlib.metadata.version
def version(name):
    if name == "fireworks-ai":
        raise importlib.metadata.PackageNotFoundError(name)
    return original(name)
importlib.metadata.version = version
from fireworks.training.sdk._core._version import __version__, PROTOCOL_CLIENT_VERSION
assert __version__ == "0+unknown"
assert PROTOCOL_CLIENT_VERSION == "0.23.0"
from fireworks.training import sdk
service = sdk.ServiceClient(api_key="fw-test", base_url="https://trainer.test", _skip_session=True,
                            _client_config={"use_pyqwest_transport": False})
service.close()
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_native_http_requests_keep_training_protocol_user_agent() -> None:
    async def run() -> None:
        observed = []

        def receive(request: httpx.Request) -> httpx.Response:
            observed.append(request.headers["User-Agent"])
            return httpx.Response(200, json={"ok": True})

        client = AsyncTrainingHTTPClient(
            api_key="fw-test",
            base_url="https://trainer.test",
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(receive)),
        )
        try:
            await client.get("/probe", cast_to=dict[str, bool])
        finally:
            await client.close()
        assert observed == ["AsyncTinker/Python 0.23.0"]

    asyncio.run(run())


def test_native_auth_does_not_implicitly_run_a_credential_command(monkeypatch) -> None:
    from fireworks.training.sdk._core._exceptions import TrainingError

    monkeypatch.delenv("FIREWORKS_API_KEY", raising=False)
    monkeypatch.setenv("TINKER_CREDENTIAL_CMD", "legacy-command")
    monkeypatch.setenv("FIREWORKS_CREDENTIAL_CMD", "native-command")
    with pytest.raises(TrainingError, match="FIREWORKS_API_KEY"):
        resolve_auth_provider(None, enforce_cmd=False)
    provider = resolve_auth_provider(None, enforce_cmd=True)
    assert provider._cmd == "native-command"
    monkeypatch.delenv("FIREWORKS_CREDENTIAL_CMD")
    with pytest.raises(TrainingError, match="FIREWORKS_CREDENTIAL_CMD"):
        resolve_auth_provider(None, enforce_cmd=True)


def test_service_close_exits_without_finalizer_errors() -> None:
    script = """
from fireworks.training import sdk
service = sdk.ServiceClient(api_key="fw-test", _skip_session=True)
service.close()
service.close()
assert service.holder._closed
"""
    result = subprocess.run(
        [sys.executable, "-Werror::RuntimeWarning", "-Werror::ResourceWarning", "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not result.stderr, result.stderr


def test_holder_close_after_loop_shutdown_is_safe() -> None:
    from unittest.mock import Mock

    loop = asyncio.new_event_loop()
    loop.close()
    holder = object.__new__(InternalClientHolder)
    holder._loop = loop
    holder._closed = False
    holder._telemetry = Mock()
    holder.close()
    holder.close()
    assert holder._closed
    holder._telemetry.stop.assert_not_called()


def test_training_tinker_name_exposes_native_sdk_without_external_dependency() -> None:
    script = """
import importlib.abc
import sys
class BlockExternal(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'tinker' or fullname.startswith('tinker.'):
            raise AssertionError(fullname)
sys.meta_path.insert(0, BlockExternal())
from fireworks.training import sdk, tinker
assert tinker is sdk
assert tinker.Datum is sdk.Datum
assert tinker.ServiceClient is sdk.ServiceClient
assert 'tinker' not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
