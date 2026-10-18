#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
repo="$PWD"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
g++ -std=c++17 -O2 bin/chart_reader.cpp -o "$tmp/chart_reader"
"$tmp/chart_reader" charts/careless.chart "$tmp/generated"
g++ -std=c++17 -g -fsanitize=address,undefined -fno-omit-frame-pointer \
    -Itests/host -Iinclude -I"$tmp/generated" tests/note_manager.cpp -o "$tmp/note_manager"
# The original manager owns two process-lifetime display objects and has no destructor.
ASAN_OPTIONS=detect_leaks=0 "$tmp/note_manager"
python3 - "$tmp" <<'PY'
import pathlib, re, subprocess, sys
p = pathlib.Path(sys.argv[1])
asm = (p / 'generated/careless.s').read_text()
source = pathlib.Path('charts/careless.chart').read_text(encoding='utf-8-sig')
records = [tuple(map(int, m)) for m in re.findall(r'(\d+) = N (\d+) (\d+)', source)]
assert len(records) == 699
assert '.balign 8' in asm
assert len(re.findall(r'\.8byte ', asm)) == len(records)
assert len(re.findall(r'\.4byte ', asm)) == 2 * len(records) + 1
assert [int(x) for x in re.findall(r'\.8byte (\d+)', asm)] == [int(t / 192 * 3567673) for t, _, _ in records]
for resolution in ('0', '192'):
    chart = p / 'bad.chart'
    chart.write_text('[Song]\n{\n' + ('Resolution = 0\n' if resolution == '0' else '') + '}\n[ExpertSingle]\n{\n100 = N 0 0\n}\n')
    result = subprocess.run([str(p / 'chart_reader'), str(chart), str(p / 'bad')], capture_output=True, text=True)
    assert result.returncode != 0 and 'Resolution' in result.stderr
print('PASS: note bounds under ASan/UBSan; 699 chart records and unchanged timing; invalid resolution rejected')
PY
