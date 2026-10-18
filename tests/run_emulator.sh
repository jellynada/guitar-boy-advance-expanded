#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mode=${1:-miss}
output=${2:-/tmp/mission002-$mode.ppm}
frames=${3:-36000}
: "${DEVKITARM:?Set DEVKITARM to the GBA toolchain directory}"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
gcc -O2 -Wall -Wextra -Werror tests/emulator_smoke.c -o "$tmp/emulator_smoke" -lmgba
symbols=$("$DEVKITARM/bin/arm-none-eabi-nm" guitar-boy-advance-expanded.elf)
symbol() {
    local address
    address=$(awk -v name="$1" '$3 == name {print $1}' <<< "$symbols")
    test -n "$address"
    echo "$address"
}
"$tmp/emulator_smoke" "$PWD/guitar-boy-advance-expanded.gba" "$(symbol recent_sprite)" \
    699 "$frames" "$output" "$mode" "$(symbol gameplayFrames)" \
    "$(symbol displayedStats)" "$(symbol careless_expertsingle_data)" 83330
