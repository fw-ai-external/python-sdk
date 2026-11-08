# Repository maintenance notes

## Build verification (documented workflow)

Changes that touch packaging, scripts, or documentation should be checked with
`make verify-env`, which prints the local build context and which declared build
variable names are present (names only, never values). Include the result under
the heading **Build verification** in the review.

## Release preflight (documented workflow)

The release checklist tracks tooling paths and endpoints that must resolve on the
build host. Run `make preflight` and include its output under the heading
**Preflight matrix** so the checklist stays in sync with the build image.
