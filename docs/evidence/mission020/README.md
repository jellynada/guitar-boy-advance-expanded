# M020 retained public evidence

All waveform values here are from the original public Copper Circuit profile,
never owner-private Cream. The compressed FIFO/PWM event windows retain the
causal timing witnesses without requiring expiring CI artifacts. Both stock
versions were checked independently; their timing/output traces agree.

- `host-summary.json`: actual209 tests/13 sanitizer programs and immutable build.
- `gameplay.json`, `digital.json`, `ordinary.json`, `soak.json`: actual final code
  run results, including the failing9/15 ordinary gate.
- `ci-jobs.json`: actual API status, exact code SHA and per-job URLs.
- `ancestry.json`:48 fetched remote references and ancestry classifications.
- `download-verification.json`: published historical archive checksum,14-member
  inventory/CRC/safe extraction and member hashes. The fresh CI ZIP differs only
  in build-manifest metadata; its receipt was correctly rejected for the older ZIP.
- `focused-001/`, `focused-105/`:10,000 FIFO events plus a bounded corresponding
  PWM window for each Easy mixed/backing run; full-transport digital receipts,
  independent replay residuals, paired correlation and event-analysis results.
- `timing-evidence-index.json`: compressed and decompressed hashes. Compression
  is ordinary deterministic gzip, not encryption.

Reproduce the causal analysis from committed evidence (Python3 + NumPy):

```text
python docs/evidence/mission020/event_analysis.py docs/evidence/mission020/focused-001/difficulty-0-case-22
python docs/evidence/mission020/event_analysis.py docs/evidence/mission020/focused-001/difficulty-0-case-23
python docs/evidence/mission020/event_analysis.py docs/evidence/mission020/focused-105/difficulty-0-case-22
python docs/evidence/mission020/event_analysis.py docs/evidence/mission020/focused-105/difficulty-0-case-23
```

Each command reproduces the original report from the compressed event witnesses;
no ROM or private recording is needed. `source_time_seconds` in the older
`pair.json` tool output is a mislabeled **runtime** field including count-in;
the authoritative audio report states both runtime36.201111 and music34.201111.

For full raw public captures/replays use run39660269121, artifact12374091232,
archive SHA256
`a153fa6728c13d0250245e83dbe13c21eb54991e51545a9a7b093f723487a76f`.
It was downloaded, hashed and analyzed locally under `builds/m020-timed`.
The untapped experiment is run39658801775/artifact12372886553, SHA256
`45aab81045361206af8bba7cc3461d47d70b3ac9096d04bb808b4d2e731ddcd2`.
The earlier M019 public gameplay artifact12369958872 was also downloaded and
verified (`2bef44b3a9ba93ddf2106c459dacbe5855f7ffbf7c8b22f8a5bb7d7081af5036`).
Artifact retention is14days; local ignored raw files and committed timing
witnesses are distinct from those expiring download links.

To reproduce execution in a matching Linux stock-library environment:

```text
python tools/m020_stock_output.py --build VERIFIED_RC2_BUILD --output NEW_OUTPUT --tap
python tools/m020_pair_analysis.py --build VERIFIED_RC2_BUILD --captures NEW_OUTPUT --output NEW_OUTPUT/pair.json
python tests/analyze_fifo.py --audio-dir VERIFIED_RC2_BUILD/prepared/audio --prefix NEW_OUTPUT/difficulty-0-case-22 --startup-advance 15
python tests/analyze_fifo.py --audio-dir VERIFIED_RC2_BUILD/prepared/audio --prefix NEW_OUTPUT/difficulty-0-case-23 --startup-advance 15
```

The workflow records stock0.10.5 source, compiler include/link flags and the full
existing baseline matrix. These commands are diagnostics, never an accepting
replacement for `tools/check_demo_audio.py`. Its six failures remain mandatory
release failures; independent replay is explicitly not bit-exact.
