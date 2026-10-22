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
provisional capacities are about eight 2-minute songs, five 3-minute songs,
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
