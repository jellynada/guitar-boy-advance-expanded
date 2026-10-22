# Mission 022 cartridge capacity study

The hard cartridge ceiling is 33554432 bytes (32 MiB). There is no compression:
each source second costs 32768 PCM bytes for two 16384 Hz signed8 mono stems.
Count-in, tail, guard, alignment, chart arrays and metadata add storage.

The initial native public prototype measures 3168904 bytes with two distinct
songs. Its PCM payload is 3074752 bytes: 2555904 for the established 75-second
song and 518848 for the 202070-sample Easy fixture, including existing padding.
Chart notes/holds cost 24 bytes per head across the supported difficulties.
The 617 combined heads therefore occupy 14808 bytes. These are prototype
measurements; final candidate receipts must carry final source identity and size.

Use tools/collection_capacity.py on the actual final ROM/ELF/manifest for exact
per-song audio, charts, descriptors, catalog entries, identity strings, selected
metadata string ranges, shared code/art ranges, alignment and linker padding.
Do not subtract unrelated standalone ROMs to infer song cost.

For planning, reserve 1 MiB for eventual artwork and future shared code, in
addition to measured shared content. A provisional chart allowance of 192 bytes
per source second plus 256 bytes per song is based on the available original
test song's combined chart density, with sensitivity estimates at 96..384
bytes/second. A private recording's chart density is not a universal rule.

At roughly 0.1 MiB shared content, a 1 MiB future reserve, 192 chart bytes/second
and approximately 0.11 MiB existing count-in/tail/guard per full-length song,
provisional capacities are about seven 2-minute songs, five 3-minute songs,
four 4-minute songs or three 5-minute songs. Final machine-readable projections
must use final measured shared overhead and show rounding and mixed libraries.
These are storage estimates, not built-and-tested song libraries.

A reasonable initial target is four full-length songs averaging around four
minutes, or five around three minutes, before compression deserves a separate
investigation. Song lengths, chart density, artwork budget and actual linker
layout can change that target. Spare ROM capacity proves neither RAM nor CPU
headroom. No song shortening or codec decision is made here.

Any near-limit packaging probe must be separately labeled capacity-only and
must never add a selectable fake song. No playable capacity guarantee is inferred
from padding. Deduplication must be measured from actual linked ranges rather
than assumed from repeated references.


## Measured native package costs

| Component | Bytes |
| --- | ---: |
| Synth Demo guitar | 1,277,952 |
| Synth Demo backing | 1,277,952 |
| Synth Demo all charts | 14,208 |
| Synth Demo catalog/descriptor/strings | 232 |
| Synth Demo unique incremental cost | 2,570,344 |
| Synth Demo 2 guitar | 259,424 |
| Synth Demo 2 backing | 259,424 |
| Synth Demo 2 Easy chart | 600 |
| Synth Demo 2 catalog/descriptor/strings | 203 |
| Synth Demo 2 unique incremental cost | 519,651 |
| Shared code including ROM-loaded IWRAM | 38,440 |
| Existing graphics and system font | 27,848 |
| Other shared data and padding | 12,621 |
| Complete native cartridge | 3,168,904 |
| Remaining below 32 MiB | 30,385,528 |

Eight bytes of inter-section linker padding are included above. PCM payload
ranges are disjoint; selected chart arrays, catalog and descriptors share no
measured song-owned ranges in this build. C++ inline references from multiple
translation units resolve to the same linked arrays. No audio deduplication
feature is claimed. Repeating a package in the explicit list is rejected.

With 78,909 current shared bytes, an additional 1,048,576-byte future reserve,
114,718 bytes of conservative per-song PCM padding/alignment and 256 metadata
bytes, the 192 chart-bytes/second planning model gives:

| Average source duration | Projected per-song bytes | Planned songs |
| --- | ---: | ---: |
| 2 minutes | 4,070,174 | 7 |
| 3 minutes | 6,047,774 | 5 |
| 4 minutes | 8,025,374 | 4 |
| 5 minutes | 10,002,974 | 3 |

The same counts hold at the tested 96 and 384 chart-bytes/second sensitivity
bounds; that does not prove every future chart fits those bounds. Four 4-minute
songs leave only 325,451 bytes after the stated reserve, so that target is tight.
A 2+3+4+5-minute mixed library projects to 29,273,781 bytes with the reserve.
A 3+3+4+4-minute library has the same total. These libraries were not built.

The optional 31 MiB nonplayable binary probe checks the packaging ceiling only.
It has a leading non-ROM warning marker, no new selectable entries, and is never
placed in the Playable-ROMs folders. It does not qualify linker performance,
gameplay, CPU, RAM or a future song library.
