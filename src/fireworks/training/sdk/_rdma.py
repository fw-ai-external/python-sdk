"""Configure the hotload connection; the trainer owns the complete weight_sync."""

from __future__ import annotations

import uuid
from typing import Any
from dataclasses import field, dataclass


@dataclass
class _RdmaSamplerBackend:
    sampler: Any
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_epoch: str = field(default_factory=lambda: str(uuid.uuid4()))

    def publication_request(self) -> dict[str, Any]:
        sampler = self.sampler
        return {
            "protocol_version": 1,
            "transport": "RDMA",
            "session_id": self.session_id,
            "source_epoch": self.source_epoch,
            "deployment": sampler._deployment_model(),
            "hotload_url": sampler.deploy_mgr.hotload_api_url.rstrip("/") + "/hot_load/v1/models/hot_load",
            "hotload_headers": sampler.deploy_mgr._hotload_headers(sampler.deployment_id, sampler.base_model),
            "operation_id": str(uuid.uuid4()),
        }

    def hotload_saved_snapshot(self, model_path: str) -> bool:
        raise ValueError("Use training_client.weight_sync() for RDMA; it includes rollout activation")

    def get_sampling_client(self, tokenizer=None, concurrency_controller=None):
        return self.sampler.get_sampling_client(tokenizer, concurrency_controller)
