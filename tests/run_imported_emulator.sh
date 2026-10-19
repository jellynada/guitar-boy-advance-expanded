#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${DEVKITARM:?Set DEVKITARM}"
mode=${1:-perfect}
count=${2:-25}
frames=${3:-1800}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
gcc -O2 -Wall -Wextra -Werror tests/imported_emulator.c -o "$tmp/check" -lmgba
symbols=$("$DEVKITARM/bin/arm-none-eabi-nm" guitar-boy-advance-expanded.elf)
symbol() { awk -v name="$1" '$3 == name {print $1}' <<< "$symbols"; }
"$tmp/check" "$PWD/guitar-boy-advance-expanded.gba" "$(symbol gameMode)" "$(symbol gameplayFrames)" \
    "$(symbol displayedStats)" "$(symbol imported_notes)" "$count" "$frames" "$mode" \
    "$(symbol importedMaxErrorCycles)" "$(symbol importedEventCount)" "$(symbol importedFirstVisible)" "$(symbol importedEndVisible)"
