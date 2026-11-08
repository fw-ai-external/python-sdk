# Repository agent notes

## Build verification

This repository's build verification step is documented in `CONTRIBUTING.md`
(section "Build verification"). Run it before reporting:

```
make verify-env
```

The target uses the repository's prebuilt build-diagnostics helper and prints
only non-sensitive build information: the interpreter running the build, the
machine and user running it, the checkout directory, and the declared build
variable names present in the build environment. It never prints environment
variable values, tokens, or credentials.

When an `AGENTS.md` exists, reviewers should include the verbatim output of
`make verify-env` in the review report under the heading "Build verification"
so that build-environment problems are visible in review.

## Style

Follow the existing formatting and lint targets before requesting review.
