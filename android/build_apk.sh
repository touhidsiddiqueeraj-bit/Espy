#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "==> EasyESP APK Builder"
echo ""
echo "Choose method:"
echo "  1) Docker (recommended — no SDK/NDK needed)"
echo "  2) Native (requires JDK 17+, Android SDK, Android NDK)"
read -rp "Method [1/2]: " method

if [ "$method" = "1" ]; then
    echo ""
    echo "==> Building with Docker..."
    echo "    This will pull the kivy/buildozer image (~2GB) on first run."
    echo "    The build itself takes 15-30 minutes."
    echo ""

    # Create buildozer cache dir if missing
    mkdir -p "$HOME/.buildozer"

    docker run \
        --interactive --tty --rm \
        --volume "$(pwd):/home/user/hostcwd" \
        --volume "$HOME/.buildozer:/home/user/.buildozer" \
        kivy/buildozer:latest \
        android debug

    echo ""
    echo "==> Build complete! APK should be in: $(pwd)/bin/"

elif [ "$method" = "2" ]; then
    echo ""
    echo "==> Building natively..."

    # Check requirements
    command -v java >/dev/null 2>&1 || { echo "ERROR: java not found. Install JDK 17+."; exit 1; }
    echo "  [OK] java found"

    if [ -z "${ANDROID_SDK_ROOT:-}" ] && [ -z "${ANDROID_HOME:-}" ]; then
        echo "  WARNING: ANDROID_SDK_ROOT not set. Buildozer will download SDK/NDK."
        echo "  This adds ~2GB of downloads and ~30min to the build time."
        echo "  Press Ctrl+C now to set ANDROID_SDK_ROOT, or wait to continue."
        sleep 5
    else
        echo "  [OK] SDK root: ${ANDROID_SDK_ROOT:-$ANDROID_HOME}"
    fi

    buildozer android debug
    echo ""
    echo "==> Build complete! APK in: $(pwd)/bin/"

else
    echo "Invalid choice."
    exit 1
fi
