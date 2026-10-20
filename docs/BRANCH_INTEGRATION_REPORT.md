# Mission 012 branch audit and integration proposal

Starting source: `a6c0328b319ce1bf48e08371c2db770ac5a5008a`. Immutable historical-main rollback point: `6c4e63460fab10733d8ff011045ee246e7201952`.

Fetched all remote heads before editing. All source mission branches001–011 are ancestors of the starting source; download branches are excluded from source ancestry. No develop branch existed. No tracked generated ROM, ELF, private recording, private header or PCM payload exists on the starting source branch. Historical tool executables and inherited demo/art/chart remain.

| Branch | Full commit | Purpose | Ancestor of Mission011 |
| --- | --- | --- | --- |
| origin | `6c4e63460fab10733d8ff011045ee246e7201952` | source | True |
| main | `6c4e63460fab10733d8ff011045ee246e7201952` | source | True |
| mission-001-download | `43710f8a9762e48d79db946015d17ccfa232cc83` | download-only | False |
| mission-001-reproducible-build | `47d340e105ff3afb899b063683b2ee0dbc5b7943` | source | True |
| mission-002-download | `58e65134f2d32e1fc151392c1750b4c05a2f7ca8` | download-only | False |
| mission-002-note-judgment | `533862124079a9dca1f84a6d88f54e40cde189cb` | source | True |
| mission-003-chart-importer | `135a55c2a0de50a4c68610f1aeb288924508bb54` | source | True |
| mission-003-download | `60d824cfd6241533bbf29caa54f8b64a47ad0c63` | download-only | False |
| mission-004-download | `145496e5179c3dbccbf464bd531ba267a495914a` | download-only | False |
| mission-004-universal-import | `1487532557a1e98b1c99c6628e5d65c291268cd2` | source | True |
| mission-005-download | `0640643a844a9fbb0c2fcc4612b090c12512a64b` | download-only | False |
| mission-005-first-playable-import | `f23cb6b4039fec93811b80f557a85518b2f626d1` | source | True |
| mission-006-audio-sync | `4fa9e6f8b2558a129075c9815c8bb2ac68e6421b` | source | True |
| mission-006-download | `d6e96a2d639479f5dd34a57a3d35c49c396c70d0` | download-only | False |
| mission-006-playtest-download | `90ee15fe548110d23df04836befa0fabfcf7285c` | download-only | False |
| mission-007-download | `0e6a37b941703184f3d76880ac7b8669261a9799` | download-only | False |
| mission-007-playtest-download | `e8b5e6f1362438474e5102835ac3d094708b9d87` | download-only | False |
| mission-007-reactive-guitar-audio | `90aaed9f2d7624258ff3485d6a0dc7858c126929` | source | True |
| mission-008-download | `9c35c2fffd0e88bde4c3db4fee2239f6597f381d` | download-only | False |
| mission-008-hotfix-download | `32e80153729d807aab9455f69221bd387a484e3b` | download-only | False |
| mission-008-hotfix-hud-completion | `71f0152c29d7008acd310808861643d5018e65a7` | source | True |
| mission-008-playtest-download | `3a1e6a948fd34a5e3de7a78deb6b33fe3ecafc0b` | download-only | False |
| mission-008-scoring-results | `a6b36a22733992b274f352a190c9ec1d39547d1d` | source | True |
| mission-009-download | `be1624dc33c9056d07ed5278ed405b43f3363912` | download-only | False |
| mission-009-playtest-download | `9984c0953cc70b41c43390c04aa642a74e7994de` | download-only | False |
| mission-009-sustain-gameplay | `f589e62a225651c7bd8a39ad27f517e3890cd1fb` | source | True |
| mission-010-download | `b7266b38290969a039e9381eac111579c55e16a4` | download-only | False |
| mission-010-stabilization | `233112a072e5a0e90e5a766207761474130f75a6` | source | True |
| mission-011-audio-graphics-stability | `a6c0328b319ce1bf48e08371c2db770ac5a5008a` | source | True |
| mission-011-cream-download | `85c765f04d883f6f6c0216dadf876b08cded2d43` | download-only | False |
| mission-011-download | `144ff62d5c175547f1d6df9621d2e4e7e4c36429` | download-only | False |

## Verified feature ancestry

- hud/results hotfix: `71f0152c29d7008acd310808861643d5018e65a7`.
- sustains: `85c637d4cf1c1029fbf8d2413ba0a63274ef234b`.
- input diagnostic: `1d9210448031d095ba125bcf4c3fe3375bb40c0a`.
- scanline DMA repair: `d0b20dcb27d40cda0f1556c5bdd1ad42c443ddfd`.

## Rollback and integration gate

Main must remain at the immutable revision above until owner approval. Review the main-to-Mission012 source comparison; never merge a download branch. After approval, use a normal reviewed merge, preserving all history. If reverting a later merge is necessary, revert that merge in a new commit; do not reset or force-push shared branches. The historical source remains retrievable by its full commit even without a new tag. No stable tag or default-branch change is proposed.

Develop may be created from final Mission012 source only if no existing remote develop exists. A diverged existing develop requires a separate decision, never replacement.

## Proposed main source integration

Comparison: https://github.com/jellynada/guitar-boy-advance-expanded/compare/main...mission-012-build-release-foundation

The exact added/modified file inventory is MAIN_INTEGRATION_FILES.txt (generated
from the main-to-source diff plus this mission's pending public documentation).
It includes engine/source fixes from Missions001–011, build/import/test tools,
public fixtures, documentation and actual historical/public screenshots. Existing
original art, demo music/chart and historical converter executables are retained;
they are not new Cream assets. There is no source merge conflict at the verified
starting point: main is an ancestor. Recheck the remote before any owner-approved
merge; future divergence must be reviewed rather than forced away.

Excluded from source/main/public packages: all download-branch commits and their
ZIP/ROM binaries; private/Cream.zip; generated private chart/header/JSON/PCM;
imports/output generated song directories; builds/private, caches, ELF/map/ROM
outputs, local captures and owner input archives. All builds/ output is ignored,
including public outputs; public delivery uses explicitly named files only on a
separate download branch. A source path allowlist rejects known private payloads
and tracked private files, rather than relying solely on ignore rules.

Recommended owner decision: approve the audited Mission012 source as the current
engineering baseline and, after reviewing this source-only comparison, authorize
main integration separately. Do not label the game a stable public release.
Develop tracks the completed source revision; future missions branch from it.
The two numerical emulator comparisons and provenance/hardware work remain
release gates, not reasons to withhold safe source commits.

If automated draft PR creation is denied, the comparison above remains the
review route. Record the actual API result in the delivery verification receipt;
never claim a PR exists merely because a comparison URL was prepared.
