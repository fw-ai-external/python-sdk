"""
Fireworks Training - GRPO/DPO/SFT with Tinker SDK

This module patches the Tinker SDK to add Fireworks-specific features like
checkpoint_type support for base/delta checkpoints.

After importing this module, the Tinker SDK is patched transparently:

    import tinker
    import fireworks.training  # Patches tinker automatically

    service = tinker.ServiceClient(base_url=trainer_url)
    client = service.create_lora_training_client(base_model=model, rank=32)

    # Now save_weights_for_sampler accepts checkpoint_type!
    client.save_weights_for_sampler("step-100", checkpoint_type="base")
    client.save_weights_for_sampler("step-200", checkpoint_type="delta")

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from .tinker_patch import patch_tinker

__all__ = [
    "patch_tinker",
    "sdk",
    "cookbook",
]

# Apply patches automatically on import so user scripts don't need to call patch_tinker().
# If tinker isn't installed, patch_tinker() is a no-op.
patch_tinker()


