# Mission 015: synthetic development builds and downloads

This slice automates the existing M014 gameplay engine. The versioned package
identifies Mission015 foundation infrastructure and full source commit; the ROM
retains its honest `M014 / SYNTH` engine label. No private profile is accepted by
the CI workflow. This is a development candidate, not hardware acceptance or a
stable release. The known strict emulator common-backing audio failure remains
open; identity/pause smoke tests do not certify all audio comparisons.

## CI and development artifacts

After owner approval to push the foundation branch, the workflow is
`.github/workflows/foundation.yml`: push to `foundation-audit-2026-10-20`, pull
requests, or manual dispatch. On a non-default branch, the Actions UI may not
show manual dispatch until the workflow is integrated; a branch push still
triggers it. No default-branch change is required. PR jobs use ordinary
`pull_request`, read-only contents permission and no persisted checkout token;
never use `pull_request_target` to execute untrusted submitted code.

1. Run all existing host sanitizer and Python tests plus public-package tests.
2. Use the existing digest-pinned devkitARM image and clean committed source.
3. Build the official synthetic profile once, with its ROM/ELF/source manifests.
4. Package only reviewed source plus that verified synthetic ROM. Fixed ZIP
   member timestamps/modes make packaging repeatable for the same build result;
   fresh builds still have different build timestamps. This does not claim
   bit-identical builds across arbitrary hosts or FFmpeg versions.
5. Verify exact archive inventory, source manifests/hashes, ROM hash/size and
   CRC before extraction into a new directory. Reject extra private payloads,
   duplicate names, changed source, wrong builds and unsafe entries.
6. Compile existing mGBA visible-identity and actual-key pause tests. Execute the
   extracted ROM through full-song single-pause, eight-pause, paused-SELECT exit
   and uninterrupted scenarios. The symbols come from its verified matching ELF.
7. Only after success, upload a versioned GitHub Actions artifact containing
   `Guitar-Boy-Advance-Foundation-M015-FULLCOMMIT-Synthetic.zip`, SHA256SUMS.txt,
   BUILD_MANIFEST.json, package-verification.json and emulator-verification.json.
   Do not upload a workspace directory, all builds, runtime private files or
   environment logs. Failed jobs publish no playable artifact. Retention is30days.

Supported Actions page after publication:
https://github.com/jellynada/guitar-boy-advance-expanded/actions

Select **Foundation synthetic build**, a successful run for the intended commit,
and its **foundation-m015-synthetic-COMMIT** artifact. GitHub wraps uploaded files
in an outer ZIP; extract that ZIP, verify SHA256SUMS.txt, then extract the inner
synthetic ZIP and load its `.gba` in mGBA or copy it to a compatible flashcart.
No compiler installation is needed just to play. START pauses/resumes imported
play; LEFT/B/A are the imported Easy frets; SELECT while paused exits.

Actions artifacts require a GitHub account/login and expire. They are development
artifacts, not anonymous permanent downloads. No successful hosted run or real
download is claimed merely because this workflow exists locally.

## Approved GitHub prerelease handoff

Do not publish automatically. Owner authorization for **public publication**,
review of inherited demo music/chart/art licensing, and successful CI are gates.
The existing original demo assets are present even in the synthetic imported-song
build. Synthetic music alone is not an inherited-asset clearance.

After those gates, use an approved development tag and title. Retrieve the exact
successful Actions artifact for the reviewed commit (GitHub UI or `gh run download
RUN_ID --name foundation-m015-synthetic-COMMIT --dir staging`). Check the recorded
commit, ZIP checksum and verification receipts. Do not rebuild/repackage it for
publication. Create a GitHub **prerelease** with that exact ZIP, SHA256SUMS.txt and
its receipts. Never use `--latest` or present it as stable. Keep permissions for
release publication separate from read-only build CI. Stable release, merging,
and default-branch changes require separate explicit approval.

Permanent approved release location:
https://github.com/jellynada/guitar-boy-advance-expanded/releases

Use the real release's **Assets** ZIP URL, not a source code ZIP, workspace link,
or guessed future tag. Verify it with an anonymous client, for example:

```sh
curl --fail --location --output downloaded.zip 'ACTUAL_APPROVED_ASSET_URL'
sha256sum downloaded.zip
unzip -t downloaded.zip
```

The hash must equal the published exact CI ZIP checksum. For complete
verification, use `verify_public_package.py` against the retained matching build
and repeat the existing extracted-ROM identity/smoke procedure. Record the actual
URL, source commit, byte size, digest, retrieval result, extraction and execution
results. Do not mark a release delivered until real retrieval succeeds. If the
environment blocks download, report it instead of retrying indefinitely.

## Local reproducible procedure

Dependencies: Python3, Docker, GCC/G++, FFmpeg and NumPy for the full host suite;
libmgba development headers/library for the smoke runner. CI uses Ubuntu24.04.
The existing devkitARM image digest remains unchanged. mGBA version differences
must be recorded; emulator behavior does not establish GBA hardware acceptance.

```sh
bash tests/check.sh
python3 tools/build_profile.py public
# Use the successful directory named by builds/public/LATEST.txt:
python3 tools/package_public.py --build builds/public/BUILD --output builds/public/review.zip
python3 tools/verify_public_package.py builds/public/review.zip --build builds/public/BUILD --extract-to builds/extracted --receipt builds/package-verification.json
# Generate nm symbols from that build's ELF with the pinned devkitARM toolchain.
python3 tools/ci_public_smoke.py --build builds/public/BUILD --extracted builds/extracted --output builds/smoke --symbols builds/symbols.txt
```

Private M014 ZIPs, password files and recordings remain untouched outside the
foundation checkout and never enter this workflow. `.github` support is restricted
to the exact reviewed workflow path; all other existing export guards remain.

## Remaining gates

- Authorized push/PR and actual GitHub Actions run, with artifact retrieval.
- Owner publication authorization and inherited asset provenance/license review.
- Approved prerelease and anonymous asset download verification.
- Broader emulator audio/graphics matrices; documented strict audio failure stays
  open. This slice changes no gameplay/audio code and relaxes no thresholds.
- Real Windows and physical GBA validation, including Mission013/014 acceptance.
- Mission016 generic package builds and versioned schema, then measured audio
  compression/capacity work; see MISSION_015_FOUNDATION_AUDIT.md.

## Implementation verification record

Before committing the first slice, `bash tests/check.sh` completed successfully:
136 Python tests and all10 ASan/UBSan C++ programs, including the new package
integrity tests and exact workflow allowlist regression. This is a local host
result, not a GitHub Actions run. The committed build is subsequently checked
with the pinned compiler and extracted-ROM smoke runner; machine-readable
package/emulator receipts remain build artifacts, not source or private assets.
No Windows or physical hardware result is claimed.
