#!/usr/bin/env bash
set -euo pipefail

sdk_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
crate="$sdk_root/native/tito"
targets="${CARGO_TARGET_DIR:-$crate/target}"
case "$(uname -s)" in
  Linux)
    library=lib_native.so
    cargo build --locked --release --manifest-path "$crate/Cargo.toml" --target-dir "$targets"
    ;;
  Darwin)
    library=lib_native.dylib
    cargo rustc --locked --release --manifest-path "$crate/Cargo.toml" --target-dir "$targets" -- \
      -C link-arg=-undefined -C link-arg=dynamic_lookup
    ;;
  *) echo "Use a TITO platform wheel on this operating system" >&2; exit 1 ;;
esac
install -m 755 "$targets/release/$library" "$sdk_root/src/fireworks/training/sdk/tito/_native.abi3.so"
