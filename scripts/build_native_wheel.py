"""Build the Linux x86-64 ABI3 SDK wheel from the same source as the universal wheel."""

from __future__ import annotations

import os
import sys
import argparse
import tempfile
import subprocess
from pathlib import Path
from zipfile import ZipFile

SDK_ROOT = Path(__file__).resolve().parents[1]
PLATFORM_TAG = "manylinux_2_34_x86_64"
WHEEL_TAG = f"cp311-abi3-{PLATFORM_TAG}"
EXTENSION_NAME = "_native.abi3.so"


def build_native_wheel(output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="tito-native-wheel-") as temp:
        directory = Path(temp)
        subprocess.run(
            [
                "maturin",
                "build",
                "--locked",
                "--release",
                "--compatibility",
                "manylinux_2_34",
                "--interpreter",
                sys.executable,
                "--out",
                str(directory),
            ],
            cwd=SDK_ROOT / "native/tito",
            check=True,
        )
        (wheel,) = directory.glob(f"*-{WHEEL_TAG}.whl")
        with ZipFile(wheel) as archive:
            payload = [path for path in archive.namelist() if ".dist-info/" not in path]
            (module,) = [path for path in payload if Path(path).name == EXTENSION_NAME]
            if any(path != module and not path.endswith("/__init__.py") for path in payload):
                raise ValueError("TITO extension must be loadable independently of wheel side files")
            extension = directory / EXTENSION_NAME
            extension.write_bytes(archive.read(module))
        subprocess.run(
            [sys.executable, "-m", "build", "--wheel", "--outdir", str(output.resolve())],
            cwd=SDK_ROOT,
            env={**os.environ, "FIREWORKS_TITO_NATIVE_EXTENSION": str(extension)},
            check=True,
        )
    (wheel,) = output.glob(f"fireworks_ai-*-{WHEEL_TAG}.whl")
    with ZipFile(wheel) as archive:
        archive.getinfo(f"fireworks/training/sdk/tito/{EXTENSION_NAME}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=SDK_ROOT / "dist")
    build_native_wheel(parser.parse_args().outdir)
