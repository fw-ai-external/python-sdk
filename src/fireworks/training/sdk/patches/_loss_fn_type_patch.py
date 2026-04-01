"""Patch tinker's LossFnType to include loss functions added after the tinker release.

Tinker's ``LossFnType`` is a ``Literal`` type alias that enumerates the
server-supported builtin loss function names.  The firetitan backend adds
new loss functions faster than tinker publishes releases, so the SDK client
may reject valid loss names at Pydantic validation time.

This patch replaces the ``LossFnType`` alias in the ``tinker.types``
namespace with an expanded version that includes all server-supported names.

Safe to import multiple times -- the patch is applied only once.
Remove individual entries when tinker adds native support for them.
"""

import logging
from typing import Literal

from typing_extensions import TypeAlias

logger = logging.getLogger(__name__)

_SENTINEL = "_loss_fn_type_patch_applied"

# All loss function names supported by the firetitan backend.
# Keep in sync with train-firetitan-py/firetitan/train/rlor/tinker_schemas.py
PatchedLossFnType: TypeAlias = Literal[
    "cross_entropy",
    "importance_sampling",
    "ppo",
    "cispo",
    "dapo",
    "gspo",
    "dro",
    "kl_distillation",
]


def _apply_loss_fn_type_patch() -> None:
    import tinker.types.loss_fn_type as loss_fn_type_module
    from tinker.types.forward_backward_input import ForwardBackwardInput

    if getattr(loss_fn_type_module, _SENTINEL, False):
        return

    old_type = loss_fn_type_module.LossFnType
    loss_fn_type_module.LossFnType = PatchedLossFnType

    # Update ForwardBackwardInput's field annotation so Pydantic validates
    # against the expanded type.
    ForwardBackwardInput.model_fields["loss_fn"].annotation = PatchedLossFnType
    ForwardBackwardInput.__annotations__["loss_fn"] = PatchedLossFnType
    ForwardBackwardInput.model_rebuild(force=True)

    setattr(loss_fn_type_module, _SENTINEL, True)
    logger.info(
        "LossFnType patch applied: expanded from %s to %s",
        old_type,
        PatchedLossFnType,
    )


_apply_loss_fn_type_patch()
