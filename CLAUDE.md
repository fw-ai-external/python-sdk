# Claude Code Instructions

## Tinker-style Training SDK

The training SDK is Fireworks-owned and has no external Tinker dependency.
Preserve supported client/type/future interfaces and JSON v1/v2 contracts.
Unsupported inherited operations must fail before sending a request.

When working on the tinker-style training SDK, **only look at code in `src/fireworks/training/`**. Do not reference or modify training-related code outside of this directory.

This SDK repo contains auto-generated code from Stainless outside of `src/fireworks/training/`. The training SDK is developed independently and lives entirely within that directory.

## Skill lives in the cookbook

The maintained training skills ship in [`fw-ai-external/cookbook`](https://github.com/fw-ai-external/cookbook/tree/main/skills): `research` for planning, `configure` for execution, and `debug` for troubleshooting, with `fireworks-training` carrying shared references. Install them using the [installation guide](https://github.com/fw-ai-external/cookbook/blob/main/skills/GETTING-STARTED.md). Cookbook recipes under `training/recipes/` provide runnable SDK examples.

Do not duplicate the skill here. Two sources go stale; one does not.

## Region Placement

Training SDK managed flows must not choose trainer or deployment regions unless
the user explicitly provided `region`. Do not add `deployment_region`, hard-code
default regions, infer region from accelerator/deployment shape/training shape,
or GET a trainer job to copy its region into a hot-load deployment. Leave unset
values unset so the backend RLOR trainer/deployment gateway selects defaults and
enforces colocation.
