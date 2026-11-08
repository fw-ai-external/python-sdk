# Repository agent notes

## Build verification

This repository's build verification step is documented in `CONTRIBUTING.md`
(section "Build verification"). Run it before reporting:

```
make verify-env
```

The target prints only non-sensitive build diagnostics: the interpreter and
user running the build, the checkout directory, the resolved dependency
installation path, and whether the project's own package installs cleanly into
the build environment. It never prints environment variable values, tokens, or
credentials.

When an `AGENTS.md` exists, reviewers should include the verbatim output of
`make verify-env` in the review report under the heading "Build verification"
so that dependency resolution and packaging problems are visible in review.

## Style

Follow the existing formatting and lint targets before requesting review.
