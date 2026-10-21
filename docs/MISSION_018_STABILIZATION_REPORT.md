# Mission 018 current baseline and release decision

**YELLOW — playable and useful development candidate; audio release gate open.**
No gameplay, chart, input-mapping, timer, mixer, scoring or sustain policy change
is justified by the investigation. RC2 changes build/menu identity and makes
release evidence and gates more reliable. RC1 remains untouched and downloadable.
Owner says RC1 works well on a real GBA; that is positive playability evidence,
not comprehensive RC2 acceptance.

## Source and baseline

Fetched every remote branch, verified full history, exact Mission017 tip
8f1c4839475ad0167782c9c4d140bd2eb751c378 and build source
113fc49fbcec851631ee4a932320de7fa803e551. Mission018 branches from that tip on
`mission-018-release-stabilization`. Main, develop, M013, M014, medium-hard,
stabilization/foundation and Arcade75 feature refs are ancestors of this source;
no newer feature fixes were found. Historical download-only branches were not
merged. Exact refs are retained in `M018_VERIFICATION.json`.

Fresh pinned-source RC1 rebuild reproduces its published SHA exactly:
243e4160c68c671a7b9e1d4dc0e2f4bb439294eccf62a1accf04b0aae5df6af6.
Fresh baseline:201 Python/13 sanitizer programs,35 game/UI probes,27420 graphics
frames and15 digital comparisons pass; ordinary output remains9/15. The source
manifest, toolchain digest, environment, audio/chart identities and before/after
measurements are machine-readable in `M018_VERIFICATION.json`.

## Supported changes

- Preserve RC1; add explicit RC2/M018 filename/identity and separate artifact
  allowlist, while verification still supports original RC1 metadata.
- Check cartridge header/checksum/logo and32MiB ceiling in candidate verification.
- Reject stale/foreign audio evidence and expose build/gameplay/digital/output
  statuses separately; never infer owner or release approval from a green build.
- CI separates those jobs and retains failing evidence. Ordinary output failure
  remains nonzero; no continue-on-error or promotion/upload-to-release job exists.
- Add read-only pause input traces and stock-library FIFO/time diagnostics,
  legal adversarial gameplay traces and lossless evidence storage.
- Fix a measurement-aggregation regex that searched for literal `\\d` and silently
  missed foreground peaks in gameplay logs. Require all expected measurements.
  This changes reporting correctness, not game speed or a performance threshold.

## Findings

See `M018_AUDIO_INVESTIGATION.md`: stock FIFO full/empty representation and
uncompensated late-event PWM placement reproduce independently. A fixed phase
experiment using the exact byte oracle reaches14/15, but residual paired-waveform
failure prevents claiming a complete explanation or clearing mandatory9/15.
No emulator correction, arbitrary timing shift or threshold change is shipped.

See `M018_PAUSE_INPUT.md`: extra case8 WrongInput is a real new B press after
resume, with the previous head already judged. It is explained under existing
rules; no manufactured edge was observed. New scenarios distinguish pressing
while paused from genuinely pressing after resume. The old failing assertion
is retained as historical evidence rather than overwritten.

All3 charts remain86/171/335 heads and11/11/10 holds. Owner explicitly chose to
keep Medium's existing final same-lane re-articulation. Trace-dependent scores
remain the contract. Private Cream15815 exact-trace/full-length output findings
are not declared revalidated unless the exact existing private regression runs.
Commercial/private content cannot enter public fallback or player packaging.

## Limits and next milestone

Cloud measurements are emulator observations, not physical DMA/IRQ/stack safety
certification. Stack sentinel measurements write only free emulated stack RAM
and are explicitly diagnostic. Pause/resume total CPU cost and physical high-water
measurements remain unmeasured. Hardware capture is needed to settle the remaining
output-phase/filter question. Do not ask the owner to set up a compiler.

Next scoped work: instrumented hardware/audio comparison of the known Easy mixed
window, after owner RC2 comfort/listening/restart checks. No next mission is begun.
Formal release and accepted integration remain blocked/pending owner approval.

## Integration and rollback proposal

At the fetched refs, develop56f6b7b243dfc710996336b99ac249806e666c85 is an ancestor
of the complete candidate history; a normal history-preserving merge is possible
without cherry-picking fragments or bringing download-only branches into source.
After review/acceptance, propose a no-fast-forward merge PR to develop with all
feature history and gate evidence. Recheck remote ancestry/conflicts immediately
before any authorized merge. Roll back a future merge with an ordinary revert
of that merge, preserving history and leaving RC1/RC2 artifacts recoverable.
No protected branch, formal release, permanent tag or history rewrite is changed.
