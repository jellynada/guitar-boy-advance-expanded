# GBA-compatible charts v1

This is an offline derivative, never an edit of source MIDI/chart/ZIP content.
Native preparation remains the default. `song_pipeline.py --arcade` opts into
75 source seconds and handheld adaptation. `--handheld` alone derives a full
natural-length chart. Controls remain Easy LEFT/B/A, Medium LEFT/RIGHT/B/A and
Hard LEFT/(UP or DOWN)/RIGHT/B/A. Original Demo is never transformed.

## Physical model and strict scope

The read-only validator sweeps pairs of heads/half-open genuine hold intervals.
A head is an instantaneous requirement; a release exactly at another onset is
not an overlap. LEFT and RIGHT cannot coexist. Hard's UP/DOWN alias is one
logical requirement, satisfied by either direction; LEFT+UP and UP+RIGHT are
adjacent-direction diagonals. Three directional lanes necessarily contain
LEFT+RIGHT and fail. Hardware diagonal ergonomics still need owner testing.

Duplicate same-lane heads fail explicitly. Native same-lane hold re-articulation
is reported separately: the inherited engine replaces the previous hold on a
fresh head; holding alone never hits it. We do not silently shorten it. A new
lane move cannot introduce a same-lane overlap or merge heads.

Only notes involved in an actual opposing-direction interval conflict can move.
Notes belonging to an originally playable multi-head chord are protected, even
if a later held-note combination becomes impossible. Playable LEFT+B+A triples
remain untouched. No challenge-based simplification or retiming exists.

## Deterministic minimal local policy

For the first remaining conflicting source pair, enumerate every single-note
move of either unprotected member to every legal logical lane. Validate the
entire moved hold interval against all heads/holds, including future events.
Reject new conflicts/re-articulations and require fewer existing conflicts.
Also reject newly introduced opposing transitions closer than one frame poll
(16,743us), or same-lane fresh attacks closer than two polls (33,486us). These
conservative preparation guards do not modify native rapid patterns.

Choose the safe move with least absolute logical-lane displacement, then lowest
original note index, then lowest destination lane. If none exists, remove one
unprotected member of that impossible pair, including its parallel hold entry;
prefer retaining earlier source records. One deletion is the minimum reduction
of that opposing pair. If protected content would have to change, fail with
precise source IDs/time. No recursive global musical rearrangement is attempted:
this v1 policy is deterministic and minimal per repaired conflict, not a claim
of globally optimal fingering over the whole song.

## Provenance and verification

Prepared schema v3 keeps `normalized-song.json` completely native. A versioned
recipe rebuilds the cut/derived header from that untouched normalized source.
`derivation-report.json` records every original ID/tick, original/runtime timing,
trim removal or tail clipping, shifted/deleted lane, and final prepared record.
It also records before/after conflicts and native re-articulations. Verification
recreates the transformation and requires exact JSON/header/inventory hashes.
This catches damage or stale bindings; hashes do not establish recording rights.
Private full provenance is included with the private owner package, never source
history. Public provenance is only the original synthetic fixture.

The actual Cream75 reference has Easy 110/20, Medium 186/38 and Hard 235/39
heads/holds. Medium shifts 3 heads; Hard shifts 4; no head/hold is deleted.
See the evidence summary for exact times and lanes. Native full-length counts
remain 395/78, 686/172 and 878/175. Full Combo/All Perfect use the prepared count.
Score metadata gives the on-time Perfect/full-hold reference in engine lane
order, with the unchanged formula; actual input/frame phase can reduce hold
bonuses. Native re-articulations make independent full holds an upper bound.
EOF misses cannot generate free points or All Perfect.
