# Mission 022 owner acceptance record

**Status: PENDING OWNER DECISION.**
Technical closeout: READY FOR OWNER DEVELOPMENT EXCEPTION REVIEW.
Technical recommendation: A — RECOMMEND DEVELOPMENT EXCEPTION.
Exception approved: **NO**. Development integration approved: **NO**. Merge authorized: **NO**.

Reviewed executable source: `c4f900bbd99734353a8de38cf82d2629cd1eaf2d`.
Accepted develop: `cf2ee6601753a2718f0e08f6c9f78ac791114e03`.
Review branch: `mission-022-multi-song`; [PR #5](https://github.com/jellynada/guitar-boy-advance-expanded/pull/5).
These documents are a documentation-only descendant; the actual final PR head is recorded in PR metadata and the owner-local closeout receipt. The preserved playable ROMs remain from the reviewed executable source.

## Actual handheld feedback

Platform: **RG SP running mGBA**. This is handheld emulation, not original Nintendo GBA hardware certification.

The owner has confirmed that the two expected owner-local Song Select entries appear. Their exact titles/ROM identities are in the owner-local record. This supports catalog display presence only.

The owner previously reported successful M021 handheld gameplay. That is historical M021 evidence and is not counted as M022 completion, switching, Restart or Hard stress coverage. No additional owner-confirmed M022 actions were supplied with this closeout. Automated mGBA runs are listed separately in the technical review.

## Pending owner checklist

All unchecked items are **pending**, not inferred successes:

- [ ] Launch Synth Demo, return to Song Select and launch the full-length owner-local track in the same mGBA session.
- [ ] Play the owner-local Easy, Medium and Hard charts where practical; exercise dense Hard notes, chords and long sustains.
- [ ] Pause/Resume, Restart the same song and Quit to Song Select; confirm the intended song/difficulty and reset state.
- [ ] Switch owner-local track → Synth Demo → owner-local track without reboot.
- [ ] Complete a song and exercise Results Retry, Change Difficulty, Song Select and Main Menu.
- [ ] Repeat sessions without power cycling; report stutters, crackles, input/timing errors, slowdown, flicker, crashes or silence.
- [ ] Record actual ROM filename/checksum, mGBA core/version, RG SP configuration, tested difficulties/actions and any symptoms.

Do not change settings merely to fill this record. Supply observations from the actual tested setup. If only some items are practical, identify those explicitly. The owner must decide the disposition of pending handheld coverage before integration is authorized; technical analysis does not wait for unavailable feedback.

Use the existing preserved M022 cartridges. The private cartridge remains PLAYTEST ONLY and must stay local. Do not replace or upload it. Public difficulty availability remains Synth Demo Easy/Medium/Hard and Synth Demo 2 Easy only.

## Decisions still required

1. Explicit owner acceptance or rejection of [the performance exception proposal](M022_PERFORMANCE_EXCEPTION_PROPOSAL.md), including historical Hard and Medium failures, 270,848-cycle monitoring reference, small deadline reserve and mandatory future alarms. A recommendation is not approval.
2. Owner acknowledgment/disposition of the recorded RG SP coverage and still-pending tests. Do not mark pending items passed on that basis.
3. Separate explicit authorization for a normal history-preserving merge of PR #5, identifying the actual final head and accepted develop base after re-fetch. No approval from PR #3/#4 carries over to this PR.

Before any separately authorized merge, Codex must reverify exact heads, no unexpected diff, mandatory development checks, the documented failed release gate, source/ROM identities and privacy/preservation. Unexpected source/check/security changes require investigation and a new review, not an automatic merge.

PR #5 stays **draft and unmerged** while these decisions are unresolved. Auto-merge stays off. No squash, rebase, force push, direct protected-branch update or formal release is authorized. No next mission, extra song, compression, audio engine or artwork work is authorized by this record.

## Independent release limitation

Strict ordinary-output remains failed at public CI 14/20, native public 15/20 and native private 22/30. Existing comparator/reference windows and failed cases remain intact. Digital PCM/FIFO success is not analog qualification. Even an accepted development exception and later merge would not authorize formal public release.

The [closeout review](M022_CLOSEOUT_REVIEW.md) distinguishes retained runtime evidence from fresh identity/security verification and records future resource constraints. Detailed private measurements, paths, signatures and captures remain in the owner-local Mission-022 reports, outside public Git history.
