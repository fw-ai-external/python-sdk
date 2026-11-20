"""Include the audited TITO extension in a platform wheel when supplied."""

from __future__ import annotations

import os
from typing import Any
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, _version: str, build_data: dict[str, Any]) -> None:
        extension_path = os.environ.get("FIREWORKS_TITO_NATIVE_EXTENSION")
        if self.target_name != "wheel" or not extension_path:
            return
        extension = Path(extension_path).resolve(strict=True)
        if extension.name != "_native.abi3.so":
            raise ValueError("Expected an audited TITO extension named _native.abi3.so")
        build_data["pure_python"] = False
        build_data["tag"] = "cp311-abi3-manylinux_2_34_x86_64"
        build_data["force_include"][str(extension)] = f"fireworks/training/sdk/tito/{extension.name}"
