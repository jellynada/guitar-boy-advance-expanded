# Mission 022 development performance exception proposal

**PROPOSED — NOT APPROVED.**
Technical recommendation: **A — RECOMMEND DEVELOPMENT EXCEPTION**.
Owner acceptance and a separate merge authorization are still required.

## Exact scope

Reviewed executable source: `c4f900bbd99734353a8de38cf82d2629cd1eaf2d`.
Accepted develop: `cf2ee6601753a2718f0e08f6c9f78ac791114e03`.
Branch: `mission-022-multi-song`; [PR #5](https://github.com/jellynada/guitar-boy-advance-expanded/pull/5).
This proposal is added in a documentation-only descendant; preserved ROMs still identify the reviewed executable source.

If accepted, the exception would permit development integration of this tested M022 multi-song behavior despite its historical incremental allowance failures. It covers the disclosed Hard comparisons and Medium same-case phase effect for the existing tested cartridges and difficulties. It does not authorize additional songs, graphics work, compression, altered clocks, scoring/timing changes or extra ongoing gameplay cost.

It does not turn a failed original measurement into a pass, remove the general +8,192 change-control history, or approve a numeric gate in CI. No test policy is changed by this proposal.

## Historical failures retained

| Original comparison | Baseline | Candidate | Increase | Beyond +8,192 |
| --- | ---: | ---: | ---: | ---: |
| Broader Hard profile peak | 254,016 | 266,432 | 12,416 | 4,224 |
| Hard case 28 | 252,544 | 266,432 | 13,888 | 5,696 |
| Medium case 28 | 225,216 | 236,608 | 11,392 | 3,200 |

Medium is an explicit disclosed part of the decision, not a silently grandfathered failure. No change in these numbers is implied by the diagnostic controls.

## Why an exception is technically supportable

The original observer schedules physical-safe stress pulses by its own frame count. Autoplay uses the actual sample clock. Song initialization and bounded readiness observation shift pulse/audio/video phase, so named cases do not place the same events on the same musical/rendering frame.

The large original Hard difference is accounted for by a wrong-input/HUD redraw overlapping dense rendering, and the extra IRQ service during that longer interval. Descriptors are bound while stopped; no large new per-frame catalog walk exists. Matched busy work is 266,112 baseline versus 266,432 candidate (+320), while all 60 Hard pulse phases on each original ROM yield maxima 271,360 versus 270,848 (-512). Those envelope peaks are different frames; this is not a claim of identical per-frame inputs or guaranteed negative implementation cost.

Controls are causal diagnostics, not replacement acceptance tests. Native sources/tools, chart/stem bytes, physical-safe inputs, counter methodology, traces and final states were checked. Read-only observation has no effect on the original per-frame audio/event captures. The smaller real PCM selector cost remains: equivalent append16 calls add 48 cycles, with about 1,000 extra IRQ cycles in the matched expensive interval. See the [closeout review](M022_CLOSEOUT_REVIEW.md) and retained owner-local evidence.

The available tests demonstrate no new functional, digital PCM/sample-clock, chart/scoring/input, graphics or navigation regression in the exercised paths. Ordinary-output case changes remain unresolved and release-blocking; analog equivalence is not asserted. No production optimization was needed to explain the peak. A broader HUD/render rewrite is not disguised as a minimal collection fix.

## Candidate-specific monitoring proposal

The proposed monitored maximum for this executable is **270,848 foreground cycles**, the expanded observed Hard maximum under the documented native stock mGBA 0.10.5/devkitARM release-65 conditions. This is a measured reference and proposed review ceiling, **not a physical worst-case bound or new approved CI threshold**. The M021 expanded 271,360 is comparison evidence, not permission to spend up to it.

The associated observed minimum in the targeted winner is **7,821 cycles from the ending timer-read instruction to the next VBlank, before remaining bookkeeping**. Nominal 280,896 minus 270,848 equals 10,048 but does not represent all remaining frame capacity. The original canonical Hard case remains 266,432. Medium's sampled control maximum is 240,512 across six tested phases, not an exhaustive Medium bound.

If the owner accepts this proposal, future changes must trigger review on any of these alarms:

1. Any reproduced increase above 270,848 in the same Hard stress family, or above the corresponding canonical/difficulty receipt in a controlled comparison. Record original inputs and phase; do not hide growth behind a new unrelated baseline.
2. Reduced measured time to the relevant VBlank against the 7,821-cycle reference under equivalent observation, any missed scanline/VBlank commit or 280,896-cycle foreground overrun. Include work outside the foreground timer bracket in deadline analysis.
3. New or increased audio IRQ/refill latency/cost relative to matched receipts; any underrun, FIFO/mixer mismatch, complete/segment clock drift, pause request during freeze, or reactive-gating regression.
4. Any new displacement, late affine/blend update, tail overflow, scoring/judgment/combo/sustain mismatch, input-mapping failure, stale selected chart/stem, unsupported difficulty, failed natural completion, Restart/Retry/Quit or A→B→A transition.
5. Increased stack usage or reduced untouched margin relative to the same public/private workload, a canary failure, unexpected static IWRAM growth, new per-frame allocation, or an unreviewed VRAM/palette/OAM/DMA/timer ownership change.
6. A changed ordinary-output failure matrix. Investigate individual cases; retain the original windows and thresholds. Known failures are never relabeled as successes.
7. Changed ROM/source identity, private content/path exposure, modified original media or failure to reproduce the intended inputs.

An alarm pauses acceptance of that future change for diagnosis and owner review; it is not an automatic waiver or permission to repeatedly rebase thresholds. Measurements must retain toolchain/emulator identity and the full intended content/difficulty workload. Do not pool unlike compiler/core results. Broader phase coverage for new content may expose a larger maximum and requires a new review.

This exception provides **zero authorized additional gameplay graphics CPU budget**, zero additional IRQ work, and no automatically reusable resource reserve. Existing ROM storage projections and the provisional 1 MiB art/code storage allowance do not grant CPU time or free VRAM.

## Uncertainty and limits

The 120 Hard phase executions cover a defined family, not every possible player input, physical bus state, song or future resource combination. Stack figures are observed watermarks. Timers, dispatch/return, DMA contention and software FIFO were measured in stock emulators, with no external BIOS qualification.

RG SP running mGBA is the owner's handheld test platform. Only its expected owner-local Song Select entries are currently confirmed for M022. There is no new exhaustive handheld completion/Hard/stability record and no original Nintendo GBA/flash-cartridge certification. Real hardware ROM wait states, contention, IRQ/FIFO behavior, all-path stacks, sustained analog output and additional graphics workloads still need separate qualification.

Strict ordinary-output remains failed: public CI **14/20**, native public **15/20**, native owner-local **22/30**. Correct digital FIFO does not resolve PWM/output or analog qualification. **Formal public-release promotion stays blocked regardless of any development exception acceptance.**

## Owner decision required

The owner may accept or reject this scoped development exception, or request additional evidence. No recommendation in this file records an approval. The pending decision must explicitly acknowledge:

- The original Hard and disclosed Medium allowance failures.
- The candidate-specific measured ceiling and future alarms above.
- The narrow emulator evidence, small measured reserve and pending handheld coverage.
- No additional graphics/feature CPU allocation and the unchanged formal-release blocker.

Acceptance would permit consideration of development integration only. It would not itself run a merge. A separate explicit normal-merge approval must name/reconfirm the then-current PR head and develop base; no auto-merge, squash, rebase or force push is authorized.
