"""Opt-in monkey-patches for tinker types.

Importing this package applies all patches; the operation is idempotent. The
Fireworks training client imports it automatically, while applications that
use Tinker directly must import this package themselves.
Remove individual patch files when tinker adds native support.
"""

# Patch order is intentional: structured future capture wraps whichever
# native or body-timeout fetch implementation is active.
# ruff: noqa: I001

import fireworks.training.sdk.patches._tinker_r3_patch  # noqa: F401
import fireworks.training.sdk.patches._discriminator_patch  # noqa: F401
import fireworks.training.sdk.patches._builtin_loss_fn_patch  # noqa: F401
import fireworks.training.sdk.patches._tinker_lora_alpha_patch  # noqa: F401
import fireworks.training.sdk.patches._tinker_grad_norm_metrics_patch  # noqa: F401
import fireworks.training.sdk.patches._tinker_future_body_timeout_patch  # noqa: F401
import fireworks.training.sdk.patches._tinker_structured_error_patch  # noqa: F401
