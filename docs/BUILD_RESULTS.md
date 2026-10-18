# Mission 001 build and test evidence

These results describe this cloud workspace, not a human playthrough.

## Build

Artifact: `/workspace/guitar-boy-advance-expanded/guitar-boy-advance-expanded.gba`

Size: **288508 bytes**.

SHA-256:

```text
277036404c00f38cb335e22b64891c4542c45fd39e11d92fad106ef785a2bee5
```

Verified commands:

```bash
bash scripts/build-docker.sh clean
bash scripts/build-docker.sh
```

A separate clean native `make -j2` using the extracted GBA toolchain produced
that same checksum. Deleting `build/note.h` and running `make -j2` regenerated
the header and produced the same checksum again. The generated ELF is a
statically linked ARM executable with debugging information; `file` identifies
the cartridge as a Game Boy Advance ROM. Final C++17 builds completed without
the earlier default-language-mode libtonc deprecation warnings.

Pinned image:

```text
devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5
```

Relevant installed versions: devkitARM r68-1 / GCC 16.1.0-1, binutils 2.46.0-1,
libtonc 1.4.5-1, libgba 0.5.4-1, maxmod-gba 1.0.15-1, grit 0.10.0-1,
gba-tools 1.2.0-1, general-tools 1.4.4-1. Container host GCC is 12.2.0 and Make
is 4.3. The game and host converter explicitly select C++17.

## Regression tests

`bash tests/check.sh` completed successfully:

```text
PASS: note bounds under ASan/UBSan; 699 chart records and unchanged timing; invalid resolution rejected
```

Generated size/offset assertions passed with the GBA compiler. The linked chart
array is 11184 bytes at an 8-byte-aligned ROM address. Reading each of its 699
records directly from the ROM as little-endian `<QII` matched the original
chart's timestamp conversion, lane and duration values.

## Actual emulator execution

The final ROM was run with Debian's **mGBA 0.10.1** library, using the committed
`tests/emulator_smoke.c` harness, with the cursor address taken from the matching
ELF. The command exited successfully and reported:

```text
PASS: 36000 frames, final cursor 699, 35656 changing frames, 39301981 nonzero audio samples, no core crash
```

This covers about ten emulated minutes, including the end of the chart and the
old approximately seven-minute signed-overflow point. Synthetic button presses
were sent throughout, including after the final note. A frame captured after
1000 frames was visually inspected: perspective highway, fret circles, notes and
score display are present. Audio samples were measured, not listened to.

No manual keyboard/controller playthrough, sound-quality judgment, timing
calibration, physical GBA testing, or extended multi-hour run was performed.
Nonzero samples do not prove that the arrangement or synchronization is correct.
