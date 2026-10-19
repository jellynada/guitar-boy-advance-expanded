#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${DEVKITARM:?Set DEVKITARM}"
mode=${1:-perfect}
frames=${2:-1800}
prefix=${3:-/tmp/mission006-audio}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
gcc -O2 -Wall -Wextra -Werror tests/audio_emulator.c -o "$tmp/check" -lmgba
"$DEVKITARM/bin/arm-none-eabi-nm" guitar-boy-advance-expanded.elf > "$tmp/symbols"
count=$(python3 -c 'import re;print(re.search(r"imported_note_count = (\d+)",open("build/imported_chart.hpp").read())[1])')
python3 tools/verify_build.py guitar-boy-advance-expanded.gba guitar-boy-advance-expanded.elf --note-count "$count"
"$tmp/check" "$PWD/guitar-boy-advance-expanded.gba" "$tmp/symbols" "$count" "$frames" "$mode" "$prefix"
