"""Offline, deterministic v1 physical validation and minimal local repairs.

Inputs are already native-adapted charts, never normalized source records.
Intervals are half-open; a zero-tail head is an instantaneous requirement.
"""
import copy
from itertools import combinations

VERSION = 'gba-handheld-chart-v1'
POLL_US = (280896 * 1000000 + 16777215) // 16777216


def opposite(difficulty, a, b):
    right = {'Easy': None, 'Medium': 1, 'Hard': 2}[difficulty]
    return right is not None and {a, b} == {0, right}


def interval(n):
    return n['start_us'], n['start_us'] + n['sustain_us']


def together(a, b):
    sa, ea = interval(a); sb, eb = interval(b)
    return sa == sb or sa < sb < ea or sb < sa < eb


def validate(chart):
    """Read only. Native re-articulations are reported, not silently shortened."""
    conflicts, articulations = [], []
    notes = chart['notes']; lanes = len(chart['controls'])
    for n in notes:
        if type(n['lane']) is not int or not 0 <= n['lane'] < lanes:
            raise ValueError('Unsupported logical lane for ' + chart['difficulty'])
        if n['sustain_us'] < 0 or n['runtime_tick'] < 0:
            raise ValueError('Negative runtime note interval')
    for a, b in combinations(notes, 2):
        if not together(a, b): continue
        ids = [a['source_note_index'], b['source_note_index']]
        if a['lane'] == b['lane']:
            row = dict(ids=ids, source_us=max(a['start_us'], b['start_us']))
            if a['start_us'] == b['start_us']:
                conflicts.append(dict(kind='duplicate-head', **row))
            else:
                articulations.append(dict(kind='native-hold-rearticulation', **row))
        elif opposite(chart['difficulty'], a['lane'], b['lane']):
            conflicts.append(dict(kind='opposing-directions', ids=ids,
                                  source_us=max(a['start_us'], b['start_us'])))
    return dict(conflicts=conflicts, rearticulations=articulations,
                physical_model='LEFT and RIGHT mutually exclusive; Hard UP/DOWN is one alias lane; adjacent-direction diagonals allowed')


def recalculate(chart):
    notes = chart['notes']
    if not notes: raise ValueError('Transformation leaves an empty chart')
    chart['note_count'] = len(notes)
    chart['genuine_sustain_count'] = sum(bool(n['sustain_us']) for n in notes)
    chart['short_release_count'] = len(notes) - chart['genuine_sustain_count']
    chart['native_overlap_count'] = len(validate(chart)['rearticulations'])
    first = 0; visible = 0
    for i, n in enumerate(notes):
        while n['start_us'] - notes[first]['start_us'] > 1200000: first += 1
        visible = max(visible, i - first + 1)
    chart['maximum_visible_notes'] = visible
    if visible > 32: raise ValueError('Transformed chart exceeds 32 visible heads')
    # Explicit on-time all-Perfect/full-hold reference, not a universal maximum:
    # inherited Perfect hit phase and same-lane replacement can change bonuses.
    head = bonus = 0
    for i, n in enumerate(notes, 1):
        multiplier = 4 if i >= 30 else 3 if i >= 20 else 2 if i >= 10 else 1
        head += 10 * multiplier
        bonus += (n['sustain_us'] // 250000) * multiplier
    chart['score_reference'] = dict(policy='on-time Perfect heads; independent full holds; upper reference if native rearticulations remain',
                                    heads=head, hold_bonus=bonus, total=head + bonus)
    return chart


def signatures(report):
    return {(r['kind'], tuple(r['ids'])) for r in report['conflicts'] + report['rearticulations']}


def new_rapid_pair(a, b, difficulty):
    # Conservative preparation-only guard for newly introduced transitions.
    sa, ea = interval(a); sb, eb = interval(b)
    gap = max(sa, sb) - min(ea, eb)
    return (a['lane'] == b['lane'] and gap < 2 * POLL_US or
            opposite(difficulty, a['lane'], b['lane']) and gap < POLL_US)


def adapt_handheld(chart):
    result = copy.deepcopy(chart); before = validate(result)
    original = {n['source_note_index']: copy.deepcopy(n) for n in result['notes']}
    if any(c['kind'] == 'duplicate-head' for c in before['conflicts']):
        raise ValueError('Duplicate native heads require an explicit source repair: ' + str(before))
    # Never move/delete notes belonging to an originally playable multi-head chord.
    groups = {}
    for n in result['notes']: groups.setdefault(n['start_us'], []).append(n)
    protected = set()
    for group in groups.values():
        if len(group) > 1 and not any(opposite(chart['difficulty'], a['lane'], b['lane']) for a, b in combinations(group, 2)):
            protected.update(n['source_note_index'] for n in group)
    changes = []
    while True:
        current = validate(result)
        if not current['conflicts']: break
        conflict = current['conflicts'][0]; ids = set(conflict['ids'])
        previous_signatures = signatures(current); candidates = []
        for i, n in enumerate(result['notes']):
            identity = n['source_note_index']
            if identity not in ids or identity in protected: continue
            for lane in range(len(result['controls'])):
                if lane == n['lane']: continue
                trial = copy.deepcopy(result); moved = trial['notes'][i]; moved['lane'] = lane
                check = validate(trial)
                if len(check['conflicts']) >= len(current['conflicts']) or signatures(check) - previous_signatures: continue
                # Full sustain interval + nearby heads. Do not introduce a new
                # same-lane re-articulation or tighter opposing-direction switch.
                unsafe = any(new_rapid_pair(moved, other, result['difficulty']) and
                             not new_rapid_pair(n, other, result['difficulty'])
                             for j, other in enumerate(result['notes']) if i != j)
                if unsafe: continue
                moved['button'] = result['controls'][lane]
                candidates.append(((abs(lane - n['lane']), identity, lane), trial,
                                   dict(action='shift', id=identity, from_lane=n['lane'], to_lane=lane,
                                        reason=conflict)))
        if candidates:
            _, result, change = min(candidates, key=lambda x: x[0]); changes.append(change); continue
        # A single removal is the smallest reduction of this opposing pair.
        # Prefer retaining earlier source records after all safe shifts fail.
        deletions = []
        for i, n in enumerate(result['notes']):
            if n['source_note_index'] not in ids or n['source_note_index'] in protected: continue
            trial = copy.deepcopy(result); trial['notes'].pop(i)
            if not trial['notes']: continue
            if len(validate(trial)['conflicts']) >= len(current['conflicts']): continue
            deletions.append((n['source_note_index'], trial, n))
        if not deletions: raise ValueError('No permitted local reassignment or minimal deletion: ' + str(conflict))
        _, result, removed = max(deletions, key=lambda x: x[0])
        changes.append(dict(action='remove', id=removed['source_note_index'], from_lane=removed['lane'],
                            to_lane=None, removed_sustain_us=removed['sustain_us'], reason=conflict))
    recalculate(result)
    result['derivation'] = VERSION
    return result, dict(version=VERSION, difficulty=chart['difficulty'], before=before, after=validate(result),
                        changes=changes, mapping=[dict(id=i, source_tick=n['source_tick'], source_us=n['start_us'],
                            from_lane=n['lane'], to_lane=next((x['lane'] for x in result['notes'] if x['source_note_index'] == i), None))
                            for i, n in original.items()])
