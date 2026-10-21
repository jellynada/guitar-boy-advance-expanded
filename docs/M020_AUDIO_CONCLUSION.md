# M020 focused audio conclusion

**AUDIO BOUNDED LIMITATION for development; release output certification open.**
The original mandatory output gate remains **9/15**.
No engine, timer, gain, sample rate, DMA, chart or judgment changes are justified
by the current evidence. RC2 remains byte-identical.

## Correctly identify the two windows

The unchanged analyzer's first Easy mixed failure is at runtime
23.64447021484375 s, with -1.007080078125 ms timing residual. Applying the
independently measured fixed 15-source-sample startup advance is a separate
diagnostic, not an accepted specification change. That diagnostic's remaining
paired-backing failure is at **runtime 36.20111083984375 s**, not the earlier
window. Runtime includes the two-second count-in; the corresponding music time
is 34.20111083984375 s. The M019 next-experiment wording conflated the first
unchanged-gate failure with the later correlation failure.

The diagnostic retains the original 4096-sample comparison, searches and
thresholds. At the later window it reproduces correlation
0.9985551608734642 (required >0.999), scale 0.9996424076657674, modeled residual
guitar -0.002277807629712923, and fixed-phase timing residual +0.244140625 ms.
The original six failures remain visible; no acceptance method has been replaced.

## Independent stock output reference

M020 first used a read-only AV callback on unmodified stock mGBA 0.10.1 and
0.10.5 (`26b7884bc25a5933960f3cdcd98bac1ae14d42e2`). Actual Easy mixed and
backing captures are byte-identical between versions. Their mixed capture is
also identical to the downloaded M019 CI capture. Observers add no emulated
instructions and are never linked into a ROM.

An isolated stock blip instance replays the observed PWM samples. Its capture
offset is the probe's measured 51,104 discarded output samples, not a fitted
shift. The first replay is **not byte-exact**: mixed has 56,931 differing samples
of 2,523,124, maximum absolute error 2 signed16 units; backing has 44,906,
maximum 1 unit. Those reference-model residuals remain explicitly open.

Nevertheless the paired waveform difference is already present before filtering:

| Layer, same inherited paired indices | Correlation | Residual RMS |
|---|---:|---:|
| Actual ordinary capture | 0.9985551608734651 | 70.10846247968342 |
| Independent blip replay | 0.9985551320645905 | 70.10909309068201 |
| Observed pre-filter PWM | 0.9975784335944782 | 92.30082328790539 |

These are diagnostic observations, not replacement passing scores. They show
that assuming the two separate play traces have identical pre-filter output is
incorrect. They do not, by themselves, establish why their PWM placement differs
or prove a hardware bound. The small independent-replay mismatch must not be
described as an exact reference.

## Reconcile actual FIFO events with PWM deadlines

The final read-only tap records FIFO indices590000..599999 and the corresponding
PWM output events on both stock versions. Tapping does not change either ordinary
capture: mixed and backing raw bytes remain identical to the untapped runs.
Every complete song independently checks1,261,568 consumed samples and315,388
mixer words with **zero mismatches and zero complete-clock drift**, separately
for mixed and genuine backing-only on both versions. Input/event/clock CSVs and
outputs are also identical across the versions.

In the10,000-event window, independently reconstructed timer request times are
exactly1024cycles apart. Host event lateness is0..48cycles. The scheduled next
PWM deadline is59cycles after each mixed FIFO request but only5cycles after
each backing-reference request. The stock `GBAAudioSampleFIFO` implementation
uses the **current** time-until-PWM value without compensating its `cycles`
lateness argument. Its two-slot write count is
`min(2, (until - 1 + 512) >> 9)` at this sound-bias resolution.

For the backing reference,3,403 events therefore see an expired deadline and
write no PWM slot.579 carry a different incoming byte from the prior held byte;
**all579 next observed PWM outputs retain that prior value, and zero emit the
incoming value**. The mixed trace has no expired deadline in the same source
window. These are actual unmodified-library observations, not a patched emulator
or a waveform fit. M019's independent tagged-value FIFO/timestamp experiments
already reproduce the same missing-event-time mechanism on both stock versions.

This explains why a backing-only recording from a separate input trace is not
a universally interchangeable common-filter reference: the stock emulator's
pre-filter slot sequence depends on timer/PWM phase and instruction lateness.
The remaining correlation failure is reproduced by the independent PWM replay,
while the byte stream arriving at the FIFO remains correct. No change to the
game's guitar gating or timer is supported by this evidence.

The longest observed expired-deadline sequence is8 source ticks,0.48828125ms;
this is a **local observation, not a universal emulator or hardware bound**.
The naive nearest-sample model leaves42 slot-end /19 slot-start samples outside
two source samples in the backing window; it must not be advertised as passing.
Repeated skipped slot updates explain why a one-sample nearest-neighbor model
is insufficient. The independent filtered reference's1..2signed16-unit rounding
residual is also retained, not rounded away or called exact.

Development classification rests on layer isolation, not listening preference:
the complete game-generated PCM, every FIFO word, sample order, count and clock
are independently correct; the discrepant transformation occurs in the stock
emulator's host PWM-slot update code after that boundary. Real GBA FIFO hardware
does not execute that host `mTimingUntil` slot-array algorithm. This is compelling
evidence against an unexplained game-side corruption or accumulating sync loss
being hidden by the comparison. It is not calibrated DAC/output certification.
Future graphics changes must retain all digital gates, compare ordinary failures
transparently, and stop on new corruption, drift, underruns or unexplained output
changes. No new acceptance thresholds or release methodology is adopted here.

## Real-recording preparation and qualification

The private pipeline remains unchanged. Source review confirms explicit stereo
to mono downmix, 16,384 Hz conversion with SWR/no dither, signed8 quantization,
no leading-silence trim and preserved codec pre-skip. It sums selected sources
by explicit guitar/backing role using the same divisor and shared
`0.85/max(1,max(abs(guitar)+abs(backing)))` gain. Quiet stems are not independently
boosted. Quantized absolute-sum peaks above127 are rejected. Shorter stems are
zero padded; common count-in and guarded tails preserve alignment. Candidate
stem roles and balance still require listening; metadata is not source isolation.

M019 historical real-Cream tests rebuilt exact RC2 locally and exercised full
Easy transport/gameplay, muting/recovery, eight pauses, EOF/results, original699
and a 3,677.957155-second private session. Historical source-chart counts are
395 heads/78 holds. Stack testing touched980 bytes with4256 untouched; static
IWRAM27276 and EWRAM9600. Full-length ordinary output10/15 remains historical
and unresolved. Those are **not fresh M020 private measurements**. Existing
authorized local ZIP is present, but it has not been uploaded or newly executed
in the public CI. Private Medium/Hard hardware qualification and professional
recording clarity are not claimed.

Transport correctness, subjective recording fidelity and formal release output
certification remain separate. The new owner RC2 report supports physical
playability and subjective listening, not calibrated timing, professional-song
clarity, every-difficulty coverage or hardware stack margins.
