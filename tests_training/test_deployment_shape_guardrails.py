"""Tests for training-profile-derived deployment shape guardrails."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from fireworks.training.sdk.deployment import DeploymentConfig, DeploymentManager


def test_config_from_training_profile_pins_rft_deployment_shape() -> None:
    profile = SimpleNamespace(deployment_shape="accounts/fireworks/deploymentShapes/rft-qwen3/versions/v1")

    config = DeploymentConfig.from_training_profile(
        deployment_id="dep-1",
        base_model="accounts/fireworks/models/qwen3",
        profile=profile,
        region="US_VIRGINIA_1",
    )

    assert config.deployment_shape == profile.deployment_shape
    assert config.expected_deployment_shape == profile.deployment_shape
    body = DeploymentManager._build_deployment_body(config)
    assert body["deploymentShape"] == profile.deployment_shape


def test_config_from_training_profile_requires_deployment_shape() -> None:
    profile = SimpleNamespace(deployment_shape=None, deployment_shape_version="")

    with pytest.raises(ValueError, match="deployment_shape_version"):
        DeploymentConfig.from_training_profile(
            deployment_id="dep-1",
            base_model="accounts/fireworks/models/qwen3",
            profile=profile,
        )


def test_create_rejects_deployment_shape_that_conflicts_with_profile() -> None:
    manager = DeploymentManager(
        api_key="test-key",
        base_url="https://api.example.com",
    )
    manager._account_id = "test-acct"
    manager._post = MagicMock(side_effect=AssertionError("request should fail before POST"))
    expected_shape = "accounts/fireworks/deploymentShapes/rft-qwen3/versions/v1"

    with pytest.raises(ValueError, match="does not match the RFT deployment shape"):
        manager._create_deployment(
            DeploymentConfig(
                deployment_id="dep-1",
                base_model="accounts/fireworks/models/qwen3",
                deployment_shape="accounts/fireworks/deploymentShapes/qwen3-fast/versions/v2",
                expected_deployment_shape=expected_shape,
            )
        )

    manager._post.assert_not_called()
    manager.close()
