# Mission 007 — reactive guitar audio

A missed note or wrong button now removes the **selected guitar recording** from
Imported Easy Test. The rest of the selected band recording continues at the
same sample position. A Perfect or Good hit restores guitar. The original demo
keeps its existing music, judgment windows, graphics and four controls.

## Download and play on Windows 11

The public review ZIP contains an original synthetic two-track exercise and full
source. It does not contain the owner's Cream music, chart or reactive ROM.

1. Install mGBA from https://mgba.io/downloads.html and open it.
2. Download and extract [mission007-review.zip](https://github.com/jellynada/guitar-boy-advance-expanded/raw/refs/heads/mission-007-download/downloads/mission007-review.zip).
3. Choose File → Load ROM and open `guitar-boy-advance-mission-007.gba`.
4. At the selector use Up/Down, then A or Start, for Imported Easy Test.
5. Map GBA Left / A / B to convenient computer keys in mGBA settings.
6. Let the first note pass: after its late window closes, the bright lead should
   disappear and the bass/percussion should continue. The label says GUITAR MUTED.
7. Hit the next note correctly: the lead returns and the label says GUITAR ON.
8. Press an incorrect active button: it mutes again. Waiting does not restore it.
9. Start+Select returns to the selector. Starting again restores the initial mix.

The public lead is a continuous triangle voice, and backing is97Hz bass plus
original generated noise percussion. The unchanged25-note Easy fixture includes
tempo changes. A sustained test sound does not implement held-note gameplay.
Original Demo remains Left / Right / A / B and699notes; its music is not gated.

A private Cream build was made and tested in this workspace. This Codex session
has **no working private artifact export/attachment tool**. A sandbox file link
is not a functioning attachment here; do not describe the local path as a public
download. The private build and inputs stay outside public source/downloads. The existing
workspace file is `/workspace/.cloud-setup/gba/mission007-private-rom/guitar-boy-advance-expanded.gba`
(also copied as `/workspace/artifacts/Sunshine-of-Your-Love-Mission-007-Private.gba`).
If your workspace client supports file export, export that file and open it in
mGBA; this chat does not expose such an export action.
The following commands reproduce it locally without editing source.

## Privately prepare the Cream song on Windows 11

Use Ubuntu/WSL and Docker Desktop with WSL integration, as explained in
[GBA_CHART_ADAPTATION.md](GBA_CHART_ADAPTATION.md#windows-11-chart-only-silent-fallback-without-editing-code).
Install host conversion tools once in Ubuntu:

```bash
sudo apt update
sudo apt install python3 ffmpeg
```

Unzip the complete Mission007 review bundle, then enter its source folder. For
example (replace YOURNAME and the path with your own):

```bash
cd "/mnt/c/Users/YOURNAME/Downloads/mission007-review/guitar-boy-advance-expanded"
```

Put your already-owned ZIP into that source folder's `imports/incoming` directory.
With Docker Desktop running, execute these two commands in Ubuntu:

```bash
python3 tools/prepare_song.py "imports/incoming/Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip" --reactive --guitar-stem guitar --backing-stem rhythm --backing-stem song --output-dir imports/output/mission007
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/mission007/imported_chart.hpp" "AUDIO_DIR=imports/output/mission007/audio"
```

Open the resulting `guitar-boy-advance-expanded.gba` in mGBA and choose Imported
Easy Test. This is the private reactive build; the public synthetic ROM has a
different filename. After2s pre-roll the recording begins; its first chart note
is at runtime6.322s. Only open the output after both commands succeed, because a
failed build may leave an older ROM on disk. Keep the ZIP, prepared outputs and
this ROM private. No new Windows dependencies beyond Mission006 are required.

For an ordinary public synthetic build, run `bash scripts/build-docker.sh`
without selections. Source and audio selection are checked every build, so this
clears an earlier private selection. The build rejects cartridges over32MiB.
Native `make -j2` uses the same variables and existing DEVKITPRO/DEVKITARM setup.
Host decoding used FFmpeg7.1.5, Python3.12.14; build tools are pinned as before.
Other FFmpeg versions record their version but need not produce identical bytes.

## Preparation and roles

`prepare_song.py --reactive` requires one explicit --guitar-stem and one or more
distinct --backing-stem selections. Duplicate roles/files, preview, ambiguous
files or missing roles fail clearly. Old --stem/--audio commands remain usable
for Mission006 fixed-mix preparation, but do not provide selective guitar muting.

For this package, guitar.opus is the candidate controllable recording;
rhythm.opus and song.opus are combined into backing. Preview is excluded. Each
file decodes to4,378,983mono samples at16384Hz (267.271912s). The original48kHz
stereo OPUS files have matching lengths and codec pre-skip. FFmpeg handles that
pre-skip; no leading silence is trimmed and neither stream is shifted by hand.
Shorter stems are zero-padded to the longest end. Source audio must cover the
last note. Both streams receive the same32768sample pre-roll,8192sample tail,
and16384sample safety guard/alignment. Chart/header hashes bind the selection.

The recordings are demonstrably different, not duplicated copies of a full mix:
guitar/rhythm waveform correlation−0.00858, guitar/song0.00157. Rhythm has about
91.8% of measured spectral energy below200Hz, consistent with a bass candidate;
guitar has a broader spectrum, and song has another distinct broad spectrum.
Each has substantial independent nonzero material and different silence patterns.
**These checks do not prove instrument identity or absence of guitar bleed.**
No human audition or automated source-separation claim is made. The owner must
listen to backing alone and confirm that it is suitable. The implementation
reliably silences the chosen recording; it cannot remove guitar that is already
present in the backing. If backing contains unacceptable guitar bleed, use the
tested fixed-mix path for that package until properly isolated stems are obtained;
do not call full-mix attenuation a guitar-only solution.

Host gain staging retains Mission006's N-source averaging. With three files:

`guitar = guitar_source/3`

`backing = (rhythm_source + song_source)/3`

Both then use shared gain `0.85/max(1, max(abs(guitar)+abs(backing)))`, followed by
independent nearest signed8 quantization. This bounds the sum even during a mute
that removes cancellation between tracks. The real mix uses gain0.85; its maximum
quantized absolute sum is58/127. No hidden runtime master attenuation is added.
Build validation checks format, rate, sample counts, padding, both hashes, chart
binding, aggregate30MiB audio budget and sample-by-sample safe mix headroom.
Corrupt explicitly supplied audio fails rather than silently selecting other music.

`gba-reactive-audio-v1` stores `imported_audio.bin` (guitar),
`imported_backing.bin` and audio.json. Both blobs have identical length and origin.
The original `gba-audio-v1` fixed mix is still supported without a reactive label.
A private chart without prepared audio retains the labeled SILENT FALLBACK.

## Judgment and fade rules

The original NoteJudgment engine is unchanged. Its synchronous events drive a
small gate; no lossy event queue or new timing window is introduced.

| Event | Guitar target |
| --- | --- |
| Start/replay | Normal volume |
| PerfectHit / GoodHit | Normal volume |
| Miss / WrongInput | Exactly zero |
| Repeated event for the current target | Keep that target |
| No event / passage of time | Keep that target |

The engine emits expired misses first, successful hits in lane order second,
and WrongInput last. The **last delivered event wins**, including events sharing
the same gameplayTick. Thus a miss followed by a hit in one update restores the
guitar; a hit plus an extra wrong button ends muted. The hit still counts.
Original Demo events never enter the imported gate.

Gain is an integer0…256. Each newly mixed sample changes it by4 toward the target.
A full transition lasts64samples=3.90625ms, ending at **exact zero** or full gain.
Reversing direction uses the current gain, rather than jumping amplitude. The
mix is `backing + guitar*gain/256`, with signed division toward zero. Input gain
bounds prevent output overflow/clipping. No timeout restores guitar.

Judgments remain frame-polled. A miss occurs only after the existing85ms late
window, plus up to approximately one frame of polling. A wrong input is observed
at the next poll. Events retain their engine gameplayTick in the diagnostic trace;
actual effect begins at the next unqueued sample, also recorded in that trace.
Already queued sound cannot be changed retroactively. Queue lead is at most32
samples(1.953ms) at the callback. From the earlier judgment snapshot, measured
first-effect positions were26–45samples later (1.59–2.75ms), including foreground
event work. The3.906ms fade follows; worst measured snapshot-to-full-transition
was under6.66ms, excluding frame polling and physical output latency. Debug text
shows the target state; the short transition can still be completing when the
label first changes. It does not imply that old FIFO samples vanish instantly.

## GBA playback architecture and safety

Both streams are ROM PCM at the existing16384Hz. A small fixed-point mixer feeds
**one** Direct Sound FIFO A, routed equally left/right. It appends16samples at a
time through four32bit CPU writes; there is no decoded whole-song RAM buffer,
heap allocation in playback, ring-buffer wrap, independent guitar cursor or DMA
read cursor. One `fillPosition` indexes both sources. Muting changes only gain;
neither source restarts, skips or advances independently.

Timer0 retains its exact1024CPUcycle sample period. Timer1 cascades and reloads
every16requests, issuing1024refill interrupts/second. Timer2 counts those blocks;
a software epoch extends its20bit sample count, including tracks beyond64s.
The clock remains timer-derived output-request index `max(0,count-1)*1024`, not a
software fill position. Both judgment and existing imported projection use it.
Timers0–2 and FIFO A belong exclusively to imported playback. DMA1/2 are stopped;
FIFO B/PSG are not used for imported audio. Timer3 profiles work at64CPUcycle
resolution. On return, imported interrupts/timers/FIFO stop before the existing
Maxmod Timer0/DMA1/DMA2 path is initialized with retained buffers.

Alternatives considered: two unmodified hardware FIFO streams cannot implement
a smooth64sample guitar fade because hardware gain only has coarse settings.
A larger DMA ring needs more cursor/prefetch/wrap management. The measured small
interrupt-fed mixer is simpler here; it is not free, and is unsuitable for adding
unbounded codec/mixing work without a new deadline analysis.

FIFO starts with32samples. Every16requests the next16are appended. A skipped
refill block increments the underrun counter and freezes playback as AUDIO ERROR;
disabled clock/refill IRQ/sound resources are also detected. The fault path freezes
judgment/scrolling rather than continuing silently. Deliberately blocking IRQs
for a frame exercises this detection. No physical FIFO-loopback status exists;
measured emulator deadlines and waveform checks support, but do not prove,
behavior on physical hardware. Long arbitrary interrupt blocking is unsupported.
At EOF the clock clamps, queued silence tail covers block rounding, and playback
stops. The foreground draw snapshot can reflect EOF one frame after the ISR;
subsequent snapshots remain fixed. Restart resets both positions and gain.

## Measurements and reproducible checks

See [MISSION_007_RESULTS.md](MISSION_007_RESULTS.md) for final hashes, ROM/RAM
sizes, CPU figures, reference timings, test counts and exact captured scenarios.

```bash
bash tests/check.sh
bash tests/run_audio_emulator.sh reactive 1800 /tmp/reactive
python3 tests/analyze_reactive.py --audio-dir build --prefix /tmp/reactive --require-mute --require-recovery
```

The emulator checks require the documented mGBA development installation; waveform
analysis additionally needs NumPy. They are developer checks, not prerequisites
for the owner's two-command build. The analyzer independently reconstructs sample
fades from actual event delivery positions and compares the captured waveform
in normal, backing-only, fade-down and recovery regions. It also fits separate
guitar/backing coefficients to detect residual guitar; merely nonzero samples
are not accepted as proof of correct backing. Known-bad full-mix substitution
is checked to fail the analyzer. Global capture-epoch residuals are reported
alongside local hardware/capture timestamp mapping, without guessed in-game
latency correction. PWM, resampling and capture uncertainty remain limitations.

Two streams cost twice the audio storage:1.875MiB/minute,7.5MiB for4minutes,
before guard/timing/code/art. Ten4minute songs require75MiB of PCM alone; they
cannot fit a conventional32MiB cartridge. No rate reduction, shortened song,
compression implementation, full menus, scoring or new sustain gameplay added.

Next priorities: owner listening to confirm stem isolation, missed-note feel,
physical-device deadline/synchronization testing and then measured compression
feasibility before adding more songs or reactive layers.
