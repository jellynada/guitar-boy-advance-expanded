# Mission 011 — audio/graphics timing stabilization

## Verified starting point and diagnostic phase

Remote `mission-010-stabilization` was fetched and verified at
`233112a072e5a0e90e5a766207761474130f75a6`; main remained
`6c4e63460fab10733d8ff011045ee246e7201952`. Hotfix71f0152,
sustains85c637d, diagnostics1d92104, framebuffer53a6134 and build guard3b0ce46
are verified ancestors. New source branch: mission-011-audio-graphics-stability.
No download branch, merge, force push, main change or new gameplay feature.

Pre-change host suite:98Python tests and8C++ sanitizer programs pass. A fresh
full395-note mixed reactive run reproduces exactly the M010 failure at232.665039s:
correlation0.9099746798974478, threshold>0.94, residual-0.67138671875ms.
Seven primary waveform models and gameplay results previously passed; one stricter
optional common-backing comparison also failed at46.137634s. No thresholds have
been changed during the diagnostic phase.

Rollback ROMs, built with ARM GCC16.1.0 /pinned official Docker image:

- M010synthetic814980bytes, SHA256
  `48ff797804e86e59f70b4e733d5af651616a75b3d9dbe6bc1bb0026c1e6790ac`.
- M010Cream9178392bytes, SHA256
  `c48ca749df60522402cc77204e5100c1f3c7121244c97f2df8539892f62b8c5d`.
- Real max foreground170560cycles/frame; typical run means99995.5–104720.5.
  Public max233728. Reactive refill maximum1472; zero ordinary underruns.
  Linked IWRAM27076real/26660synthetic; EWRAM3464/3096 plus padding.
  Tail strips11real/31synthetic in full regressions. Physical hardware untested.

## Observation without changing emulated execution

`tests/hardware_tap.c` interposes the installed mGBA0.10.1 host functions. It
observes actual FIFO words, consumed signed8 samples, pre-resampler PWM samples,
scanline-register writes and their emulated timestamps. No GBA instructions or
CPU-cycle delays are added. The full tapped M010 reactive capture is byte-identical
to the untapped fresh capture; this is an explicit observer-effect check. It uses
mGBA private headers and is version-specific; it is not linked into the ROM.
Earlier M010 in-ROM instrumentation had nonzero observer overhead; it is not used
as the quantitative controlled comparison here.

In the fresh baseline,1,104,984observed four-byte FIFO writes match an independent
source+event/gain model exactly. All4,419,952observed consumed samples match the
model after a fixed15sample advance, with zero sample mismatches. This distinguishes
digital PCM correctness from PWM/resampler output; it does not yet declare the
waveform regression solved. Startup priming and emulator FIFO details are being
investigated separately; no arbitrary audio offset is added to the game.

## Controlled graphics experiment design

`tests/run_timing_matrix.py` exports a pinned source revision, uses one compiler
and checks each build before saving its matching ROM/ELF. Artificial combinations
are developer-only. It generates original tones/zeros with the real267.271912s
sample count, identical pre-roll/tail/guard and two equally-sized PCM streams;
manifest hashes bind the selected chart. None is a playable replacement song.

Cases: original Maxmod demo; short synthetic chart/audio; same chart silent;
real chart/real audio; real chart/long synthetic tones; synthetic chart/long tones;
synthetic chart/long zero streams; real chart/audio with only tail drawing omitted.
The tail experiment preserves judgments and hold logic.1800frames per case include
four60-frame consecutive native sequences. Normal gameplay runs retain tails.

The host framebuffer oracle projects the real affine texture/map/palette and
counts actual highway-colored pixels outside their expected floor locations.
It includes existing15/16floor blending (Tonc clamp's upper bound is exclusive),
requires actual highway pixels, and is not a black-mask/screenshot similarity test.
It can also expose foreground table/scanout races; the silent baseline has five
flagged frames without late IRQ writes. That uncertainty is retained rather than
calling every pixel difference an IRQ artifact. Original Demo's different texture
is assessed by actual sequences and register-write timing, not this imported oracle.

Provisional controlled observations: real/tones/zeros all reproduce displaced
floor lines; omitting tails does not remove them. Thus Cream's recording content
is not required. Short synthetic also has measurable defects despite appearing
clean to the owner, while Original's normal music has no recurrent software FIFO
refill IRQ and no late affine writes in this comparison. Long test streams keep
exercising the fault after the short public song has already ended. These results
explain opportunity/architecture differences; they do not prove the owner's exact
photograph or perceived severity has been reproduced on Windows.

## IRQ and resource audit before selecting a repair

The linked Tonc `isr_master` acknowledges all simultaneously pending flags, selects
one callback by table priority, masks interrupts and leaves IME off during that
callback. Timer1 was inserted at priority0; HBlank is later. Simultaneous requests
can therefore lose a graphics callback, and running FIFO work can delay another.
The1344–1472cycle refill exceeds a1232cycle scanline and far exceeds272cycle HBlank.
A missed perspective reference write also leaves the old PB/PD increment behavior
active, producing displaced rather than simply dimmer floor pixels. Foreground
rewrites of the table during scanout are an additional smaller race to eliminate.

Imported audio owns Timers0–2 and FIFO A, and stops DMA1/2; original Maxmod uses
DMA1/2. No application code owns DMA0/3. Tonc sprite/memory copies and BIOS LZ77
are CPU operations here. Candidate: imported-only, double-buffered affine/fog
scanline tables using DMA0/3, rearmed in VBlank and stopped before scene changes.
Original renderer/Maxmod remain on their established path. This avoids introducing
nested IRQ stack/reentrancy changes throughout the game. Shortening the mixer
alone cannot prove every HBlank deadline, particularly with simultaneous flag loss.
Implementation and final measured results will follow only after validation.
