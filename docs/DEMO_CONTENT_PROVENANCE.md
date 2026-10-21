# Public demo content provenance

Copper Circuit is a newly generated original instrumental arrangement for this
owner-requested public demo. `tools/compose_public_demo.py` is its complete
score, chart design and software synthesizer: 128 BPM, E minor/C/G/D harmony,
42 bars (78.75 seconds), contrasting upper-register section and closing phrase.
Separate driven plucked-harmonic guitar and bass/drum backing are synthesized
mathematically. No external recording, sample, soundfont or downloaded chart
is used. Musical enjoyment still needs owner listening/playtesting.

The existing Arcade75 pipeline derives the first 40 bars (75 seconds), with
its existing count-in and end fade. It retains immutable source WAV/chart
hashes, preparation recipe and per-note derivation. Easy has 86 heads/11 holds,
Medium 171/11, Hard 335/10. Playable LEFT+B+A triples survive. No impossible
chord repairs are required for these original charts; crossing tails are clipped.

The owner explicitly requested public delivery and confirmed being the original
creator of the inherited game code/artwork. See `licenses/OWNER_PERMISSION.txt`.
Upstream has no general LICENSE; no blanket license has been invented here.
Original attribution to startfliing is preserved. This permission does not clear
the inherited commercial `careless_whisper.mod` or its chart. Both remain in
historical source, but are not compiled, linked, offered in the public menu or
included in the player ZIP. Cream is neither requested nor used.

Third-party notices: Tonc library/font MIT (gbadev-org/libtonc commit
`c5af1b2cb019dcde43216596390490bc07800b21`); Tonc mode7/shell-sort example
ancestry CC0 (gbadev-org/libtonc-examples commit
`db70fa29a0baae12c5c7603426d8535ebb5cc6ed`). Maxmod ISC notice is retained for
legacy source, although the public profile excludes its song bank and player.
GCC runtime exception/GPLv3 and newlib notices accompany the compiler runtime.
See `docs/licenses/`. Tonc documentation's separate noncommercial license is
not used as a code license; documentation prose was not incorporated.

Publication safety is positive as well as negative: the public build accepts
no owner song input, packaging independently regenerates this exact composition
and all three prepared charts, checks actual embedded PCM and the source marker,
then packages an explicit player-file allowlist. Exported source excludes the
separate public download binaries to prevent recursive packaging.
