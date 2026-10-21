# Mission 019 audio gate

**AUDIO BLOCKED.** ROM `9ccc460693fa7254527177330f32e56153720237`, public RC2
SHA256 `9c4af95ff97eddd266dca3d7491ac9a5b1256f417684aae51b7c126443afafde`.
This was a bounded investigation of the existing six failures, not a new audio
implementation or a change in release criteria.

## Separate measured layers

| Layer | Fresh M019 evidence | Meaning / limit |
|---|---|---|
| Generated PCM and mixer words |15/15 full transports on stock0.10.1, zero mismatches; all9 segments in eight-pause case checked|Source samples and integer mixing match; does not establish speaker output |
| Transport clock |All segment complete-clock drift0; paused FIFO requests0|Pauses excluded explicitly; hook request timestamps fluctuate1022–1026 emulated cycles about1024 |
| Ordinary captured output |9/15 on stock0.10.1 and0.10.5; same6 fail|Original `<1ms`, correlation, clipping, gain and leakage criteria retained |
| Physical input identity |All6 cross-version traces identical,4728–4732 all-miss /4693–4697 mixed frames|Same ROM and observed input sequence, not assumed equivalence |
| Independent startup phase |Digital first-byte trace observes fixed15 source samples =0.91552734375ms|Constant startup observation, not per-window fitting |
| Separate fixed-phase model |14/15, Easy mixed remains below paired-backing correlation requirement|Diagnostic only; cannot clear ordinary gate |
| Hardware |Historical positive owner RC1 listening/playability only|No RC2 synchronized audio capture or quantitative phase proof |

New stock0.10.5 no-input backing references were also captured per difficulty;
using those matching-version references leaves all six failures unchanged.
Normal captures use the unmodified stock libraries, with no LD_PRELOAD, lateness
correction or emulator patch. Digital observation uses a host tap separately;
its correction environment option is disabled. Optional PWM log writing was
disabled for disk space; FIFO words and every consumed sample were still checked.

## Independent mechanisms reproduced

`tests/mgba_fifo_capacity.c` again reproduces both mechanisms on both stock
libraries. Directly priming28 bytes leaves seven words and delivers tagged
sample2. Priming32 wraps the eight-word cursor to the read cursor and is read as
empty (sample0). The ROM primes a real hardware32-byte FIFO; reducing its slack
solely to conceal an emulator representation issue is not justified.

With identical FIFO state, `cyclesLate=0` and600 produce the same output slots
`[5,9]`; a separate diagnostic600-cycle event-distance adjustment gives`[9,9]`.
This isolates an effect of missing event-time context on PWM placement. It does
not prove every captured difference or alter the emulator used for acceptance.

The ordinary model starts source index0 at a counter-derived epoch. The measured
15-sample advance accounts for a substantial phase component; some original
measurements still exceed1ms (1.007080–1.068115ms). The separate constant-phase
diagnostic leaves Easy mixed paired-backing correlation approximately0.998555,
below required`>0.999`, despite corrected timing residual0.244141ms. PWM slots,
resampling/filtering, pause/capture epochs and waveform-model assumptions remain
possible contributors. There is no measured accumulating digital song-clock drift.
Digital identity and lack of drift do not eliminate the output discrepancy.

No thresholds changed, no windows were independently realigned to force success,
and no new acceptance method was adopted. A proposed future specification would
need independent calibration of startup/filter delay, identical input replay,
separate sample/gain/event/phase checks and **explicit owner review**. The original
strict comparison would remain a diagnostic. No such approval is presumed.

## Smallest next experiment and accessible hardware plan

Engineering: focus on the retained Easy mixed window at source time23.644470s
and its true backing-only counterpart. Reconcile their PWM event times, counter
epochs and common-filter residual under a deterministic capture model; show why
the residual violates0.999 before proposing any criterion change. Repeat on
both stock versions, then rerun the unchanged complete ordinary gate. Do not
broaden this into a ROM audio rewrite or a new mission without authorization.

Owner: first do ordinary RC2 listening/play using [the checklist](OWNER_M019_PLAYTEST.md).
If you already own a computer with a real line-in input or suitable USB audio
input and a GBA headphone cable, optionally record uncompressed WAV at a fixed
44.1/48kHz rate with enhancement/automatic gain off. Keep the level below clipping.
Record one Easy song including deliberate misses/recovery and two pauses; record
device, flash cartridge, ROM hash, interface/rate and approximate button times.
Keep volume comfortable. No soldering, device modification or lab purchase is
required. If that input is unavailable, report listening observations instead.

An unsynchronized line-in recording can expose audible drift, stutter, pops,
muting/recovery and repeated-transition damage. It cannot establish absolute
sub-millisecond FIFO phase or distinguish GBA DAC/filter delay from capture
latency. Microphone video cannot establish that either. Sample-level hardware
claims would need a synchronized reference and calibrated acquisition by an
equipped tester; no such measurement has occurred in this cloud session. No
extra diagnostic ROM was warranted merely to obtain another file.

Inherited full-length Cream ordinary output10/15 remains historical, not newly
cleared by M019's private gameplay tests. It is not substituted for this public
matrix. See [verification](M019_VERIFICATION.json) and
[historical investigation](M018_AUDIO_INVESTIGATION.md).
