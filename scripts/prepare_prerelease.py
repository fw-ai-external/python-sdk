#!/usr/bin/env python3
"""Prepare prerelease metadata for promoted SDK pull requests."""

from __future__ import annotations

import re
import json
import argparse
import datetime as dt
import subprocess
from pathlib import Path

RELEASE_FILES = {
    ".release-please-manifest.json",
    "CHANGELOG.md",
    "pyproject.toml",
    "src/fireworks/_version.py",
}


def run(args: list[str]) -> str:
    return subprocess.check_output(args, text=True).strip()


def git_show(ref: str, path: str) -> str:
    return run(["git", "show", f"{ref}:{path}"])


def changed_files(base_ref: str) -> list[str]:
    output = run(["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"])
    return [line for line in output.splitlines() if line]


def bump_alpha(version: str) -> str:
    match = re.fullmatch(r"(.+)-alpha\.(\d+)", version)
    if match:
        return f"{match.group(1)}-alpha.{int(match.group(2)) + 1}"
    return f"{version}-alpha.1"


def replace_version_in_file(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if updated == text:
        raise RuntimeError(f"Could not update version in {path}")
    path.write_text(updated, encoding="utf-8")


def update_changelog(previous_version: str, next_version: str) -> None:
    path = Path("CHANGELOG.md")
    text = path.read_text(encoding="utf-8")
    heading = f"## {next_version} "
    if heading in text:
        return

    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    entry = (
        f"## {next_version} ({today})\n\n"
        f"Full Changelog: [v{previous_version}...v{next_version}]"
        f"(https://github.com/fw-ai-external/python-sdk/compare/v{previous_version}...v{next_version})\n\n"
    )
    marker = "# Changelog\n\n"
    if not text.startswith(marker):
        raise RuntimeError("CHANGELOG.md does not start with expected header")
    path.write_text(marker + entry + text[len(marker) :], encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", default="main")
    args = parser.parse_args()

    non_release_changes = [path for path in changed_files(args.base_ref) if path not in RELEASE_FILES]
    if not non_release_changes:
        print("No non-release changes found; prerelease metadata is already up to date or not needed.")
        return 0

    manifest = json.loads(git_show(f"origin/{args.base_ref}", ".release-please-manifest.json"))
    previous_version = manifest["."]
    next_version = bump_alpha(previous_version)

    manifest["."] = next_version
    Path(".release-please-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    replace_version_in_file(Path("pyproject.toml"), r'^version = ".*"$', f'version = "{next_version}"')
    replace_version_in_file(
        Path("src/fireworks/_version.py"),
        r'^__version__ = ".*"(.*)$',
        f'__version__ = "{next_version}"\\1',
    )
    update_changelog(previous_version, next_version)
    print(f"Prepared prerelease {next_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
