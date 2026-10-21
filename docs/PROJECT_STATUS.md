# Current status — Mission 020

Development recommendation **APPROVED WITH DOCUMENTED LIMITATIONS**, audio
**AUDIO BOUNDED LIMITATION**, formal release **BLOCKED**. Engine changes NONE;
RC2 checksum and original Copper Circuit are preserved. Actual new CI passes
host/sanitizers,38 gameplay/graphics checks,15 digital transports and public soak;
strict ordinary output9/15 remains failed. The paired reference discrepancy is
localized to stock emulator PWM-slot updates; see M020_AUDIO_CONCLUSION.md.

New owner evidence: positive RC2 physical-GBA playability and subjective audio,
without inferred exhaustive difficulty/timing/stack/recording-fidelity coverage.
Private full Cream resource/testing numbers remain retained M019 evidence.
No graphics, merge, formal release or private upload. Baseline and resource
contract await owner/reviewer approval. Current report:
[M020](MISSION_020_FOUNDATION_CLOSEOUT.md). All following status is historical.

# Historical status — Mission 019

Foundation recommendation **BLOCKED**, audio **AUDIO BLOCKED**. No runtime
changes and no RC3: immutable Copper Circuit RC2 was independently rebuilt and
downloaded/tested again.209 Python,13 regular sanitizers,38 ROM checks and15/15
complete digital transports pass; ordinary output9/15 on stock0.10.1/0.10.5.
Public both versions, private full Cream Easy and original699 each exceeded an
emulated hour. Remote CI actually passes build/gameplay/digital/soak and fails
ordinary output. Owner RC2 all-difficulty acceptance, precise hardware margins
and source-license choice remain pending. No integration or graphics approval.

See [M019 report](MISSION_019_FOUNDATION_CERTIFICATION.md),
[verification](M019_VERIFICATION.json), [owner checklist](OWNER_M019_PLAYTEST.md).
Older status below is historical and does not override this decision.

# Current authoritative status — Mission018

**YELLOW**, playable public Copper Circuit; audio-output release gate unresolved.
Easy/Medium/Hard and song selection are implemented. RC1 received positive real
GBA playability feedback. RC2 requires separate owner testing. Extra pause-case8
WrongInput is explained as a real new B press, not a manufactured edge.
Medium pattern remains unchanged by owner choice.

Use MISSION_018_STABILIZATION_REPORT.md and M018_VERIFICATION.json for current
source, features, measurements, gates and next milestone. The current private
Windows launcher/build profiles are preserved; no private delivery is attempted.

The older mission notes below are historical evidence, not current feature status.

# Mission 017 current candidate

Original Copper Circuit public profile implemented on isolated mission branch.
Easy/Medium/Hard, scoring/sustains, reactive stems, pause/results/replay preserved.
Public profile excludes commercial original-demo content; legacy remains intact.
**Release gate blocked** by strict ordinary audio output comparison; exploratory
pause/repress finding and owner real-GBA acceptance remain open. No merge/tag.
See MISSION_017_PUBLIC_DEMO.md and M017_VERIFICATION.json for exact evidence.

# Current: post Medium/Hard stabilization candidate

## Arcade75 / handheld candidate — provisional

Offline versioned cut/adaptation recipes preserve normalized native inputs.
Cream75: Easy 110 heads/20 holds, Medium 186/38, Hard 235/39; 3/4 shifted heads
remove the Medium/Hard physical conflicts without deletion. No on-device chart
rewriting. The only runtime compatibility path is finite EOF settlement for
cut builds; full-length binaries must match stabilization outside revision.
See ARCADE75_VERIFICATION.md for measurements, test evidence and open gates.
Owner handheld acceptance, authorized private transfer and the inherited strict
full-length audio output issue remain open. No merge or stable release.


Frozen base3ed8be72f9652ada15c32ef4f77bbafddc2615bf; new isolated branch
stabilization-post-medium-hard. Startup readiness is explicit and immutable
bounds/fonts prepare at boot. Imported affine translation is reused exactly.
All37original regressions now pass unchanged; measured Hard peak249280perfect /
256448mixed stress is below280896cycles. Full report and evidence:
STABILIZATION_POST_MEDIUM_HARD.md and evidence/stabilization.

Open: native opposing-direction chords need owner policy approval; ordinary
mGBA output comparisons are10/15, while exact digital checks pass. No public
Cream upload, private download route, Windows GUI or real GBA acceptance is
claimed. No merge or stable release. Historical reports below remain scoped
records, not the current acceptance status.

# Current: Mission014 provisional pause/resume

Branch `mission-014-pause-resume` starts from Mission013 `664c83ea624c4cec1c81d4c83f066e8abf0d2d87`. Owner authorized provisional work; Mission013 handheld acceptance is unconfirmed. No develop/main merge. Imported-only pause, sample-preserving FIFO transport, resume input seeding, independent hold policy and static overlay are implemented. Original controls, charts, audio preparation, scoring and Windows build profiles are retained.

See MISSION_014_PAUSE_RESUME.md, evidence/mission014 and OWNER_M014_PLAYTEST.md for current tests and limits. Cream delivery is blocked: keep ROM local until an authorized private route exists. Public encrypted hosting is not used. Owner acceptance and stable baseline designation remain pending. Next sequence: complete private delivery and handheld checks; review/approve dependent integrations; only then plan Mission015.

Current gate: one strict ordinary mGBA0.10.1 backing comparison remains failed; exact FIFO/model continuity passes and an emulator-only lateness diagnostic passes. The correction is not shipped. No all-green audio QA or stable-release claim.

Historical Mission013 report follows.

# Mission013 — physical controls review candidate

Current work: mission-013-physical-controls, based on verified develop
56f6b7b243dfc710996336b99ac249806e666c85. Develop and main are not modified.
Imported Easy logical lanes0/1/2 now bind to LEFT/B/A through an allocation-free
physical-to-logical layer. Receptor labels/activation and all diagnostic prompts
agree with that order. Original699-note Demo keeps LEFT/RIGHT/A/B. Menu/results
A/Start and B/Select navigation remain unchanged.

Chart headers, note positions/times/sustains, PCM, timing windows, scoring rules,
reactive mixer and scanline DMA code remain unchanged. Six label map cells are
restored exactly on scene exit. Medium/Hard exist only as future design/test
fixtures; Up/Down aliases coalesce before logical edge detection. No new playable
difficulty, song, front end, pause, animation, codec or score feature is added.

Mission012 official public/private profiles and Windows launcher remain, with
M013 output identities/filenames. Public review uses original synthetic assets;
real Cream is built/tested locally and delivered by the previously authorized
AES-password workflow, never as a plaintext public song/ROM. No secret is stored
in source or public GitHub metadata. See the mission report/download receipt.

Owner acceptance of the new mapping is **pending**. Older Mission011 hardware
feedback is valuable but does not approve Mission013. Preserve emulator audio
compatibility, physical DMA margin/stack and inherited asset review gates.
Detailed tests, known results and owner checklist: MISSION_013_PHYSICAL_CONTROLS.md.
Architecture: PHYSICAL_INPUT.md. Windows local alternative: WINDOWS_PRIVATE_BUILD.md.

## Historical Mission012 status (superseded for the new mission branch)

# Project status — Mission012 build/release foundation

Current source: `mission-012-build-release-foundation`, descended only from
verified Mission011 `a6c0328b319ce1bf48e08371c2db770ac5a5008a`. The source-only
integration baseline is develop; historical main remains
`6c4e63460fab10733d8ff011045ee246e7201952` until owner approval. No download
branch, stable tag, branch deletion or default-branch change enters this source.

Both official profiles build the same committed engine in fresh isolated folders.
Public: M012 / SYNTH, original synthetic fixture plus inherited Original Demo and
INPUT / CHORD TEST. Private: M012 / CREAM / LOCAL, owner's local ZIP,395 Easy
heads/78 genuine sustains/reactive stems. Versioned outputs/manifests/checksums
and exact ROM/ELF guards reject stale pairs. Public packaging reads only audited
committed source and a verified synthetic-profile result. private/ and builds/
are ignored; tracked private payloads are rejected even if ignored by name.

Windows owner workflow: one-time WSL Ubuntu + Docker Desktop + Python/FFmpeg;
place ZIP in private/Cream.zip, double-click Build-Cream-ROM.bat. Linux pipeline
is tested; actual Windows double-click execution remains owner validation.
No automatic music download/upload and no new public Cream build in Mission012.

Owner-reported Mission011 acceptance: flicker gone in Windows/mGBA and on physical
GBA, good music and working score/holds/results/replay. This is scoped acceptance,
not comprehensive hardware certification. Two additional strict emulator audio
comparisons, measured physical DMA margins/stack, inherited asset provenance and
historical download rights remain release concerns. Engineering source saves and
development-baseline review need not wait for every stable-release question.

No gameplay/control/scoring/audio/projection changes beyond build labels and the
selector's reserved label sprites. Left/A/B stays current; Left/B/A and other
future mappings, white sustain feedback and audio compression/storage are backlog.

See MISSION_012_BUILD_FOUNDATION.md for performed checks, build identities/hashes,
negative leakage/stale tests, clean reproduction and remaining limitations.
WINDOWS_PRIVATE_BUILD.md is the owner guide; RELEASE_PROCESS.md and
BRANCH_INTEGRATION_REPORT.md describe review/approval/rollback.

## Historical Mission011 handoff (superseded by the status above)

### Mission011 status at its handoff

**Outcome B: graphics repair verified; audio emulator compatibility still blocks
stable promotion. Owner Windows/physical-GBA acceptance is pending.**

Source: `mission-011-audio-graphics-stability`, based on verified remote M010
`233112a072e5a0e90e5a766207761474130f75a6`. All previous fixes, playable sustains,
INPUT / CHORD TEST, framebuffer tests and build-pair verification are ancestors.
Main remains historical6c4e634; no repository consolidation or merge.

Imported Easy now publishes the unchanged affine/fog scanline tables into two
EWRAM buffers. DMA0/3 transfer them on time independently of the CPU audio IRQ;
foreground polls VBlank to rearm them even if Tonc drops that IRQ callback.
Buffers/channels are released before results/diagnostics/selection/Original Demo.
Original Maxmod DMA1/2 and CPU scanline path remain. BG0HUD/receptors, BG1mask/results,
BG2floor, note/hold sprites and the sample-clock/scoring/gate/hold classes remain.
No new difficulty, song library, codec, animation or score policy.

Full Cream graphics regression:0/16086frames flagged after repair versus
16085/16085before; zero late final affine/fog writes or rearm misses. Native
synthetic before/after60-frame sequences are available.108Python tests and8C++
sanitizer programs pass;10real full-song,17synthetic/error,5input and3original
699-note runs pass, plus fixed/silent compatibility and intentional corruptions.
395Perfect/78completed holds still earns15815. Digital FIFO words/samples exactly
match the independent source/gain model. All8ordinary primary real waveform
models pass unchanged limits. Two additional unmodified-emulator strict backing
comparisons still fail; an emulator-only timestamp correction resolves them with
identical event/clock traces. This is diagnostic evidence, not a shipped emulator
patch or a reason to hide failed checks. QA-010-004 stays open as a platform gate.

Public build ID: **M011 TIMING**; synthetic review ROM/source/visual sequences
linked from README. Real Cream ROM privately built/reproduced; direct private
transfer unavailable, verified [Windows two-command workflow](RELEASE_PROCESS.md).
No new public Cream music/chart/ROM. Original assets and historical public Cream
history retain separate permissions-review requirements.

Next: owner full-song/chord/replay playtest, qualified emulator/capture validation
and physical-GBA/stack measurements before stable integration or visual polish.
Full evidence: [MISSION_011_AUDIO_GRAPHICS](MISSION_011_AUDIO_GRAPHICS.md),
[KNOWN_ISSUES](KNOWN_ISSUES.md), [QA_TEST_PLAN](QA_TEST_PLAN.md).

## Historical Mission010 status (superseded)


Current source: **mission-010-stabilization**, based on final M009 `f589e62`.
All Mission001–009 source tips and hotfix `71f0152` are verified ancestors.
Main remains historical `6c4e634`; download branches are separate.

Architecture: original four-lane mode uses Maxmod and frame-clock judgments;
Imported Easy uses exact sample-clock snapshots, NoteJudgment, NoteScore,
fixed-storage Holds, reactive two-stem PCM/FIFO audio and the existing Mode7
highway plus bounded head/tail sprites. BG0 provides receptors/HUD, BG1depth mask
and results, BG2the affine floor. Offline Python imports chart/MIDI/ZIP, adapts
Easy and prepares PCM; the host C++ chart converter preserves the original ABI.
New mode3 is an isolated, silent13-case input diagnostic with its own26heads and
fiveholds, same existing judgments/scoring/hold controller, and explicit hardware
versus target versus outcome labels. It does not alter the real song or audio.

Established features remain: original699-note demo; imported395-head/78-sustain
real reference; taps/chords, Perfect/Good/Miss/WrongInput, sample-synchronized
reactive guitar, unchanged combo/scoring/250msbonuses, readable HUD/results,
replay/menu reset. No new difficulty/song library/codec/polish animations.

Current QA:98Python tests,8sanitizer executables;10real full-song gameplay runs,
17synthetic scenarios,5input scenarios,3original699-note runs, compatibility and
visual negatives. All gameplay/navigation scenarios pass. **One required reactive
waveform window fails (0.909975versus>0.94 at232.665039s)**; cause remains open,
so stable promotion is blocked. Owner/Windows/physical-hardware acceptance remains
pending. Scanline seams reproduced and narrowed to audio/HBlank contention;
not repaired by a broad rendering rewrite. See issue IDs and owner actions in
[KNOWN_ISSUES](KNOWN_ISSUES.md).

Public synthetic review ROM/source/instructions are linked from README and
versioned separately. Real M010 ROM built locally; private uploader unavailable;
verified clean local two-command workflow in [RELEASE_PROCESS](RELEASE_PROCESS.md).
Historical M006–009 public Cream binaries and original-demo assets need a separate
permissions review. No new M010 Cream data is publicly uploaded.

Next sequence: owner diagnostic/song playtest → resolve audio-analysis failure
and bounded scanline scheduling work → approved feedback polish → manual/hardware
acceptance and explicit source integration approval → consider future features.
No main merge, default-branch change, new stable reference, deletion or history
rewrite was performed. Full evidence: [MISSION_010_STABILIZATION](MISSION_010_STABILIZATION.md)
and [QA_TEST_PLAN](QA_TEST_PLAN.md).

## Historical Mission009 status (superseded)



Current branch: **mission-009-sustain-gameplay**, based on the verified owner-tested
hotfix `71f0152`. All Missions001–008 are ancestors; main remains unmerged.

Imported Easy now has a fixed-storage hold controller, genuine-duration tails,
integer quarter-second bonuses at the onset's captured multiplier, release grace,
and completed/early-release/bonus result statistics. Head scoring, combo rules,
FC/AP eligibility, controls, original demo, PCM audio/guitar gate are preserved.
The actual395-note/78-hold Cream chart and full recording are tested privately.
The public25-head fixture includes six holds, A+B overlap, and same-lane retirement.

[Sustain design and Windows build](SUSTAIN_GAMEPLAY.md) ·
[Mission009 test evidence and delivery](MISSION_009_RESULTS.md).

Cream delivery follows Mission009's current restriction: no public new Cream ROM
without redistribution confirmation. No private artifact transfer is connected;
the supported owner delivery is the verified local two-command build, using the
existing uploaded/source ZIP. The public synthetic ROM/review ZIP are downloadable.

Remaining features: further curated songs, imported Medium/Hard, song library,
star power and failure/health remain unimplemented. No such expansion is part of
this mission. Recommended next work is owner sustain playtesting and focused
polish of the existing horizon/sprite glitches before song-library expansion.
No manual Windows listening/playing or physical-GBA test is claimed here.

## Historical Mission008 status

Current hotfix: `mission-008-hotfix-hud-completion`. Larger Tonc system font,
explicit SCORE/COMBO/MULT HUD, visible build identifier, and bounded EOF
diagnostic. Composed-framebuffer tests supersede internal-only acceptance.
The owner-reported Windows softlock remains unconfirmed in Linux mGBA.
See [hotfix findings](MISSION_008_HOTFIX.md) and
[validation evidence](MISSION_008_HOTFIX_RESULTS.md).
Main remains unmerged. Owner authorized public Cream playtest ROM delivery.

The following describes the pre-hotfix Mission 008 baseline.

Base:verified Mission007 source `90aaed9f2d7624258ff3485d6a0dc7858c126929`,
containing the prior chain. New branch:mission-008-scoring-results. Main is not
merged. The original demo remains the unscored699-note four-lane flow.

Imported Easy adds a graphics/audio-independent fixed-storage scoring consumer,
chart-identity deduplication, combos and1x–4x multipliers. Perfect10/Good5base;
combo increments before award. Miss/WrongInput reset combo; max combo/highest
multiplier persist. Accuracy is successful notes/selected chart count in0.01%
units. FC/AP require completed nonempty sessions and zero wrong inputs.

HUD reuses existing8x8font on two BG0rows above incoming notes, preserving the
BG1 depth mask/highway. Results reuse BG1 after audio EOF and coherent judgment
completion. Replay and mode selection restore the existing audio/camera/layer
initialization. Audio faults and unresolved end states show interrupted/data
errors with partial statistics and no completion awards. Silent fallback has
an explicit last-note+late-window+frame endpoint. Titles come from bounded
sanitized metadata. New result states do not replace the judgment engine.

Mission007 PCM/mixing/gate code, source samples, timing windows and imported
contact geometry are unchanged. Scoring uses the same synchronous event order,
with no effect on guitar volume or playback position. Audio gating remains
Miss/WrongInput→zero, Perfect/Good→audible,64sample fade, no timeout.

Automated rules cover395Perfect=15230, all-Good=7615, threshold boundaries,
identities/chords/holds, event order,8192notes, saturation, accuracy/empty charts
and safe finalization. Real private/public/full-song and original regressions,
measurements and exact delivery status are recorded in MISSION_008_RESULTS.md.
No human/physical-hardware playtest of the new scoring/results is claimed.

Private Mission008 audio/chart/ROM/full traces remain ignored/local. Public
review content uses original synthetic imported audio/chart and tracked source.
A private attachment/export tool is unavailable; exact Windows reproduction and
workspace paths are documented without claiming a path is a download link.

Limits:no scoring/results retrofit for Original Demo, saves, sustain scoring,
new difficulties, codec/mixing changes or full menus. Next:owner HUD/results
feedback, physical hardware and focused design priorities for Mission009.

[Scoring rules and owner guide](SCORING_AND_RESULTS.md). Historical status follows.

---

# Project status — Mission 007

Started from verified Mission006 `4fa9e6f8b2558a129075c9815c8bb2ac68e6421b`,
including the earlier mission chain. New source branch:
`mission-007-reactive-guitar-audio`. No automatic merge to main.

Imported Easy now has independently prepared guitar/backing PCM, a64sample
anti-click fade and a two-state gate driven by unchanged NoteJudgment events.
Miss/WrongInput target zero; Perfect/Good restore full gain; no timeout. Event
emission order is preserved (misses, hits, WrongInput; last event wins).
Backing does not depend on gate state. GUITAR ON/MUTED debug text shows target.

New reactive_prepare.py decodes explicit candidate roles with the existing
FFmpeg workflow, zero-pads to matching lengths and applies common headroom before
separate signed8 quantization. Build validation binds both hashes and chart.
Default builds generate original two-track synthetic audio without external
recordings. Legacy fixed-mix and labeled silent fallback paths remain supported.

Playback uses one tiny software mixer and FIFO A, primed with32samples and
refilled16samples at a time. Both ROM streams share one index. Timer0 still
runs16384Hz; Timer1 refill IRQ and Timer2 plus epoch preserve an authoritative
output-request clock beyond64s. DMA1/2 are free while imported; original Maxmod
regains its original resources on mode return. No per-sample IRQ, heap allocation,
whole-song RAM copy or independent guitar clock is introduced.

All395private Cream Easy notes and the complete267.27s recording were exercised
with all-hit, no-input, hit/miss/hit and wrong/hit input scripts, plus mode replay.
Captured synthetic/private outputs are compared against independently generated
sample mixes, including backing-only and fade/recovery windows. Original699-note
regressions remain. See MISSION_007_RESULTS.md for final evidence and limitations.

Stem inspection establishes distinct, aligned recordings and bass-like rhythm
spectra; it cannot establish no guitar bleed or replace human audition. Selected
guitar samples reach exact digital zero; other guitar already in backing would
remain. Owner listening and physical hardware are outstanding.

Private Mission007 inputs, converted streams, traces and ROM stay ignored/local.
No working private artifact attachment tool is available in this session. The
public review bundle contains only original synthetic imported content, tracked
source and aggregate private findings. Windows reproduction and retrieval paths
are documented in REACTIVE_GUITAR_AUDIO.md. No new private download is claimed.

Limits:mono8bit quality, two-stream ROM cost, frame-polled event delivery, tiny
FIFO deadlines and emulator-only performance/sync validation. No scoring, health,
Medium/Hard imported mode, holds, reactive multistem library or full menus added.
Two-stream4minute audio costs7.5MiB; ten songs exceed32MiB substantially. Proposed
Mission008:human stem/feel checks, hardware validation, then compression budget.

[Owner guide and architecture](REACTIVE_GUITAR_AUDIO.md). Historical status follows.

---

# Project status — Mission 006

Base:Mission005 `f23cb6b4039fec93811b80f557a85518b2f626d1`; all five earlier
missions are present. Source branch `mission-006-audio-sync`; source and download
branches stay separate. Main remains original, with no automatic merges.

Imported Easy now plays16,384Hz signed8 mono PCM directly from ROM via FIFO A
and DMA1. Cascaded counters driven by the same sample timer provide a monotonic
timer-derived playback position. Notes and rendering share that snapshot.
This is not speaker feedback. Start/end, pre-roll, replay, disabled-resource fault
freeze and a labeled silent fallback are implemented. Original module playback,
699-note data, judgment windows, four controls and projection are preserved.

Host tools:audio_prepare.py decodes/mixes explicitly selected sources with FFmpeg;
prepare_song.py combines validated Easy chart + selected audio; build_audio.py
validates asset/hash/chart binding and builds deterministic synthetic defaults.
AUDIO_DIR and IMPORTED_HEADER opt in to private prepared content. The public
build includes an original25-note tone exercise with sound. No OPUS/runtime
codec or multi-song framework was added. Cartridge size is capped at32MiB.

A pixel/OAM check found Mission005 imported notes crossed the fret line about54ms
late despite correct judgments. Imported contact depth/lane centers are corrected
and tested at the actual line. Original four-lane math/assets remain unchanged.
The return chord no longer also confirms a selector item. Maxmod is reinitialized
through public mmInit using retained buffers, avoiding repeated allocation; its
clock epoch starts after initialization finishes.

Owner's actual WaveGroup cover package was converted privately, selecting guitar,
rhythm and song OPUS stems. Complete267.27s playback and395Easy notes passed in
mGBA, including visual line checks. Captured waveform matching at first/middle/
final notes shows sub-millisecond offsets and no resolved cumulative drift beyond
the method's timing variation. Three-lane controls remain Left/A/B. See
MISSION_006_RESULTS.md for exact measurements and tests. No human listening,
physical hardware/latency or subjective-quality claim is made.

Private ZIP, chart data, normalized/adapted files, audio and private ROM are not
committed/published. Public review bundle contains full tracked source, the
synthetic audio/chart ROM and aggregate test evidence only. Original asset
permission caveats remain; new synthetic audio contains no recorded samples.

Current limits:lo-fi8bit mono, one mixed recording, no reactive stem volumes,
no sustain/HOPO/tap mechanics, no scoring, imported Medium/Hard or full menus.
Foreground work is measured separately from full CPU utilization. Sample FIFO
identity/physical output is not directly observable by software; timer and sound
resource checks catch disabled playback, and emulator waveform validation supports
the nominal timing model. No calibration slider or in-game pause is implemented.

Ten4-minute songs exceed conventional32MiB at the chosen format. Ten3-minute
songs might fit narrowly; separate packs/lower rate or a qualified compressed
codec are practical future options, not implemented packaging. Recommended
Mission007:human/hardware calibration plus measured compressed-audio feasibility
and quality/CPU budget before expanding reactive mixing or song libraries.

Current Windows11 workflow and detailed storage/clock contract:
[GBA_AUDIO_PIPELINE.md](GBA_AUDIO_PIPELINE.md). Historical mission status follows.

---

# Project status — Mission 005

Started from Mission 004 `1487532557a1e98b1c99c6628e5d65c291268cd2`, containing
Missions001–004. New branch `mission-005-first-playable-import`. Main remains
original; no automatic merges. Historical status follows below.

New:explicit Easy adaptation, separate original/adapted JSON and generated header,
release/sustain classification, CPU-cycle runtime adapter reusing NoteJudgment,
three-lane Left/A/B Mode7 test, and a two-choice selector with clean mode restarts.
Imported mode is silent; original four-lane controls/content/formulas remain.
Default public build uses a clearly labeled original25-note synthetic fixture.
Host Python3 is now required for builds, including inside the pinned Docker image.

Real owner-supplied Cream/WaveGroup package was inspected privately:Easy395 notes,
lanes0/1/2, no chords,329 tempo points; Medium686/11 D-pad onset conflicts,
Hard878/20. Easy adaptation preserves395 notes:317 short releases,78 genuine
sustains at the documented160 tick threshold (PPQ480). INI cutoff0 retained,
explicit test classification overrides it without changing any native lengths.
Private395-note ROM passed all-hit/all-miss mGBA tests in silence. No actual chart,
normalized notes, audio or private chart-containing ROM is committed/published.

Architecture:tools/prepare_easy.py combines package import and adapt_chart.py;
prepare_runtime.py chooses the build's explicit local header or default synthetic.
ImportedRuntime uses CPU-cycle NoteJudgment units and two visibility cursors.
gameSession exposes mode-aware sprite count/appearance; main owns selector,
mode reset and audio start/stop. Three-lane floor derives from the original
palette/texture; switching back restores original assets. No per-frame allocation.
Original manager is now static rather than heap-allocated. NoteJudgment itself
and original NoteManager timing/math are unchanged.

Remaining:audio clock/decoding/format and alignment, true sustain/HOPO/tap rules,
imported Medium/Hard and renderer policies, scoring, menus beyond the test selector,
reactive mixing. No manual play/listening, hardware or human latency calibration
claimed. Real chart is playable as silent onsets only, not completed music playback.
See GBA_CHART_ADAPTATION.md for Windows 11 steps, timing limits and future audio
contract; MISSION_005_RESULTS.md records actual validation/build/review outcomes.

Recommended Mission 006:an authorized synthetic audio playback/sample-clock proof,
with measured memory/CPU/latency and beginning/middle/end alignment; retain legacy
demo and silence fallback. Establish actual cover-recording alignment and a
supported GBA audio format before considering reactive stems or new features.

---

# Project status — Mission 004

Mission 004 starts from tested Mission003 `135a55c2a0de50a4c68610f1aeb288924508bb54`
on `mission-004-universal-import`. Git ancestry confirms Missions001→002→003.
Live remote main remains original `6c4e63460fab10733d8ff011045ee246e7201952`;
none are merged. Source review branches and separate download branches remain
separate. No main merge is performed.

Implemented: bounded dependency-free MIDI Type0/1 PPQ parser, exact tempo timing,
four independent five-fret difficulties, native sustains/chords, marker separation,
raw unsupported event preservation, unified ZIP/folder/file inspection, INI metadata
and explicit offsets, audio/art discovery, clear validation/compatibility reports,
onset and sustained D-pad conflict checks. MIDI and chart share normalized spans
and timing/compatibility code. Existing chart-only command/header output remains.

Architecture: `midi_importer.py` parses/normalizes MIDI; `song_package.py` discovers
and validates packages/metadata; `import_song.py` writes reports/normalized JSON.
`chart_importer.py` continues to own shared math and compatibility. New synthetic
MIDI fixture/tests contain no third-party content. No GBA source, Makefile,
judgment windows, controls, art, chart or audio changed.

Actually playable: original699-note demo only, Left/Right/A/B, Mission002 judgment.
Imported data is prepared, not playable; Easy3/Hard5 fretboards do not exist.
No lane collapse, Expert relabeling, menus, scores, compression or reactive audio.
The named Cream/WaveGroup ZIP was not present; use the private command in
[SONG_PACKAGE_IMPORT.md](SONG_PACKAGE_IMPORT.md). No target-song analysis claimed.

Remaining limitations: SysEx open/tap effects, player HOPO/sustain cutoff and INI
mechanical overrides retained but not applied; Type2/SMPTE unsupported; no audio
decoding/codec validation or copyright verification; no imported absolute-time
runtime, recording calibration or lane adapter. Sustain counts preserve all MIDI
release lengths. Stem roles are filename conventions, not proof of isolation.
Human listening, hardware playability and latency remain untested. Music still
loops without resetting chart judgment. Original code/music/art permissions are
not newly established.

Next sequence: privately inspect targetpackage and review warnings; establish
exact audio-origin/sample-clock/pre-roll and explicit difficulty/marker policies;
prove a synthetic imported song through a separate opt-in adapter; qualify audio
memory/CPU and matching recording synchronization; then extend renderers and
approved difficulty selection. Reactive mixing follows validated audio playback.
See [MISSION_004_RESULTS.md](MISSION_004_RESULTS.md) for actual checks/review state.

The Mission003 status below is historical, including its then-unsupported list
and its recommendation for Mission 004. Current support is described above.

---

# Project status — Mission 003

## Branches and preserved baseline

Mission 003 starts at tested Mission 002 source commit
`533862124079a9dca1f84a6d88f54e40cde189cb`, on `mission-003-chart-importer`.
Mission 002 contains Mission 001: ancestry was verified with Git, not inferred
from branch names. All repository branches were listed/checked; download branches
contain binaries separately from source review branches.

| Branch | Role / state at Mission 003 start |
| --- | --- |
| `main`, original `work` checkout | Original `6c4e634`; no mission fixes merged |
| `mission-001-reproducible-build` | `47d340e`, working native/pinned builds and end-of-song safety |
| `mission-001-download` | Preserved original tested download |
| `mission-002-note-judgment` | `5338621`, reliable judgment, Left/Right/A/B, unchanged demo |
| `mission-002-download` | Preserved Mission 002 download |
| `mission-003-chart-importer` | New source work; based on Mission 002, not main |

No automatic merge into main is performed. The future target is now **Sunshine
of Your Love by Cream**, superseding the earlier long-term song/audio plan. This
mission prepares community charts only; it does not import a target song or
implement reactive audio.

## Current game — unchanged

The same 699-note Careless Whisper demo, module, art, perspective highway, camera,
button animations and **D-pad Left / D-pad Right / A / B** controls remain.
Mission 002's per-note Pending/Perfect/Good/Missed states, 25 ms Perfect,
50 ms early/85 ms late Good, fresh-press input, chord rules, hit/miss counters,
WRONG indicator and gameplay event interface are preserved. No gameplay source,
converter, Makefile, toolchain image, chart, graphics or music changed.

A clean ROM build has exactly the Mission 002 checksum. New imports are not
wired into its legacy clock or compiled by the default Makefile. No new three/
five-lane renderer, difficulty menu, song selection, audio changes or scoring was
added. The owner can continue using the known working game while data work proceeds.

## New importer architecture

| Component | Responsibility |
| --- | --- |
| `tools/chart_importer.py` | Parse/validate metadata/events, exact cumulative tempo map, normalized data, compatibility analysis and prepared header |
| `tools/import_chart.py` | One-command file/folder workflow, readable/JSON reports, managed outputs and error exit status |
| `imports/incoming/` | User-supplied authorized charts; ignored by Git |
| `imports/output/` | Per-chart reports, normalized JSON and C++17 tables; ignored by Git |
| `tests/fixtures/charts/` | Original synthetic charts with independently calculated expected timestamps; no audio |
| `tests/test_chart_importer.py` | Math, parsing, validation, CLI/determinism/failure cases and host/GBA header compilation |
| `tests/check.sh` | Existing judgment/sanitizer/699-note tests plus new importer suite |

See `CHART_IMPORT_GUIDE.md` for beginner commands and compatibility warnings.
See `SONG_DATA_ARCHITECTURE.md` for the old-converter audit, new schema, exact
timing model, offset convention and integration boundaries.

## Supported versus prepared versus playable

- Metadata, resolution, all BPM changes, boundary timing, signed decimal Offset,
  meter metadata, source-order chords and tempo-aware sustain durations are parsed.
- Easy/Medium/Hard/Expert Single tracks stay independent. Logical frets 0–4 and
  open notes are retained; HOPO/tap markers are separate records, not fake notes.
- Phrases, text, anchors and unknown instrument rows are retained with explicit
  warnings. Not every retained feature has gameplay semantics or header tables.
- Duplicate/unsorted/malformed/overflowing supported events fail clearly rather
  than being silently fixed or dropped. Unknown note types are errors.
- Future layout reports identify Easy 3, Medium 4 and Hard 5 button arrangements,
  fret-count mismatches, opposing D-pad chords and diagonals. Lanes are not collapsed.
- Successful import means **prepared, not playable**. Even four-lane note-shape
  compatibility does not enable the new clock, recording or audio adapter.

## Validation and limitations

`MISSION_003_RESULTS.md` records actual test counts, math examples, build logs,
checksum identity and mGBA results. Generated headers compile on both desktop C++
and devkitARM ARM7TDMI/Thumb. The original 699-note chart is valid in the new
pipeline, while all live note timestamps remain exactly unchanged.

No authorized Sunshine of Your Love chart was supplied; none was downloaded,
fabricated or substituted. No Cream audio or official Guitar Hero assets were
obtained. Tests use original synthetic fixtures and the existing checked-in demo.
A GHIII cover chart must not be assumed to match Cream's original performance.

Remaining data/runtime work:

- An explicit absolute-time gameplay adapter, audio-origin/pre-roll policy,
  calibration and measured beginning/middle/end alignment.
- Approved three/five-lane renderers and difficulty selection; Expert is not
  automatically renamed Hard, and five-lane community charts are not reduced.
- `song.ini` metadata/delay overrides, MIDI and other instruments are not applied.
- Anchors are editor metadata; contradictory anchor/tempo information is warned
  about, not used to invent a new clock.
- HOPO/tap/open/sustain/phrase gameplay is not implemented. D-pad checks cover
  simultaneous onsets; held-sustain overlaps and ergonomics need later validation.
- Audio licensing, recording/version matching and preparation need authorization;
  no compression, muting or guitar-volume features have been implemented.
- Music still loops without resetting demo notes. Physical hardware testing,
  manual listening/play, latency measurement and multi-hour runs remain outstanding.
- Baseline code/music/art redistribution permissions are not newly established.
  Source credits remain; ignored input/output folders avoid accidental community
  chart redistribution.

## Recommended Mission 004 sequence

1. Obtain a properly authorized chart and matching recording, or continue with
   synthetic data until those are available. Keep source/author/license/version.
2. Review the import report and required lane layouts without silently remapping.
3. Design and test the absolute-time game/audio adapter, retaining a verified
   legacy demo path or measuring any proposed recalibration explicitly.
4. Implement only the approved difficulty renderer/integration next. Do not add
   reactive audio penalties or new assets just because import preparation passed.
5. Later, existing judgment events can drive an authorized reactive-audio task.

PR creation previously failed with GitHub API Forbidden while Git pushes worked.
The final handoff reports the new attempt separately; a source branch or compare
link must not be described as an opened pull request. Download branches remain
separate and must not be merged into main.

## Mission 003 review handoff

Implementation commit `747c3f7` was pushed to `mission-003-chart-importer`.
A draft PR against `mission-002-note-judgment` was attempted, but GitHub returned
`Post https://api.github.com/graphql: Forbidden`. No PR was opened by that command;
main and prior download branches were not merged or changed. Git push works, so
no new secret or login was requested.

Review comparison:
https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-002-note-judgment...mission-003-chart-importer

Suggested title: **Mission 003: import community charts with exact tempo timing**.
The prepared description is `PULL_REQUEST.md` in the bundle. Someone with GitHub
access can choose **Create pull request**, paste it, and create a draft without
merging. The separate `mission-003-download` branch supplies the ROM and standalone
import tools/examples; that download branch must not be merged into main.
