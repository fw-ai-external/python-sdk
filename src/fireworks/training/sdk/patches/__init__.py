"""Monkey-patches for tinker types.

All patches are applied at import time and are idempotent.
Remove individual patch files when tinker adds native support.
"""

import fireworks.training.sdk.patches._tinker_r3_patch  # noqa: F401
import fireworks.training.sdk.patches._discriminator_patch  # noqa: F401
import fireworks.training.sdk.patches._builtin_loss_fn_patch  # noqa: F401
