"""Generate the SDK's installed snapshot of the existing Cookbook tool encoder."""

from __future__ import annotations

import argparse
from pathlib import Path


def generate(source: str) -> str:
    header = (
        "# TEMPORARY DUPLICATION: generated from the maintained Cookbook\n"
        "# training/renderer/kimi_k2_5_tool_declaration_ts.py tool encoder.\n"
        "# Upstream notice: _vendored/kimi_k2/LICENSE (Moonshot AI).\n"
        "# Regenerate: python scripts/generate_kimi_k2_tools.py\n"
        "# Removal: delegate the Cookbook encoder to this SDK implementation\n"
        "# once the matching SDK is the supported Cookbook dependency floor.\n"
    )
    source = source.replace(
        '"""\n\nimport dataclasses',
        '"""\n\nfrom __future__ import annotations\n\nimport dataclasses',
        1,
    )
    return header + source.replace(
        "import dataclasses\nimport json\nimport logging\nfrom collections.abc import Sequence\nfrom typing import Any",
        "import json\nimport logging\nimport dataclasses\nfrom typing import Any\nfrom collections.abc import Sequence",
        1,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sdk = Path(__file__).resolve().parents[1]
    source = sdk.parent / "cookbook/training/renderer/kimi_k2_5_tool_declaration_ts.py"
    destination = sdk / "src/fireworks/training/sdk/_kimi_k2_tools.py"
    expected = generate(source.read_text(encoding="utf-8"))
    if args.check:
        return int(destination.read_text(encoding="utf-8") != expected)
    destination.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
