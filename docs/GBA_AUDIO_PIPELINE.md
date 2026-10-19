# Mission 006: imported audio playback and synchronization

The public ROM now **plays original synthetic audio** with its matching 25-note
Easy chart. The owner's actual Cream/WaveGroup package was converted and played
privately, end to end, with its 395-note Easy chart. Imported mode remains
Left / A / B and onset-only. No reactive audio, scoring or sustain mechanics.

The two-choice selector and original 699-note demo remain. Up/Down chooses a
mode; A or Start begins; Start+Select returns. The return chord cannot also
confirm a selection. A mode starts a fresh audio timeline and note state.

## Windows 11: two commands after installation

Use the complete source review bundle, unzip it, and open **Ubuntu/WSL**. The
commands below belong in Ubuntu. Docker Desktop should be running with Ubuntu
WSL integration enabled. The WSL/Docker installation steps are in
[GBA_CHART_ADAPTATION.md](GBA_CHART_ADAPTATION.md).

Install/check the host decoder once:

```bash
sudo apt update
sudo apt install python3 ffmpeg
python3 --version
ffmpeg -version
ffprobe -version
```

Python 3.10+ is required. Actual conversion tests used FFmpeg7.1.5, including
its OPUS decoder, and Python3.12.14. Ubuntu's packaged FFmpeg/ffprobe is the
recommended install. Version and conversion settings are recorded in audio.json;
byte-identical output across different decoder versions is not promised. Repeat
conversion with the tested version produced identical PCM hashes. No pip package
is needed to prepare/build; optional developer waveform analysis uses NumPy.
The pinned GBA build container already has Python; it does not need FFmpeg because
it consumes prepared PCM or generates the public synthetic clip with standard Python.

In Ubuntu, change into the extracted project folder, for example:

```bash
cd "/mnt/c/Users/YOURNAME/Downloads/mission006-review"
```

Replace YOURNAME/path with yours. Put your authorized ZIP into imports/incoming.
Then run these two commands, one at a time:

```bash
python3 tools/prepare_song.py "imports/incoming/Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip" --stem guitar --stem rhythm --stem song
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/song-runtime/imported_chart.hpp" "AUDIO_DIR=imports/output/song-runtime/audio"
```

The explicit stem options include all three matching gameplay stems. Preview is
excluded. We do not assume song.opus is the complete mix. Open the resulting
`guitar-boy-advance-expanded.gba` in mGBA and choose **Imported Easy Test**.
It displays LOCAL/AUDIO. The matching package cover plays, with the first chart
note at approximately6.322seconds on this test timeline (2s pre-roll +4.322s).
No Python/C++ editing or Git commands are required.

Read `imports/output/song-runtime/audio/audio_report.txt`, `adaptation_report.txt`
and the source report under `source/<package-name>/report.txt`. Missing/ambiguous
files, unavailable decoder, invalid content or mismatched audio/chart assets fail
clearly. Generated chart/audio are ignored by Git. Keep your real package,
prepared files and resulting third-party-content ROM private.

For the public synthetic build, omit both selections:

```bash
bash scripts/build-docker.sh
```

For native toolchains, use the same variables with `make -j2` and the established
DEVKITPRO/DEVKITARM exports. Source headers and audio selection are rechecked each
build; switching back to defaults removes an earlier private selection.
Open the new ROM only after both commands succeed; a failed build may leave the previous ROM on disk.
An explicitly supplied missing/bad AUDIO_DIR fails; it cannot silently substitute
music. `AUDIO_DIR=none`, or choosing a private chart header without AUDIO_DIR,
produces a visibly labeled **SILENT FALLBACK** using Mission005's frame clock.

## Pipeline and output

`package → validated normalized chart → Easy adaptation + explicit stems → host decode/downmix → signed8 PCM → validated ROM assets → FIFO playback + timer clock`

- `tools/prepare_song.py` performs package inspection, explicit Easy lead selection
  and audio preparation in one command. Use repeated --audio exact/package/file.wav
  instead of --stem to resolve multiple formats explicitly. It rejects preview, duplicate/ambiguous
  stem selections and audio ending before the final note onset.
- `tools/audio_prepare.py` owns bounded FFmpeg decoding, mixing, quantization,
  deterministic synthetic generation and the versioned `gba-audio-v1` manifest.
- `tools/prepare_audio.py --file file1 --file file2 --output-dir PATH` converts
  explicitly selected individual files. Pair its output with an explicitly
  prepared chart and verify the recording/offset. The package command also binds
  the PCM manifest to the generated chart-header SHA256.
- `tools/build_audio.py` validates hash, lengths, padding, rate, channel count,
  chart binding and final late-window coverage; it builds default synthetic assets
  without FFmpeg. Missing private assets fail before compiling.
- `source/pcmPlayback.cpp` owns imported FIFO/timers and exclusive handoff to the
  existing Maxmod original demo. `audioClock.hpp` defines the sample-index clock.
- `ImportedRuntime::updateTick` feeds that snapshot into the existing judgment and
  visibility engine. `NoteJudgment` and original NoteManager formulas are unchanged.

Prepared audio outputs:imported_audio.bin, audio.json and audio_report.txt.
The raw binary includes the declared pre-roll/tail/guard. It contains no file
header or runtime codec. Preserve the private manifest with the private assets.

## Format choice, quality and mixing

Selected: **16,384Hz, mono, signed8 PCM**, read directly from ROM. GBA Direct Sound
accepts8-bit samples; it does not decode OPUS, MP3 or ADPCM in hardware. A timer
period of1024CPUcycles divides the nominal16,777,216Hz clock exactly, avoiding
rate approximations. GBA DMA1 sends4word bursts to FIFO A, routed to both speakers.
No full-song RAM copy, decoder, per-sample CPU callback or software stream refill.

The installed **GBA Maxmod1.0.15** header exports module/effect functions and lacks
a GBA mmStreamOpen interface. Shared DS stream/ADPCM types do not establish GBA
support. Its module path remains the original demo's owner. ADPCM would require a
new tested software decoder/buffer path; it was not assumed available or added.
This small alternate PCM path is mutually exclusive with Maxmod, rather than a
replacement audio framework.

Host conversion rules:

1. Validate exactly one audio stream per selected file, and at most8selected
   stems. Decode OPUS pre-skip through FFmpeg. Keep decoded leading silence;
   do not trim or seek by guessed intro length.
2. Downmix each stem to mono and resample to16384Hz with swresample, one thread,
   no dither. WAV/OGG/OPUS/MP3 are supported inputs; codecs are actually decoded,
   not inferred just from extension. Protocol/demuxer allowlists prevent following
   network playlists or arbitrary package scripts.
3. Average the explicitly selected N stems; zero-pad shorter ends to the longest
   stem. Apply gain `0.85/max(1,mix_peak)`. This provides headroom and only reduces
   gain; it does not amplify a quiet mix. No reactive runtime volume changes.
4. Round to signed8 with symmetric nearest rounding, clamp to±127, report peak
   and quantization SNR against the resampled mono mix. Raw bytes are deterministic
   for identical sources/options/decoder version. Output count preserves decoded
   duration to within an output sample (61.035microseconds).
5. Prefix32768zero samples (2s), append8192zero samples (0.5s late-window tail),
   and add16384zero guard samples plus16-byte alignment. Guard is not song content.
   Limits:30minutes decoded source,128MiB per package audio read,30MiB audio-asset
   ceiling, and an enforced32MiB conventional cartridge size limit after linking.

Measured private mix:267.271912s,4,378,983source samples,4,436,336asset bytes,
output peak58/127, quantization SNR30.483dB. Each of the three OPUS stems decodes
from48kHz stereo. Probe container duration includes codec framing; decoded sample
count is authoritative. The source INI length267271ms is consistent with decoding.
No source trim or chart tempo stretching is used.

This is deliberately lo-fi:mono,8-bit quantization and an8.192kHz Nyquist limit.
The SNR metric excludes the stereo/downsampling losses and does not substitute
for listening. The synthetic track is newly generated integer triangle tones
from the project's original fixture; it contains no recorded third-party samples.

## Exact clock and latency contract

Timer0 both triggers FIFO sample output and advances cascaded Timer1+Timer2.
Those two16-bit counters form a32-bit count of sample timer overflows, read with
high/low/high retry. They continue independently of main-loop rendering. The
clock is **timer-derived output-request position**, not speaker feedback or a
software write/refill cursor. No VBlank-to-time approximation is labeled audio.
DMA availability and nominal output identity were verified using captured audio.

For consumed count N, the currently requested sample index is max(0,N−1).
Gameplay CPU-cycle ticks are `sample_index ×1024`. Header timestamps are still
`round((source_start_us +2,000,000) ×16777216/1,000,000)`. Thus source audio sample
zero follows exactly32768prefix samples and shares the chart's2s origin. A first
sample request adds one hardware sample period from timer enable; the index
convention accounts for that startup. There is no second pre-roll or BPM scaling.

Both judgment and sprite geometry use one immutable main-loop snapshot. Original
Demo keeps its VBlank×BPM clock. Imported audio mode never calls mmFrame/mmVBlank
while owning DMA/timers. It checks the timer, cascade, DMA and sound-enable state;
a disabled resource freezes the chart clock and displays AUDIO ERROR. EOF is a
known end state with a clamped clock, not an unexpected stop. The0.5s tail allows
final late judgments. VBlank services EOF, stopping DMA before the guard can be
exhausted during normal operation. The1s guard does not qualify a program that
masks interrupts/stalls all servicing for longer than1s.

Returning to the selector stops DMA/timers and resets FIFO routing. Replaying the
original uses public mmInit with retained buffers matching mmInitDefault's exact
mode3/16-channel configuration; repeated mmInitDefault would allocate again.
Initialization finishes before resetting/enabling its gameplay clock. There is no
in-game pause; emulator-wide pause stops the emulated hardware timeline too.

No arbitrary frontend latency value is baked into the chart. The one-sample
index convention above is the fixed startup accounting. Captured synthetic
waveform residual is about0.275ms; private reference windows0.37–0.49ms. These
include emulator PWM/resampler/capture behavior. Capture epoch variation is up
to0.244ms in the private run, so0.122ms spread cannot establish analog drift.
Host-device audio buffering/display/input latency remains a human calibration
question. No physical speaker-loopback measurement is claimed.

## Visual line synchronization

A new OAM check measured the actual rendered note-center crossing, rather than
only the judgment callback. Mission005's copied contact depth placed imported
notes about54ms late at the fret circles. Mission006 corrects only imported
contact geometry:relative z at the note time is−21000, and world x is
0xE380/0xFC00/0x11480. The floor remains the same three-lane Mode7 view; original
four-lane projection/math is untouched. Incoming speed retains the existing
fixed visual scale, independent of the imported song's tempo changes.

The test reads GBA OAM positions and affine IDs to identify the actual note at the
fret line (screen y116, centers x48/120/192). It checks all three lanes and first,
middle and final references. First sampled crossings remain within one video
frame, with expected perspective movement beyond the line. See results for
actual clock/sample/error values. No note is judged twice or discarded.

## Actual measurements

| Reference | Expected runtime | Displayed first crossing | Line error | Waveform/clock offset |
| --- | ---: | ---: | ---: | ---: |
| Synthetic first | 2.000000s | 2.003906s | 3.906ms | 0.275ms |
| Synthetic middle | 9.333333s | 9.337219s | 3.886ms | 0.275ms |
| Synthetic final | 13.333333s | 13.338684s | 5.351ms | 0.275ms |
| Private first | 6.322000s | 6.323425s | 1.425ms | 0.488ms |
| Private middle | 139.434000s | 139.444702s | 10.702ms | 0.427ms |
| Private final | 264.880000s | 264.881042s | 1.042ms | 0.397ms |

GBA frame period16.742706ms. Maximum all-note scheduled-hit error:synthetic
16.052246ms, private16.725123ms. Those are frame/input sampling limits, not
accumulating drift. Waveform correlations exceed0.999synthetic and0.989private;
no captured clipping. Beginning/middle/end waveform offset spread is0synthetic,
0.092ms private, within the capture method's timing variation. Complete tracks,
not only early excerpts, were played/captured; EOF output settled to silence.
No human-perceived sync is inferred from those tests.

Foreground work measured with Timer3:about26%of a frame on the synthetic run,
27%private; measured peaks below34%. This excludes idle VBlank waiting and ISR
work outside the measured interval; it is not a complete hardware CPU-utilization
profile. DMA bus cost is small but not separately hardware-profiled.

Public linked memory:25,344bytes IWRAM sections before stack/BIOS reservations,
2,528bytes EWRAM. Private:25,712bytes IWRAM, same EWRAM. Original Maxmod buffers
reserve3,584bytes within those totals. Imported PCM has no RAM sample buffer;
its counters/state are a few words. Public ROM537,696bytes; private4,720,736bytes.
Physical GBA performance/memory behavior still needs a hardware run.

## Ten-song feasibility

Audio payload only; add chart/code/art and per-song prefixes/tails. MiB=1048576.
Only the first configuration is implemented for imported recordings today.

| Configuration | MiB/min | 3min/song | 4min/song | 10songs,3–4min each | Cost/status |
| --- | ---: | ---: | ---: | ---: | --- |
| **16384Hz mono8PCM** | 0.938 | 2.813 | 3.750 | 28.125–37.500 | Implemented; DMA, no decoder/buffer; 10short songs might fit narrowly,10four-minute songs do not |
| 8192Hz mono8PCM | 0.469 | 1.406 | 1.875 | 14.063–18.750 | Hardware-feasible future variant; lower4.096kHz bandwidth; rate configuration/testing not implemented |
| 32768Hz mono8PCM | 1.875 | 5.625 | 7.500 | 56.250–75.000 | Future variant; more ROM/bus traffic, still8-bit; not implemented |
| 16384Hz two mono PCM stems | 1.875 | 5.625 | 7.500 | 56.250–75.000 | Future independent mixing doubles storage; software/hardware mixing policy needed |
| 16384Hz4-bit ADPCM estimate | 0.469 | 1.406 | 1.875 | 14.063–18.750 +headers | Software decoder and block RAM/CPU required; unsupported/unbenchmarked, not a promised solution |
| Existing Maxmod module | Content-dependent | Not a recording conversion | Not a recording conversion | Cannot infer | Existing demo works; module patterns/samples are a different content model |

Current per-song pre-roll/tail/guard adds about0.055MiB. Ten3minute songs would
therefore use about28.67MiB before code/charts/art; four-minute songs about38.05MiB.
Ten copies of this267.27s private mix would exceed42MiB of prepared audio alone.
A conventional GBA cartridge exposes32MiB of unique ROM data; emulator-only
oversized images are not a hardware strategy. The build rejects over32MiB.

Practical options:separate smaller ROM packs, a qualified lower-rate mode, or a
benchmarked compressed format with an acceptable sound-quality budget. No packs,
multisong menu or codec framework is implemented here. Independent guitar/backing
mixing is physically possible later but needs storage/clock/CPU validation.

## Human calibration

1. In mGBA enable sound, use normal speed, and choose a stable small audio buffer.
   Record emulator version, audio settings and controller/keyboard mapping.
2. Play the synthetic mode. Listen for each tone as its note reaches the fret
   circle. Record the screen and sound together if possible. A240fps camera has
   about4.2ms frame resolution; video-player recording latency must also be checked.
3. Measure early/middle/late events separately. A constant offset suggests display/
   audio buffering; a growing offset suggests a clock/recording problem. Do not
   replace the supplied cover with a studio recording or change chart BPM to
   mask a buffer delay. No in-game latency slider is added in this mission.
4. Repeat on physical hardware using speaker/microphone plus screen recording,
   documenting the flashcart and audio output. A photodiode/audio loopback test
   would be stronger. Physical hardware and human listening have not been tested.

See MISSION_006_RESULTS.md for exact test commands, artifacts and review state.

Measurement interpretation: line crossings use the game draw snapshot and OAM sprite positions; physical scanout and host presentation latency were not measured. Miss-run REFERENCE rows record the late judgment deadline, not a note-line crossing. The mixed legacy input script varies with launch phase; its 177 hits split into 59 Perfect/118 Good in this final run, without changing judgment windows.
