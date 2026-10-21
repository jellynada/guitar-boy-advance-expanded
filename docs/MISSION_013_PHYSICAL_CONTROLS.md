# Mission013 — physical controls and input abstraction

## Source and scope

Starting branch fetched and verified: develop at
`56f6b7b243dfc710996336b99ac249806e666c85`. All Missions001–012 are ancestors,
including M008 hotfix71f0152, M009 sustains85c637d, M010 diagnostic1d92104,
M011 DMA repaird0b20dc and M012 profiles/Windows launcher. Historical main remains
`6c4e63460fab10733d8ff011045ee246e7201952`. New source branch is
`mission-013-physical-controls`; no merge into develop/main, tag, default-branch
change, force-push, history deletion or download-branch merge is performed.

Engine regression revision: `61c49d66f2f09a96161ad0eb3bee2a2f8da50cbe`.
Final source includes documentation/evidence only afterward. Final build manifests
and download receipts identify the exact full delivery revision and hashes;
the final ROM bytes are compared outside the40byte revision marker before smoke
checks. Both public/private profiles compile that same final source revision.

Only imported Easy physical bindings change: logical0/1/2 = **LEFT/B/A**.
Original699-note controls stay LEFT/RIGHT/A/B. No chart note/header, lane position,
color, music, sample rate, clock, timing window, score/hold rule or projection/DMA
code is changed. No pause, front end, new difficulty, song, compression, visual
polish or score feature is added. M013 labels identify the new files; launcher
and official profile mechanics are preserved with M013 filenames.

## Input and labels

PhysicalInput is a fixed-size constexpr bitmask mapping/edge layer. No dynamic
allocation, hardware reads, clocks or gameplay policy. Production bindings and
Easy labels live in gameControls.hpp; Original constants retain their old values.
Existing gameplay judgments already derive presses from logical held states and
remain unchanged. Diagnostic edge calculation uses the shared helper.

Receptor activation and displayed LEFT/B/A labels agree with gameplay. Labels use
existing font tiles below the receptors, stamped once during initialization.
Exactly six BG0 map cells are saved/restored; no broad black row or road mask is
introduced. The physical emulator check proves the original cells return exactly
and Original's four receptor responses remain intact.

Diagnostic prompts/results/mask labels now use B for logical1 and A for logical2:
LEFT+B, LEFT+A, B+A, LEFT+B+A, hold LEFT/tap B, release B/keep A, rapid B and
LEFT B A sequence. Menu/results A/Start replay and B/Select return are unchanged.
See PHYSICAL_INPUT.md for the API and historical chart annotation distinction.

Medium LEFT/RIGHT/B/A and Hard LEFT/(UP or DOWN)/RIGHT/B/A are **test-only design
fixtures**, not production tables or playable modes. Aliases coalesce before
edge detection: UP→both→DOWN or direct UP→DOWN never creates a second logical
press/release while an alias remains held. Only both released ends the lane.
Future chart/conflicting-D-pad/sustain-switch design remains separately scoped.

## Actual build/data validation

Both official profiles build successfully from separate clean exported sources
using the unchanged pinned devkitARM Docker image/GCC16.1.0 and host FFmpeg7.1.5.
The private owner ZIP is present and actually converted; no substitute audio is
used. Both complete prepared asset summaries match Mission012 exactly, including
chart headers/PCM hashes (docs/evidence/mission013/asset-identity.json). Cream has
395 Easy heads,78 genuine sustains, full267.271912s source recording and explicit
guitar plus rhythm/song backing stems. Public remains25-head/6-sustain synthetic.

Source importer/adapter and note records are untouched. Historical adapted JSON
physical annotations are retained as legacy metadata, not runtime input authority.
The new manifest explicitly records physical_controls=[LEFT,B,A]. Local profiles
still reject mismatched chart/audio, dirty/incomplete source, failed compilation,
stale ROM/ELF and wrong profile; all19 M012 build/release tests continue passing.
Windows double-click execution remains unperformed in this Linux cloud; the
actual clean export/Python/FFmpeg/pinned-Docker chain is exercised. Existing
Build-Cream-ROM.bat/PowerShell workflow remains available without code editing.

## Automated results

**127 Python tests and9 ASan/UBSan C++ programs pass.** The new physical test
independently enumerates1024 raw hardware masks,8192 logical edge combinations,
all Easy chords, staggered overlaps, rapid B taps while LEFT stays held, repeated
held-state no-edge behavior, held-at-reset and Original/future mappings.

The emulator receives actual hardware key bits, never input/judgment RAM writes.
Physical/receptor checks pass on both profiles: actual font pixels LEFT/B/A,
8 held combinations, release-B/keep-A, exact BG0 restoration and Original receptor
mapping. Diagnostic checks pass perfect/partial/wrong/early/stuck on both profiles,
including all13 actual visible prompts/results, raw masks, no repeated presses,
independent simultaneous holds and scene/retry/Original sound resets.

Behavior matrix:17 synthetic scenarios (including six deliberate fault cases),
10 full16400frame Cream scenarios,10 input runs,3 Original36000frame runs all pass.
395Perfect/full holds still yields **15815**,395combo,585hold bonus,78completed.
Early release remains15442total,212bonus,78early with combo preserved. Both
independent interval-count hold oracles pass. Tap-only Perfect15230 and Good7615
remain unchanged. Results/statistics/awards, EOF, A/Start replay, B/Select return,
fresh audio and repeated Original/Imported transitions pass composed-frame checks.

Full Cream graphics:16400frames,16086eligible frames, **zero displaced pixels**,
182522585observed floor-colored pixels,11peak tail strips, zero tail overflow,
zero underruns. Rearm misses0, latest VCOUNT162, maximum2048CPUcycles. Frame-work
maximum161408cycles/mean107213.011 and hold-perfect refill maximum1408/mean1341.597.
Existing labels account for expected composition changes; there is no claim of
pixel identity for the newly labeled frames. The M011 final-write13cycle margin
remains emulator-only history; hardware margins/stack high-water are not measured.

Four synthetic and all eight primary real waveform models pass unchanged >0.94
correlation/<1ms limits. Three additional ordinary common-backing comparisons
also pass unchanged >0.999, with minimum correlations:

| Scenario | Minimum common-backing correlation | Result |
| --- | --- | --- |
| scoring |0.9999964059087505|PASS |
| wrong |0.9999528968746556|PASS |
| reactive |0.9999648060145864|PASS |

These are ordinary unmodified mGBA0.10.1 captures, no experimental late-event
correction. The prior M011/M012 two failures remain compatibility history, not
silently reclassified as passed. No audio code, threshold/window, offset fit or
phase padding was changed to obtain this result. A build-layout/event-phase
change can avoid that emulator defect; a pass on this build is not a general
emulator repair or multi-version/hardware audio certification.

## Expected negative checks and privacy

The old independent LEFT/A/B hardware diagnostic script rejects the new ROM
(exit134). A deliberately one-line-shifted DMA source is still detected on
569/569eligible frames (137878bad pixels, worst395), proving the new labels do
not conceal the highway defect. These expected failures are separate from the
passing ordinary regression matrix.

Public review packaging rejects an actual private-profile result; a unique
ignored private canary is absent from every source ZIP member and public ROM.
No private/build/download files are tracked on source. Existing stale/missing/
failed-command/source-manifest tests remain unchanged except build version names.
Public evidence contains aggregate real metrics and synthetic/Original logs and
native screenshots only; no real chart tables, sample streams or secret password.

## Delivery and owner acceptance

Public: M013 / SYNTH review ZIP with ROM, complete public source/launcher/docs,
manifest and test evidence. It contains no Cream payload or private encrypted ZIP.
Private playtest: M013 / CREAM / LOCAL, delivered through the previously owner-
authorized AES-256/password workflow. Only ciphertext is hosted on a dedicated
download branch; its strong password is supplied in owner chat, never source,
GitHub metadata or public receipts. Download, require the password, verify the
extracted file's SHA against its build manifest and run that exact extracted ROM.
The published download receipt records final verification and any GitHub PR limit.
No local cloud path is represented as a downloadable attachment.

Actual owner GBA acceptance of Mission013 is **pending**. Earlier Mission011
handheld feedback is not acceptance of the new mapping. Follow
OWNER_M013_PLAYTEST.md for single buttons, chords, overlapping/released holds,
rapid presses, full Cream, sound/highway, results/replay and Original checks.
No merge into develop/main is permitted until approval. Known emulator cross-
build/version behavior, actual Windows launcher validation, keyboard ghosting,
physical stack/DMA measurements and inherited asset/historical-download rights
remain documented. No stable public release is claimed.

## Detailed behavior summary

| Scenario | Result | Selected observations |
| --- | --- | --- |
| public-sustain-perfect | PASS | SCORE: score512 combo25 maximum25 highest3 accuracy10000 FC1 AP1 session1; HOLDS: total6 completed5 released1 missed0 bonus42; IRQ: refills15189 max1408 mean1384.2 cycles, underruns0 gate1 gain256 |
| public-sustain-release | PASS | SCORE: score494 combo25 maximum25 highest3 accuracy10000 FC1 AP1 session1; HOLDS: total6 completed0 released6 missed0 bonus24; IRQ: refills15189 max1408 mean1384.1 cycles, underruns0 gate1 gain256 |
| public-perfect | PASS | SCORE: score470 combo25 maximum25 highest3 accuracy10000 FC1 AP1 session1; HOLDS: total6 completed0 released6 missed0 bonus0; IRQ: refills15189 max1408 mean1384.2 cycles, underruns0 gate1 gain256 |
| public-good | PASS | SCORE: score235 combo25 maximum25 highest3 accuracy10000 FC1 AP0 session1; HOLDS: total6 completed0 released6 missed0 bonus0; IRQ: refills15189 max1408 mean1384.2 cycles, underruns0 gate1 gain256 |
| public-miss | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills15189 max1472 mean1408.8 cycles, underruns0 gate0 gain0 |
| public-scoring | PASS | SCORE: score160 combo2 maximum3 highest1 accuracy7600 FC0 AP0 session1; HOLDS: total6 completed0 released4 missed2 bonus0; IRQ: refills15189 max1472 mean1388.7 cycles, underruns0 gate1 gain256 |
| public-wrong | PASS | SCORE: score250 combo0 maximum2 highest1 accuracy10000 FC0 AP0 session1; HOLDS: total6 completed0 released6 missed0 bonus0; IRQ: refills15189 max1472 mean1406.7 cycles, underruns0 gate0 gain0 |
| public-reactive | PASS | SCORE: score170 combo2 maximum2 highest1 accuracy6800 FC0 AP0 session1; HOLDS: total6 completed0 released4 missed2 bonus0; IRQ: refills15189 max1472 mean1391.1 cycles, underruns0 gate1 gain256 |
| public-returnmenu | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills15189 max1472 mean1408.8 cycles, underruns0 gate0 gain0 |
| public-returnselect | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills15189 max1472 mean1408.8 cycles, underruns0 gate0 gain0 |
| public-replaystart | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills15189 max1472 mean1408.8 cycles, underruns0 gate0 gain0 |
| public-fault_dma | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1404.0 cycles, underruns0 gate0 gain0 |
| public-fault_sound | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1404.0 cycles, underruns0 gate0 gain0 |
| public-fault_irq | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1404.0 cycles, underruns0 gate0 gain0 |
| public-fault_underrun | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1404.0 cycles, underruns1 gate0 gain0 |
| public-fault_timer | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session2; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1404.0 cycles, underruns0 gate0 gain0 |
| public-inconsistent | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session3; HOLDS: total6 completed0 released0 missed6 bonus0; IRQ: refills6826 max1472 mean1404.0 cycles, underruns0 gate1 gain256 |
| cream-sustain-perfect | PASS | SCORE: score15815 combo395 maximum395 highest4 accuracy10000 FC1 AP1 session1; HOLDS: total78 completed78 released0 missed0 bonus585; IRQ: refills276246 max1408 mean1341.6 cycles, underruns0 gate1 gain256 |
| cream-sustain-release | PASS | SCORE: score15442 combo395 maximum395 highest4 accuracy10000 FC1 AP1 session1; HOLDS: total78 completed0 released78 missed0 bonus212; IRQ: refills276246 max1408 mean1341.7 cycles, underruns0 gate1 gain256 |
| cream-perfect | PASS | SCORE: score15230 combo395 maximum395 highest4 accuracy10000 FC1 AP1 session1; HOLDS: total78 completed0 released78 missed0 bonus0; IRQ: refills276246 max1408 mean1341.7 cycles, underruns0 gate1 gain256 |
| cream-good | PASS | SCORE: score7615 combo395 maximum395 highest4 accuracy10000 FC1 AP0 session1; HOLDS: total78 completed0 released78 missed0 bonus0; IRQ: refills276246 max1408 mean1341.7 cycles, underruns0 gate1 gain256 |
| cream-miss | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total78 completed0 released0 missed78 bonus0; IRQ: refills276246 max1472 mean1371.1 cycles, underruns0 gate0 gain0 |
| cream-scoring | PASS | SCORE: score2465 combo0 maximum3 highest1 accuracy7494 FC0 AP0 session1; HOLDS: total78 completed0 released61 missed17 bonus0; IRQ: refills276246 max1472 mean1348.3 cycles, underruns0 gate0 gain0 |
| cream-wrong | PASS | SCORE: score3850 combo0 maximum2 highest1 accuracy10000 FC0 AP0 session1; HOLDS: total78 completed0 released78 missed0 bonus0; IRQ: refills276246 max1472 mean1363.4 cycles, underruns0 gate0 gain0 |
| cream-reactive | PASS | SCORE: score2630 combo0 maximum2 highest1 accuracy6658 FC0 AP0 session1; HOLDS: total78 completed0 released49 missed29 bonus0; IRQ: refills276246 max1472 mean1351.0 cycles, underruns0 gate0 gain0 |
| cream-returnmenu | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total78 completed0 released0 missed78 bonus0; IRQ: refills276246 max1472 mean1371.1 cycles, underruns0 gate0 gain0 |
| cream-returnselect | PASS | SCORE: score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1; HOLDS: total78 completed0 released0 missed78 bonus0; IRQ: refills276246 max1472 mean1371.1 cycles, underruns0 gate0 gain0 |
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
