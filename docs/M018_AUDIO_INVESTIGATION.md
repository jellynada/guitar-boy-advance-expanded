# Audio investigation — measurements, not a tolerance change

RC1 was rebuilt from113fc49fbcec851631ee4a932320de7fa803e551 with the pinned
compiler and reproduced SHA243e4160c68c671a7b9e1d4dc0e2f4bb439294eccf62a1accf04b0aae5df6af6.
Fresh ordinary captures reproduce9/15: all-miss case4 and mixed case22 fail on
Easy/Medium/Hard. Original `<1ms`, correlation, leakage and paired-backing
thresholds are unchanged. Fresh digital15/15 passes with zero sample/word
corruption or complete-song clock drift, with the existing explicit startup
advance15. Passing digital identity alone is not output timing clearance.

## Confirmed stock-emulator mechanisms

`tests/mgba_fifo_capacity.c` independently calls the unmodified stock library:
28-byte priming leaves7 words, consumes the first tagged word correctly;
32-byte priming wraps the eight-word write cursor to the read cursor and is
interpreted as empty. Stock0.10.1 and0.10.5 reproduce it. Game startup legitimately
primes a hardware32-byte FIFO. Do not reduce its slack just to mask an emulator
representation problem. No game audio/IRQ change is made here.

A separate controlled function-call experiment provides identical FIFO state
and varies cyclesLate0/600. Stock output slots stay[5,9] in both cases because
slot selection uses the current sample-event distance, without accounting for
the earlier FIFO event time. An isolated600-cycle event-distance adjustment
produces[9,9], demonstrating that missing time context can change PWM placement.
This is a host diagnostic, not a patched emulator or delivered game change.
See `fifo-diagnostic-0101.log` / `fifo-diagnostic-0105.log` in mission evidence.

## What this explains, and what remains open

Ordinary analysis assumes source index0 at its counter-derived epoch, whereas
the independent consumed-byte oracle observes the existing fixed15-sample
startup advance (0.915527ms). This is a constant phase component, not a fitted
window offset or gradual clock drift. Small event/PWM/capture phase variations
then push some measurements beyond1ms (observed1.007080–1.068115ms).

`tools/diagnose_demo_phase.py` makes a separate expected waveform using that
independently established phase; it does not alter mandatory analysis or time
thresholds. On fresh RC1 captures it passes14/15. Easy mixed still fails the
paired-backing correlation test (.998555 versus required>.999), despite its
corrected timing residual0.244141ms. This prevents a claim that one calibration
fully explains or fixes all output discrepancies. Timing/filter/capture-model
contributions to that last difference remain open.

Fresh stock0.10.5 ordinary Easy Perfect and true backing-reference runs pass;
Easy mixed reproduces the unchanged timing failure. Normal output comparisons
use no LD_PRELOAD or correction. Digital observation is a separate host tap,
with its optional lateness correction disabled. FIFO/gate/time traces and raw
waveforms are retained, not replaced with favorable summaries.

## Decision and smallest next experiment

Time-boxed result: confirmed emulator compatibility mechanisms and one residual
waveform-model discrepancy; **mandatory ordinary gate stays unresolved**.
No ROM-side evidence justifies changing gameplay time, timer rates, IRQ priority,
PCM priming, gain ramps or chart alignment. Inherited full Cream10/15 remains
historical/open; owner-private assets are not substituted or published.

Next engineering experiment: capture known tagged FIFO startup and the specific
Easy mixed window on physical GBA output with a clock reference, compared with
stock-emulator PWM/capture event times. This needs measurement equipment and
cannot be completed by cloud emulation. The owner's RC1 “works great” report
supports playability but cannot resolve sub-millisecond timing/filter questions.
