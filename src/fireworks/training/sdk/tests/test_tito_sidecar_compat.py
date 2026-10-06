"""Synthetic HTTP regressions for container access and tool-call round trips."""

from __future__ import annotations

import os
import json
import socket
import asyncio
import subprocess
from typing import Any
from collections.abc import Mapping, Sequence

import httpx
import pytest
from openai import AsyncOpenAI

from fireworks.training.sdk.tito import TITOSidecar, TITOChatRequest, TITOParsedAssistant, TrajectoryDriftPolicy
from fireworks.training.sdk.tito._artifact import _turn, _request, _turn_value, _request_value
from fireworks.training.sdk.tests.test_tito import FakeSampler, FakeRenderer

_ARGUMENTS = ('{ "z": 1, "a": {"y": 2, "b": 3} }', '{"path":"x","command":"ls"}')
_CALLS = [
    {
        "id": f"call-{index}",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }
    for index, (name, arguments) in enumerate(zip(("search", "run"), _ARGUMENTS))
]


class _ToolRenderer(FakeRenderer):
    def render_conversation_tokens(self, request: TITOChatRequest) -> Sequence[int]:
        # Use the admitted wire history, as the certified HF renderers do.
        messages = (request.wire_value() or {}).get("messages", request.messages)
        output = [1]
        for message in messages:
            if message["role"] == "assistant" and message.get("tool_calls"):
                output.extend([2, *self._text(self._tool_text(message)), 3])
            else:
                output.extend(self._message(message))
        return [*output, 2]

    @staticmethod
    def _tool_text(message: Mapping[str, Any]) -> str:
        return "|".join(call["function"]["arguments"] for call in message["tool_calls"])

    def parse_assistant(
        self,
        request: TITOChatRequest,
        completion_ids: Sequence[int],
        completion_text: str,
        finish_reason: str,
    ) -> TITOParsedAssistant:
        return TITOParsedAssistant(
            message={"role": "assistant", "content": None, "tool_calls": _CALLS},
            output_kind="tool_calls",
        )


def _sidecar(**kwargs: Any) -> TITOSidecar:
    renderer = _ToolRenderer()
    output = [*renderer._text(renderer._tool_text({"tool_calls": _CALLS})), 3]
    return TITOSidecar.from_deployment_sampler(
        FakeSampler(outputs=(output,)),
        renderer=renderer,
        max_context_tokens=4096,
        max_output_tokens=512,
        **kwargs,
    )


@pytest.mark.parametrize("stream,echo_indices", [(False, False), (True, False), (True, True)])
async def test_http_preserves_tool_arguments_and_stream_indices(stream: bool, echo_indices: bool) -> None:
    sidecar = _sidecar()
    await sidecar.start()
    try:
        trajectory = sidecar.create_trajectory()
        headers = {"authorization": f"Bearer {trajectory.api_key}", "idempotency-key": "tools"}
        payload = {"messages": [{"role": "user", "content": "q"}], "stream": stream}
        async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
            first = await client.post(f"{trajectory.openai_base_url}/chat/completions", headers=headers, json=payload)
            replay = await client.post(f"{trajectory.openai_base_url}/chat/completions", headers=headers, json=payload)
            assert first.status_code == replay.status_code == 200
            if stream:
                chunks = [json.loads(line[6:]) for line in first.text.splitlines() if line.startswith("data: {")]
                message = chunks[0]["choices"][0]["delta"]
                assert [call["index"] for call in message["tool_calls"]] == [0, 1]
                assert chunks[1]["choices"][0]["delta"] == {}
                assert "data: [DONE]" in first.text
                if not echo_indices:
                    for call in message["tool_calls"]:
                        call.pop("index")
            else:
                assert first.content == replay.content
                message = first.json()["choices"][0]["message"]
                assert all("index" not in call for call in message["tool_calls"])
            assert [call["function"]["arguments"] for call in message["tool_calls"]] == list(_ARGUMENTS)
            assert message["tool_calls"] == (
                [dict(call, index=index) for index, call in enumerate(_CALLS)] if echo_indices else _CALLS
            )
            followup = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers={"authorization": f"Bearer {trajectory.api_key}"},
                json={
                    "messages": [
                        *payload["messages"],
                        message,
                        {"role": "tool", "tool_call_id": "call-0", "content": "ok"},
                    ]
                },
            )
            assert followup.status_code == 200
        artifact = await sidecar.finish_trajectory(trajectory.trajectory_id)
        assert len(artifact.segments) == 1
        assert artifact.segments[0].turns[1].prompt_disposition == "append"
        assert artifact.metrics.counters.get("lineage/boundary_reason_history_rewrite", 0) == 0
        followup_request = artifact.segments[0].turns[1].request
        assert all("index" not in call for call in followup_request.messages[1]["tool_calls"])
        if echo_indices:
            assert [call["index"] for call in followup_request.wire_value()["messages"][1]["tool_calls"]] == [0, 1]
        restored = type(artifact).unpack(artifact.pack())
        for value in (artifact, restored):
            assistant = value.segments[0].turns[0].assistant
            assert assistant.response_message["tool_calls"][0]["function"]["arguments"] == _ARGUMENTS[0]
            assert assistant.message["tool_calls"][0]["function"]["arguments"] == '{"a":{"b":3,"y":2},"z":1}'
            assert all("index" not in call for call in assistant.message["tool_calls"])
        legacy = _turn_value(artifact.segments[0].turns[0])
        legacy["assistant"].pop("response_message")
        assert _turn(legacy).assistant.message == artifact.segments[0].turns[0].assistant.message
        conflicting = json.loads(json.dumps(_turn_value(artifact.segments[0].turns[0])))
        conflicting["assistant"]["response_message"]["tool_calls"][0]["function"]["name"] = "different"
        with pytest.raises(ValueError, match="differs from canonical"):
            _turn(conflicting)
    finally:
        await sidecar.close()


def test_response_arguments_are_detached_and_objects_keep_order() -> None:
    arguments = {"z": {"y": 2, "a": 1}, "b": 3}
    parsed = TITOParsedAssistant(
        message={
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {"type": "function", "function": {"name": "run", "arguments": arguments}},
            ],
        }
    )
    arguments["z"]["y"] = 99
    assert parsed.response_message["tool_calls"][0]["function"]["arguments"] == '{"z":{"y":2,"a":1},"b":3}'
    assert parsed.message["tool_calls"][0]["function"]["arguments"] == '{"b":3,"z":{"a":1,"y":2}}'


def test_stream_indices_normalize_only_at_request_admission() -> None:
    calls = [dict(call, index=index) for index, call in enumerate(_CALLS)]
    payload = {"messages": [{"role": "assistant", "content": None, "tool_calls": calls}]}
    original = json.dumps(payload)
    request = TITOChatRequest.from_openai(payload, wire_request_body=original)
    assert json.dumps(payload) == original
    assert request.wire_request_body == original
    assert request.wire_value() == payload
    assert all("index" not in call for call in request.messages[0]["tool_calls"])
    assert "messages[0].tool_calls[0].index:stream_index_removed" in request.normalization_steps
    assert "messages[0].tool_calls[1].index:stream_index_removed" in request.normalization_steps

    legacy = TITOChatRequest(messages=tuple(payload["messages"]))
    restored = _request(json.loads(json.dumps(_request_value(legacy))))
    assert [call["index"] for call in restored.messages[0]["tool_calls"]] == [0, 1]
    assert restored.canonical_value() == legacy.canonical_value()


@pytest.mark.parametrize("address", ["127.0.0.2", "::1"])
async def test_sidecar_binds_and_advertises_specific_address(address: str) -> None:
    if address == "::1":
        probe = socket.socket(socket.AF_INET6)
        try:
            probe.bind((address, 0))
        except OSError:
            pytest.skip("IPv6 loopback is unavailable")
        finally:
            probe.close()
    sidecar = _sidecar(bind_address=address)
    await sidecar.start()
    try:
        trajectory = sidecar.create_trajectory()
        host = f"[{address}]" if ":" in address else address
        assert trajectory.openai_base_url.startswith(f"http://{host}:{sidecar.port}/")
        assert sidecar._site._server.sockets[0].getsockname()[0] == address
        async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
            response = await client.get(
                f"{trajectory.openai_base_url}/models", headers={"authorization": f"Bearer {trajectory.api_key}"}
            )
            assert response.status_code == 200
            assert (await client.get(f"{trajectory.openai_base_url}/models")).status_code == 401
    finally:
        await sidecar.close()


@pytest.mark.parametrize("address", ["", "localhost", "0.0.0.0", "::", "127.0.0.1:8080"])
def test_sidecar_requires_specific_ip_address(address: str) -> None:
    with pytest.raises(ValueError, match="bind_address"):
        _sidecar(bind_address=address)


@pytest.mark.parametrize("arguments", ["not-json", '{"z":"\u00e9","a":"  x  "}', '{"z":1,"z":2,"a":3}'])
def test_parser_argument_strings_are_never_reencoded(arguments: str) -> None:
    parsed = TITOParsedAssistant(
        message={
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {"type": "function", "function": {"name": "run", "arguments": arguments}},
            ],
        }
    )
    assert parsed.response_message["tool_calls"][0]["function"]["arguments"] == arguments


async def test_semantic_argument_equivalence_does_not_bypass_token_drift() -> None:
    sidecar = _sidecar(default_drift_policy=TrajectoryDriftPolicy(max_masked_tokens=0))
    await sidecar.start()
    try:
        trajectory = sidecar.create_trajectory()
        headers = {"authorization": f"Bearer {trajectory.api_key}"}
        payload = {"messages": [{"role": "user", "content": "q"}]}
        async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
            first = await client.post(f"{trajectory.openai_base_url}/chat/completions", headers=headers, json=payload)
            message = first.json()["choices"][0]["message"]
            for call in message["tool_calls"]:
                call["function"]["arguments"] = json.dumps(json.loads(call["function"]["arguments"]), sort_keys=True)
            followup = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers=headers,
                json={
                    "messages": [
                        *payload["messages"],
                        message,
                        {"role": "tool", "content": "ok", "tool_call_id": "call-0"},
                    ]
                },
            )
            assert followup.status_code == 200
        artifact = await sidecar.finish_trajectory(trajectory.trajectory_id)
        assert len(artifact.segments) == 2
        assert artifact.segments[1].start_reason == "token_drift"
    finally:
        await sidecar.close()


async def test_failed_bind_leaves_sidecar_restartable() -> None:
    sidecar = _sidecar()
    with socket.socket() as occupied:
        occupied.bind(("127.0.0.1", 0))
        occupied.listen()
        with pytest.raises(OSError):
            await sidecar.start(port=occupied.getsockname()[1])
    assert sidecar.port == 0
    await sidecar.start()
    try:
        assert sidecar.create_trajectory().openai_base_url.startswith("http://127.0.0.1:")
    finally:
        await sidecar.close()


async def test_openai_stream_assembler_keeps_parallel_calls_separate() -> None:
    sidecar = _sidecar()
    await sidecar.start()
    try:
        trajectory = sidecar.create_trajectory()
        async with AsyncOpenAI(base_url=trajectory.openai_base_url, api_key=trajectory.api_key) as client:
            async with client.chat.completions.stream(
                model="policy", messages=[{"role": "user", "content": "q"}]
            ) as stream:
                result = await stream.get_final_completion()
        calls = result.choices[0].message.tool_calls
        assert [call.function.name for call in calls] == ["search", "run"]
        assert [call.function.arguments for call in calls] == list(_ARGUMENTS)
    finally:
        await sidecar.close()


@pytest.mark.skipif(not os.environ.get("FIREWORKS_TITO_DOCKER_TEST_IMAGE"), reason="optional Docker integration")
async def test_bridge_container_can_reach_host_sidecar_without_host_networking() -> None:
    config = json.loads(
        subprocess.check_output(
            [
                "docker",
                "network",
                "inspect",
                "bridge",
                "--format",
                "{{json .IPAM.Config}}",
            ],
            text=True,
        )
    )
    sidecar = _sidecar(bind_address=config[0]["Gateway"])
    await sidecar.start()
    try:
        trajectory = sidecar.create_trajectory()
        # Pass the temporary trajectory key on stdin, not in Docker argv/env.
        script = (
            "import json,sys,urllib.request; d=json.load(sys.stdin); "
            "r=urllib.request.Request(d['url']+'/models', headers={'Authorization':'Bearer '+d['key']}); "
            "o=urllib.request.build_opener(urllib.request.ProxyHandler({})).open(r, timeout=5); "
            "assert o.status==200; assert json.load(o)['object']=='list'"
        )
        completed = await asyncio.to_thread(
            subprocess.run,
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "bridge",
                "-i",
                "--entrypoint",
                "python3",
                os.environ["FIREWORKS_TITO_DOCKER_TEST_IMAGE"],
                "-c",
                script,
            ],
            input=json.dumps({"url": trajectory.openai_base_url, "key": trajectory.api_key}),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
    finally:
        await sidecar.close()
