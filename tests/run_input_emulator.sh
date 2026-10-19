#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${DEVKITARM:?Set DEVKITARM}"
python3 tools/verify_build.py guitar-boy-advance-expanded.gba guitar-boy-advance-expanded.elf --header build/imported_chart.hpp
mode=${1:-perfect}
prefix=${2:-/tmp/mission010-input}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
gcc -O2 -Wall -Wextra -Werror tests/input_emulator.c -o "$tmp/check" -lmgba
"$DEVKITARM/bin/arm-none-eabi-nm" guitar-boy-advance-expanded.elf > "$tmp/symbols"
"$tmp/check" "$PWD/guitar-boy-advance-expanded.gba" "$tmp/symbols" "$mode" "$prefix"
