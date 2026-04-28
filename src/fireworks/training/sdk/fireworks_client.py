"""Fireworks platform client for trainer-free operations.

Provides account-level operations that don't require a running trainer
job: checkpoint promotion, training shape resolution, model listing, etc.

:class:`TrainerJobManager` extends this with trainer-specific lifecycle
methods (create, wait, reconnect, delete).
"""

from __future__ import annotations

import re
import logging
import warnings
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

# 4-segment checkpoint resource name preferred by promote_checkpoint:
# accounts/<a>/rlorTrainerJobs/<j>/checkpoints/<c>.
_CHECKPOINT_NAME_RE = re.compile(
    r"^accounts/([^/]+)/rlorTrainerJobs/([^/]+)/checkpoints/([^/]+)$"
)


def _parse_checkpoint_name(name: str) -> tuple[str, str, str] | None:
    """Parse the 4-segment checkpoint name into (account, job, checkpoint)."""
    m = _CHECKPOINT_NAME_RE.match(name)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


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
    sharding, deployment shape, trainer mode, etc.  Returned by
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
        trainer_mode: str = "",
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
        self.trainer_mode = trainer_mode

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
        """Pinned deployment shape version from the training shape.

        Returns the full versioned resource name (e.g.
        ``accounts/fw/deploymentShapes/ds-x/versions/1``).
        The deployment creation API accepts versioned paths and pins
        to the exact version, avoiding accidental drift to a newer
        validated version.

        NOTE: always pass versioned paths (with ``/versions/``) to
        ``DeploymentConfig.deployment_shape`` to ensure version pinning.
        """
        return self.deployment_shape_version or None

    @property
    def supports_lora(self) -> bool:
        """Whether the validated training shape is LoRA-capable."""
        return self.trainer_mode == "LORA_TRAINER"


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
        """Fetch a training shape version and return its profile.

        Accepts either a bare shape path (resolves latest validated version)
        or a versioned path (fetches that exact version).

        Args:
            training_shape_id: Full training shape resource name:
                - ``accounts/fireworks/trainingShapes/ts-qwen3-8b-policy``
                  (resolves latest validated)
                - ``accounts/fireworks/trainingShapes/ts-qwen3-8b-policy/versions/abc``
                  (fetches exact version)

        Returns:
            :class:`TrainingShapeProfile` with all shape-derived fields.
        """
        is_versioned = "/versions/" in training_shape_id
        if not re.match(
            r"^accounts/[^/]+/trainingShapes/[^/]+(/versions/[^/]+)?$",
            training_shape_id,
        ):
            raise ValueError(
                format_sdk_error(
                    "Invalid training_shape_id format",
                    f"'{training_shape_id}' is not a valid training shape resource name.",
                    "Expected: accounts/<account>/trainingShapes/<shape>[/versions/<ver>]\n"
                    "  Example: accounts/fireworks/trainingShapes/ts-qwen3-8b-policy",
                )
            )

        if is_versioned:
            path = f"/v1/{training_shape_id}"
        else:
            path = (
                f"/v1/{training_shape_id}/versions?"
                f"{urlencode({'filter': 'latest_validated=true', 'pageSize': 1})}"
            )
        resp = self._get(path, timeout=30)
        if not resp.is_success:
            error_msg = parse_api_error(resp)
            show_support = False
            if resp.status_code == 401:
                solution = (
                    "The API key was rejected for training APIs. Ensure you are using a "
                    "training-scoped Fireworks API key; inference-only keys return 401 here."
                )
            elif resp.status_code == 404:
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

        if is_versioned:
            version = resp.json()
        else:
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
            trainer_mode=snapshot.get("trainerMode", ""),
        )

    # -- Checkpoint promotion ----------------------------------------------------

    def promote_checkpoint(
        self,
        job_id: str | None = None,
        checkpoint_id: str | None = None,
        output_model_id: str | None = None,
        base_model: str | None = None,
        *,
        name: str | None = None,
        hot_load_deployment_id: str | None = None,
    ) -> dict:
        """Promote a trainer checkpoint to a Fireworks model.

        Calls the account-level ``:promote`` endpoint to turn a sampler
        checkpoint into a deployable model. Two equivalent calling forms:

        Preferred (4-segment ``name=`` from ``list_checkpoints`` output)::

            entry = client.list_checkpoints(job_id)[0]
            client.promote_checkpoint(
                name=entry["name"],         # accounts/<a>/rlorTrainerJobs/<j>/checkpoints/<c>
                output_model_id="my-model",
                base_model="accounts/fireworks/models/qwen3-8b",
            )

        Legacy (2-segment id + ``job_id`` positional)::

            client.promote_checkpoint(
                job_id, checkpoint_id, output_model_id, base_model,
            )

        Both forms are accepted by the gateway; the new ``name=`` form
        is preferred because it eliminates the manual disassembly of the
        4-segment resource name returned by ``list_checkpoints``.

        Public docs: see ``/fine-tuning/training-api/saving-and-loading``
        on docs.fireworks.ai for the full promote API contract.

        Args:
            job_id: RLOR trainer job ID. Required when ``name`` is not set.
            checkpoint_id: Checkpoint identifier (the ``snapshot_name``
                from :class:`SaveSamplerResult`). Required when ``name``
                is not set.
            output_model_id: Desired model ID for the promoted model.
                Must be 1-63 chars, lowercase a-z, 0-9, or hyphen.
            base_model: Base model resource name for metadata inheritance
                (e.g. ``accounts/fireworks/models/qwen3-8b``).
            name: Full 4-segment checkpoint resource name
                ``accounts/<a>/rlorTrainerJobs/<j>/checkpoints/<c>`` —
                pass directly from ``list_checkpoints`` output.
            hot_load_deployment_id: Deployment ID for legacy jobs whose
                checkpoints are associated with a deployment. Omit for
                newer jobs (the gateway resolves the bucket URL from the
                trainer's stored metadata).

        Returns:
            Model dict from the API response (includes ``state``,
            ``kind``, ``peftDetails``, etc.).
        """
        if name is not None:
            if checkpoint_id is not None:
                raise ValueError("pass either name= or checkpoint_id, not both")
            parsed = _parse_checkpoint_name(name)
            if parsed is None:
                raise ValueError(
                    f"Invalid checkpoint name {name!r}. Expected 4 segments: "
                    "accounts/<account>/rlorTrainerJobs/<job>/checkpoints/<id>."
                )
            parsed_account, parsed_job_id, parsed_checkpoint_id = parsed
            if job_id is not None and job_id != parsed_job_id:
                raise ValueError(
                    f"job_id={job_id!r} conflicts with name's trainer job "
                    f"{parsed_job_id!r}."
                )
            account_id = parsed_account
            job_id = parsed_job_id
            checkpoint_id = parsed_checkpoint_id
        else:
            if not job_id or not checkpoint_id:
                raise ValueError(
                    "Either name= (4-segment resource path) or both job_id "
                    "and checkpoint_id are required."
                )
            warnings.warn(
                "promote_checkpoint(job_id, checkpoint_id, ...) positional form "
                "is deprecated. Pass the 4-segment resource name instead: "
                "promote_checkpoint(name=entry['name'], output_model_id=..., "
                "base_model=...). The 'name' field comes straight from "
                "list_checkpoints output. See the public docs at "
                "/fine-tuning/training-api/saving-and-loading.",
                DeprecationWarning,
                stacklevel=2,
            )
            account_id = self.account_id

        if not output_model_id or not base_model:
            raise ValueError("output_model_id and base_model are required")
        if hot_load_deployment_id is not None:
            warnings.warn(
                "promote_checkpoint(hot_load_deployment_id=...) is deprecated. "
                "The gateway resolves the bucket URL from the trainer's stored "
                "metadata for any run on cookbook >= 0.3.0 (both PER_TRAINER "
                "and PER_DEPLOYMENT bucket scopes). Omit this argument unless "
                "you are promoting a checkpoint from a deployment that predates "
                "the stored-bucket-URL migration. See the public docs at "
                "/fine-tuning/training-api/saving-and-loading.",
                DeprecationWarning,
                stacklevel=2,
            )

        errors = validate_output_model_id(output_model_id)
        if errors:
            raise ValueError("\n\n".join(errors))

        path = (
            f"/v1/accounts/{account_id}"
            f"/checkpoints/{checkpoint_id}:promote"
        )
        output_model = f"accounts/{account_id}/models/{output_model_id}"
        trainer_job = f"accounts/{account_id}/rlorTrainerJobs/{job_id}"
        logger.info(
            "Promoting checkpoint '%s' -> model '%s'",
            checkpoint_id,
            output_model,
        )

        body: dict = {
            "output_model": output_model,
            "trainer_job_id": trainer_job,
            "base_model": base_model,
        }
        if hot_load_deployment_id is not None:
            body["hot_load_deployment_id"] = (
                f"accounts/{account_id}/deployments/{hot_load_deployment_id}"
            )

        resp = self._post(path, json=body, timeout=300)
        if not resp.is_success:
            error_msg = parse_api_error(resp)
            raise RuntimeError(
                format_sdk_error(
                    f"Failed to promote checkpoint '{checkpoint_id}'",
                    error_msg,
                    f"Check that the checkpoint is valid and base_model is correct.\n"
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

    # -- Checkpoint listing -----------------------------------------------------

    def list_checkpoints(
        self,
        job_id: str,
        *,
        page_size: int = 200,
    ) -> list[dict]:
        """List checkpoints the server knows about for a trainer job.

        Calls the control-plane ``ListRlorTrainerJobCheckpoints`` endpoint,
        which reads the job's bucket URL from the database and scans GCS.
        The trainer job may be in **any** state — running, completed,
        failed, cancelled, or already deleted — as long as the DB record
        still exists and the GCS blobs haven't been garbage-collected.

        The distinction vs :meth:`FiretitanTrainingClient.list_checkpoints`:
        that call hits the **live trainer pod** and returns DCP checkpoint
        names only. This method hits the **control plane** and returns
        both sampler and DCP checkpoints with promotability metadata, even
        after the trainer is gone.

        Args:
            job_id: RLOR trainer job ID (the short ID, not the full
                ``accounts/<a>/rlorTrainerJobs/<id>`` resource name).
            page_size: Maximum rows per HTTP request. The method
                auto-paginates through ``nextPageToken`` and returns the
                full list.

        Returns:
            List of checkpoint dicts. Each dict is the raw JSON entry
            from the API and contains at least:

            - ``name``:  full resource name
              (``accounts/<a>/rlorTrainerJobs/<job>/checkpoints/<ckpt>``)
            - ``createTime`` / ``updateTime``: RFC3339 timestamps
            - ``checkpointType``: server enum string (e.g.
              ``"CHECKPOINT_TYPE_INFERENCE_BASE"``,
              ``"CHECKPOINT_TYPE_INFERENCE_LORA"``,
              ``"CHECKPOINT_TYPE_TRAINING_LORA"``,
              ``"CHECKPOINT_TYPE_INFERENCE_ARC_V2"``). Treat as opaque
              and filter on ``promotable``.
            - ``promotable``: bool — authoritative. ``True`` iff
              :meth:`promote_checkpoint` will accept this row.

            Sort order follows the server, which returns **oldest
            ``createTime`` first**. Callers who want newest-first
            (typical for picking a checkpoint to promote) should
            re-sort client-side.
        """
        base_path = (
            f"/v1/accounts/{self.account_id}"
            f"/rlorTrainerJobs/{job_id}/checkpoints"
        )

        rows: list[dict] = []
        page_token: str | None = None
        while True:
            query: dict[str, str] = {"pageSize": str(page_size)}
            if page_token:
                query["pageToken"] = page_token
            path = f"{base_path}?{urlencode(query)}"
            resp = self._get(path, timeout=30)
            if not resp.is_success:
                error_msg = parse_api_error(resp)
                if resp.status_code == 404:
                    solution = (
                        f"Trainer job '{job_id}' was not found in this account. "
                        "Verify the job ID and that your API key resolves to the "
                        "account that owns it."
                    )
                elif resp.status_code == 403:
                    solution = (
                        "Your API key does not have access to this trainer job."
                    )
                else:
                    solution = None
                raise RuntimeError(
                    format_sdk_error(
                        f"Failed to list checkpoints for trainer job '{job_id}' "
                        f"(HTTP {resp.status_code})",
                        error_msg,
                        solution or "Retry; if it persists, contact Fireworks support.",
                        docs_url=DOCS_SDK,
                        show_support=solution is None,
                    )
                )

            body = resp.json() or {}
            page = body.get("checkpoints") or body.get("rlorTrainerJobCheckpoints") or []
            rows.extend(page)

            page_token = body.get("nextPageToken") or body.get("next_page_token")
            if not page_token:
                break

        return rows
