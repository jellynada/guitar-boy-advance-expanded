# Mission 020 current policy

Development approval and release certification are independent. The proposed
source baseline is33b4d227e7e8142639486d1effeb67a81c15903e; unchanged runtime
is9ccc460693fa7254527177330f32e56153720237. Exact RC2 SHA256 is required.
M020's actual CI passes build/host, gameplay/graphics, digital and soak; strict
ordinary output9/15 remains a nonzero failure. Its promotion reporter records
“blocked”; it never releases, merges or overrides mandatory failures.

The stock PWM-slot limitation is documented for development, not waived for
release. A corrected future output specification needs independent calibration,
old-versus-proposed results and explicit review; no threshold change is implied.
Content isolation, licensing and formal owner approval remain mandatory.

Frozen-RC2 CI certifies this baseline. Before later graphics changes are accepted,
extend branch triggers and build/test the exact changed candidate too. Keep
separate source/build identities and regression/resource comparisons. Do not
substitute an unchanged-baseline green check for candidate execution.

Docs-only closeout commits do not rerun/cancel the recorded code run. Preserve
immutable public RC2 links and private source/launcher behavior; never upload
private music, its ROM or encrypted packages. No protected merge or formal release
is authorized. See M020_DEVELOPMENT_BASELINE_PLAN.md and M020_VERIFICATION.json.

All policies below are retained historical context.

# Mission 019 historical release policy

The exact engine remains RC2 source9ccc460; verification-only changes do not
create RC3. The workflow checks out frozen source separately, rebuilds it and
requires the immutable ROM hash. Digital observation uses the verified pinned
Debian environment; ordinary Ubuntu output remains its independent failing gate.
No continue-on-error or automatic release/merge is used. The promotion report
may succeed in recording a blocked result; that is not approval.

The actual run39653084111 passes build/gameplay/digital/soak and fails ordinary
output9/15. Documentation-only follow-up does not rerun or cancel that code run;
its exact source/tool commit is recorded separately. Remote artifacts are
short-lived evidence; immutable RC1/RC2 public links remain the owner delivery.
Never publish private music in a public encrypted archive.
[M019 report](MISSION_019_FOUNDATION_CERTIFICATION.md), [proposed integration](M019_INTEGRATION_PLAN.md).

Older policies below are historical.

# Mission018 current promotion policy

Build success, gameplay pass, exact digital pass, ordinary output pass, owner
acceptance and release approval are independent statuses. A failed mandatory
output gate stays red/nonzero even while an original public playtest is hosted.
No automatic merge/release job exists. Candidate manifests bind source/tree,
toolchain, profile, tests and ROM/chart/audio hashes. Packaging regenerates the
original composition, checks positive allowlist, extraction and downloaded ROM.
RC1's4 delivery files stay untouched; RC2 uses its own4 allowlisted paths.
The later artifact/evidence commit is distinct from the ROM source commit.

Old release notes below are historical. Owner approval precedes any protected
merge, release/tag or broader licensing choice.

# Mission 017 public playtest delivery

Build from clean committed source only. Independently regenerate original
Copper Circuit inputs during packaging; public profile has no owner-song input.
Check actual embedded stems, identity, chart derivation, license notices and
explicit ZIP inventory. Verify extracted ROM and stock-emulator results.

Use only the mission branch's four allowlisted public-demo-downloads files.
Artifact-only commit is distinct from manifest source commit; exclude those
files from future source exports/build inputs. Retrieve immutable raw GitHub
URLs, recheck ZIP/ROM hashes, safely extract and emulate downloaded ROM.
A failure in strict audio comparison keeps release approval blocked even if
the candidate is available for playtesting. No formal Release/tag, merge,
force push or main/develop change without owner approval. Third-party music
is never made public through this workflow.

# Current foundation release policy

## Arcade75 development delivery (not a stable release)

Push only `arcade75-handheld-chart-adaptation`. Existing synthetic CI now also
prepares a two-stem original Arcade75 exercise, builds it with the generic
profile, independently regenerates/allowlists its exact prepared manifest,
packages it with source, verifies extraction and runs all difficulty smoke
cases on the extracted ROM. This narrow public allowlist does not make generic
owner song builds public. The old synthetic review ZIP remains separate.

The real Cream native-All and Arcade75 ROMs stay in a private AES-256 ZIP with a
fresh strong password stored separately. Include exact source/build identities,
ROM SHA-256 values, recipe and full original-to-derived provenance. Verify with
independent 7-Zip and emulate the extracted owner ROM. Only an authorized private
upload route can complete delivery. No such route is currently configured; do
not publish the encrypted recording to public GitHub. Never claim a download
was verified from a local path alone. Record actual CI/download status separately.
Owner approval is required for any integration into develop/main and for any
subsequent mission; emulator evidence cannot declare hardware acceptance.


See [Mission015 build and delivery](MISSION_015_BUILD_DELIVERY.md). Public push,
artifact publication and release creation require owner approval. Public release
also requires inherited-asset review. The Mission013 encrypted-delivery wording
below is historical; encryption does not establish distribution permission.
No private recording, generated private ROM, encrypted private ZIP or password
may enter the new public CI artifacts. Mission014 private files remain unchanged.

# Mission014 delivery restriction

Build official public/private profiles from the same clean source. Only synthetic review artifacts may be uploaded publicly. The owner chose to retain the Cream ROM locally until authorized private transfer exists. Do not upload a Cream ROM or encrypted Cream ZIP to a public GitHub branch/release; a password is not access control or redistribution rights. Prepare a fresh-password AES256 ZIP locally, verify extraction/hash/emulator execution, retain the password separately, and report private delivery as blocked. No local path or unsuccessful sandbox link counts as a download test.

Source branch mission-014-pause-resume; no automatic develop/main merge. Preserve Build-Cream-ROM.bat/PowerShell launcher and both profiles. Build identity must be M014 and match the full source commit in manifest. Do not claim owner acceptance, Windows GUI testing or handheld testing from cloud results.

# Source workflow and public/private builds — Mission013

Saving source, accepting a development baseline, and releasing a stable public
game are different decisions. Owner-reported Mission011 hardware acceptance is
recorded in MISSION_012_BUILD_FOUNDATION.md; emulator and inherited-asset gates
remain. Source can still be saved and reviewed safely.

## Branch policy

- `main`: reviewed source after explicit owner approval. It is currently historical
  `6c4e63460fab10733d8ff011045ee246e7201952`, an immutable rollback point.
- `develop`: existing Mission012 integration baseline; Mission013 stays isolated
  until owner approval. It was created from the audited Mission012 source
  chain. Never overwrite a diverged branch.
- `mission-XXX-*`: isolated work branched from the accepted development baseline.
  Commit, test, push and review; retain existing history.
- `*-download` / `*-playtest-download`: compiled delivery only. Never merge into
  source. A future GitHub release may replace these when suitable; no stable tag
  or release is created here.

Full remote inventory/ancestry and rollback plan: BRANCH_INTEGRATION_REPORT.md.
Main's default-branch setting, historical branches and commit history are unchanged.

## Two official profiles, one committed engine

Use Python3 and Docker with the pinned image in scripts/toolchain-image.txt.
Public needs no FFmpeg or private package. Private additionally needs FFmpeg on
the WSL/Linux host. In an exported source folder, SOURCE_MANIFEST.json replaces
Git metadata; do not delete it or modify its recorded source files.

```bash
# Public original synthetic chart/audio, from public committed source only:
python3 tools/build_profile.py public

# Private owner-local Cream package; never downloads or uploads music:
python3 tools/build_profile.py cream
```

Private default input is `private/Cream.zip`. An explicit existing local ZIP may
be selected with `--input /path/to/Cream.zip`. No automatic fallback to synthetic
is allowed for this profile. Windows users double-click Build-Cream-ROM.bat; see
[WINDOWS_PRIVATE_BUILD.md](WINDOWS_PRIVATE_BUILD.md) for one-time setup.

Outputs are isolated and versioned under `builds/public/` or `builds/private/`.
Each successful directory contains a descriptively named ROM, matching ELF,
manifest, source-file manifest, log and validated runtime assets. Private runtime
assets stay private. LATEST.txt selects only a successful latest attempt;
LAST_ATTEMPT.json records success/failure. A new attempt removes the pointer,
retains older dated builds and only publishes fresh verified files on success.

Build manifests identify full source commit/tree, profile, chart/PCM hashes,
explicit stem choices, input ZIP hash (private only), compiler image/version,
FFmpeg version, ROM size and SHA-256. The ELF/ROM program/data guard and embedded
profile/commit marker reject stale pairs and wrong profiles. Input hashes are
rechecked after compilation; output timestamps must follow compilation and input
files. Dirty tracked source is rejected. Different FFmpeg releases may produce
different PCM bytes; tool/version hashes document this limitation.

Low-level `bash scripts/build-docker.sh` / `make` remain for developers and legacy
fixed/silent compatibility tests. Use the official driver for deliverable ROMs.
It forces explicit profile inputs and clears inherited make override variables.
Never select a ROM left over after a failed low-level make.

## Safe public review packaging

```bash
python3 tools/package_public.py --build builds/public/NAME_FROM_LATEST --output builds/public/packages/mission013-review.zip
```

Only a verified public-profile build matching the exact committed source is
accepted. Packaging regenerates and verifies the original synthetic fixture,
then includes the ROM, build manifest, complete audited source/launcher/docs and
source manifest. No working-folder recursion or `git add -f .` is used. Runtime
private directories are never an input to public packaging. Tests/evidence are
recorded in the committed Mission012 report.

Source path checks reject private/, builds/, downloads/, generated imports,
private headers/audio metadata, ROM/ELF/PCM/ZIP/recording payloads and symlinks.
A tracked private file is rejected even if .gitignore would otherwise ignore it.
The ignore rules cover local private inputs and all build outputs. For source
commits, stage explicit source paths; inspect `git diff --cached --name-only` and
`git diff --cached --check` before committing. Never stage private output manually.

Delivery branches may contain **only the allowlisted synthetic ZIP/ROM**, hashes
and verification receipt. Download it anonymously, check hashes/ZIP CRC, inspect
all members and compare its source-file manifest before offering the URL.

## Integration proposal and stable gates

Recommend Mission012 as the reviewed **development baseline**, not an approved
stable public release. After owner approval, integrate the source branch into
main with a normal reviewed merge/fast-forward, preserving full ancestry. If
main diverges, compare independent work and resolve explicitly; no force push.
No merge into main, default-branch change, branch deletion or stable tag is
performed automatically. Audio compatibility does not prevent safe source saves.

Stable/public game release separately requires remaining emulator comparisons,
platform timing/stack validation, owner acceptance for subsequent changes, and
permissions review. Retain original demo/music/art/chart in their existing
historical arrangement; no repository-wide LICENSE was found. Do not imply these
assets have been cleared for unrestricted distribution.

Historical M006–011 Cream download branches include previously owner-requested
public binaries. Ignoring files now does not remove history or establish rights.
They remain untouched and require a separate legal/provenance review. Mission012
publishes no new Cream recording, chart, converted audio or ROM. Owner-side local
building is the supported private delivery workflow; local cloud paths are not
presented as downloadable attachments.

## Mission013 delivery and review

Mission013 starts from verified develop56f6b7b and does not merge into develop/main.
Source work: mission-013-physical-controls. Public synthetic review files are on
mission-013-download. The real test ROM uses a separate AES-256 encrypted ZIP
under the previously owner-authorized password workflow. Ciphertext may be hosted
publicly; the secret stays outside GitHub and is supplied only in the owner chat.
The public synthetic review ZIP must never include that private encrypted payload,
plaintext Cream ROM/audio/chart, or password. Download both artifacts back, require
the password, compare decrypted ROM hash to the manifest and run the delivered ROM.
Do not call a publicly readable plaintext archive private or publish its key.
No password belongs in source, logs, commit messages or public receipts.

Actual handheld LEFT/B/A acceptance must come from the owner, separately from
agent emulator checks or earlier M011 acceptance. See MISSION_013_PHYSICAL_CONTROLS.
