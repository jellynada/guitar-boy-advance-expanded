# Mission 006: measured results and delivery

## Baseline and source boundaries

Started from Mission005 `f23cb6b4039fec93811b80f557a85518b2f626d1`, containing
Missions001–005. Source branch:mission-006-audio-sync. Main remains original
6c4e634; no automatic merges. Artifact branches stay separate from source.

The original chart, music, graphics, Note ABI, NoteManager, NoteJudgment windows
and Mode7 projection source are unchanged. New imported playback owns FIFO A,
DMA1 and timers0–2 exclusively. Original Maxmod uses the same mode3/16-channel
configuration with retained buffers through public mmInit, so mode handoff does
not repeatedly allocate. Its VBlank clock epoch starts after initialization.
Imported contact geometry was calibrated from actual OAM positions:Mission005's
contact depth crossed the line about54ms late; the new imported depth/lane centers
cross within one frame. This does not change the original demo's geometry.

## Host and conversion checks

`bash tests/check.sh` actually passed:

-32existing chart tests, including host and actual devkitARM header compilation;
-34existing MIDI/package tests;
-9existing Easy adaptation tests;
-12new audio tests:WAV/OPUS decoding, pre-skip/sample counts, different lengths,
 deterministic bytes/manifests, safe headroom/padding, explicit source selection,
 missing decoder, invalid/empty audio, CLI stale-output cleanup, explicit silent
 fallback, corrupt/missing assets, full package preparation, preview rejection,
 short-audio rejection and resolving competing formats by exact package filename.
-Existing C++ ASan/UBSan/leak tests for judgment and the complete699-note chart;
 imported runtime tests for first/final/boundary/hour-long/frame rounding/reset;
 and new sample-clock tests for zero, pre-roll, exact long duration, safe64bit
 arithmetic, shared judgments, monotonic snapshots and misses after frame skips.

**87Python tests passed**, plus the C++ test programs. No GBA compiler test was
skipped in this environment. Python3.12.14, host GCC14.2, FFmpeg7.1.5/ffprobe.
The pinned Docker build uses hostGCC12.2 and the same devkitARM GCC16.1 toolchain.

The actual owner package was accessible and selected explicitly:

```text
python3 tools/prepare_song.py "<owner ZIP path>" --stem guitar --stem rhythm --stem song
```

It decoded the matching package's3OPUS stems, each from48kHz stereo, with
4,378,983resampled mono samples. Duration267.2719116s. Source codec framing/OPUS
pre-skip is handled by FFmpeg; chart source offsets remain0, with the existing2s
pre-roll. No replacement Cream studio recording or unrelated soundtrack.
Repeat full private conversion produced the identical PCM SHA256. Original and
prepared private source/notes/audio remain outside public tracked data.

Private mix:4,436,336bytes including pre-roll/tail/guard/alignment; peak58/127;
quantization-only SNR30.483dB against the resampled mono reference. It is lo-fi
8-bit/mono audio; this metric does not quantify downsampling or subjective quality.

## Actual builds

Public native:

```bash
make -j2
```

Public clean pinned Docker:

```bash
bash scripts/build-docker.sh clean
bash scripts/build-docker.sh
```

Private build:

```bash
make -j2 IMPORTED_HEADER=imports/output/song-runtime/imported_chart.hpp AUDIO_DIR=imports/output/song-runtime/audio
```

Explicit silent fallback:

```bash
make -j2 AUDIO_DIR=none
```

Public synthetic ROM:guitar-boy-advance-expanded.gba, **537696bytes**, SHA256:

```text
b363b4f2f731e20140be56d2c9d7deea01bacf9d5a1ef350a6251a6d45ac03fd
```

Private chart+audio ROM:4720736bytes; retained privately, never published.
No oversized emulator-only cartridge assumptions:post-build check enforces32MiB.
The public synthetic recording has202070source samples (12.333374s),2s pre-roll,
0.5s tail and1s safety guard. Its entire duration is tested. Raw public audio blob
is259424bytes. Actual linked PCM bytes/alignment and all699legacy Note records
are checked against the source/generated inputs. Default builds restore the
synthetic selection after explicit private/silent variants.

## Actual mGBA0.10.1 runs

| Scenario | Frames | Outcome |
| --- | ---: | --- |
| Original perfect | 36000 | 699Perfect,0Miss,0Wrong; sound and hit artwork |
| Original miss | 36000 | 699Miss,0Wrong; sound |
| Original mixed | 36000 | 59Perfect,118Good,522Miss,1200Wrong; sound |
| Synthetic audio perfect | 1800 | 25Perfect,0Miss,0Wrong; full audio/EOF |
| Synthetic audio miss | 1800 | 25Miss,0Wrong; full audio/EOF |
| Private cover audio perfect | 18000 | 395Perfect,0Miss,0Wrong; full267s recording/EOF |
| Private cover audio miss | 18000 | 395Miss,0Wrong; full267s recording/EOF |
| Unexpected timer stop | 1000 | AUDIO ERROR; clock and judgments freeze |
| Unexpected DMA stop | 1000 | AUDIO ERROR; clock and judgments freeze |
| Unexpected sound disable | 1000 | AUDIO ERROR; clock and judgments freeze |
| Labeled silent fallback | 1800 | 25Miss,0nonzero audio samples; frame clock |
| Mission005 silent all-hit harness | 1800 | 25Perfect; unchanged silent controls/judgments |

New audio scenarios each repeat4original/imported return cycles:original audio
resumes, counters and sample position reset, and no core crash. The old silent
harness also repeats3return cycles. Fault scenarios inject new lane presses after
the fault and verify they cannot award/judge notes or add wrong-input events.
Original all-hit visible feedback remains6081frames, matching Mission005.

Imported tests inspect actual OAM affine IDs/positions at the fret line, including
all3lanes and first/middle/final references. They require crossing error≤one
GBAframe and expected positions. The observed pixel crossings are sampled, not
sub-frame optical measurements. A synthetic screenshot was inspected; original
floor/art and the two-choice layout are preserved.

## Audio verification beyond nonzero samples

Full emulated output was captured as mono32768Hz signed16 samples. Left/right
are asserted equal for imported mono. CPU timing traces capture actual cascaded
hardware counts and the software snapshot. Independent NumPy waveform matching
compares the captured sound against the prepared PCM (not just note timestamps).

| Reference | Expected runtime | Actual line crossing | Line error | Captured waveform residual |
| --- | ---: | ---: | ---: | ---: |
| Synthetic first | 2.000000s | 2.003906s | 3.906ms | 0.275ms |
| Synthetic middle | 9.333333s | 9.337219s | 3.886ms | 0.275ms |
| Synthetic final | 13.333333s | 13.338684s | 5.351ms | 0.275ms |
| Private first | 6.322000s | 6.323425s | 1.425ms | 0.488ms |
| Private middle | 139.434000s | 139.444702s | 10.702ms | 0.427ms |
| Private final | 264.880000s | 264.881042s | 1.042ms | 0.397ms |

Actual requested sample indices at the displayed crossings are recorded in the
CSV trace; gameplay ticks=sample_index×1024. Source sample zero follows32768
prefix samples. Header/source first actual note4.322s therefore reaches the line
near runtime6.322s. The clock uses sample request index max(0,count−1), not a
software fill/write cursor. No additional guessed frontend correction is applied.

Waveform correlations:synthetic≥0.99919, private≥0.98988. Output peaks17001 and
10720 of32767, respectively;0clipped samples. Last captured second after natural
EOF is silent. Observed early/middle/late residual spread:0synthetic,0.09155ms
private. Private capture-epoch variation is0.24414ms, so this cannot establish
analog drift below that measurement uncertainty. Maximum all-note hit sampling
error16.052246ms synthetic,16.725123ms private; video period16.742706ms.

Capture checking commands (public):

```bash
bash tests/run_audio_emulator.sh perfect 1800 /tmp/synthetic
python3 tests/analyze_audio.py --pcm build/imported_audio.bin --capture /tmp/synthetic.raw --csv /tmp/synthetic.csv --times 2,9.333333,13.333333 --output /tmp/synthetic-analysis.json
```

The optional analysis requires NumPy. Owner preparation/build needs only Python,
FFmpeg/ffprobe and the documented GBA toolchain/container. No manual listening,
human-perceived synchronization, physical GBA run or latency calibration claimed.
Public evidence includes synthetic captures; private audio/captures/trace data
are excluded. Only aggregate private findings and requested reference measurements
are published.

## Performance, memory and feasibility

Timer3 measures foreground work, excluding idle VBlank waiting and IRQ work
outside that interval. Synthetic mean about72698cycles/frame (25.9%), peak94528
(33.7%). Private mean about76248 (27.1%), peak94336 (33.6%) across scenarios.
This is not a complete physical-hardware CPU-utilization measurement. DMA bus
traffic/ISR costs are not independently hardware-profiled. No per-sample CPU
handler, software decoder or imported PCM RAM buffer exists.

Public linked IWRAM sections25344bytes; private25712bytes, before stack/BIOS
reservations. EWRAM2528bytes for both. Original Maxmod buffers reserve3584bytes
within those totals; PCM state adds a few words, with music left in ROM.

Audio payload at16384Hz mono8:0.9375MiB/minute,2.8125MiB/3min,3.75MiB/4min.
Ten songs:28.125–37.5MiB plus about0.55MiB total per-song timing/guard overhead,
plus code/charts/art. Ten3minute songs might fit narrowly; ten4minute songs do
not fit conventional32MiB. Ten similarly sized private mixes exceed42MiB of
prepared audio. Lower-rate PCM or a qualified ADPCM decoder/quality budget and
separate ROM packs are options, not implemented multisong support.

## Review handoff and remaining limits

Review base:mission-005-first-playable-import. Source head:mission-006-audio-sync.
The exact source commit is recorded in the bundle. Public downloads use a separate
mission-006-download branch; it must not be merged into source/main. PR creation
outcome is recorded after the actual attempt below.

Limits:one mixed recording, lo-fi mono8bit, no runtime OPUS/MP3/ADPCM decoder,
no reactive stems, imported Medium/Hard, scoring, sustain mechanics or full song
menu. Timer-derived clock is not speaker feedback; disabled-resource checks do
not constitute hardware FIFO loopback. Guard assumes normal IRQ servicing.
No in-game pause/calibration slider, subjective-quality or physical-device claim.
Next:human/hardware calibration and compressed-format feasibility measurements
before expanding the library or reactive audio.

Measurement interpretation: line crossings use the game draw snapshot and OAM sprite positions; physical scanout and host presentation latency were not measured. Miss-run REFERENCE rows record the late judgment deadline, not a note-line crossing. The mixed legacy input script varies with launch phase; its 177 hits split into 59 Perfect/118 Good in this final run, without changing judgment windows.
