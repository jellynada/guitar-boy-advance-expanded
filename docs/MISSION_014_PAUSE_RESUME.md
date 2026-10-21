# Mission 014 — provisional pause/resume

## Authorization and source

The owner explicitly authorized provisional Mission014 work on Mission013 and
chose to keep the Cream ROM local until a private delivery route is available.
Mission013 handheld acceptance is **unconfirmed**. This is not a stable release
or owner acceptance. Starting source: mission-013-physical-controls,
`664c83ea624c4cec1c81d4c83f066e8abf0d2d87`. Develop remains Mission012 at
`56f6b7b243dfc710996336b99ac249806e666c85`; main remains
`6c4e63460fab10733d8ff011045ee246e7201952`.
Source branch: `mission-014-pause-resume`. No merge is authorized.
Final build manifests and the download receipt identify delivered source/hash.

## Controls and state machine

Imported Easy retains logical0/1/2 = **LEFT/B/A**. START pauses Playing; a new
START press resumes Paused. SELECT exits Paused to the existing selector.
Simultaneous START+SELECT exits before any pause/resume/replay action. Opposite
fresh system-button presses within six UI polls (about100ms), in either order,
also exit, including when the first button was released. START acts immediately;
a later SELECT still exits. SELECT alone during Playing starts this short chord
window but otherwise does nothing. Holding START never repeats. After an exit,
start controls must be released before the selector accepts a fresh start.

PlayTransport's fixed-size Controller has Selector/Playing/Paused/Results/Exiting
phases. The historical gameMode scene IDs and imported completion/error codes
are retained. Only imported Playing polls pause commands; results keep A/START
replay and B/SELECT return. Original699-note Demo keeps LEFT/RIGHT/A/B and its
existing START+SELECT exit; START alone does not pause Original or diagnostics.
No menu/front-end, difficulties, songs, compression or scoring system is added.

## Frozen transport and rendering

Audio remains the existing synchronized signed8 guitar/backing mixer on FIFO A.
Pausing disables Timer0, which consumes the shared mix at16384Hz. It preserves
the FIFO, Timer1/2 cascade counters, software count extension, fill cursor, both
stem indices, gate/gain/ramp and event history. One already-pending normal refill
is serviced before acknowledging its IRQ. Tonc's irq_disable clears Timer1's IRQ
bit; resume validates its paused cascade configuration before restoring IRQ.
Sound routing is disconnected without resetting the FIFO. Resume restores
routing/IRQ and Timer0 without re-priming, seeking or resetting the mixer.

Timer0 restart begins one full1024-cycle period. Its interrupted fractional DAC
interval is not preserved: the boundary adds less than61.04microseconds of
interval phase. Integer sample/chart position remains identical. This is an
explicit transport boundary, not a fitted per-window offset, skipped source
sample, repeated source sample or new chart delay. An abrupt cut/unmute can
produce a small boundary transient; this is not a click-free hardware claim.

A successful pause takes one last ordinary gameplay/render poll at the frozen
sample tick, then publishes Paused after VBlank and panel drawing. While Paused,
chart time, judgment, misses, holds, score/combo, completion, camera, feedback and
random camera effects do not update. VBlank still re-arms the existing double-
buffered DMA0 affine and DMA3 blend tables every frame: stopping that re-arm
would let scanline DMA run beyond its table. No new DMA/IRQ/timer is introduced.

The opaque160x40 pause panel saves/restores exactly100 BG0 cells (200EWRAM bytes).
It uses reserved font tiles prepared at boot, no additional OAM. It is drawn
once and removed once in VBlank; paused frames do not redraw the highway/HUD.
Boot preparation avoids extending scene initialization enough to miss the
existing rapid exit/restart input sequence.

## Resume input and sustains

At resume, the current physical frets seed judgment's previous logical held
mask. Buttons held before pause or pressed during pause cannot synthesize hits
or wrong inputs merely from resuming. Releasing and pressing again works.
Active holds are independently seeded from that same snapshot, with no elapsed
time/bonus update. Held frets continue. A missing fret starts the existing50ms
musical-time grace; it earns nothing while absent, then releases normally if
not restored. A fret released/re-held entirely during pause can continue its
existing hold when down at resume. Pause duration does not extend musical grace.
No head judgments, multiplier, combo, hold totals or points are rewritten.

The inherited hold rule starts bonus accumulation at max(chart onset, actual hit
tick). Thus all-Perfect head judgments need not produce one universal hold bonus:
sub-frame hit timing can cross a250ms bonus boundary. The established regression
reference remains15815 (585hold bonus); a separate actual-key pause driver can
produce different bonuses with its different hit phases. Tests freeze and compare
score during pause, and independently check unchanged scoring/hold rules; do not
mistake a different input trace for an identical scoring reference.

## Verification and limits

See evidence/mission014 for actual host, behavior, pause, graphics, audio and
resource reports. The pause driver exercises short/count-in/window/active-B/
active-A/muted/B/A/BA/released/new-fret/ten-minute/held-START/eight-cycle/
simultaneous/both sequential orders/paused-chord/paused-SELECT/final-note cases,
plus an uninterrupted reference. Inputs are actual emulated hardware keys;
gameplay state is observed, not overwritten. Paused checks compare clock,
score/statistics, gate/gain/events, mixer/refill state and composed framebuffer.

The independent digital oracle checks every consumed sample and mixed FIFO word
against the prepared two-stem data and gameplay-event gate model. It allows
only observed Timer0 stop/start gaps; existing uninterrupted audio thresholds
and graphics tests are unchanged. No experimental emulator lateness correction
is used for acceptance. PWM/resampling behavior is a separate measurement from
FIFO byte continuity. Physical sound output, Windows GUI and handheld behavior
remain owner tests. Emulator stack canaries are observations, not an exhaustive
stack proof or physical-hardware timing certification.

## Delivery and integration

The public synthetic review ZIP contains the synthetic ROM, complete clean
source, launcher, documentation and build identity. It contains no Cream ZIP,
PCM or Cream ROM. The local Cream AES archive is not uploaded: encryption alone
is not permission to host third-party recordings publicly. No supported private
upload/attachment route is available in this session. A local path is not a
working download link. The owner explicitly chose local retention.

The Windows launcher is preserved, with M014 output filenames. Its actual clean
Python/FFmpeg/pinned-Docker build chain is exercised here; double-clicking it on
Windows11 is unperformed. Do not tell the owner to install WSL/Docker to get a
ROM they only want to play. Private delivery remains a separate blocker.

Before integration: owner accepts Mission013 controls, obtains the Cream ROM
through an authorized private route, and completes OWNER_M014_PLAYTEST.md.
Then explicitly approve a reviewed Mission013 integration followed by Mission014
(or another reviewed dependency-preserving sequence). Never merge the download
branch or automatically advance develop/main. Mission015 is not started.

## Recorded results (engine ce70e4a)

- **127 Python tests and10 ASan/UBSan C++ programs pass.**
- All37 existing gameplay/input regressions pass:17 synthetic scenarios (including
  six deliberate fault checks),10 full16400-frame Cream runs,10 diagnostic runs.
- Original Demo: all699 Perfect, all699 missed and mixed36000-frame runs pass.
  Physical receptor/label checks pass on both profiles; no chart/audio asset hash
  differs from Mission013. Cream reference:15815score,395Perfect,78complete,
  585hold bonus; early-release reference15442 remains unchanged.
- Pause matrix:21 scenarios per profile including uninterrupted control and near-
  EOF;42 passes. The public final-head-window case legitimately hits one Good
  at the frozen tick. Its first driver assertion incorrectly required every head
  Perfect; the corrected driver requires all heads resolved without misses.
  Existing timing windows and regression thresholds are untouched. Muted/eight-
  cycle cases are rechecked with actual muted state and audible song positions.
- Every one of4419952 consumed Cream samples and1104984 mixed words matches the
  independent source model across8 audible pauses. No paused FIFO requests;
  0digital/mixer mismatches. Both profiles pass muted and repeated-pause byte
  checks. The inherited15-sample silent startup advance is explicit, not fitted.
- All18 independent waveform windows per profile pass >0.94 correlation/<1ms:
  before each of8pauses,64source samples after each resume,2seconds later and
  near the final audible samples. The first3.90625ms after routing restoration
  is excluded for filter settling; exact digital samples include that boundary.
- All12 ordinary primary waveform checks pass. **One of3 stricter common-backing
  comparisons fails**: Cream reactive at204.268494s, correlation0.979593 versus
  required>0.999. Scoring/wrong common-backing checks pass. No threshold/window
  is relaxed; this candidate does not have an all-green audio QA result.
- The failed run's entire unmodified FIFO stream also passes the existing exact
  oracle (0mismatches;1022–1026cycle requests,0full-song clock drift). Repeating
  the same ROM with the previously documented host-only mGBA0.10.1 FIFO-event
  lateness correction makes the strict comparison pass. This supports the known
  emulator output defect rather than skipped/mixed game source data. That
  diagnostic correction is never shipped or counted as ordinary acceptance.
  Hardware/other-emulator audio still needs confirmation.
- Full Cream graphics:16400frames,16086eligible,0displaced pixels among182521269
  observed road-colored pixels;11peak tail strips,0underruns. Foreground max
  161472cycles/mean107092.172, versus M013161408/107213.011. Refill max1408cycles
  remains unchanged. Existing VBlank DMA deadline assertions pass. Paused
  composed framebuffer equality is checked for every waiting frame, including
  36000frames (over10minutes) on each profile.

| Cream resource | M013 | M014 |
| --- | ---: | ---: |
| ROM bytes |9185256|9187576|
| EWRAM bytes |9264|9464|
| IWRAM payload bytes |27124|27164|
| Observed normal user-stack bytes from top |916|932|
| Observed IRQ-stack bytes |40|40|
| Untouched user-stack canary bytes |4472|4416|

The normal stack observation covers full song/results/replay/Original switching;
the8-pause full-Cream stack run also observes932user/40IRQ bytes touched and4416untouched user bytes. Silent fallback separately completes8pauses and results at512points. Reserved IRQ stack is
160bytes. No extra OAM, DMA channel, timer or IRQ is allocated. No physical
stack/timing measurement or exhaustive transition-cycle bound is claimed.
Screenshots: [paused](screenshots/mission014/paused.png),
[resumed](screenshots/mission014/resumed.png), [results](screenshots/mission014/end.png).
Final documentation/test-only commit changes the ROM's identity marker; final
ROMs are compared against this tested engine outside that40-byte marker and
smoke-tested after extraction.
