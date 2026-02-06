"""
Tinker SDK patches for Fireworks RLOR trainers.

This module patches the Tinker SDK to add `checkpoint_type` support to
`save_weights_for_sampler`, enabling base/delta checkpoint saves for
efficient hotloading.

After importing `fireworks.rl`, users can use the normal Tinker API:

    import tinker
    import fireworks.rl  # Patches tinker automatically

    client = service.create_lora_training_client(...)
    client.save_weights_for_sampler("step-1", checkpoint_type="base")
    client.save_weights_for_sampler("step-2", checkpoint_type="delta")

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

_patched = False


def patch_tinker() -> None:
    """Apply Fireworks patches to the Tinker SDK.

    This patches TrainingClient.save_weights_for_sampler to accept a
    `checkpoint_type` parameter ("base" or "delta").

    After patching, users can call:
        client.save_weights_for_sampler("name", checkpoint_type="base")

    This is called automatically when importing `fireworks.rl`.
    """
    global _patched
    if _patched:
        return

    try:
        _patch_training_client()
        _patched = True
    except ImportError:
        # tinker not installed, skip patching
        pass


def _patch_training_client() -> None:
    """Patch TrainingClient to support checkpoint_type in save_weights_for_sampler."""
    from tinker import types
    from tinker.lib.client_connection_pool_type import ClientConnectionPoolType
    from tinker.lib.public_interfaces.training_client import TrainingClient

    # Import internal types needed for the implementation
    from tinker.lib.api_future_impl import _APIFuture

    # Only patch once
    if hasattr(TrainingClient, "_fw_patched"):
        return

    # Store original for reference (not used, but good for debugging)
    TrainingClient._fw_original_save_weights_for_sampler = TrainingClient.save_weights_for_sampler

    # Replacement implementation that supports checkpoint_type
    async def _save_weights_for_sampler_impl_with_checkpoint_type(
        self,
        request_id: int,
        name: str,
        checkpoint_type: str | None = None,
    ) -> types.SaveWeightsForSamplerResponseInternal:
        """Internal implementation that passes checkpoint_type via extra_body."""
        import asyncio
        import time

        assert asyncio.get_event_loop() == self.holder.get_loop()
        start_time = time.time()

        async def _send_request():
            request = types.SaveWeightsForSamplerRequest(
                model_id=self._guaranteed_model_id(),
                path=name,
                seq_id=request_id + 1,
            )
            # Build extra_body with checkpoint_type if provided
            extra_body = None
            if checkpoint_type:
                extra_body = {"checkpoint_type": checkpoint_type}

            with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
                return await client.weights.save_for_sampler(
                    request=request,
                    extra_body=extra_body,
                )

        async with self._take_turn(request_id):
            future = await self.holder.execute_with_retries(_send_request)

        return await _APIFuture(
            types.SaveWeightsForSamplerResponseInternal,
            self.holder,
            future,
            request_start_time=start_time,
            request_type="SaveWeightsForSampler",
            queue_state_observer=self,
        )

    def patched_save_weights_for_sampler(self, name: str, checkpoint_type: str | None = None):
        """Save model weights for use with a SamplingClient.

        Args:
            name: Name for the saved sampler weights
            checkpoint_type: Type of checkpoint to save:
                - "base": Full checkpoint (all weights)
                - "delta": Incremental checkpoint (XOR from previous base)
                - None: Server default

        Returns:
            APIFuture containing the save response with sampler path

        Example:
            # Save base checkpoint
            client.save_weights_for_sampler("step-100", checkpoint_type="base")

            # Save delta checkpoint (more efficient)
            client.save_weights_for_sampler("step-200", checkpoint_type="delta")
        """
        request_id = self._get_request_id()

        async def _save_async():
            result = await _save_weights_for_sampler_impl_with_checkpoint_type(
                self, request_id, name, checkpoint_type
            )
            assert result.path is not None
            return types.SaveWeightsForSamplerResponse(path=result.path)

        return self.holder.run_coroutine_threadsafe(_save_async())

    async def patched_save_weights_for_sampler_async(self, name: str, checkpoint_type: str | None = None):
        """Async version of save_weights_for_sampler with checkpoint_type support."""
        return patched_save_weights_for_sampler(self, name, checkpoint_type)

    # Apply the patches
    TrainingClient.save_weights_for_sampler = patched_save_weights_for_sampler
    TrainingClient.save_weights_for_sampler_async = patched_save_weights_for_sampler_async
    TrainingClient._fw_patched = True


