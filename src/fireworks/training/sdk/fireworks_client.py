"""Fireworks platform client for trainer-free operations.

Provides account-level operations that don't require a running trainer
job: checkpoint promotion, training shape resolution, model listing, etc.

:class:`TrainerJobManager` extends this with trainer-specific lifecycle
methods (create, wait, reconnect, delete).
"""

from __future__ import annotations

import re
import logging
from urllib.parse import urlencode

from fireworks.training.sdk.errors import (
    DOCS_SDK,
    CONSOLE_URL,
    parse_api_error,
    format_sdk_error,
)
from fireworks.training.sdk._rest_client import _RestClient

logger = logging.getLogger(__name__)

_RESOURCE_ID_RE = re.compile(r"^[a-z0-9-]+$")


def validate_output_model_id(output_model_id: str | None) -> list[str]:
    """Validate a model ID for checkpoint promotion.

    Returns a list of error strings (empty if valid).
    """
    errors = []
    if not output_model_id:
        errors.append("output_model_id is required")
    elif not _RESOURCE_ID_RE.match(output_model_id):
        errors.append(
            f"output_model_id '{output_model_id}' contains invalid characters. "
            "Must be lowercase a-z, 0-9, or hyphen."
        )
    if output_model_id and len(output_model_id) > 63:
        errors.append(
            f"output_model_id '{output_model_id}' is too long ({len(output_model_id)} chars). "
            "Maximum is 63 characters."
        )
    return errors


class TrainingShapeProfile:
    """Resolved training shape profile from the control plane.

    Contains all shape-derived config: region, accelerator, image tag,
    sharding, deployment shape, etc.  Returned by
    :meth:`FireworksClient.resolve_training_profile`.
    """

    def __init__(
        self,
        training_shape_version: str,
        trainer_image_tag: str,
        max_supported_context_length: int,
        node_count: int,
        deployment_shape_version: str,
        deployment_image_tag: str,
        accelerator_type: str,
        accelerator_count: int,
        base_model_weight_precision: str,
        pipeline_parallelism: int,
    ):
        self.training_shape_version = training_shape_version
        self.trainer_image_tag = trainer_image_tag
        self.max_supported_context_length = max_supported_context_length
        self.node_count = node_count
        self.deployment_shape_version = deployment_shape_version
        self.deployment_image_tag = deployment_image_tag
        self.accelerator_type = accelerator_type
        self.accelerator_count = accelerator_count
        self.base_model_weight_precision = base_model_weight_precision
        self.pipeline_parallelism = pipeline_parallelism

    @property
    def training_shape(self) -> str | None:
        """The parent training shape name (without /versions/...)."""
        v = self.training_shape_version
        if not v:
            return None
        idx = v.find("/versions/")
        return v[:idx] if idx != -1 else v

    @property
    def deployment_shape(self) -> str | None:
        """The parent deployment shape name (without /versions/...)."""
        v = self.deployment_shape_version
        if not v:
            return None
        idx = v.find("/versions/")
        return v[:idx] if idx != -1 else v


class FireworksClient(_RestClient):
    """Fireworks platform client for operations that don't require a trainer.

    Use this directly for checkpoint promotion, training shape resolution,
    and other account-level operations.  For trainer job lifecycle
    management, use :class:`TrainerJobManager` which extends this class.

    Args:
        api_key: Fireworks API key.
        base_url: Control-plane API base URL.
        additional_headers: Extra HTTP headers for all requests.
        verify_ssl: Override SSL verification (``None`` = auto-detect).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.fireworks.ai",
        additional_headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            additional_headers=additional_headers,
            verify_ssl=verify_ssl,
        )

    # -- Training shape resolution ------------------------------------------------

    def resolve_training_profile(
        self,
        training_shape_id: str,
        **_kwargs,
    ) -> TrainingShapeProfile:
        """Fetch the latest validated version of a training shape.

        Reads the latest validated training-shape version and extracts all
        shape-derived config (region, accelerator, image tag, deployment
        shape, etc.) from its embedded snapshot.

        Args:
            training_shape_id: Full training shape resource name, e.g.
                ``accounts/fireworks/trainingShapes/ts-qwen3-8b-policy``.

        Returns:
            :class:`TrainingShapeProfile` with all shape-derived fields.
        """
        if not re.match(r"^accounts/[^/]+/trainingShapes/[^/]+$", training_shape_id):
            hint = "Expected: accounts/<account>/trainingShapes/<shape>\n"
            if "/versions/" in training_shape_id:
                hint += "  Do not include /versions/<ver> — this method resolves the latest version for you."
            else:
                hint += "  Example: accounts/fireworks/trainingShapes/ts-qwen3-8b-policy"
            raise ValueError(
                format_sdk_error(
                    "Invalid training_shape_id format",
                    f"'{training_shape_id}' is not a valid training shape resource name.",
                    hint,
                )
            )
        path = (
            f"/v1/{training_shape_id}/versions?"
            f"{urlencode({'filter': 'latest_validated=true', 'pageSize': 1})}"
        )
        resp = self._get(path, timeout=30)
        if not resp.is_success:
            error_msg = parse_api_error(resp)
            show_support = False
            if resp.status_code == 404:
                solution = (
                    f"Training shape '{training_shape_id}' was not found. "
                    "Verify the training_shape_id is correct and the shape exists."
                )
            elif resp.status_code == 403:
                solution = (
                    f"Permission denied for training shape '{training_shape_id}'. "
                    f"Ensure your account owns or has access to this shape."
                )
            else:
                solution = "Verify the training_shape_id and account have the shape registered."
                show_support = True
            raise RuntimeError(
                format_sdk_error(
                    f"Failed to fetch training shape '{training_shape_id}' (HTTP {resp.status_code})",
                    error_msg,
                    solution,
                    docs_url=DOCS_SDK,
                    show_support=show_support,
                )
            )
        data = resp.json()
        versions = data.get("trainingShapeVersions", []) or []
        if not versions:
            raise RuntimeError(
                format_sdk_error(
                    f"Failed to resolve latest validated training shape for '{training_shape_id}'",
                    "No latest validated training-shape version was returned.",
                    (
                        "Validate a training-shape version first, or check that the "
                        "training_shape_id is correct and visible to your account."
                    ),
                    docs_url=DOCS_SDK,
                    show_support=False,
                )
            )
        version = versions[0]
        snapshot = version.get("snapshot", {}) or {}
        sharding = snapshot.get("trainerShardingScheme", {}) or {}
        pp = int(sharding.get("pipelineParallelism", 1) or 1)
        return TrainingShapeProfile(
            training_shape_version=version.get("name", ""),
            trainer_image_tag=snapshot.get("trainerImageTag", ""),
            max_supported_context_length=snapshot.get("maxSupportedContextLength", 0),
            node_count=snapshot.get("nodeCount", 1),
            deployment_shape_version=snapshot.get("deploymentShapeVersion", ""),
            deployment_image_tag=snapshot.get("deploymentImageTag", ""),
            accelerator_type=snapshot.get("acceleratorType", ""),
            accelerator_count=snapshot.get("acceleratorCount", 0),
            base_model_weight_precision=snapshot.get("baseModelWeightPrecision", ""),
            pipeline_parallelism=pp,
        )

    # -- Checkpoint promotion ----------------------------------------------------

    def promote_checkpoint(
        self,
        job_id: str,
        checkpoint_id: str,
        output_model_id: str,
    ) -> dict:
        """Promote a trainer checkpoint to a Fireworks model.

        Calls the account-level ``:promote`` endpoint to turn a sampler
        checkpoint into a deployable model.  The trainer job ID is used
        only to resolve the GCS bucket where the checkpoint files reside —
        no running trainer is needed.

        The base model for metadata inheritance is automatically resolved
        from the trainer job's training config (same as the original
        promotion endpoint).

        Args:
            job_id: RLOR trainer job ID that produced the checkpoint.
            checkpoint_id: Checkpoint identifier (the ``snapshot_name``
                from :class:`SaveSamplerResult`).
            output_model_id: Desired model ID for the promoted model.
                Must be 1-63 chars, lowercase a-z, 0-9, or hyphen.

        Returns:
            Model dict from the API response (includes ``state``,
            ``kind``, ``peftDetails``, etc.).
        """
        errors = validate_output_model_id(output_model_id)
        if errors:
            raise ValueError("\n\n".join(errors))

        path = (
            f"/v1/accounts/{self.account_id}"
            f"/checkpoints/{checkpoint_id}:promote"
        )
        output_model = f"accounts/{self.account_id}/models/{output_model_id}"
        trainer_job = f"accounts/{self.account_id}/rlorTrainerJobs/{job_id}"
        logger.info(
            "Promoting checkpoint '%s' -> model '%s'",
            checkpoint_id,
            output_model,
        )

        body: dict = {
            "output_model": output_model,
            "trainer_job_id": trainer_job,
        }

        resp = self._post(path, json=body, timeout=300)
        if not resp.is_success:
            error_msg = parse_api_error(resp)
            raise RuntimeError(
                format_sdk_error(
                    f"Failed to promote checkpoint '{checkpoint_id}'",
                    error_msg,
                    f"Check that the job {job_id} exists and the checkpoint is valid.\n"
                    f"  Console: {CONSOLE_URL}",
                    docs_url=DOCS_SDK,
                )
            )

        result = resp.json()
        model = result.get("model", {})
        state = model.get("state", "UNKNOWN")
        kind = model.get("kind", "UNKNOWN")
        logger.info("Promoted! Model state=%s, kind=%s", state, kind)

        peft = model.get("peftDetails", {})
        if peft:
            logger.info(
                "PEFT: base=%s, r=%s, targets=%s",
                peft.get("baseModel"),
                peft.get("r"),
                peft.get("targetModules"),
            )

        return model
