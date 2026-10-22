# Mission 022: explicit multi-song cartridge

Based on accepted develop merge cf2ee6601753a2718f0e08f6c9f78ac791114e03.
Review branch: mission-022-multi-song. No automatic merge or release.

The collection specification explicitly lists approved packages; it never scans
a music directory. Public builds accept only two fixed original generators.
Synth Demo is the existing Copper Circuit preparation (75 source seconds, Easy,
Medium and Hard). Synth Demo 2 is the original runtime fixture: its independent
continuous triangle guitar and 97 Hz bass/noise backing, 25 Easy heads, tempo
changes and genuine holds. Its 202070 source samples are about 12.3334 seconds;
it has Easy only. The two-second count-in and existing tails/guards are retained.

Public build:
python3 tools/build_collection.py --spec tests/fixtures/collection/public.json
This uses the existing pinned container toolchain. Native Windows uses --native
with the existing process-local devkitARM/make environment and a path without
spaces (a temporary drive alias is sufficient). No installer or system change
is part of the builder.

An owner-local private specification can list a public generator and an explicit
verified prepared package. Such a specification, packages, manifests, captures
and private ROMs stay outside tracked source and public CI. Prior ROMs remain
unchanged. The importer and preparation recipes are unchanged.

## Production interfaces

- SongAssets: immutable ROM descriptor referencing the single generated catalog,
  per-difficulty chart choices, independently aligned stems, exact source,
  playback/storage counts, EOF policy and chart-manifest identity.
- UiScreens::catalog returns that generated catalog under GBA_MULTI_SONG.
  Navigation remains the same hardware-independent reducer.
- beginImported validates catalog index, asset reference and supported difficulty,
  chooses that descriptor's chart, computes its last note/hold boundary while
  stopped, configures the existing runtime/scoring/holds, and starts a new epoch.
- pcmSelect copies only two pointers and three counts into a 20-byte EWRAM
  selector while audio is disabled. It neither copies nor decodes music.
- The existing PCM IRQ reads selected source pointers/counts. Its gate, gain,
  FIFO writes, sample clock, pause and resume algorithm are unchanged.
- Cut EOF handling becomes a per-song policy; preparation itself is unchanged.
- Existing single-song build paths remain available without GBA_MULTI_SONG.
  Collection candidates omit the legacy commercial demo and its Maxmod storage.

Maximum chart capacity is the largest single difficulty in the explicit set,
not the sum of charts. Existing static state is reset on every launch, restart
and switch. No song data goes onto the stack or into a full-length RAM buffer.
No new DMA, timer, OAM ownership, frame heap allocation or codec is introduced.

## Verification

The builder independently compares ROM/ELF bytes (excluding gbafix header fields),
cartridge header/ceiling, source/profile identity, every linked chart note/hold
array and every stem against the selected packages. It checks assembler start/end
boundaries, inventories/hashes, and non-overlapping stem regions. Public provenance
comes from allowlisted generation, not title-string scanning.

The actual-ROM observer checks catalog and active chart/stem addresses against
the verified manifest, all supported difficulties, full completions, every Results
action, pause/resume/restart/quit, held confirmation, invalid index and 40
alternating switches without reboot. It waits for the accepted readiness flag
before observing gameplay initialization. Inherited gameplay, physical chord,
sustain, graphics, deadline and stack assertions remain in their original probes;
the adapter changes song menu travel only. Observer symbol aliases never enter
the ROM. The exact FIFO oracle retains startup advance15 and no lateness correction.

CI runs the actual collection candidate. Ordinary-output comparisons retain the
original 6.322/37.5/76.7-second windows for Synth Demo and the original comparator
and thresholds. Failures remain visible in a separate strict release job.
Development integration remains blocked by any unexplained digital, timing,
graphics, resource or gameplay regression. Formal release also requires resolving
the documented strict ordinary-output limitation and later owner acceptance.

Exact final source IDs, ROM hashes, per-case results and measurements belong to
the candidate receipts and owner-local Mission-022 report. Early prototype evidence
must not be substituted for final-head verification.

Rollback before merge is to retain the accepted baseline and leave this branch
unmerged. If a future normal merge is separately approved, revert that merge with
git revert -m 1 MERGE_SHA on a rollback branch, test, and submit a normal PR.
Never reset or force-push shared history.

Legacy public package smoke drivers now detect the accepted navigation UI and
use the existing M021 menu adapters and a title/options glyph identity observer.
The old pre-navigation OAM identity assertion remains for historical ROMs.
Gameplay assertions, all original smoke cases and -Werror remain enabled.
The cartridge-only verifier needs standard-library Python; NumPy synthesis stays
on the preparation host, outside the pinned compiler image.
