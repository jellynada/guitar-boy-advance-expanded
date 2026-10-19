# Mission 007 results and review handoff

Base:verified Mission006 `4fa9e6f8b2558a129075c9815c8bb2ac68e6421b`, containing
the full earlier mission chain. Source branch:mission-007-reactive-guitar-audio.
Main is not merged. Private inputs, audio, charts, full traces and reactive ROM
are excluded from source commits and public downloads.

## Implemented behavior

Miss and WrongInput gate only the selected guitar track to exactly zero through
a64sample(3.90625ms) fade. PerfectHit/GoodHit restore it. No timeout, health,
scoring, holds or new controls. Both ROM streams share an unchanged16384Hz clock
and one sample cursor. The original demo is not gated. The public25-note fixture
has independently distinguishable original lead and bass/percussion recordings.

Existing NoteJudgment and original NoteManager source are unchanged. Imported
contact coordinates, floor speed, perspective and judgment windows remain those
validated in Mission006. The synchronous engine's event order is retained:
misses, hits, WrongInput, with the last event deciding the gate. A diagnostic ring
retains serial, first unqueued source sample, current gain and gameplayTick; it is
observability only, not playback scheduling or a lossy event delivery queue.

## Actual builds and storage

Both public and private native builds succeeded. The public ROM was also built
with the pinned devkitARM Docker image. Final ROM sizes/hashes and measurements
are recorded below. Windows installation itself was not
performed; the included source bundle was rebuilt using the documented script.

Toolchain:devkitARM r68/GCC16.1.0, Tonc1.4.5, MaxmodGBA1.0.15, Python3.12.14,
FFmpeg7.1.5, mGBA0.10.1. Native hostg++14.2; pinned container hostg++12.2.
No new build/conversion dependencies; NumPy is optional developer analysis only.

Docker image:
`devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5`.

Private audio retains the entire4,378,983samples (267.271912s), not a shortened
excerpt. Each padded stream occupies4,436,336bytes; both total8,872,672bytes,
exactly twice Mission006's audio payload. Public audio occupies518,848bytes.
All prepared streams have matching prefix/tail/guard/sample counts and hashes.
The cartridge post-build guard rejects files larger than32MiB.

## Stem inspection and quality

All three candidate recordings are48kHz stereo OPUS, decoded with unchanged
codec pre-skip. Direct waveform correlation guitar/rhythm=−0.00858 and
guitar/song=0.00157. Rhythm's measured energy is91.8%below200Hz; guitar is broader.
This establishes distinct aligned signals consistent with assigned candidate
roles, **not** absence of guitar bleed or proof of musical content. No human
listening was performed. The next owner test must confirm backing-only content.
If guitar bleed is unacceptable, use the tested fixed-mix fallback until suitable
stems are supplied. No artificial source isolation is claimed.

Mixing uses N-source averaging and shared0.85gain with absolute-sum peak checks.
Private quantized maximum absolute guitar+backing sum:58/127, no overflow/clipping.
Quantization-only SNR against resampled/gain-staged mono floats:guitar26.925dB,
backing28.013dB. This excludes losses from mono conversion and8.192kHz bandwidth;
it is not a subjective-quality rating. Existing Mission006 owner listening
approval does not establish approval of the new separated/gated mix.

## Host tests

`bash tests/check.sh`:92Python tests (32chart,34MIDI/package,9adaptation,12audio,
5reactive), plus sanitizer-backed C++ judgment, full699-note chart, imported
runtime, sample-clock and gate checks. No compiler-dependent checks skipped.
Gate tests cover Perfect/Good, misses, wrong input, recovery, repeated events,
no timeout, exact zero, fade completion/reversal, reset and real-engine
same-update miss+hit / hit+WrongInput priority. Preparation tests include
mismatched source lengths, deterministic roles, duplicate/missing selections,
preview rejection, stale-output cleanup, corrupt backing and unsafe mix rejection.

## Complete emulator scenarios

Public synthetic runs cover1800frames, including the entire12.333374s source
plus2s pre-roll,0.5s tail, EOF and four original/imported replay cycles.
Private runs cover18000frames, including the entire267.271912s source and EOF,
then four original/imported cycles with original music audible and counters,
clock and guitar gain reset. Full-song scenarios:

| Input | Public | Private Cream |
| --- | --- | --- |
| All notes hit | 25Perfect | 395Perfect |
| No input | 25Miss | 395Miss |
| Hit/miss/hit pattern | 17Perfect,8Miss | 263Perfect,132Miss |
| Wrong presses plus successful hits | 25Perfect,59Wrong | 375Perfect,20Good,625Wrong |

Every note is counted once. No normal-run underruns or core crashes detected.
Separate fault tests disable Timer0, refill timer, sound, refill IRQ or block all
IRQs for a frame. Playback/judgment freeze and report AUDIO ERROR. Injected missed
refills increment the underrun counter; ordinary runs keep it at zero.
`fault_dma` is a historical harness name now disabling Timer1, because imported
playback no longer uses DMA. The stopped original Maxmod DMA path is retained.

Original demo runs36000frames each:all-hit699Perfect; no-input699Miss; mixed
59Perfect,118Good,522Miss,1200Wrong, with original sound and visible hit feedback.
Mixed-script timing can vary with launch phase; its177hits and windows remain.
The separately tested1800frame silent fallback has no imported audio. A1000frame
legacy fixed-mix check retains continuous full-mix sound despite18misses, emits
no gate events, and passes four mode/replay cycles; its full song was not rerun. Replay after EOF restores full guitar and resets
both stream positions; neither track is restarted for a miss or recovery.

## Captured sound evidence

Tests capture actual mono32768Hz signed16 output, asserting equal left/right.
The analyzer independently models integer gain/sample mixes from the real event
trace, then checks normal, muted, fade-down and recovery waveform windows. In a
mute, the model equals the backing PCM exactly; its guitar contribution is zero.
Captured audio is compared to that expected backing, not merely checked nonzero.
Separate guitar/backing least-squares coefficients rule out a quiet full-mix
substitute within the stated measurement tolerance. A known-bad all-on capture
substituted into a no-input run fails waveform matching (correlation about0.713).

The public hit/miss script has8recoveries; private has131recoveries. Detailed
public audio/check results are bundled. Only aggregate private results and the
requested first/middle/final references are published; full private traces,
waveforms, prepared PCM and chart records remain local.

Capture positioning uses nearby independently observed hardware-counter/output
sample pairs. A fixed global epoch is also reported, including its variation;
local mapping must not be mistaken for fitting a delay to the waveform. PWM,
resampling and frontend capture scheduling introduce sub-millisecond residuals.
GBA timers still share exactly one16384Hz timebase; no drift correction, per-track
clock, note offset adjustment or guessed speaker latency is applied.

OAM note crossings are sampled against the actual projected fret line for all
three lanes plus first/middle/final notes. They remain within one16.742706ms
frame. They measure draw snapshots, not physical scanout or host presentation.
Miss-log REFERENCE rows are late judgment deadlines, not line-crossing errors.

## Performance and memory interpretation

Timer3 samples elapsed work at64CPUcycle resolution. Foreground work excludes
idle VBlank waiting but includes interrupts that occur inside its interval.
Refill measurements cover callback work, excluding dispatcher/entry/exit overhead.
These overlapping measurements must **not** be added as independent CPU costs.
At1024callbacks/sec, callback-body mean cycles/16384 expresses its share of the
CPU budget, before dispatch overhead. IRQ deadline is16384CPUcycles per16samples.
Measured worst callback remains far below that deadline, but this is emulator
validation rather than a physical-hardware guarantee. HBlank/VBlank costs and
bus contention were not separately profiled on hardware.

Linked RAM totals exclude stack/BIOS reservations. Original retained Maxmod
buffers are included. New state/mixer code and384byte diagnostic ring add small
fixed RAM overhead; PCM stays in ROM, with only the hardware32byte FIFO queue.
The mixer allocates no heap or large audio buffer in either thread or interrupt.

Two-stream PCM costs1.875MiB/minute;10four-minute tracks require75MiB before
prefix/guard/code/art, so they cannot fit32MiB. Compression or separate packs
need later measured design work. No source is shortened or downsampled here.

## Review and delivery limits

Public source and review download branches are separate; neither merges to main.
The public bundle contains complete tracked source and a synthetic reactive ROM,
not the Cream package or reactive recording/ROM. A private artifact tool is not
available in this session. See REACTIVE_GUITAR_AUDIO.md for precise local retrieval
and Windows reproduction; no nonworking sandbox link is advertised as delivery.
Draft PR status and the final compare link are recorded after the actual attempt.

No manual listening, physical GBA test, subjective-quality or complete
instrument-isolation claim. Recommended Mission008:owner listening/feel and
stem suitability, physical-device deadline tests, then compression feasibility.

## Final measured artifacts and timing

| Build | ROM bytes | IWRAM sections | EWRAM sections |
| --- | ---: | ---: | ---: |
| Public original synthetic | 798276 | 25896 | 2912 |
| Private Cream reactive | 9158220 | 26264 | 2912 |

IWRAM is552bytes above the corresponding Mission006 build, and EWRAM384bytes
above it (the diagnostic ring). Stack high-water and physical hardware were not
measured. Private audio size alone is8872672bytes, versus4436336in Mission006.

Public SHA256:

```
fbb8b8d770d7b431d2402e0009d41bf59b50511d72035ca75e2d04b3dcbbcb72
```

Private SHA256 (file remains local):

```
8aef8d43e1a0a33a026698b6a4d5ce37169bb302d65af328fcd9fe790b28ed60
```

The private ROM is `/workspace/.cloud-setup/gba/mission007-private-rom/guitar-boy-advance-expanded.gba`,
also copied to `/workspace/artifacts/Sunshine-of-Your-Love-Mission-007-Private.gba`.
These are workspace paths, not working download links. Both linked aligned PCM
blobs were compared byte-for-byte to prepared files in each ROM. Repeating the
complete private conversion also produced identical guitar/backing bytes.

All-hit timing references (2s pre-roll included):

| Reference | Expected runtime | Actual note-line snapshot | Absolute line error | Waveform/local-clock residual |
| --- | ---: | ---: | ---: | ---: |
| Public first | 2.000000s | 2.003662s | 3.662ms | −0.671ms |
| Public middle | 9.333333s | 9.337036s | 3.703ms | −0.671ms |
| Public final | 13.333333s | 13.338501s | 5.168ms | −0.732ms |
| Private first | 6.322000s | 6.323303s | 1.303ms | −0.610ms |
| Private middle | 139.434000s | 139.444641s | 10.641ms | −0.610ms |
| Private final | 264.880000s | 264.881104s | 1.104ms | −0.702ms |

Using a single fixed capture epoch instead, private waveform offsets were
−0.488/−0.671/−0.824ms. Capture-clock epoch varies across the long emulator run;
local hardware timestamp translation is reported explicitly, without altering
game timing or inferring speaker latency. All checked local residuals are below
1ms. No accumulating independent stem-position error exists: both sources are
read at the identical index for every mixed sample.

First unqueued effect positions were26–45samples after the judgment snapshot
(1.59–2.75ms), including callback delivery work, then a64sample fade. Worst
measured snapshot-to-complete transition is under6.66ms, additional to frame
polling/the unchanged miss window. This does not measure physical output latency.

Captured waveform minima across checked windows:public0.99398, private0.97969.
Public backing-only guitar/backing fitted gain magnitude stayed below0.13%;
private no-input and hit/miss patterns stayed below3% with the unfiltered model.
Some short wrong-input windows produced a negative3.6% apparent guitar coefficient
from filtering/model bias. An independent hardware-filtered no-input capture was
therefore used for that scenario:all backing-only correlations≥0.99982, backing
scale0.99985…1.00051, residual fitted guitar≤0.043%. The raw waveform/model checks
remain in force. This is evidence within measurement tolerance, not a claim of
analog zero noise; source arithmetic reaches exactly zero guitar contribution.
No clipped samples, no normal-run underruns; post-EOF final second is silent.

Measured CPU work (callback mean share excludes dispatch; foreground includes overlapping IRQ work):

| Build/scenario | Foreground mean cycles (%frame) | Foreground max cycles | Refill mean cycles | Refill max cycles |
| --- | ---: | ---: | ---: | ---: |
| public/perfect | 79881.8 (28.44%) | 109248 | 1342.4 | 1344 |
| public/miss | 80598.6 (28.69%) | 107776 | 1346.9 | 1408 |
| public/reactive | 79965.3 (28.47%) | 109248 | 1343.7 | 1472 |
| public/wrong | 81324.4 (28.95%) | 113728 | 1346.7 | 1472 |
| private/perfect | 87030.1 (30.98%) | 107136 | 1342.4 | 1344 |
| private/miss | 87789.4 (31.25%) | 110080 | 1399.7 | 1472 |
| private/reactive | 87332.9 (31.09%) | 113024 | 1360.3 | 1472 |
| private/wrong | 88558.7 (31.53%) | 117632 | 1383.9 | 1472 |

Worst measured callback1472cycles vs16384cycle interval; body averages about8.2–8.6%of CPU while playing, plus unmeasured dispatch overhead. Foreground maxima reach41.9%of a frame. These are bounded emulator measurements, not additive or complete hardware utilization.
