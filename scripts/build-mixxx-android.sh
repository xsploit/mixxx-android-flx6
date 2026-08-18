#!/usr/bin/env bash

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIXXX_SOURCE="${MIXXX_SOURCE:-/root/mixxx-android-src}"
MIXXX_BUILD="${MIXXX_BUILD:-/root/mixxx-android-build}"
OUTPUT_DIR="${OUTPUT_DIR:-${REPO_DIR}/artifacts}"
BUILD_JOBS="${BUILD_JOBS:-4}"
KEYSTORE_PATH="${KEYSTORE_PATH:-/root/mixxx-android-local.keystore}"

if [[ ! -d "${MIXXX_SOURCE}/.git" ]]; then
    echo "Mixxx source checkout not found: ${MIXXX_SOURCE}" >&2
    exit 1
fi

cd "${MIXXX_SOURCE}"

WSL_PATCH="${REPO_DIR}/patches/mixxx-android-wsl.patch"
if git apply --check "${WSL_PATCH}" 2>/dev/null; then
    git apply "${WSL_PATCH}"
fi

set +u
source tools/android_buildenv.sh setup
set -u

if [[ ! -f "${KEYSTORE_PATH}" ]]; then
    keytool -genkeypair \
        -keystore "${KEYSTORE_PATH}" \
        -storetype JKS \
        -storepass mixxx-local \
        -keypass mixxx-local \
        -alias mixxx-local \
        -keyalg RSA \
        -keysize 2048 \
        -validity 3650 \
        -dname "CN=Local Mixxx Android Build"
fi

export QT_ANDROID_KEYSTORE_ALIAS=mixxx-local
export QT_ANDROID_KEYSTORE_KEY_PASS=mixxx-local
export QT_ANDROID_KEYSTORE_PATH="${KEYSTORE_PATH}"
export QT_ANDROID_KEYSTORE_STORE_PASS=mixxx-local

cmake \
    -S "${MIXXX_SOURCE}" \
    -B "${MIXXX_BUILD}" \
    -DCMAKE_TOOLCHAIN_FILE="${MIXXX_VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" \
    -DCMAKE_SYSTEM_NAME=Android

cmake --build "${MIXXX_BUILD}" --target apk --parallel "${BUILD_JOBS}"

APK_PATH="$(find "${MIXXX_BUILD}" -type f -name '*release-signed.apk' -print -quit)"
if [[ -z "${APK_PATH}" ]]; then
    APK_PATH="$(find "${MIXXX_BUILD}" -type f -name '*.apk' -print -quit)"
fi

if [[ -z "${APK_PATH}" ]]; then
    echo "Build completed but no APK was found under ${MIXXX_BUILD}" >&2
    exit 1
fi

mkdir -p "${OUTPUT_DIR}"
cp -f "${APK_PATH}" "${OUTPUT_DIR}/mixxx-android-arm64.apk"
git rev-parse HEAD > "${OUTPUT_DIR}/mixxx-source-commit.txt"
sha256sum "${OUTPUT_DIR}/mixxx-android-arm64.apk" > "${OUTPUT_DIR}/mixxx-android-arm64.apk.sha256"

echo "APK=${OUTPUT_DIR}/mixxx-android-arm64.apk"
