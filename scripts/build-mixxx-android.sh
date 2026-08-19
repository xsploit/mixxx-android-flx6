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

apply_patch_if_needed() {
    local patch_path="$1"
    if git apply --check "${patch_path}" 2>/dev/null; then
        git apply "${patch_path}"
    elif ! git apply --reverse --check "${patch_path}" 2>/dev/null; then
        echo "Patch is neither applicable nor already applied: ${patch_path}" >&2
        exit 1
    fi
}

apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-wsl.patch"
if ! grep -qE 'android:versionName="0\.(3\.0-active-phone-ui|4\.0-performance-view|5\.0-waveform-fix|6\.0-android-storage)"' packaging/android/AndroidManifest.xml; then
    apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-phone-ui.patch"
    apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-v0.3-version.patch"
    apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-active-phone-ui.patch"
fi
if ! grep -qE 'android:versionName="0\.(4\.0-performance-view|5\.0-waveform-fix|6\.0-android-storage)"' packaging/android/AndroidManifest.xml; then
    apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-v0.4-performance-view.patch"
fi
if ! grep -qE 'android:versionName="0\.(5\.0-waveform-fix|6\.0-android-storage)"' packaging/android/AndroidManifest.xml; then
    apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-v0.5-version.patch"
    apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-v0.5-waveform-fix.patch"
fi
if ! grep -q 'android:versionName="0.6.0-android-storage"' packaging/android/AndroidManifest.xml; then
    apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-v0.6-version.patch"
    apply_patch_if_needed "${REPO_DIR}/patches/mixxx-android-v0.6-storage-access.patch"
fi

install -m 0644 \
    "${REPO_DIR}/controller-mapping/Pioneer-DDJ-FLX6.midi.xml" \
    "${MIXXX_SOURCE}/res/controllers/Pioneer-DDJ-FLX6.midi.xml"
install -m 0644 \
    "${REPO_DIR}/controller-mapping/Pioneer-DDJ-FLX6-script.js" \
    "${MIXXX_SOURCE}/res/controllers/Pioneer-DDJ-FLX6-script.js"

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
