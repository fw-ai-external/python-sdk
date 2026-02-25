"""Tests for cookbook config defaults and alignment with industry standards.

Verifies that default hyperparameters match conventions from slime/AReaL.
"""

from __future__ import annotations


class TestGRPODefaults:
    def test_temperature(self):
        from fireworks.training.cookbook.recipes.grpo_loop import Config

        assert Config().temperature == 1.0

    def test_max_completion_tokens(self):
        from fireworks.training.cookbook.recipes.grpo_loop import Config

        assert Config().max_completion_tokens == 1024

    def test_max_seq_len(self):
        from fireworks.training.cookbook.recipes.grpo_loop import Config

        assert Config().max_seq_len == 4096

    def test_group_size(self):
        from fireworks.training.cookbook.recipes.grpo_loop import Config

        assert Config().group_size == 4

    def test_kl_beta(self):
        from fireworks.training.cookbook.recipes.grpo_loop import Config

        assert Config().kl_beta == 0.001


class TestDPODefaults:
    def test_has_tokenizer_model_field(self):
        from fireworks.training.cookbook.recipes.dpo_loop import Config

        cfg = Config()
        assert hasattr(cfg, "tokenizer_model")
        assert cfg.tokenizer_model == ""

    def test_max_seq_len(self):
        from fireworks.training.cookbook.recipes.dpo_loop import Config

        assert Config().max_seq_len == 4096


class TestSFTDefaults:
    def test_has_tokenizer_model_field(self):
        from fireworks.training.cookbook.recipes.sft_loop import Config

        cfg = Config()
        assert hasattr(cfg, "tokenizer_model")
        assert cfg.tokenizer_model == ""

    def test_max_seq_len(self):
        from fireworks.training.cookbook.recipes.sft_loop import Config

        assert Config().max_seq_len == 4096


class TestISConfigDefaults:
    def test_clip_high(self):
        from fireworks.training.cookbook.utils.importance_sampling import ISConfig

        assert ISConfig().clip_high == 2.0

    def test_clip_low(self):
        from fireworks.training.cookbook.utils.importance_sampling import ISConfig

        assert ISConfig().clip_low == 0.0


class TestDAPODefaults:
    def test_eps_clip(self):
        from fireworks.training.cookbook.utils.dapo import DAPOConfig

        assert DAPOConfig().eps_clip == 0.2

    def test_eps_clip_high(self):
        from fireworks.training.cookbook.utils.dapo import DAPOConfig

        assert DAPOConfig().eps_clip_high == 0.28


class TestGSPODefaults:
    def test_clip_ratio(self):
        from fireworks.training.cookbook.utils.gspo import GSPOConfig

        assert GSPOConfig().clip_ratio == 0.2


class TestAdamDefaults:
    def test_adam_params(self):
        from fireworks.training.cookbook.utils.config import DEFAULT_ADAM

        assert DEFAULT_ADAM["beta1"] == 0.9
        assert DEFAULT_ADAM["beta2"] == 0.999
        assert DEFAULT_ADAM["eps"] == 1e-8
        assert DEFAULT_ADAM["weight_decay"] == 0.01
