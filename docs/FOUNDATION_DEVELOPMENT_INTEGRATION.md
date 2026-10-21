# Accepted foundation: development integration proposal

The owner explicitly accepts M020's **APPROVED WITH DOCUMENTED LIMITATIONS**
recommendation and authorizes preparation/verification of a normal merge PR into
develop. This acceptance does **not** approve completing that PR's merge, starting
graphics, changing main, publishing a release or uploading private recordings.
M020's original reports remain historical evidence; this record updates only the
owner-approval scope.

## Exact reviewed history

- Current develop: `56f6b7b243dfc710996336b99ac249806e666c85`.
- Unchanged main: `6c4e63460fab10733d8ff011045ee246e7201952`.
- Accepted code baseline: `33b4d227e7e8142639486d1effeb67a81c15903e`.
- Accepted final closeout: `81f104e5b206eea579f55bfe744e16d8004e9920`.
- Frozen runtime/build identity: `9ccc460693fa7254527177330f32e56153720237`.

Full, non-shallow fetched history verifies develop is an ancestor of both accepted
commits. The closeout adds only42 documentation/evidence files relative to the
accepted code commit. The accepted closeout is39 commits ahead of develop,
including physical controls, pause transport, generic song preparation, all three
difficulties, stabilization, Arcade75 and Copper Circuit plus M018–M020 evidence.
Existing historical public-download commits are already part of that lineage;
no download-only branch is separately merged and no history is dropped.

This integration adds only PR verification/approval records, two host guards and
nine negative gate tests. No runtime, song, chart, input, scoring, graphics, audio
parameter, private pipeline or Windows launcher changes are introduced.

## Verify the actual proposed merge

The PR workflow checks out GitHub's proposed merge commit with complete history.
The guard verifies the accepted ancestry and pinned develop parent, checks every
runtime/build-input path against frozen RC2, and rejects unreviewed scope after
the accepted closeout. It separately records the actual candidate Git commit,
tree and parents, avoiding confusion with the retained runtime identity.

CI independently rebuilds frozen RC2, then compiles the **actual proposed merge
tree** with the identical prepared original Copper Circuit inputs and the retained
RC2 runtime marker. Retaining that marker is allowed only after source-input
equality is proved. The two complete ROM files must be byte-identical to SHA256
`9c4af95ff97eddd266dca3d7491ac9a5b1256f417684aae51b7c126443afafde`.

CI also downloads the immutable hosted ROM/ZIP, checks their published hashes,
validates the14-member ZIP inventory/CRC and safe paths, and compares the extracted
ROM with the actual merge-tree compilation. Downstream gameplay/graphics, digital
and stress jobs execute that actual downloaded-and-extracted ROM. Existing
composition regeneration, embedded-stem and forbidden-private/legacy-payload
checks remain mandatory. No private music is used by public CI.

The previous branch-push trigger is replaced by develop-targeted PR verification
so this phase tests the proposed merge rather than only a detached historical
baseline. Manual dispatch remains available. No test is disabled or relaxed.

## Separate development and release gates

Build/host, gameplay/graphics, digital, stress and focused stock-output jobs must
all pass. The new **Development integration readiness** check additionally requires
the complete, exact known strict-output matrix:9/15 with only cases4 and22 failing
on each difficulty. Missing evidence, wrong hashes, new failures, crashes and
relocated failures block development readiness. Even an unexpected improvement
requires review rather than silently redefining the accepted limitation.

The existing strict ordinary-output job stays **failed with nonzero exit**.
There is no `continue-on-error`, weakened threshold, accepting replacement output
comparator or release waiver. Release promotion remains blocked; a reporting job
that records this fact is not publication approval. The new check cannot approve
a PR merge, a release or graphics implementation. Nine negative tests protect this
boundary. Actual statuses and the tested synthetic merge SHA/tree belong in the
PR handoff, rather than being inferred merely from workflow presence.

## Resource contract applies to both profiles

[M020_GRAPHICS_RESOURCE_CONTRACT.md](M020_GRAPHICS_RESOURCE_CONTRACT.md) governs
both public Copper Circuit and private Cream builds. In particular, private static
IWRAM27276 and observed main-stack remainder4256 are tighter than public8308 and
23288. Public spare memory or Easy-only timings cannot justify private Hard work.
Initial future changes add no IWRAM, OAM allocation, IRQ work or DMA ownership;
the proposed frame/EWRAM/ROM increments remain profiling limits, not hardware
guarantees. The private pipeline and launcher remain unchanged. Private performance
evidence is retained M019 evidence, not newly claimed public-CI private execution.

No graphics branch or art change begins through this PR. Before later visual
changes can be accepted, their exact candidate source must be built/profiled on
both applicable profiles with all transport/resource checks; this integration's
explicit unchanged-RC2 scope guard must not be bypassed to bless new runtime code.

## Review, merge and rollback

Review the exact PR head, base, proposed merge SHA/tree and CI receipts. If either
parent moves, reverify before approval. Merge only after a separate owner approval,
using a normal **merge commit**, never squash/rebase, force-push or history rewrite.
Do not enable auto-merge. develop/main are left untouched during preparation.

After an approved merge, record its actual SHA (which may differ from GitHub's
temporary test-merge SHA). If rollback is needed, create a normal review branch
from develop and run `git revert -m 1 ACTUAL_MERGE_SHA`; review/test that revert
and merge it normally. This preserves all feature history. Without intervening
develop changes it restores the pre-merge develop tree. Keep frozen RC2/hash and
the acceptance/limitations record available independently of the working branch.
