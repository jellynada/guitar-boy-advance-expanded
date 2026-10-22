# M021 audio differential audit

**A. KNOWN BOUNDED LIMITATION - NO NEW ENGINE REGRESSION DEMONSTRATED.** Development integration and formal release are separate decisions. The strict ordinary-output job remains failed. This is not a claim of identical analog output or an all-green workflow.

Runtime candidate: `ea1832bf8454c82a84f0a5ae5142917853e44a60`. Accepted base: `d167d269f23b3d0f32d2753e6233f7f21771cd3d`. The closeout changes only review documents and the public audio test-window policy; it does not change or replace the playable ROMs.

## Scenarios and original assertions

Each of the following runs on Easy, Medium and Hard: 5x3=15 cases. UP/DOWN alias handling and chart-native physical controls come from the retained observer, not the UI reducer.

| Case | Physical/input sequence | Expected behavior |
|---|---|---|
| 19 | Autoplay due chart heads, hold native sustains; no pause | No missed/wrong heads, synchronized reactive mix, full EOF |
| 4 | No gameplay lane presses; START pauses at observer frame180, hold30 frames, START resumes | Every head missed; guitar fades/mutes, backing continues after resume |
| 22 | Play heads except every third (`next%3==1`); genuine all-lane press every30 frames; no pause | Real misses/wrong presses/muting and hit-driven recovery; original gain model |
| 0 | Autoplay; START pauses at frame8 of playback observer, duration1 frame; resume | Count-in continuity, no manufactured edge |
| 12 | Autoplay; first pause near first head+120 frames, then eight total pauses, each30 frames | Frozen PCM/clock/score while paused; exact resumed stream |

Auxiliary case23 is not a sixteenth gate case: one real A press at frame30 before notes, then no gameplay keys and no pause. It supplies the independently muted backing capture for cases4/22. Case22 also requires recovery. Native/CI observers explicitly navigate their actual launcher; only that menu travel and the documented paused A/B menu semantics differ from retained old probes. Chart counts: public86/171/335; private395/686/878. Observations cover complete songs; M020 public limit4900 frames, M0215200, private16683; observers stop on completion.

The unchanged `tests/analyze_reactive.py` requires source correlation>.94, absolute nearest-observed-epoch error<1ms, paired backing correlation>.999, backing scale between.98 and1.02, residual guitar below.01, true mute/recovery where requested, no clipping, zero underruns and frozen ended clocks. Some failed comparisons exit before later assertions; a first failure is not a claim that every later ordinary-output assertion passed. Independent full digital checks cover the transport/gate model separately.

**Audit correction:** M021's driver used public reference times6.322,37.5,75.2 instead of the original6.322,37.5,76.7. No threshold changed, but the last window was unintentionally different. Closeout restores the exact original times and adds a policy regression test. All45 retained public comparisons were freshly rerun with the original windows and comparator. The totals and failed-case sets below are unchanged by restoration. Private times remain the separately documented6.322,136,265; private music is not interchangeable with Copper Circuit.

## Exact matrices

| Difficulty / scenario | Frozen RC2, M020 recertification | M021 CI public | M021 native public | M021 native private (different recording) |
|---|---|---|---|---|
| Easy / 19 autoplay, no pause | PASS | PASS | PASS | PASS |
| Easy / 4 all miss, one pause | FAIL | FAIL | FAIL | FAIL |
| Easy / 22 mixed input, no pause | FAIL | FAIL | FAIL | PASS |
| Easy / 0 count-in pause | PASS | PASS | PASS | PASS |
| Easy / 12 eight pauses | PASS | PASS | PASS | PASS |
| Medium / 19 autoplay, no pause | PASS | PASS | PASS | PASS |
| Medium / 4 all miss, one pause | FAIL | PASS | FAIL | FAIL |
| Medium / 22 mixed input, no pause | FAIL | FAIL | FAIL | FAIL |
| Medium / 0 count-in pause | PASS | PASS | PASS | PASS |
| Medium / 12 eight pauses | PASS | PASS | PASS | PASS |
| Hard / 19 autoplay, no pause | PASS | PASS | PASS | PASS |
| Hard / 4 all miss, one pause | FAIL | PASS | PASS | FAIL |
| Hard / 22 mixed input, no pause | FAIL | FAIL | FAIL | PASS |
| Hard / 0 count-in pause | PASS | PASS | PASS | PASS |
| Hard / 12 eight pauses | PASS | PASS | PASS | PASS |
| Total | 9/15 | 11/15 | 10/15 | 11/15 |

Public changes from RC2: native Hard/case4 becomes passing; CI Medium/case4 and Hard/case4 become passing. All public failures remain among RC2's six failed case IDs; first failing windows can move. All case19/count-in/eight-pause cases pass. The scores do not demonstrate sound-quality improvement.

The private matrix is a different recording/chart workload and cannot be subtracted from public RC2's total. Fresh same-environment old-local versus M021-private checks show all three case4 waveform-correlation failures already on the old ROM. **Private Medium/case22 is a newly failing strict comparison relative to that old local ROM**; it was investigated rather than hidden. No fresh complete15-case old-private total is claimed.

## Every recorded first failure

Times are runtime seconds including count-in. These are the actual unchanged-comparator assertions, not substituted passing diagnostics.

| Dataset | Difficulty/case | Classification | Recorded assertion |
|---|---|---|---|
| RC2/M020 | Easy/22 | phase/alignment | ('backing-only', 'runtime_seconds', 23.64447021484375, 'error_ms', -1.007080078125) |
| RC2/M020 | Easy/4 | phase/alignment | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'error_ms', -1.068115234375) |
| RC2/M020 | Medium/22 | phase/alignment | ('backing-only', 'runtime_seconds', 53.78021240234375, 'error_ms', -1.068115234375) |
| RC2/M020 | Medium/4 | phase/alignment | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'error_ms', -1.007080078125) |
| RC2/M020 | Hard/22 | phase/alignment | ('backing-only', 'runtime_seconds', 39.21282958984375, 'error_ms', -1.007080078125) |
| RC2/M020 | Hard/4 | phase/alignment | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'error_ms', -1.007080078125) |
| M021 CI | Easy/22 | phase/alignment | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'error_ms', -1.007080078125) |
| M021 CI | Easy/4 | phase/alignment | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'error_ms', -1.03759765625) |
| M021 CI | Medium/22 | phase/alignment | ('backing-only', 'runtime_seconds', 37.70794677734375, 'error_ms', -1.068115234375) |
| M021 CI | Hard/22 | phase/alignment | ('backing-only', 'runtime_seconds', 50.76654052734375, 'error_ms', -1.068115234375) |
| M021 native public | Easy/22 | phase/alignment | ('backing-only', 'runtime_seconds', 38.71282958984375, 'error_ms', -1.007080078125) |
| M021 native public | Easy/4 | phase/alignment | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'error_ms', -1.03759765625) |
| M021 native public | Medium/22 | phase/alignment | ('backing-only', 'runtime_seconds', 53.78021240234375, 'error_ms', -1.03759765625) |
| M021 native public | Medium/4 | phase/alignment | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'error_ms', -1.007080078125) |
| M021 native public | Hard/22 | phase/alignment | ('backing-only', 'runtime_seconds', 51.26849365234375, 'error_ms', -1.068115234375) |
| M021 native private | Easy/4 | waveform correlation | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'correlation', 0.925070220105383, 'error_ms', -0.579833984375) |
| M021 native private | Medium/22 | paired backing correlation | ('backing-only', 'backing capture differs', {'label': 'backing-only', 'runtime_seconds': 25.64935302734375, 'correlation': 0.9936267247560909, 'error_ms': -0.640869140625, 'global_epoch_error_ms': -0.640869140625, 'capture_epoch_at_reference': -618, 'backing_scale': 189.23741959435327, 'guitar_to_backing_scale': 0.0027465743780112272, 'backing_capture_correlation': 0.9966754830373064, 'backing_capture_scale': 0.991359157296634, 'residual_guitar_after_common_filter': -0.006687625866056748}) |
| M021 native private | Medium/4 | waveform correlation | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'correlation', 0.9238433383532797, 'error_ms', -0.67138671875) |
| M021 native private | Hard/4 | waveform correlation | ('sync-reference', 'runtime_seconds', 6.314178466796875, 'correlation', 0.9220666027325667, 'error_ms', -0.640869140625) |

The public failures are approximately-1.007..-1.068ms phase/alignment residuals, not accumulating transport-clock drift. The private all-miss source correlations are.922..925, below.94; old local ROM reproduces.920..925 failures in those same scenarios. Private Medium22 fails paired correlation.996675483 (<.999); scale.991359157 and residual-guitar-.006687626 are individually within their original limits. This is not evidence that guitar failed to mute. No new failed FIFO sample, mixer word, underrun or digital clock-drift check was observed.

## Separate ROM/build effects from host effects

Fresh controlled replay uses the existing unmodified stock mGBA0.10.5 core at `26b7884bc25a5933960f3cdcd98bac1ae14d42e2`, same Windows host compiler/library for each ROM. The exact CI-built RC2 and M021 public ROMs were replayed on Windows. All seven selected raw captures per CI ROM matched their retained Linux/CI counterparts byte-for-byte, including the previously changed Medium/Hard all-miss cases and Easy mixed/backing. Thus Windows-versus-Linux or0.10.1-versus0.10.5 alone does not explain those observed differences. This is selected-case evidence, not an exhaustive cross-platform equivalence proof.

The Windows-native and CI M021 ROM hashes differ. All public prepared guitar/backing bytes are identical across RC2, CI M021 and native M021. Binary/build/layout and actual pre-play initialization paths affect the emulated timer/PWM phase. Direct observation for native Hard case4 gives request-phase residues241/243 modulo512 initially and211/213 after resume; adding only1,2,3 title-wait frames changes these residues and the ordinary waveform. All three delayed controls fail strict alignment (-1.0376,-1.0376,-1.0071ms), while the undelayed identical ROM passes. Each delayed full digital stream still passes. These are declared diagnostic input delays at the title, never waveform timing shifts or modifications to the comparator or ROM.

## Explain the newly failing private comparison

At the original private Medium22 failing window (runtime25.649353s), old-local paired correlation is.999991133; M021 is.996675483. A read-only host tap observes the actual pre-filter output. At the same inherited paired indices:

| Layer | Old local ROM | M021 private |
|---|---:|---:|
| Ordinary correlation | .999991133 | .996675483 |
| Independent stock blip replay correlation | .999991137 | .996675333 |
| Observed pre-filter PWM correlation | .999982068 | .995952463 |

The difference is present before host output filtering. In a bounded40000-request region (FIFO indices400000..439999), M021 mixed has16148 requests with no PWM slot written, versus zero for its backing reference. Old-local mixed/backing have zero such requests there. M021 mixed time-until-PWM is-44..4 cycles with lateness0..48; backing is6..56. The unchanged stock `GBAAudioSampleFIFO` computes its slot count from current time-until-PWM without compensating its `cycles` lateness parameter. At this resolution the count is `min(2,(until-1+512)>>9)`; nonpositive counts write no slot and retain prior slot values. M020 already demonstrated this same mechanism on stock0.10.1/0.10.5 with correct FIFO input. This is observed post-FIFO host behavior, not inferred corrupted prepared stems.

The independent blip replay is **not byte-exact**: in these full private captures its maximum residual is4..5 signed16 units, both baseline and candidate. It is diagnostic evidence, not a replacement acceptance model or certified DAC model. An initial audit observer omitted4936 samples drained by navigation helpers, producing an invalid replay offset; that result is retained locally and explicitly rejected. Counting all actual discarded samples changes the measured offset51104 to56040. No fitted shift was applied. Corrected/uncorrected raw audio, FIFO, consumed-sample, clock/event and transport files are byte-identical; only offset bookkeeping changes. The corrected replay above closely reproduces the discrepancy while retaining its small reference error.

## Digital integrity and preserved behavior

Fresh focused checks:34/34 complete game/FIFO/sample oracles across RC2, both public candidate binaries, title-delay controls, old private and new private. Every oracle retains startup advance15, zero mixer/consumed-sample mismatches and zero complete-clock drift; no lateness correction was enabled. Retained exact-candidate checks are30/30 native (both profiles) and15/15 CI. The declared15-sample digital startup relationship is inherited; ordinary-output comparisons receive no corresponding undocumented shift.

PCM/mixer/FIFO source, sample rate, chart timing/judgment/scoring/control headers, stem preparation/adaptation and both original audio comparators are byte-unchanged from develop. Full private stems match the successful pre-UI build; public stems match RC2. UI changes scene travel and cleanup, including masking the already-ended Timer1 IRQ at Results. That cleanup is after EOF and cannot explain an active-playback window. No new engine fix is justified by this audit, and none was made.

## Identities and retained evidence

| Artifact | Source / identity |
|---|---|
| Frozen RC2 | source9ccc460693fa7254527177330f32e56153720237; ROM9c4af95ff97eddd266dca3d7491ac9a5b1256f417684aae51b7c126443afafde |
| M021 CI public | sourceea1832bf8454c82a84f0a5ae5142917853e44a60; ROMb19b6034cd7e33e3f5825b6e53a5f113de06f1e2bab5d5b531f3903b4985fceb |
| M021 Windows native public | same source; ROM80e1b93e996a0c3ef1fc7f190bfe5b51ff1872c1d5da53d63259e4194c2647ef |
| Native private baseline/candidate | Exact ROM/ELF/capture hashes recorded only in owner-local closeout report |
| Public build image | devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5 |
| Native build | devkitARM r65/GCC14.2.0; existing portable tools; local executable/library hashes recorded |
| Stock emulator | retained Debian0.10.1 and stock0.10.5 commit26b7884bc25a5933960f3cdcd98bac1ae14d42e2; read-only host observers, never linked into a ROM |

[M020 recertification](https://github.com/jellynada/guitar-boy-advance-expanded/actions/runs/39660269121) artifacts: ordinary-output12372873410, gameplay12372932749, build12371659910, focused-output12374091232. [M021 candidate](https://github.com/jellynada/guitar-boy-advance-expanded/actions/runs/39721249192) artifacts: observations12402065014, build12401495787, digital12400534494. Downloaded archives were checked against GitHub's published SHA-256 digests; full digests and per-input hashes are retained locally. Exact M020 and candidate evidence is independent; frozen RC2 is never relabeled M021.

**Release remains blocked.** This bounds the observed emulator-output differences sufficiently for controlled development review. It does not certify original-GBA timing, analog fidelity, every possible execution phase, absence of all defects or exact physical waveform equivalence.
