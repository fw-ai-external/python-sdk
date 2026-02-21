"""Infrastructure setup utilities: RLOR jobs, deployments, training clients."""

from __future__ import annotations

import logging

from fireworks.training.sdk.client import FiretitanServiceClient, FiretitanTrainingClient
from fireworks.training.sdk.trainer import TrainerJobConfig, TrainerJobManager, TrainerServiceEndpoint
from fireworks.training.sdk.deployment import DeploymentInfo, DeploymentManager
from fireworks.training.cookbook.utils.config import InfraConfig, DeployConfig

logger = logging.getLogger(__name__)


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
