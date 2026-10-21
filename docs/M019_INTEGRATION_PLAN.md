# Mission 019 proposed integration and rollback

**Proposal only. BLOCKED pending audio evidence and owner acceptance. No merge,
force-push, branch deletion, tag, release or history rewrite was performed.**

## Verified lineage

Fetched full history and all current branch tips. Protected refs at audit:

- `main`: `6c4e63460fab10733d8ff011045ee246e7201952`.
- `develop`: `56f6b7b243dfc710996336b99ac249806e666c85`.
- M017: `8f1c4839475ad0167782c9c4d140bd2eb751c378`.
- M018/M019 parent: `7cb0a3fca5b102e0cceaf4c2aecc92ddaff84889`.
- M019 verified executable/tool head: `e61614e64dba326876ff14634a6f1b705c9f7320`.

`develop` is an ancestor of that exact M019 head;35 commits are ahead at that
code head (the final certification documentation is an additional commit).
Mission013 mapping,014 pause,015 foundation,016 pipeline, selectable controls,
stabilization, Arcade75 and public Copper Circuit all lie on this history. The
full commit list and every fetched ref/ancestry decision are retained in evidence.
There is no competing newer feature tip outside the baseline among the fetched
source branches. Download-only branch tips are separate and are not proposed
for integration; their old artifacts are not evidence of additional gameplay.

## Source versus artifacts

ROM build source remains `9ccc460693fa7254527177330f32e56153720237` regardless of
later test/docs commits. RC1 artifact commit`e8ef0a59ddf1eecca84895c32c5e1e87722b51f5`
and RC2 artifact commit`437410b45881119084cf675735b30cf3c841dad5` are already in the
source lineage, with deliberately allowlisted public downloads. Related later
source commits document those downloads. This pre-existing artifact history is
not hidden or silently removed. Canonical source manifests exclude these reviewed
download outputs as build inputs; public source checks reject unexpected binary
payloads. No historical private download branch is being merged or rewritten.

The future canonical development candidate is exactly
`e61614e64dba326876ff14634a6f1b705c9f7320` plus its certification-only documentation
commit. This identifies the measured engine and tools; it is **not yet an accepted
baseline**. The pushed M019 branch is the one review location; artifact-only
branches are not development heads.

## Smallest safe integration sequence, after explicit approval

1. Close or explicitly review the audio evidence under the existing rules;
   complete RC2 owner hardware checks and document the decision. License choice
   and public release permission remain separate owner decisions.
2. Fetch again and bind the approved source, tools, docs and artifact hashes to
   exact commits. Re-run gates if code, inputs, environment or target changes.
3. Recheck `develop` ancestry. Its current ancestor relationship means no content
   conflict is predicted; this is not a claim that an actual merge was executed.
4. Open/review an integration PR into `develop`. Preserve the feature history;
   a normal `--no-ff` merge after approval would give a clear rollback boundary.
   Never merge download-only branches or force the protected branch to a hash.
5. Verify the merged tree's engine/input identity and required gates before any
   graphics branch. Only then, with fresh owner authorization, create that branch
   from the accepted `develop` commit. M019 starts no graphics work.

Rollback of a future merge: revert that merge with its correct first parent on
a new review branch, retest and review the revert. Do not reset/force-push shared
history. Keep RC1 and RC2 links/hashes available for comparison. Reverting a source
merge does not revoke already distributed artifacts; those immutable references
must remain clearly identified.
