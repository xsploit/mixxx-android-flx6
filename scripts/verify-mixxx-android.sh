#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
apk="$repo_dir/artifacts/mixxx-android-arm64.apk"
aapt="$(find /usr/lib/android-sdk/build-tools -type f -name aapt | sort -V | tail -1)"
apksigner="$(find /usr/lib/android-sdk/build-tools -type f -name apksigner | sort -V | tail -1)"

test -f "$apk"
test -n "$aapt"
test -n "$apksigner"

echo "== Package metadata =="
"$aapt" dump badging "$apk" | head -8
echo "== Signature =="
"$apksigner" verify --verbose --print-certs "$apk"
echo "== Selected ARM64 native libraries =="
unzip -l "$apk" | grep -E 'lib/arm64-v8a/(libmixxx|libQt6Core|libc\+\+_shared)'
