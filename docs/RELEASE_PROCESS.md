# Review builds, licensing and stable integration

Mission010 is a **review candidate**, not a stable release. Owner acceptance and
QA-010-004 remain open. Do not merge or label it stable on automated counts alone.

## Source and branch policy

- Original upstream initial revision: `c27bd247a06561330a84773203772199fa210cdf`.
- Historical project main: `6c4e63460fab10733d8ff011045ee246e7201952`.
- M008 HUD/results hotfix: `71f0152c29d7008acd310808861643d5018e65a7`.
- Final M009 source: `f589e62a225651c7bd8a39ad27f517e3890cd1fb`
  (gameplay implementation `85c637d4cf1c1029fbf8d2413ba0a63274ef234b`).
- Current work: `mission-010-stabilization`, derived from that M009 source.
- `mission-010-download` holds review binaries; do not merge it into source.
- All earlier `*-download` / `*-playtest-download` branches are delivery history,
  not development branches. Full inventory is in MISSION_010_STABILIZATION.

Proposed consolidation, **only after explicit owner authorization**:

1. Review mission ancestry, source comparison and third-party permissions audit.
2. Resolve QA-010-004, complete owner playtest and physical-hardware risk review.
3. If separately approved, add a backup tag at historical main; do not rewrite it.
4. Fetch and confirm main still points to the recorded historical revision, with
   no new independent work. Create a reviewed source PR/comparison from the mission
   source chain, never a download branch. No `.gba`, owner ZIP or generated Cream
   data may enter the source change; retained original music/art needs its own
   rights review. The existing source chain contains original third-party assets.
5. With approval, fast-forward main to the accepted source (`git merge --ff-only`
   of the accepted source revision), or use the owner's reviewed integration
   choice if GitHub policies require it. Stop on divergence; do not force push.
6. Create a stable candidate reference only after the gates pass and that action
   is authorized. No backup tag, stable tag/branch, default-branch change, merge,
   branch deletion or history rewrite is performed in this mission.

The source is reviewable and independently buildable, but **not approved for
stable promotion** while an unexpected required waveform check fails.

## Reproducible public build

Use the source folder from the public review ZIP, or clone and check out the
source branch. `bash scripts/build-docker.sh` uses pinned devkitARM image
`sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5`.
Native tested compiler is ARM GCC16.1.0. The public default uses original synthetic
imported data/audio. The unchanged original699-note demo remains in the ROM.
The build generates note.h, chart assembly, graphics, soundbank, imported headers
and PCM; host converter source replaces the Windows-only executable.
`make` now validates chart/hold/EOF bounds, cartridge size, matching ELF/ROM and
compiled note count. Do not continue packaging after a nonzero build exit.

Version each bundle with source commit, selector identifier, SHA256, toolchain,
test outcome and known issues. Keep source and binaries separate. Include
synthetic native screenshots and Windows instructions. Download the public URL
back without authentication, test ZIP CRC, compare its ROM and source bytes to
the intended commit, and test the downloaded build. A workspace path or an
unverified sandbox link is not evidence of successful download delivery.

## Windows 11 — build the owner's Cream ZIP locally

This fallback was exercised in a clean Linux source export with the existing
owner ZIP and produced the identical private ROM. Windows GUI installation and
human keyboard play were not tested. Tools and commands are the established
WSL procedure; no programming changes are required.

One-time setup:

1. Install mGBA from https://mgba.io/downloads.html.
2. Install Ubuntu using Windows Terminal (administrator):
   `wsl --install -d Ubuntu`. Restart if Windows requests it; open Ubuntu and
   finish its initial account setup.
3. Install Docker Desktop from https://www.docker.com/products/docker-desktop/.
   Use Linux containers and enable Ubuntu under Settings → Resources → WSL
   Integration. Start Docker Desktop before building.
4. In Ubuntu run `sudo apt update` then `sudo apt install -y python3 ffmpeg`.
5. Extract the public review ZIP. Move its `guitar-boy-advance-expanded` folder
   into `C:\gba\mission010` so Makefile is at
   `C:\gba\mission010\guitar-boy-advance-expanded\Makefile`.
6. Copy the original owner song ZIP into that source folder and name it
   `Cream.zip`. Enable Explorer's View → Show → File name extensions to avoid
   accidentally naming it `Cream.zip.zip`.
7. In Ubuntu: `cd /mnt/c/gba/mission010/guitar-boy-advance-expanded`.

Then run exactly these two commands in Ubuntu:

```bash
python3 tools/prepare_song.py Cream.zip --reactive --guitar-stem guitar --backing-stem rhythm --backing-stem song --output-dir imports/output/mission010
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/mission010/imported_chart.hpp" "AUDIO_DIR=imports/output/mission010/audio"
```

Stop if either command reports failure; do not open an older ROM left behind.
Open `C:\gba\mission010\guitar-boy-advance-expanded\guitar-boy-advance-expanded.gba`
in mGBA. Confirm **M010 QA / LOCAL / AUDIO**, then choose Imported Easy Test.
The diagnostic mode is also present. Easy lane order: Left / A / B. Results:
A/Start replay, B/Select selection. Start+Select returns during play.
Ubuntu FFmpeg versions can produce different bytes; the recorded identical hash
applies to this environment's FFmpeg7.1.5 conversion and pinned compiler.
A default build afterward replaces this output with the synthetic version.

## Third-party content and actual delivery limits

The owner ZIP remains available; the current real build contains the original
WaveGroup cover, all395heads and78sustains, with matching reactive stems. Private
ROM hash: `c48ca749df60522402cc77204e5100c1f3c7121244c97f2df8539892f62b8c5d`.
Size9,178,392bytes. Full-song gameplay scenarios pass; one strict reactive
waveform analysis remains open, so this is not a fully accepted stable build.

There is no supported private attachment uploader or connected private file
location in this workspace. Historical chat download links failed for the owner.
No local pathname is offered as a verified download. The local workflow above is
the supported fallback, not a claim that a chat attachment was delivered.

Earlier owner requests resulted in publicly committed Cream ROMs in M006–009
playtest/download branches, including M009 commit
`9984c0953cc70b41c43390c04aa642a74e7994de`. These ROMs embed recording/chart data;
archive/source packages on historical branches also need review. A request to
upload them does not itself establish music/chart redistribution rights. This
mission does not remove or rewrite that history, or publish a new Cream ROM.
Source tracks original careless.chart, careless_whisper.mod, art and Tonc-derived
rendering code; no repository-wide LICENSE file was found. Preserve attribution
and separately confirm permissions before a broader public release. New public
review additions use synthetic chart/audio; the retained original demo is still
subject to that historical provenance review.

## Release checklist

- [x] Source baseline and mission ancestry verified; download branches separated.
- [x] Host suite98Python tests and8C++ sanitizer programs passed.
- [x] Composed frames checked; hidden-layer failures rejected.
- [x] Thirteen chord/hold cases and negative-input scenarios exercised.
- [x] Ten real full-song gameplay scenarios and three original-demo runs checked.
- [x] Results/replay/menu and fresh replay audio confirmed in mGBA.
- [ ] All required audio analyses pass (QA-010-004 remains open).
- [x] Public synthetic download published and downloaded back for verification
  (exact link/commit/hash in final handoff and bundle manifest).
- [x] Private reproducible workflow exercised; direct private delivery unavailable.
- [ ] Owner Windows11 manual acceptance received.
- [ ] Physical GBA acceptance / stack high-water measurements completed.
- [ ] Third-party permissions review completed.
- [ ] Owner approved final source integration.
