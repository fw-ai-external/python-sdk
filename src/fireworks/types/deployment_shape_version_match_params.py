# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.
# NOTE: hand-written in generated style (Stainless codegen is currently
# unwired, PR #26426) against the stainless/openapi.yml entry from PR #47681.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "DeploymentShapeVersionMatchParams",
    "DeploymentShapeVersionMatchCreateDeploymentRequest",
    "DeploymentShapeVersionMatchDeployment",
]

# Aliased for export from fireworks.types: bare `Deployment` collides with the
# deployment response model and `CreateDeploymentRequest` with the server-side
# proto name.
# (Export aliases at the bottom of the file, after the class definitions.)


class Deployment(TypedDict, total=False):
    base_model: Required[Annotated[str, PropertyInfo(alias="baseModel")]]
    """The base model the deployment will serve."""

    enable_addons: Annotated[bool, PropertyInfo(alias="enableAddons")]
    """If true, LORA addons are enabled for the deployment."""


class CreateDeploymentRequest(TypedDict, total=False):
    parent: Required[str]
    """The resource name of the parent account, e.g. accounts/fireworks."""

    deployment: Required[Deployment]
    """The properties of the deployment being created."""


class DeploymentShapeVersionMatchParams(TypedDict, total=False):
    account_id: str

    create_deployment_request: Required[
        Annotated[CreateDeploymentRequest, PropertyInfo(alias="createDeploymentRequest")]
    ]
    """The deployment create request to match deployment shape versions for."""


# Aliased for export from fireworks.types: bare `Deployment` collides with the
# deployment response model and `CreateDeploymentRequest` with the server-side
# proto name.
DeploymentShapeVersionMatchCreateDeploymentRequest = CreateDeploymentRequest
DeploymentShapeVersionMatchDeployment = Deployment
