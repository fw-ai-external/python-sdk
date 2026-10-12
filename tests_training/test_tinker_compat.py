from __future__ import annotations

import pytest

from fireworks.training.sdk import (
    install_tinker_service_client,
    patched_tinker_service_client,
    restore_tinker_service_client,
)
from fireworks.training.sdk.client import FiretitanServiceClient


def test_install_tinker_service_client_patches_and_restores() -> None:
    import tinker

    original = tinker.ServiceClient
    patched_original = install_tinker_service_client(
        model_name="accounts/acct/models/qwen3-8b",
        tokenizer_model="Qwen/Qwen3-8B",
        lora_rank=8,
        deployment_id="dep-1",
    )

    try:
        assert patched_original is original
        service = tinker.ServiceClient(
            {"owner": "cookbook"},
            project_id="proj-1",
            base_url="https://api.test",
            api_key="fw-key",
            default_headers={"x-route": "1"},
        )

        assert isinstance(service, FiretitanServiceClient)
        assert service._managed_config.base_model == "accounts/acct/models/qwen3-8b"
        assert service._managed_config.tokenizer_model == "Qwen/Qwen3-8B"
        assert service._managed_config.lora_rank == 8
        assert service._managed_config.deployment_id == "dep-1"
        assert service._managed_base_url == "https://api.test"
        assert service._fireworks_api_key == "fw-key"
        assert service._managed_additional_headers == {"x-route": "1"}
        assert service._default_user_metadata == {"owner": "cookbook"}
        assert service._default_project_id == "proj-1"
    finally:
        restore_tinker_service_client(original)

    assert tinker.ServiceClient is original


def test_patched_service_client_context_manager_restores() -> None:
    import tinker

    original = tinker.ServiceClient
    with patched_tinker_service_client(
        model_name="accounts/acct/models/base",
    ):
        service = tinker.ServiceClient(base_url="https://api.test", api_key="fw-key")

        assert isinstance(service, FiretitanServiceClient)
        assert service._managed_base_url == "https://api.test"

    assert tinker.ServiceClient is original


def test_patched_service_client_rejects_unknown_service_kwargs() -> None:
    import tinker

    original = tinker.ServiceClient
    install_tinker_service_client(model_name="accounts/acct/models/base")

    try:
        with pytest.raises(TypeError, match="Unsupported"):
            tinker.ServiceClient(base_url="https://api.test", unsupported=True)
    finally:
        restore_tinker_service_client(original)
