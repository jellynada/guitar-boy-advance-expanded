# Mission 020 foundation closeout

**Development recommendation: APPROVED WITH DOCUMENTED LIMITATIONS.**
**Public release: RELEASE BLOCKED.**
**Audio: AUDIO BOUNDED LIMITATION. Engine changes: NONE.**

The engine is sufficiently characterized for a separately approved, incremental
graphics-development phase under the [resource contract](M020_GRAPHICS_RESOURCE_CONTRACT.md).
This recommendation neither starts graphics work nor approves a merge or release.
RC2 remains the correct binary; there is no RC3 or replacement song.

## Identities and reproduction

M019 remote tip matches `d0dda65a5ca71702cb6650ba06d0931bc10350d5`.
Complete, non-shallow Git history confirms RC2 and all audited historical source
branches are its ancestors. M020 branches from that exact M019 tip, preserving
history. Recommended verification/source baseline:
`33b4d227e7e8142639486d1effeb67a81c15903e`. Runtime remains
`9ccc460693fa7254527177330f32e56153720237`.

| Fresh M020 gate | Result |
|---|---|
| Host tests | 209 Python tests and13 ASan/UBSan programs pass in actual CI |
| Clean pinned-toolchain RC2 rebuild | Required immutable ROM hash reproduced |
| Exact extracted-ROM gameplay/UI/readiness/graphics | 38/38 checks pass |
| Full digital transport | 15/15, including every resumed segment |
| Unchanged strict ordinary output | **9/15; six failures remain release-blocking** |
| Composed reference-valid graphics | 27,420 frames, zero displacement |
| Stress | One measured public emulated hour passes; M019's four-profile campaign retained rather than repeated |
| Focused stock0.10.1 /0.10.5 | Same ROM, identical inputs/events/ordinary bytes; both mixed and backing full transports pass independently |
| Published artifact download | Exact hosted ROM/ZIP hashes,14-member CRC/safe extraction; ZIP ROM matches direct ROM and executed CI ROM |
| Content | Copper Circuit original composition and all three difficulties retained; no private payload uploaded |

Actual code runs are [initial baseline](https://github.com/jellynada/guitar-boy-advance-expanded/actions/runs/39658801775)
and [final instrumented verification](https://github.com/jellynada/guitar-boy-advance-expanded/actions/runs/39660269121).
The second run adds the focused FIFO/PWM causal measurement; it is not a different
game build. Their ordinary gate fails visibly. A successful promotion-status
report means “blocked recorded”, not release approval. No `continue-on-error`,
threshold adjustment or replacement accepting comparator was added.

Fresh results come from Linux GitHub runners, not a Windows GUI emulator session.
Bundled Python/NumPy performed local waveform/evidence analysis; no software or
system settings were changed on the owner's Windows PC. Raw public diagnostic
artifacts were downloaded and hash-verified. Private Cream tests/resources are
explicitly retained M019 evidence, not fresh M020 private execution.

## Why development and release decisions differ

[The focused audio report](M020_AUDIO_CONCLUSION.md) separates the original
23.644470s timing failure from the later36.201111s fixed-phase correlation
failure. At the latter, the supposedly common backing reference has stock
emulator PWM deadlines only5cycles after FIFO requests. Event lateness reaches
48cycles;579 changed incoming values with expired deadlines all produce the old
held PWM value. The mixed run's59cycle deadline avoids this. Both stock versions
reproduce it, and observation does not change ordinary output bytes.

Every actual FIFO byte, mixer word and complete song clock remains independently
correct. The discrepancy is localized after the game/FIFO boundary to a stock
host output-slot algorithm, not an unexplained game-side loss of samples or
accumulating timing error. The independent PWM-to-blip replay reproduces the
paired correlation discrepancy; its own1..2signed16-unit residual remains open.
No universal hardware bound is claimed from the observed8expired-tick sequence.

This supports a bounded development limitation with strict transport/resource
safeguards. It does **not** certify absolute analog phase, approve a revised
output specification, resolve historical Cream10/15, establish professional
recording clarity, or override the existing mandatory9/15 release failure.
Formal release additionally needs remaining licensing and owner approval.

## Owner hardware evidence

The owner reports that RC2 works great on a real GBA, sounds fine, and has not
crashed during their use. Record this as **positive RC2 physical-GBA playability
and subjective audio feedback**. The owner also says the available song does
not let them judge real-recording quality/clarity. Copper Circuit is the original
public composition; it is not a commercial multistem recording qualification.
No particular difficulty coverage, session duration, calibrated timing, stack,
IRQ margin or redistribution permission is inferred from that feedback.

## Safeguards, handoff and smallest remaining release step

Private full Cream uses27,276static IWRAM bytes versus8,308public; its measured
main-stack margin is much tighter. The proposed first graphics increment adds
no IWRAM, IRQ work, DMA ownership or OAM entries; bounded ROM/EWRAM/frame work
still requires profiling both profiles. Existing OAM slots are all reserved,
even when the observed scene uses few of them. Physical worst-case stack/bus
timing remains unmeasured. See the resource contract and
[history-preserving integration proposal](M020_DEVELOPMENT_BASELINE_PLAN.md).

The smallest remaining **output-release** experiment is a deterministic stock
PWM/quantization reference calibrated independently against synchronized output,
including the8-expired-tick case and the1..2unit blip residual, followed by the
unchanged complete ordinary gate or an explicitly reviewed specification proposal.
This is a focused release-methodology question, not authorization to rewrite the
audio engine. Development need not wait for subjective tuning of future songs.

Owner next action: review this recommendation and approve or reject the proposed
development baseline/resource contract. No protected merge, graphics work or
formal publication has occurred.

## Play the unchanged original-song RC2

[Direct ROM](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/437410b45881119084cf675735b30cf3c841dad5/public-demo-downloads/Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.gba)
and [player ZIP](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/437410b45881119084cf675735b30cf3c841dad5/public-demo-downloads/Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.zip).
ROM SHA256:
`9c4af95ff97eddd266dca3d7491ac9a5b1256f417684aae51b7c126443afafde`.
ZIP SHA256:
`194c34e77deade95e2c60f4d57cc55c946dbd199cf56cf48cfb9fd1e2d08b77b`.
Open the `.gba` in mGBA or copy it normally to the flash cartridge. Choose Copper
Circuit, then Easy/Medium/Hard. START pauses/resumes; SELECT while paused exits.
No compilation is required. Local copies were saved beside this chat's workspace.
