# Mission 016: general song preparation/build foundation

Starting source: `7fee39d93693d4437da188a0b5d9e89e8e9081d2`, new branch
`mission-016-song-pipeline`. Mission015 artifact retrieval and draft PR#2 are
owner-reported complete: https://github.com/jellynada/guitar-boy-advance-expanded/pull/2.
No repeat of its authentication investigation or unchanged ROM builds is needed.

## Assessment and controlled plan

The bounded package/chart/MIDI readers, Easy adapter, host FFmpeg preparation,
pinned compiler and successful-build inventory are reusable. The official driver
has only a fixed public fixture and Cream regression profile; its Cream395-head,
78-sustain and three-stem checks are appropriate fixture assertions, not generic
song acceptance. Existing adapted-v1 descriptive controls predate LEFT/B/A.
Keep those fixtures byte-for-byte stable and introduce an independent versioned
prepared-song contract that describes the actual runtime controls.

Add a `song` build profile, private by default even for caller-supplied synthetic
content. It consumes a verified prepared directory, never changes source code,
and records the song manifest hash alongside source/toolchain/ROM identities.
Use explicit relative audio paths (fixed mix or guitar plus backing), not
Cream stem names. Bind normalized source, adaptation, chart header and audio
with hashes; validate onset and genuine-sustain end alignment. Reject malformed,
unsupported, ambiguous or incompatible data instead of repairing it.

First prove two generated original packages: constant-tempo chart/fixed mix and
tempo-changing MIDI/reactive audio, with different titles, counts, lengths and
sustains. Generate WAV audio locally; do not commit binaries/recordings. Reuse
existing actual-key emulator tests with metadata-derived song counts/duration.
No runtime, judgment, audio clock, mixer, renderer or gameplay changes are needed.
Keep public packaging restricted to the original public fixture. No publication,
merge or stable release is part of this mission.
