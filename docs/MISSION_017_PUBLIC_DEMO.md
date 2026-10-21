# Mission 017 — public demo candidate

Status: playable development candidate; **release approval blocked by strict
ordinary emulator audio comparison**. Owner handheld acceptance is pending.
No formal release/tag or merge is authorized or performed.

## Source and scope

Baseline: `arcade75-handheld-chart-adaptation` at
`1e8fec75eca86dd99798ec31e52c53dca34974f1` (84 commits, complete history).
Remote refs/history were fetched and baseline ancestry checked. The separate
foundation audit branch adds no newer feature commit outside this baseline.
All work stays on `mission-017-public-demo`; protected branches remain intact.
The build manifest records the exact final source SHA, independently from the
later artifact-only download commit. Neither an old dirty ROM nor a historical
Cream build is used for public delivery.

## What changed

- Added original **Copper Circuit** score/synth/chart generator. The previous
  Arcade75 exercise was an engineering tone fixture, unsuitable as the intended
  musical demo. New arrangement has a melodic guitar part, bass, kick, snare,
  hi-hats and a contrasting section. Enjoyment is not established by unit tests.
- Added `public-demo` build profile. It does not generate/link the commercial
  original-demo song bank/chart, initialize Maxmod or expose the removed mode.
  Original files and other profiles are preserved. Converter `--layout-only`
  still emits the same checked ABI header without requiring a song chart.
- Small conditional menu labels identify the game, song and controls. Song →
  difficulty → play → results → replay/return is retained. Help opens the
  existing Easy input diagnostic; START+SELECT exits it.
- Added an optional short display title to the existing preparation recipe.
  Absent that argument, old recipes/behavior remain unchanged.
- Added immutable-source original-demo builder, independently regenerating
  player ZIP packager, checksum/extraction verifier and emulator probes.
  Public binaries are an explicit four-path delivery allowlist excluded from
  source exports; arbitrary ZIP/ROM/private files are still rejected.

Judgment windows, scoring formulas, combo thresholds, hold bonuses, input
mapping, PCM transport/mixer, sample clock, highway and DMA implementation have
not been redesigned. Other profiles retain original selection/navigation.

## Content and charts

75 seconds of music + existing two-second count-in. Source composition remains
78.75 seconds; cut/fade/guard handling comes from Arcade75. Separate 16384Hz
signed8 mono guitar/backing streams. Source synthesis is PCM16 before existing
preparation. No imported recording or external instrument samples.

| Difficulty | Heads | Genuine holds | Layout |
|---|---:|---:|---|
| Easy | 86 | 11 | LEFT/B/A |
| Medium | 171 | 11 | LEFT/RIGHT/B/A |
| Hard | 335 | 10 | LEFT/UP-or-DOWN/RIGHT/B/A |

Preparation reports zero impossible-direction conflicts/repairs, preserves
playable LEFT+B+A triples, and clips crossing final holds. All chart onsets
coincide with actual guitar events. See `DEMO_CONTENT_PROVENANCE.md` for rights.

## Verification and limits

`tests/check.sh` exercises all existing Python and ASan/UBSan programs plus
composition/package-boundary tests. Public emulator tests exercise all three
difficulties, complete hits/misses/mixed traces, repeated pauses, held START,
paused return, near-EOF pause, results/replay, startup readiness, Up/Down aliases
and framebuffer/highway observations. Exact delivered-ROM receipts and cycle
measurements are summarized in `M017_VERIFICATION.json`.

A broader exploratory reuse of legacy pause case8 on the new Easy chart fails
its zero-WrongInput expectation after releasing/repressing a hold during pause:
86 Perfect, 0 Miss, 1 WrongInput. The identical trace also fails in the preserved non-public profile with the
same new chart (same 86/0/1 result), so it is not introduced by public-profile
isolation. It is not treated as a passing acceptance test. Preserve this finding;
physical pause/repress acceptance needs particular attention. Host input-edge,
sustain-release and pause-policy assertions remain unchanged. No gameplay code
or assertion was weakened to force a pass.

The ordinary public matrix currently passes9/15 comparisons.
Strict ordinary output comparison fails in mixed play on stock mGBA0.10.1 and
unmodified stock0.10.5: at23.644470s one backing window has -1.007080ms residual
against the unchanged absolute<1ms criterion. Digital PCM/FIFO comparison is
separate and passes without word/sample corruption. A no-input run initially
has audible guitar until its first miss; the independent backing reference
therefore uses a real wrong A press during count-in. No emulator patch, timing
padding or tolerance relaxation is shipped. Audio-output gate stays blocked.
This measurement is not proof of an audible defect, nor proof of hardware sync.
Inherited full-length Cream comparison remains10/15; it was not fixed/retested
or included in this public content mission.

## Delivery and reproduction

Only original demo ROM, player ZIP, checksum list and delivery record go into
`public-demo-downloads/` on this mission branch. These are development playtest
files, not a formal release. The player needs no compilation. An immutable raw
GitHub URL at the artifact commit is downloaded back, hashed, ZIP-extracted and
emulated before delivery is claimed. The record distinguishes exact source and
artifact commits. No private music, source checkout, ELF or evidence recordings
are in the player ZIP.

Maintainer-only commands: `python3 tools/build_public_demo.py`, then
`tools/package_public_demo.py`, `tools/verify_demo_zip.py`,
`tools/test_public_demo.py`, `tools/check_demo_audio.py` with the produced build
and extracted ROM. Compiler container digest remains pinned. CI deliberately
fails the strict audio gate while retaining candidate evidence; a successful
build/gameplay receipt alone is not release clearance.

## Integration proposal

1. Review this branch's engine/profile diff and content permissions, keeping
   inherited history. Resolve the strict public output comparison and classify
   the exploratory pause/repress finding with a focused trace.
2. Owner follows `OWNER_M017_PLAYTEST.md` on real GBA for all difficulties,
   audio, D-pad diagonals, aliases, sustains, pause and replay.
3. Rerun exact-candidate checks after any fix; build/package/download anew.
4. Only after explicit owner acceptance, propose a normal non-squash merge PR
   of the accepted feature ancestry into `develop`, retain review evidence and
   keep download artifacts separate from build inputs. Owner approves the merge.
5. A stable release/tag, licensing choice and later features need separate
   approval. No default-branch or historical branch changes are needed now.
