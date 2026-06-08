# Claude Code Instructions

## Tinker-style Training SDK

When working on the tinker-style training SDK, **only look at code in `src/fireworks/training/`**. Do not reference or modify training-related code outside of this directory.

This SDK repo contains auto-generated code from Stainless outside of `src/fireworks/training/`. The training SDK is developed independently and lives entirely within that directory.

## Skill lives in the cookbook

There is **no** skill in this repo. The maintained Claude Code skills for the training SDK ship in the cookbook: [`skills/dev/` in fw-ai/cookbook](https://github.com/fw-ai/cookbook/tree/main/skills/dev) for day-to-day training work, with [`skills/research/`](https://github.com/fw-ai/cookbook/tree/main/skills/research) for research-grade work (coming soon). Clone the cookbook and Claude picks them up. The cookbook is the reference implementation — every SDK call an agent typically needs is exercised in `training/recipes/*.py`, and the skills point the agent at those files directly.

Do not duplicate the skill here. Two sources go stale; one does not.

## Region Placement

Training SDK managed flows must not choose trainer or deployment regions unless
the user explicitly provided `region`. Do not add `deployment_region`, hard-code
default regions, infer region from accelerator/deployment shape/training shape,
or GET a trainer job to copy its region into a hot-load deployment. Leave unset
values unset so the backend RLOR trainer/deployment gateway selects defaults and
enforces colocation.
