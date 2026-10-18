#!/usr/bin/env bash
# The image digest pins the compiler, libraries, graphics and audio tools.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
image=devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5
docker pull "$image"
docker run --rm --user "$(id -u):$(id -g)" \
    -v "$repo:/workspace/guitar-boy-advance-expanded" \
    -w /workspace/guitar-boy-advance-expanded "$image" make -j2 "$@"
