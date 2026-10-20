# Arcade Cut v1 — 75 source seconds

Developer command (the owner should play supplied ROMs, not compile):

```
python3 tools/song_pipeline.py SONG.zip --output NEW_DIRECTORY --difficulty All --guitar PATH --backing PATH --arcade
```

`--arcade` defaults to 75 seconds and handheld derivation. `--max-duration 60`
changes the limit; `--arcade --max-duration none` disables the limit while
retaining derivation. Omitting these options preserves all legacy full-length
profiles, their original tail, hashes and reference traces. Output directories
must be new; sources are never overwritten. No multi-song storage is added.

## Authoritative timeline

MIDI tempo maps/chart tempo and explicit chart/INI offsets are normalized to
integer microseconds by the existing importer first. The cut compares those
source timestamps, never raw musical ticks. FFmpeg honors Opus pre-skip/padding
and resamples with the existing exact settings. The current full decode and
shared guitar/backing gain are retained before cutting, so audio before the
fade is byte-identical to the corresponding full-length prepared stream.

Both signed8 mono 16,384Hz stems are sliced at the same sample indexes. The
count-in remains 32,768 samples (2 seconds). A 75-second song has 1,228,800 source
samples and 1,261,568 playback samples: 77 seconds including count-in, with no
half-second playback tail. A shorter song retains its decoded natural length.
The existing safety guard/alignment is stored but never played. Configurable
limits must fall on exact sample boundaries; fractional-sample requests fail.

An identical deterministic linear integer envelope fades the last 1,228 samples
of each source stream (74.951171875ms), reaching signed zero. No fade-in,
retiming, mixing of roles or runtime effect is added. Reactive guitar behavior
and format/rate are unchanged.

## Heads, holds and EOF

Keep starts strictly before the rational source cutoff. Exclude starts at/after
it. Clip crossing genuine tails; a zero-length tail becomes a head only. The
inherited clock points at the last consumed sample, not the boundary after it.
Thus clipped holds end no later than that representable clock (about 61us before
75s), with microsecond/cycle rounding bounded conservatively. No extra samples
are appended to finish a hold. Raw original lengths remain in provenance.

Only cut headers define `GBA_IMPORTED_CUT`. At real audio EOF, after the ordinary
hold update, pending heads still inside their late window become normal misses
at the final audio tick. This is the one necessary engine compatibility change:
it prevents DATA ERROR/unfinished results without imaginary clock advancement,
free hits, longer audio or altered judgment windows. Full-length ROMs compile
out this path and are compared byte-for-byte outside their revision marker.

The visible song title `ARCADE75 / HANDHELD` identifies a 75s derivative. Existing
M014 build-profile labels remain for compatibility; the complete source SHA,
recipe, chart variant and manifest distinguish builds. Do not identify a ROM
by the historical M014 label alone.

## Storage and audio gates

Each Cream75 stem stores 1,277,952 bytes including count-in, guard and alignment;
both store 2,555,904 bytes (~2.438MiB). Source music alone is 2,457,600 bytes
(2.34375MiB). Ten source cuts would use 23.4375MiB, but identical current per-song
padding raises that to 24.375MiB before code/charts/art/metadata. This is a
forecast, not an implemented library. Final measurements appear in evidence.

The inherited ordinary mGBA output comparison issue is unresolved. Exact FIFO/
mixer identity and hardware sample duration are separate from resampled output
correlation. No emulator correction, threshold relaxation or phase padding is
shipped. A passing short trace cannot clear the full-length audio gate.
