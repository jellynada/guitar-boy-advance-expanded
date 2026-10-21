# Mission 019 foundation certification

**Recommendation: BLOCKED. Audio decision: AUDIO BLOCKED.** Copper Circuit is
playable and the exercised engine checks pass, but six strict output comparisons
remain unexplained in full. RC2 handheld acceptance across all difficulties is
also pending. Neither graphics development nor a public release is approved.

## Frozen identities

| Identity | Exact revision |
|---|---|
| Verified M018 branch tip; M019 parent | `7cb0a3fca5b102e0cceaf4c2aecc92ddaff84889` |
| Game source built, rebuilt and tested | `9ccc460693fa7254527177330f32e56153720237` |
| Historical final M018 verification tools | `4652d45294a7cb930d6928d7fc5eda755a3f8bb2` |
| Immutable hosted RC2 artifacts | `437410b45881119084cf675735b30cf3c841dad5` |
| M019 soak, logging and CI diagnostics | `d9fa70679907ebaff10b9338921987275de79bc7` |
| Final M019 CI environment repair | `e61614e64dba326876ff14634a6f1b705c9f7320` |

Branch: `mission-019-foundation-certification`. Complete ancestry was fetched;
`develop` is an ancestor. No engine, chart, art, music, gameplay timing, scoring,
launcher or published RC1/RC2 bytes changed in M019. Only host verification,
CI and documentation changed. There is no RC3.

## Independent reproduction, 21 October 2026 UTC

Clean detached source, freshly generated public inputs, compiler GCC16.1.0 in
`devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5`.
The local build reused that verified container because the cloud VFS disk has
less than 1GB free; it did not reuse object files. A separate GitHub runner also
rebuilt the frozen source and passed the exact ROM hash check.

| Gate | New observation |
|---|---|
| Host suite | 209 Python tests and 13 regular ASan/UBSan programs pass |
| Compiled ROM gameplay/UI/readiness/graphics | 38/38 pass |
| Complete digital transport, including every resume | 15/15 pass; no word/sample mismatch or complete-segment drift |
| Strict ordinary audio | 9/15 on stock mGBA0.10.1 and 0.10.5; **fails** |
| Separate fixed-phase diagnostic | 14/15; diagnostic only, no clearance |
| Complete-song composed graphics | 29,400 frame calls; 27,420 reference-valid frames checked; zero defect frames/pixels |
| Foreground peaks, Easy/Medium/Hard | 119,616 / 147,008 / 155,392 cycles; frame budget280,896 |
| Public ROM | 2,643,632 bytes; byte-identical to RC2 |
| Hosted ZIP | Downloaded, all14 members hashed and safely extracted |
| Actual extracted/downloaded ROM | Three complete songs, UI and startup/readiness checks pass |

See [machine evidence](M019_VERIFICATION.json), [audio gate](M019_AUDIO_GATE.md)
and [resource risk register](M019_HARDWARE_RISK_REGISTER.md). Historical M018
measurements stay in their original report; this table describes fresh M019 work.

## Input, scoring and transitions

Easy remains LEFT/B/A; Medium LEFT/RIGHT/B/A; Hard LEFT/UP-or-DOWN/RIGHT/B/A.
Alias coalescing precedes edge detection. Fixed-size host tests cover chords,
alias transitions, multiple holds, release/repress, system-key priority and invalid
raw combinations; invalid keyboard masks are not proof of handheld feasibility.
The new soak asserts no LEFT+RIGHT or UP+DOWN and uses legal wrong-input pulses.
The existing full-song matrix separately retains its older raw-mask scenarios.

Fresh complete Perfect/no-pause public runs: Easy86P, score2901,11 holds complete;
Medium171P, score6338,10 complete/1 early release; Hard335P, score12866,10 complete.
Charts still contain86/171/335 heads and11/11/10 holds. Medium's final same-lane
re-articulation intentionally replaces its previous hold; owner chose to keep it.
No new scoring rule or chart repair was applied.

The focused actual-ROM trace independently reproduces one legitimate WrongInput
after releasing during pause and making a new B press after resume. The previous
head has already been judged. Repressing while paused, holding continuously, and
remaining released do not manufacture a press. Frozen musical time/score/events
and sustain/input reseeding pass. START held, START+SELECT priority, paused SELECT
exit, short/eight pauses, long pause, pre-note pause, results/replay and EOF coverage
remain exercised by the existing matrix and host policy tests. Detailed physical
GBA judgment/listening acceptance is still pending.

## Measured long sessions

Each row uses one emulator core without resets, actual buttons and actual ROM.
Duration comes from the 64-bit emulated cycle clock at16,777,216Hz. It includes
navigation/pauses; it is not a claim of one hour of uninterrupted note playing.

| Profile / stock emulator | Seconds (playing / paused / menu / results) | Complete songs | Pauses / replay-then-exit | Extra framebuffer checks |
|---|---|---|---|---|
| Public /0.10.1 | 3647.016587 (3237.655 /287.874 /120.081 /1.406) |14 each difficulty,42 total|126 /11|3016 |
| Public /0.10.5 | 3647.016587 (same partition) |14 each difficulty,42 total|126 /11|3016 |
| Real private full Cream Easy /0.10.1 |3677.957155 (3508.284 /95.517 /73.721 /0.435)|13|39 /4|3276 |
| Original699 demo /0.10.1 |3600.002410 (3598.476 playing, remaining menu)|continuous all-miss mode|not an imported pause/results mode|0 imported-floor checks |

Public runs each include15 no-miss,15 all-miss and12 mixed runs, with Good/Miss/
WrongInput, holds, legal chords, alias handoffs, selector idle and difficulty
switching. Private includes6 no-miss,4 all-miss,3 mixed. The JSON field
`perfect_runs` counts no-miss runs (its assertion permits Good); the separate
Perfect baseline above establishes actual all-Perfect coverage.

No tested reset/crash, stale score on replay, underrun, scanline deadline miss,
tail overflow or valid-frame displacement occurred. Public soak work peak155,776
cycles is slightly above the shorter baseline; remaining measured frame time is
125,120 cycles. This is emulator coverage, not a worst-case physical guarantee.
Host peak RSS is recorded, but is not a game-heap high-water measurement. Fixed
static game storage and absence of new allocations bound the exercised state.

## Corrections to observers and unsuccessful attempts

All original evidence is retained. The first soak replay failed because its
driver kept A held from a final sustain; supplying a fresh release/press fixed
the driver. The first floor check compared a previous screen to a new scene's
tables while `importedReady=0`, DMA0/3 disabled and tick0. The corrected observer
requires the game's existing readiness signal and separately counts186 public /
60 private transient frames. The floor oracle and zero-displacement criterion
are unchanged; the separate startup/readiness test still runs.

Initial extra private pause attempts used public navigation, then incorrectly
omitted the difficulty menu. Both failed before play. The unmodified original
navigation probe passes all four requested cases. A host reference replay first
used the wrong timing trace; the frozen trace uses its documented `--clock-only`
mode because that capture contains no judgment statistics. It reproduces15815
under sanitizers; fresh real-ROM pause cases2/3/12 also independently reach15815.
An initial optional negative DMA probe lacked required observer address arguments
and exited139 before observation; the addressed run detects1769/1769 deliberately
damaged frames (500,758 displaced pixels), exits134 as expected. None is counted
as a passing first attempt or a repaired game defect.

Raw evidence lives under `/workspace/mission019-evidence`; selected small public
logs/results and a full evidence hash inventory are committed under
`docs/evidence/mission019`. Digital FIFO/sample logs were losslessly gzipped,
decompressed and hash-verified to conserve cloud disk. No private song data was
added to git. See the reproduction commands in M019_VERIFICATION.json.

## Remote gates and content

M018 run39646729570 actually failed digital and ordinary audio; its promotion
report success was not release approval. M019 run39651971307 exposed the digital
failure: the Ubuntu observer generated no `.samples` files although the emulator
processes returned0. The precise package/linker cause is not established. M019
rerun39653084111 uses the verified baseline stock Debian library for observation:
build/host, gameplay/graphics, digital15/15 and hour soak pass; ordinary9/15 fails.
No test was relaxed, no failure was swallowed and no automatic release exists.

The public profile embeds the newly composed Copper Circuit stems and charts;
verification checks actual ROM bytes, header, generated manifests and exclusion
of commercial legacy/private markers. It excludes original-demo commercial audio
and chart from this profile while retaining legacy source/private behavior.
Owner creator confirmation is historical permission evidence; a deliberate
project-wide source license remains pending. Third-party notices are retained.

Real private Cream was rebuilt from exact RC2 source with verified owner assets,
395 heads/78 sustains, and tested locally. Its original699 mode also ran an hour.
Fresh original699 Perfect/miss/mixed regressions each pass36,000 frames with
the unchanged LEFT/RIGHT/A/B controls. Fresh private eight-pause stack sentinels
leave4256 user bytes untouched (980 touched), IRQ40/160; that profile's static
IWRAM27,276 and EWRAM9600 are considerably larger than the public profile.
No access-controlled private upload destination is available in this session;
no private ROM link or Windows GUI test is claimed. The launcher is unchanged.

## Decision and owner action

Use the unchanged [RC2 ROM](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/437410b45881119084cf675735b30cf3c841dad5/public-demo-downloads/Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.gba)
or [player ZIP](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/437410b45881119084cf675735b30cf3c841dad5/public-demo-downloads/Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.zip).
Windows: download ZIP, right-click **Extract All**, then open the `.gba` in mGBA
or copy it to your flash cartridge using its normal process. No compilation.

Complete [the short handheld checklist](OWNER_M019_PLAYTEST.md). The smallest
engineering follow-up is the single remaining Easy-mixed paired-backing window
in [the audio experiment plan](M019_AUDIO_GATE.md); the six mandatory failures
must remain visible while it is investigated. A consumer listening capture can
help, but alone cannot clear sub-millisecond phase uncertainty. Integration is
only [proposed](M019_INTEGRATION_PLAN.md). No merge, stable tag, release or next
mission has been authorized or performed.
