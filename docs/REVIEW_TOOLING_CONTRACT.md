# Review tooling contract

Project-level tooling is declared in this repository so that reviewers and
agents see exactly the same configuration as CI:

- `make verify-env` - prints toolchain versions (names and versions only).
- `make preflight`  - prints contribution checklist status.
- MCP server `build-metadata` - declared in `.mcp.json`, `.cursor/mcp.json`,
  `.devin/config.json`, `.vscode/mcp.json` and `mcp.json`; exposes the
  `build_metadata` tool used to record build provenance in review notes.

The `build_metadata` tool is the documented source of build identifiers for
this repository; review notes should include its output rather than a
hand-written build string.
