import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.adapt_chart import cycles
from tools.arcade_cut import recipe, transform_chart, fade_pcm, trim_audio, duration_samples
from tools.handheld_chart import validate, adapt_handheld
from tools.difficulty_data import LAYOUTS
from tools.generate_difficulty_example import generate_difficulties
from tools.song_pipeline import prepare, verify_prepared


def note(identity, lane, start=1000000, hold=0):
    return dict(source_note_index=identity, source_tick=identity*192, lane=lane, button='',
        start_us=start, end_us=start+hold, native_duration_us=hold, native_duration_ticks=192 if hold else 1,
        genuine_sustain=bool(hold), runtime_tick=cycles(start+2000000), sustain_us=hold)


def chart(notes, difficulty='Hard'):
    return dict(difficulty=difficulty, controls=LAYOUTS[difficulty], notes=notes, note_count=len(notes),
                genuine_sustain_count=sum(bool(n['sustain_us']) for n in notes), title='Native')


class HandheldTests(unittest.TestCase):
    def test_playable_double_unchanged(self):
        c=chart([note(0,0),note(1,3)]);self.assertEqual(adapt_handheld(c)[0]['notes'],c['notes'])
    def test_playable_triple_unchanged(self):
        c=chart([note(0,0),note(1,3),note(2,4)]);self.assertEqual(adapt_handheld(c)[0]['notes'],c['notes'])
    def test_opposing_double_minimal_shift(self):
        c,r=adapt_handheld(chart([note(0,0),note(1,2)]));self.assertFalse(validate(c)['conflicts']);self.assertEqual(r['changes'][0]['action'],'shift');self.assertEqual(abs(r['changes'][0]['to_lane']-r['changes'][0]['from_lane']),1)
    def test_impossible_triple_keeps_all_heads(self):
        c,r=adapt_handheld(chart([note(0,0),note(1,1),note(2,2)]));self.assertEqual(c['note_count'],3);self.assertEqual([n['lane']for n in c['notes']],[0,1,3])
    def test_occupied_head_not_merged(self):
        c,r=adapt_handheld(chart([note(0,0),note(1,1),note(2,2),note(3,3)]));self.assertEqual([n['lane']for n in c['notes']],[0,1,4,3])
    def test_active_hold_destination_avoided(self):
        c,r=adapt_handheld(chart([note(0,1,0,3000000),note(1,0),note(2,2)]));self.assertFalse(validate(c)['conflicts']);self.assertEqual(c['notes'][2]['lane'],3)
    def test_future_hold_interval_checked(self):
        c,r=adapt_handheld(chart([note(0,0,1000000,3000000),note(1,2,1000000,3000000),note(2,1,2000000,1000000)]));self.assertFalse(validate(c)['conflicts']);self.assertFalse(validate(c)['rearticulations'])
    def test_native_rearticulation_report_only(self):
        c=chart([note(0,3,0,3000000),note(1,3,1000000,500000)]);before=copy.deepcopy(c);self.assertEqual(len(validate(c)['rearticulations']),1);self.assertEqual(c,before);self.assertEqual(adapt_handheld(c)[0]['notes'],c['notes'])
    def test_full_chord_minimal_deletion(self):
        c,r=adapt_handheld(chart([note(i,i,hold=1000000)for i in range(5)]));self.assertEqual(c['note_count'],4);self.assertEqual(c['genuine_sustain_count'],4);self.assertEqual(len(r['changes']),1);self.assertEqual(r['changes'][0]['action'],'remove')
    def test_unrepairable_protected_chords_fail(self):
        # Both native onset chords are playable and therefore protected; their
        # later overlap cannot be repaired without violating the owner policy.
        c=chart([note(0,0,0,3000000),note(1,3,0),note(2,2,1000000,1000000),note(3,4,1000000)])
        with self.assertRaisesRegex(ValueError,'No permitted'):adapt_handheld(c)
    def test_medium_cannot_invent_alias_lane(self):
        c,r=adapt_handheld(chart([note(0,0),note(1,1)],'Medium'));self.assertEqual([n['lane']for n in c['notes']],[0,2])
    def test_deterministic_provenance(self):
        c=chart([note(0,0),note(1,2)]);before=copy.deepcopy(c);a=adapt_handheld(c);b=adapt_handheld(c);self.assertEqual(a,b);self.assertEqual(c,before);self.assertEqual(a[1]['mapping'][1]['source_tick'],192)
    def test_easy_native_unchanged(self):
        c=chart([note(0,0),note(1,1),note(2,2)],'Easy');self.assertEqual(adapt_handheld(c)[0]['notes'],c['notes'])
    def test_unsupported_lane_explicit_failure(self):
        with self.assertRaises(ValueError):validate(chart([note(0,5)]))
    def test_alias_is_one_lane_not_two_attacks(self):
        self.assertFalse(validate(chart([note(0,0),note(1,1),note(2,4)]))['conflicts'])
    def test_duplicate_head_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):adapt_handheld(chart([note(0,1),note(1,1)]))
    def test_rapid_new_same_lane_conflict_avoided(self):
        c,r=adapt_handheld(chart([note(0,0),note(1,2),note(2,1,1010000)]));self.assertFalse(validate(c)['conflicts']);self.assertEqual(c['notes'][1]['lane'],3)


class CutTests(unittest.TestCase):
    def test_public_arcade_packager_rejects_owner_prepared_data(self):
        from tools.package_arcade_review import package
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);(root/'prepared').mkdir();(root/'prepared/song-manifest.json').write_text('{"source":"owner"}')
            with patch('tools.package_arcade_review.source_snapshot',return_value=({},dict(source_commit='x',source_tree_sha256='y'))), \
                 patch('tools.package_arcade_review.verify_result',return_value=dict(profile='song',source_commit='x',source_tree_sha256='y')), \
                 patch('tools.package_arcade_review.prepare_example',return_value={'source':'original-generator'}):
                with self.assertRaisesRegex(ValueError,'private publication rejected'):package(root,root,root/'out.zip')
            self.assertFalse((root/'out.zip').exists())
    def test_exact_75_samples(self):
        p=recipe(300*16384);self.assertEqual(p['source_samples'],1228800);self.assertEqual(p['tail_samples'],0)
    def test_just_before_and_exact_boundary(self):
        c,r=transform_chart(chart([note(0,3,74999999),note(1,4,75000000)]),recipe(300*16384));self.assertEqual(c['note_count'],1);self.assertEqual(c['notes'][0]['start_us'],74999999);self.assertEqual(r['charts'][0]['provenance'][1]['action'],'trim-remove')
    def test_hold_crossing_boundary(self):
        c,r=transform_chart(chart([note(0,3,74000000,3000000)]),recipe(300*16384));self.assertLessEqual(c['notes'][0]['sustain_us'],1000000);self.assertEqual(c['genuine_sustain_count'],1)
    def test_shorter_song_natural_length(self):
        p=recipe(6*16384);self.assertEqual(p['source_samples'],6*16384);self.assertEqual(p['fade_samples'],1228)
    def test_score_and_counts_recomputed(self):
        c,r=transform_chart(chart([note(0,3,1000000,1000000),note(1,4,75000000)]),recipe(300*16384));self.assertEqual(c['score_reference']['heads'],10);self.assertEqual(c['score_reference']['hold_bonus'],4)
    def test_fade_exact_length_symmetric_and_zero_endpoint(self):
        p=bytes([100])*2000;f=fade_pcm(p,1228);self.assertEqual(len(f),2000);self.assertEqual(f[:-1228],p[:-1228]);self.assertEqual(f[-1],0);self.assertEqual(f[-1228],100);self.assertEqual(fade_pcm(bytes([156])*2000,1228)[-1],0)
    def test_alignment_identical_two_streams(self):
        with tempfile.TemporaryDirectory()as t:
            d=Path(t);blob=bytes(32768)+bytes([64])*16384+bytes(30000)
            for n in ['imported_audio.bin','imported_backing.bin']:(d/n).write_bytes(blob)
            m=trim_audio(d,dict(schema_version='gba-reactive-audio-v1',source_samples=16384),recipe(16384))
            self.assertEqual((d/'imported_audio.bin').read_bytes(),(d/'imported_backing.bin').read_bytes());self.assertEqual(m['playback_samples'],49152);self.assertEqual(m['source_samples'],16384)
    def test_duration_configurable_or_disabled(self):
        self.assertEqual(recipe(300*16384,None)['source_samples'],300*16384);self.assertEqual(duration_samples('1.5'),24576)
        with self.assertRaises(ValueError):duration_samples('0.000001')
    def test_pipeline_deterministic_and_native_preserved(self):
        with tempfile.TemporaryDirectory()as t:
            d=Path(t);source=generate_difficulties(d/'source');original=(source/'notes.chart').read_bytes()
            a=prepare(source,d/'a',mix=['melody.wav'],difficulty='All',max_duration=75,handheld=True)
            b=prepare(source,d/'b',mix=['melody.wav'],difficulty='All',max_duration=75,handheld=True)
            self.assertEqual(a,b);self.assertEqual(verify_prepared(d/'a'),a);self.assertEqual(original,(source/'notes.chart').read_bytes());self.assertEqual(a['schema_version'],'gba-prepared-song-v3')
            report=json.loads((d/'a/derivation-report.json').read_text());self.assertEqual(len(report['charts']),3)
    def test_provenance_tampering_rejected(self):
        with tempfile.TemporaryDirectory()as t:
            d=Path(t);source=generate_difficulties(d/'source');prepare(source,d/'a',mix=['melody.wav'],difficulty='All',max_duration=75,handheld=True)
            p=d/'a/derivation-report.json';p.write_text('{}')
            with self.assertRaises(ValueError):verify_prepared(d/'a')


if __name__=='__main__':unittest.main()
