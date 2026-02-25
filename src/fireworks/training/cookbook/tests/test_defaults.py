"""Tests for defaults changed in this PR (aligned with slime/AReaL)."""

from __future__ import annotations


def test_grpo_temperature():
    from fireworks.training.cookbook.recipes.grpo_loop import Config

    assert Config().temperature == 1.0


def test_grpo_max_completion_tokens():
    from fireworks.training.cookbook.recipes.grpo_loop import Config

    assert Config().max_completion_tokens == 1024


def test_tis_clip_high():
    from fireworks.training.cookbook.utils.importance_sampling import ISConfig

    assert ISConfig().clip_high == 2.0


def test_dpo_has_tokenizer_model():
    from fireworks.training.cookbook.recipes.dpo_loop import Config

    assert hasattr(Config(), "tokenizer_model")
