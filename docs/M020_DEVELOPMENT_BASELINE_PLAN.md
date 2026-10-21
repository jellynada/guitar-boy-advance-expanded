# M020 development baseline proposal

No integration, tag, formal release or graphics implementation is authorized.
The complete local object history is not shallow. Fresh ancestry checks confirm
all five listed historical source tips are ancestors of the M019 starting tip.

| Branch | Audited tip |
|---|---|
| main | `6c4e63460fab10733d8ff011045ee246e7201952` |
| develop | `56f6b7b243dfc710996336b99ac249806e666c85` |
| mission-017-public-demo | `8f1c4839475ad0167782c9c4d140bd2eb751c378` |
| mission-018-release-stabilization | `7cb0a3fca5b102e0cceaf4c2aecc92ddaff84889` |
| mission-019-foundation-certification | `d0dda65a5ca71702cb6650ba06d0931bc10350d5` |
| mission-020-foundation-closeout initial verification | `5dab12062f6760db4abc657a5c4e0d87a310e6a1` |
| mission-020-foundation-closeout final verification code | `33b4d227e7e8142639486d1effeb67a81c15903e` |

RC2 runtime source is `9ccc460693fa7254527177330f32e56153720237`, an
ancestor of M019. Comparing source/, include/, graphics/, charts/, music/ and
Makefile between that runtime and M019 produces no differences. M020 changes
host observers, CI and reports only. Existing download commits are already in
the historical lineage; no download-only branch is being merged now.

Recommended development source candidate is exactly
`33b4d227e7e8142639486d1effeb67a81c15903e`, with unchanged runtime source
`9ccc460693fa7254527177330f32e56153720237`. Include the later documentation-only
M020 closeout commit in the proposed integration review; it records the explicit
development limitations and independent release block. No accepted baseline
exists until the owner/reviewer approves it. A recommendation is not acceptance.

After owner/reviewer approval:

1. Re-fetch and check that develop is still an ancestor of the reviewed final
   M020 commit. Review the complete feature ancestry, including the inherited
   historical artifact commits; do not silently drop feature history.
2. Propose a normal history-preserving `--no-ff` merge into develop through a PR.
   Require code/report review, immutable RC2 checksum, host and sanitizer checks,
   gameplay/graphics, digital transport, resource, content isolation, artifact
   download/extraction/execution, reproducibility and the explicit audio decision.
3. Keep strict ordinary audio and content/licensing/owner acceptance as separate
   release requirements. A documented development exception must never turn a
   failed strict output check green or enable release promotion.
4. Record the approved merge SHA and RC2 hash as the frozen development baseline.
   Only then base a separately authorized graphics branch on that merge SHA.
   Extend its CI trigger and build the exact changed candidate as well as frozen
   RC2; the present immutable-RC2 job cannot alone validate a visual modification.
5. On regression, revert the merge on a review branch using normal `git revert
   -m 1 MERGE_SHA`, preserving its ancestry. Revalidate RC2 and the prior checks.

main is historical, not declared stable. Protected-branch settings were not
changed; actual administration-level branch protection has not been asserted.
Release jobs must return nonzero on mandatory failures; a reporting job that
records “blocked” is not a passing release gate. Owner approval is still required
even after all technical checks eventually pass.
