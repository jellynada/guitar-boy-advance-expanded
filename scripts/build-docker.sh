#!/usr/bin/env bash
# The image digest pins the compiler, libraries, graphics and audio tools.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
image=$(cat "$repo/scripts/toolchain-image.txt")
docker pull "$image"
docker run --rm --user "$(id -u):$(id -g)" \
    -v "$repo:/workspace/guitar-boy-advance-expanded" \
    -w /workspace/guitar-boy-advance-expanded "$image" make -j2 "$@"
