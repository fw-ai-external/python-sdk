"""ReconnectableClient -- wraps FiretitanTrainingClient with auto-reconnect.

Transparently handles pod preemption so the training loop needs no try/except.
"""

from __future__ import annotations

import logging
from typing import Any

import tinker

from fireworks.training.sdk.client import FiretitanServiceClient, FiretitanTrainingClient
from fireworks.training.sdk.trainer import TrainerJobManager, TrainerServiceEndpoint

logger = logging.getLogger(__name__)

_RECONNECT_ERRORS = (tinker.NotFoundError, tinker.APIConnectionError)


class ReconnectableClient:
    """Training client that auto-reconnects on pod preemption.

    Wraps a ``FiretitanTrainingClient`` and retries failed API calls after
    re-establishing the connection to the RLOR trainer job.
    """

    def __init__(
        self,
        rlor_mgr: TrainerJobManager,
        job_id: str,
        base_model: str,
        lora_rank: int = 0,
        api_key: str = "tml-local",
        max_retries: int = 3,
    ):
        self._rlor_mgr = rlor_mgr
        self._job_id = job_id
        self._base_model = base_model
        self._lora_rank = lora_rank
        self._api_key = api_key
        self._max_retries = max_retries
        self._endpoint: TrainerServiceEndpoint | None = None
        self._client: FiretitanTrainingClient | None = None
        self._connect()

    @property
    def inner(self) -> FiretitanTrainingClient:
        """Access the underlying training client directly."""
        assert self._client is not None
        return self._client

    @property
    def endpoint(self) -> TrainerServiceEndpoint:
        assert self._endpoint is not None
        return self._endpoint

    @property
    def job_id(self) -> str:
        return self._job_id

    def forward(self, data, loss_fn):
        return self._call(lambda c: c.forward(data, loss_fn))

    def forward_backward_custom(self, data, loss_fn):
        return self._call(lambda c: c.forward_backward_custom(data, loss_fn))

    def optim_step(self, params):
        return self._call(lambda c: c.optim_step(params))

    def save_state(self, name: str):
        return self._call(lambda c: c.save_state(name))

    def load_state_with_optimizer(self, path: str):
        return self._call(lambda c: c.load_state_with_optimizer(path))

    def resolve_checkpoint_path(self, name: str, source_job_id: str | None = None) -> str:
        return self.inner.resolve_checkpoint_path(name, source_job_id=source_job_id)

    # -- Internal --------------------------------------------------------------

    def _connect(self) -> None:
        ep = self._rlor_mgr.wait_for_existing(self._job_id)
        svc = FiretitanServiceClient(base_url=ep.base_url, api_key=self._api_key)
        self._client = svc.create_training_client(
            base_model=self._base_model,
            lora_rank=self._lora_rank,
        )
        self._endpoint = ep

    def _reconnect(self) -> None:
        logger.warning("Trainer %s lost connection, reconnecting...", self._job_id)
        ep = self._rlor_mgr.reconnect_and_wait(job_id=self._job_id)
        svc = FiretitanServiceClient(base_url=ep.base_url, api_key=self._api_key)
        self._client = svc.create_training_client(
            base_model=self._base_model,
            lora_rank=self._lora_rank,
        )
        self._endpoint = ep
        logger.info("Trainer %s reconnected.", self._job_id)

    def _call(self, fn):
        for attempt in range(self._max_retries):
            try:
                return fn(self._client)
            except _RECONNECT_ERRORS:
                if attempt == self._max_retries - 1:
                    raise
                self._reconnect()
        raise RuntimeError("unreachable")
