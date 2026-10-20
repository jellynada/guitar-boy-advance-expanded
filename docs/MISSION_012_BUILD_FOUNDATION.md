# Mission012 — source consolidation and reproducible local builds

## Scope and acceptance

This mission changes release/build tooling and labels only. No mapping, judgment,
score, sustain, audio playback, projection, codec, art or difficulty feature was
added. The title owns24 selector sprites instead of16 so the complete private
identity is visible; normal gameplay OAM allocations remain unchanged.

Owner reports Mission011 works fantastically on actual GBA/compatible flash
cartridge: flicker gone, music good, score/holds/results/replay working. They also
report successful Windows/mGBA flicker/audio playtest. This is owner-reported
acceptance of those functions, not an agent-performed hardware test, exhaustive
certification or approval for a stable public release. New Windows double-click
launcher execution remains unperformed on this Linux cloud machine.

## Verified source and branch audit

Started from fetched `mission-011-audio-graphics-stability` at full commit
`a6c0328b319ce1bf48e08371c2db770ac5a5008a`. All source mission001–011 heads are
verified ancestors, including HUD/results71f0152, holds85c637d, diagnostic1d92104
and scanline repaird0b20dc (full hashes in BRANCH_INTEGRATION_REPORT). Main is still
`6c4e63460fab10733d8ff011045ee246e7201952`, the immutable original rollback point.
No develop existed at initial audit. Mission012 source branch is
`mission-012-build-release-foundation`; develop is created from its completed
source history only after checking the remote still has no develop. No download
branch enters that ancestry. No main merge, default-branch change, deletion,
force-push, history rewrite or stable tag is authorized/performed.

Branch policy, full inventory, proposed main file list and rollback are in
BRANCH_INTEGRATION_REPORT.md and MAIN_INTEGRATION_FILES.txt. Recommend this as the
reviewed development baseline; main integration still requires explicit owner
approval. External stable-release gates do not prevent safe source saves.

## Profiles and source isolation

`python3 tools/build_profile.py public` exports only clean committed/audited
public source into a fresh folder, clears inherited make overrides and forces the
original synthetic fixture. Identity **M012 / SYNTH**,25 heads/6 sustains, imported
reactive synthetic audio plus unchanged inherited Original Demo and diagnostic.
No private ZIP or FFmpeg is required for this profile.

`python3 tools/build_profile.py cream` uses the exact same source revision with
`private/Cream.zip`, explicit guitar=guitar and backing=rhythm+song roles, freshly
prepares off-device data, and requires395 heads/78 genuine sustains/full reactive
recording. Identity **M012 / CREAM / LOCAL**. No fallback, download or upload.
Generated chart/audio binding and stream hashes are validated by the existing
build plus the profile driver. Preparation bytes exactly match accepted M011.

The pinned compiler image is unchanged:
`devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5`.
ARM GCC16.1.0, this host FFmpeg7.1.5. Different FFmpeg versions may change bytes;
recorded tool/asset hashes define reproducibility, not a universal byte guarantee.
Both profiles were built independently from clean source exports without Git
metadata. SOURCE_MANIFEST.json verifies every source file in the ZIP workflow.

## One-click Windows workflow

One-time WSL Ubuntu, Docker Desktop Ubuntu integration and Python3/FFmpeg setup
is in WINDOWS_PRIVATE_BUILD.md. Owner places the existing ZIP in private/Cream.zip
and double-clicks Build-Cream-ROM.bat. A small PowerShell bridge checks WSL,
translates paths without embedding them in shell code, invokes the same Python
pipeline and preserves failure exit status. Source paths with spaces are supported
by argument-list execution and fixed container working paths. Native Windows
batch/PowerShell execution has **not** been performed here; Linux engine/export/
Docker stages are real verified executions, not mocked success claims.

On success the launcher prints the exact versioned builds/private path, profile,
full source commit and ROM SHA-256, then mGBA/flash-cartridge instructions.
The adjacent manifest identifies source tree, ZIP/chart/audio hashes, stems,
compiler image/version, FFmpeg, ROM size and checksum. Public manifests omit
private package identity. Every attempt invalidates LATEST.txt first; only fresh
successful outputs select a new folder. Old dated files remain explicitly old.
ROM/ELF must postdate compile start and inputs, match linked program/data/count,
contain the correct profile/source marker and pass runtime validation. Inputs
are rehashed after compilation. Dirty/incomplete/modified source exports stop.

## Asset and packaging audit

No private music/PCM/ZIP/chart/header/ROM is tracked on source. Existing historical
Windows converter executables, art, original chart/module and old screenshots are
retained; Linux uses the converter source. Their provenance needs separate review.
The new private/ and builds/ trees, root Cream.zip and generated imports remain
ignored. Source staging uses explicit paths, never broad force-add. A tracked
private payload is rejected even if an ignore pattern would match it.

Public packaging requires a matching verified public build, independently
regenerates its synthetic assets, then allowlists committed source, manifest and
that ROM. It never recursively copies a working/build directory. Forbidden source
paths include private/builds/downloads/generated imports and ROM/ELF/recording/
PCM/prepared headers/audio metadata. Symlinks are rejected. Source archives carry
file checksums and are independently usable by the Windows launcher.

Historical owner-requested public Cream branches, including mission-011-cream-download,
remain untouched. Ignoring new files cannot remove their history or settle rights.
Mission012 uploads no new Cream assets/ROM. There is no supported private attachment
service here; the local Windows workflow replaces misleading cloud download paths.

## Actual tests and results

The complete engine-regression revision is `5de174ac3bb14ec321a24d76aa7b30816cd0afa0`.
Subsequent source changes are documentation/test logging and Windows path/checksum handoff only. No further engine changes. Final deliverable
profiles are rebuilt from the same final committed revision; their manifests give
the exact full source/hash, avoiding self-referential commit hashes in this file.
Final delivery verification compares game bytes outside the embedded revision
marker and repeats downloaded-ROM smoke checks. See the download receipt.

Host suite: **127 Python tests** (108 existing+19 new) and **8 ASan/UBSan C++
programs**, all pass. New negatives include tracked private files despite ignore,
unsafe paths/symlinks, modified/incomplete source export, dirty source, absent
private ZIP, an actually executed exit37 Docker command, stale ROM/runtime,
incomplete inventory and wrong embedded revision. Expected failures stay separate
from ordinary emulator compatibility failures.

Clean exported profiles compiled successfully with matching source and linked
ELF/count checks. Visible label composition checked real OAM and framebuffer ink:
public516pixels, private828pixels. Merely storing the label string cannot pass.

Behavior: **17 synthetic scenarios**, **10 full395-note Cream scenarios**, **5 input
scenarios on each profile**, **3 Original Demo scenarios of36000frames** all pass.
Perfect/Good/Miss/Wrong timing, mute/recovery, combo/score, early release, results,
EOF, replay and resource teardown remain covered.395Perfect/78completed holds:
585bonus and15815total. Early-release:78released,212bonus,15442total,395combo.
Independent sustain interval reconstruction passes both (same M011 behavior).

Full Cream frame oracle:16400emulated frames,16086eligible frames,
**zero displaced pixels**,184676819visible floor pixels,11peak tail sprites,
zero underruns and zero scanline rearm misses. Foreground max161408cycles,
mean107203.515; refill max1408cycles/mean1383.682 for this hold-perfect run.
The M011 minimum13cycle DMA final-write margin is emulator evidence; actual
hardware margin and stack high-water are still unmeasured.

Four ordinary synthetic and all eight primary real waveform models pass unchanged
>0.94 correlation / <1ms residual limits. The same two **additional** ordinary
mGBA0.10.1 common-backing comparisons fail unchanged >0.999:

| Scenario | Runtime | Correlation | Result |
| --- | --- | --- | --- |
| scoring |135.874938965s|0.997610305697|FAIL, retained |
| wrong |128.039001465s|0.998855768776|FAIL, retained |
| reactive common-backing | full checked windows | meets threshold | PASS |

Real raw captures and judgment events for reactive, scoring, wrong, perfect holds
and early release are **byte-for-byte identical to M011**; chart/guitar/backing
hashes also match. Thus this restructuring adds no observed audio/timing/gameplay
regression in those cases. M011 established zero digital corruption and an emulator
late-event cause; no corrected emulator is used or shipped by Mission012. Owner's
good listening report does not erase the strict failures or loosen thresholds.

## Leakage, stale-output and error exercises

A unique fake canary was placed in private/ before a repeat clean public build.
ROM remained byte-identical. No canary appeared in any decompressed public ZIP
member or ROM. An actual checkout private canary was ignored and absent from dry
run staging; no tracked private/build/download path exists on source. Unit tests
also force-track a fake private asset and require rejection.

The actual private build was passed to public packaging: rejected. A copied
public runtime header was corrupted: rejected. An actual invalid ZIP with no
chart/audio caused preparation failure, removed a prior latest pointer, delivered
no ROM and preserved an explicitly old file. Missing-input/failed-command tests
likewise cannot present stale output as success. Logs show earlier integration
failures (compiler not on container PATH, then linker discarding unused identity)
were diagnosed and fixed; those failed attempts never delivered successful files.

Aggregate reports and public-only logs are in docs/evidence/mission012. No real
sample streams, real note-event tables or private chart exports are in that folder.
Detailed real captures remain outside source. Test summaries follow:

| Scenario | Result | Selected runtime observations |
| --- | --- | --- |
| public-sustain-perfect | PASS | SCORE: score512 combo25 maximum25 highest3 accuracy10000 FC1 AP1 session1; HOLDS: total6 completed5 released1 missed0 bonus42; IRQ: refills15189 max1408 mean1361.6 cycles, underruns0 gate1 gain256 |
| public-sustain-release | PASS | SCORE: score494 combo25 maximum25 highest3 accuracy10000 FC1 AP1 session1; HOLDS: total6 completed0 released6 missed0 bonus24; IRQ: refills15189 max1408 mean1361.9 cycles, underruns0 gate1 gain256 |
| public-perfect | PASS | SCORE: score470 combo25 maximum25 highest3 accuracy10000 FC1 AP1 session1; HOLDS: total6 completed0 released6 missed0 bonus0; IRQ: refills15189 max1408 mean1362.4 cycles, underruns0 gate1 gain256 |
| public-good | PASS | SCORE: score235 combo25 maximum25 highest3 accuracy10000 FC1 AP0 session1; HOLDS: total6 completed0 released6 missed0 bonus0; IRQ: refills15189 max1408 mean1362.0 cycles, underruns0 gate1 gain256 |
| public-miss | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills15189 max1472 mean1388.7 cycles, underruns0 gate0 gain0 |
| public-scoring | PASS | SCORE: score160 combo2 maximum3 highest1 accuracy7600 FC0 AP0 session1; HOLDS: total6 completed0 released4 missed2 bonus0; IRQ: refills15189 max1472 mean1367.1 cycles, underruns0 gate1 gain256 |
| public-wrong | PASS | SCORE: score250 combo0 maximum2 highest1 accuracy10000 FC0 AP0 session1; HOLDS: total6 completed0 released6 missed0 bonus0; IRQ: refills15189 max1472 mean1386.6 cycles, underruns0 gate0 gain0 |
| public-reactive | PASS | SCORE: score170 combo2 maximum2 highest1 accuracy6800 FC0 AP0 session1; HOLDS: total6 completed0 released4 missed2 bonus0; IRQ: refills15189 max1472 mean1369.6 cycles, underruns0 gate1 gain256 |
| public-returnmenu | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills15189 max1472 mean1388.7 cycles, underruns0 gate0 gain0 |
| public-returnselect | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills15189 max1472 mean1388.7 cycles, underruns0 gate0 gain0 |
| public-replaystart | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills15189 max1472 mean1388.7 cycles, underruns0 gate0 gain0 |
| public-fault_dma | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1383.2 cycles, underruns0 gate0 gain0 |
| public-fault_sound | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1383.2 cycles, underruns0 gate0 gain0 |
| public-fault_irq | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1383.2 cycles, underruns0 gate0 gain0 |
| public-fault_underrun | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1383.2 cycles, underruns1 gate0 gain0 |
| public-fault_timer | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1383.2 cycles, underruns0 gate0 gain0 |
| public-inconsistent | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session3; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1383.2 cycles, underruns0 gate1 gain256 |
| cream-sustain-perfect | PASS | SCORE: score15815 combo395 maximum395 highest4 accuracy10000 FC1 AP1 session1; HOLDS: total78 completed78 released0 missed0 bonus585; IRQ: refills276246 max1408 mean1383.7 cycles, underruns0 gate1 gain256 |
| cream-sustain-release | PASS | SCORE: score15442 combo395 maximum395 highest4 accuracy10000 FC1 AP1 session1; HOLDS: total78 completed0 released78 missed0 bonus212; IRQ: refills276246 max1408 mean1383.7 cycles, underruns0 gate1 gain256 |
| cream-perfect | PASS | SCORE: score15230 combo395 maximum395 highest4 accuracy10000 FC1 AP1 session1; HOLDS: total78 completed0 released78 missed0 bonus0; IRQ: refills276246 max1408 mean1383.7 cycles, underruns0 gate1 gain256 |
| cream-good | PASS | SCORE: score7615 combo395 maximum395 highest4 accuracy10000 FC1 AP0 session1; HOLDS: total78 completed0 released78 missed0 bonus0; IRQ: refills276246 max1408 mean1383.7 cycles, underruns0 gate1 gain256 |
| cream-miss | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total78 completed0 released0 missed78 bonus0; IRQ: refills276246 max1472 mean1411.7 cycles, underruns0 gate0 gain0 |
| cream-scoring | PASS | SCORE: score2465 combo0 maximum3 highest1 accuracy7494 FC0 AP0 session1; HOLDS: total78 completed0 released61 missed17 bonus0; IRQ: refills276246 max1472 mean1389.9 cycles, underruns0 gate0 gain0 |
| cream-wrong | PASS | SCORE: score3850 combo0 maximum2 highest1 accuracy10000 FC0 AP0 session1; HOLDS: total78 completed0 released78 missed0 bonus0; IRQ: refills276246 max1472 mean1404.2 cycles, underruns0 gate0 gain0 |
| cream-reactive | PASS | SCORE: score2630 combo0 maximum2 highest1 accuracy6658 FC0 AP0 session1; HOLDS: total78 completed0 released49 missed29 bonus0; IRQ: refills276246 max1472 mean1392.5 cycles, underruns0 gate0 gain0 |
| cream-returnmenu | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total78 completed0 released0 missed78 bonus0; IRQ: refills276246 max1472 mean1411.7 cycles, underruns0 gate0 gain0 |
| cream-returnselect | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total78 completed0 released0 missed78 bonus0; IRQ: refills276246 max1472 mean1411.7 cycles, underruns0 gate0 gain0 |
| public-input-perfect | PASS | PASS: diagnostic perfect; 87 composed labels, 4 chord observations, 267 valid holds, 19 new presses; retry/exit/imported/original audio checked |
| public-input-partial | PASS | PASS: diagnostic partial; 87 composed labels, 3 chord observations, 267 valid holds, 19 new presses; retry/exit/imported/original audio checked |
| public-input-wrong | PASS | PASS: diagnostic wrong; 87 composed labels, 4 chord observations, 267 valid holds, 19 new presses; retry/exit/imported/original audio checked |
| public-input-early | PASS | PASS: diagnostic early; 87 composed labels, 4 chord observations, 198 valid holds, 19 new presses; retry/exit/imported/original audio checked |
| public-input-stuck | PASS | PASS: diagnostic stuck; 87 composed labels, 4 chord observations, 267 valid holds, 17 new presses; retry/exit/imported/original audio checked |
| cream-input-perfect | PASS | PASS: diagnostic perfect; 87 composed labels, 4 chord observations, 267 valid holds, 19 new presses; retry/exit/imported/original audio checked |
| cream-input-partial | PASS | PASS: diagnostic partial; 87 composed labels, 3 chord observations, 267 valid holds, 19 new presses; retry/exit/imported/original audio checked |
| cream-input-wrong | PASS | PASS: diagnostic wrong; 87 composed labels, 4 chord observations, 267 valid holds, 19 new presses; retry/exit/imported/original audio checked |
| cream-input-early | PASS | PASS: diagnostic early; 87 composed labels, 4 chord observations, 198 valid holds, 19 new presses; retry/exit/imported/original audio checked |
| cream-input-stuck | PASS | PASS: diagnostic stuck; 87 composed labels, 4 chord observations, 267 valid holds, 17 new presses; retry/exit/imported/original audio checked |

## Remaining gates and next work

Owner needs to validate the actual Windows launcher and local M012 ROM on mGBA/
flash cartridge. Preserve the two strict emulator comparisons, physical margins/
stack work, keyboard rollover, physical button-order issue and inherited-asset/
historical-download permissions review. This is a development foundation, not an
owner-approved stable public release.

Approved future directions are recorded without implementation in DESIGN_BACKLOG:
Easy Left/B/A, Medium Left/Right/B/A, Hard Up-or-Down as one alternative lane with
explicit sustain-switch/conflict rules; active white/pulsing sustain feedback;
and audio/storage feasibility because roughly9MB/song cannot fit ten songs in32MiB.
Next: owner one-click acceptance, then a tightly scoped physical-order control
mission and targeted compatibility/hardware measurements. Do not start features
or codecs as part of this build mission.
