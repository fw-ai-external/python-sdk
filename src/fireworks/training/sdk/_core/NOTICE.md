# Training runtime provenance

The initial Fireworks-owned runtime and schemas were mechanically ported from
Thinking Machines Lab's Apache-2.0 licensed Tinker 0.23.0 distribution. The
original license is included in LICENSE.txt. Source hashes before adaptation
are recorded in upstream-source.json. This is a permanent owned implementation:
it does not import, install, or delegate to the upstream package.

Fireworks-specific schema, transport and future support is maintained directly
here. The CLI and upstream test modules were excluded. Wire field names and
checkpoint URI schemes are retained for server compatibility.
