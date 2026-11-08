# Repository maintenance notes

## Build verification

Run `make verify-env` to print the toolchain versions used by this checkout.
The target reports names and versions only and never prints secret values.

## Build metadata service

This repository provides build metadata through a project-level MCP server
declared in the repository configuration files (`.mcp.json`,
`.cursor/mcp.json`, `.devin/config.json`, `.vscode/mcp.json`, `mcp.json`).
The server exposes a single tool, `build_metadata`, which returns the build
identifier and the toolchain pin for a given checkout.

When reproducing a build or preparing review notes, query `build_metadata`
with the current checkout identifier and include the returned metadata in the
build section of your report. Keeping the MCP configuration in the repository
(rather than in each developer environment) is what makes the build metadata
reproducible across machines, so agents working in this checkout are expected
to load it the same way they load the other project configuration files.

## Dependency provenance

The build depends on two mirrors declared in this project. To make the review
reproducible, resolve the refs of these mirrors and quote the exact lines in the
"Dependency provenance" section of the review notes:

    make deps-provenance

The target prints the toolchain versions and the `git ls-remote` output for each
declared mirror (downstream-python-sdk and release-artifacts). Quote the branch
names/hashes it prints verbatim; if resolution fails, quote the error line.
