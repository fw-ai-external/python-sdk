"""Infrastructure setup utilities: RLOR jobs, deployments, training clients."""

from __future__ import annotations

import re
import time
import logging

from fireworks.training.sdk.client import FiretitanServiceClient, FiretitanTrainingClient
from fireworks.training.sdk.trainer import TrainerJobConfig, TrainerJobManager, TrainerServiceEndpoint, TrainingShapeProfile
from fireworks.training.sdk.deployment import DeploymentInfo, DeploymentManager
from fireworks.training.cookbook.utils.config import InfraConfig, DeployConfig

logger = logging.getLogger(__name__)


def resolve_and_apply_shape(
    rlor_mgr: TrainerJobManager,
    base_model: str,
    infra: InfraConfig,
    deploy_cfg: DeployConfig,
) -> TrainingShapeProfile:
    """Fetch training shape and apply it to infra/deploy configs.

    Calls ``GET /v1/accounts/{id}/trainingShapes/{shapeId}`` to fetch
    the shape, then populates unset fields on ``infra`` and ``deploy_cfg``
    from the shape.  Fields already set by the customer are left as-is.

    Returns the resolved profile for inspection/logging.
    """
    if not infra.training_shape_id:
        raise ValueError("training_shape_id is required for shape resolution")
    profile = rlor_mgr.resolve_training_profile(
        training_shape_id=infra.training_shape_id,
    )
    logger.info(
        "Resolved training shape: %s (accel=%s, image=%s)",
        profile.training_shape_version,
        profile.accelerator_type,
        profile.trainer_image_tag,
    )

    if not infra.accelerator_type and profile.accelerator_type and profile.accelerator_type != "ACCELERATOR_TYPE_UNSPECIFIED":
        infra.accelerator_type = profile.accelerator_type
    if not infra.accelerator_count and profile.accelerator_count:
        infra.accelerator_count = profile.accelerator_count
    if not infra.custom_image_tag and profile.trainer_image_tag:
        infra.custom_image_tag = profile.trainer_image_tag
    if profile.node_count and infra.node_count == 1:
        infra.node_count = profile.node_count

    if not deploy_cfg.deployment_shape and profile.deployment_shape_version:
        dsv = profile.deployment_shape_version
        shape_name = re.sub(r"/versions/[^/]+$", "", dsv)
        deploy_cfg.deployment_shape = shape_name
    if not deploy_cfg.deployment_id:
        model_short = base_model.rsplit("/", 1)[-1]
        deploy_cfg.deployment_id = f"{model_short}-{int(time.time())}"

    return profile


def create_trainer_job(
    rlor_mgr: TrainerJobManager,
    *,
    base_model: str,
    infra: InfraConfig,
    lora_rank: int = 0,
    max_seq_len: int = 4096,
    learning_rate: float = 1e-5,
    grad_accum: int = 4,
    display_name: str = "trainer",
    hot_load_deployment_id: str | None = None,
    extra_args: list[str] | None = None,
    job_id: str | None = None,
) -> TrainerServiceEndpoint:
    """Create a new RLOR trainer job or reuse an existing one.

    If *job_id* is provided, the existing job is reused (resumed if needed).
    Otherwise a new job is created and waited on until ready.
    """
    if job_id:
        return _reuse_or_resume_job(rlor_mgr, job_id)

    logger.info("Creating trainer job '%s' (nodes=%d)...", display_name, infra.node_count)
    return rlor_mgr.create_and_wait(
        TrainerJobConfig(
            base_model=base_model,
            lora_rank=lora_rank,
            max_context_length=max_seq_len,
            learning_rate=learning_rate,
            gradient_accumulation_steps=grad_accum,
            node_count=infra.node_count,
            display_name=display_name,
            hot_load_deployment_id=hot_load_deployment_id,
            region=infra.region,
            custom_image_tag=infra.custom_image_tag,
            extra_args=extra_args or infra.extra_args,
            accelerator_type=infra.accelerator_type,
            accelerator_count=infra.accelerator_count,
            skip_validations=infra.skip_validations,
        )
    )


def setup_deployment(
    deploy_mgr: DeploymentManager,
    deploy_cfg: DeployConfig,
    base_model: str,
    infra: InfraConfig,
) -> DeploymentInfo | None:
    """Create or get a deployment. Returns None if no deployment configured."""
    if not deploy_cfg.create_deployment or not deploy_cfg.deployment_id:
        if deploy_cfg.deployment_id:
            return deploy_mgr.get(deploy_cfg.deployment_id)
        return None
    dep_config = deploy_cfg.to_deployment_config(base_model, infra)
    info = deploy_mgr.create_or_get(dep_config)
    if info.state != "READY":
        info = deploy_mgr.wait_for_ready(
            dep_config.deployment_id,
            timeout_s=deploy_cfg.deployment_timeout_s,
        )
    return info


def setup_training_client(
    endpoint: TrainerServiceEndpoint,
    base_model: str,
    api_key: str = "tml-local",
    lora_rank: int = 0,
) -> tuple[FiretitanServiceClient, FiretitanTrainingClient]:
    """Create a ServiceClient + TrainingClient for a trainer endpoint."""
    svc = FiretitanServiceClient(base_url=endpoint.base_url, api_key=api_key)
    cli = svc.create_training_client(base_model=base_model, lora_rank=lora_rank)
    return svc, cli


def _reuse_or_resume_job(rlor_mgr: TrainerJobManager, job_id: str) -> TrainerServiceEndpoint:
    job = rlor_mgr.get(job_id)
    state = job.get("state", "")
    resumable = ("JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_PAUSED", "JOB_STATE_COMPLETED")
    if state in resumable:
        logger.info("Job %s is %s, resuming...", job_id, state)
        return rlor_mgr.resume_and_wait(job_id)
    return rlor_mgr.wait_for_existing(job_id)
