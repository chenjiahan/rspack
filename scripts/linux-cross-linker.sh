#!/usr/bin/env bash
set -euo pipefail

# Cargo selects Rust's bundled LLD; retain NAPI cross's libc and GCC runtime.
exec clang \
  --target="$RUST_TARGET" \
  --sysroot="$TARGET_SYSROOT" \
  --gcc-toolchain="${TARGET_SYSROOT%/*/*}" \
  "$@"
