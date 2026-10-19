import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools.adapt_chart import adapt,cycles,header,MAX_SONG_US
from tools.chart_importer import normalize


def source():
    return normalize(Path('tests/fixtures/runtime/easy.chart').read_text(),'Synthetic Easy Test')


def prepare(song):return adapt(song,difficulty='Easy',instrument='five_fret_lead_guitar',synthetic=True)


class AdaptTests(unittest.TestCase):
    def test_result_title_escaped_bounded_and_notes_preserved(self):
        s=source();before=prepare(s)
        s['metadata']['Name']='Title "quoted" \\ café\n'+'x'*120
        a=prepare(s);h=header(a)
        line=next(x for x in h.splitlines() if 'imported_title[]' in x)
        title=json.loads(line.split(' = ',1)[1][:-1])
        self.assertEqual(len(title),96)
        self.assertTrue(all(32<=ord(c)<=126 for c in title))
        self.assertEqual(before['notes'],a['notes'])
        self.assertIn('\\"quoted\\"',line)

    def test_no_notes_or_source_mutated(self):
        s=source();original=copy.deepcopy(s);a=prepare(s)
        self.assertEqual(s,original)
        self.assertEqual(a['note_count'],25)
        self.assertEqual(a['short_release_count'],19)
        self.assertEqual(a['genuine_sustain_count'],6)
        self.assertEqual([n['lane'] for n in a['notes']],[n['lane'] for n in s['tracks'][0]['notes']])
        self.assertEqual(a['controls'],['Left','A','B'])
        self.assertTrue(a['synthetic'])

    def test_independent_boundaries_first_last(self):
        a=prepare(source());n=a['notes']
        self.assertEqual(n[0]['start_us'],0)
        self.assertEqual(n[4]['start_us'],2000000)
        self.assertEqual(n[8]['start_us'],6000000)
        self.assertEqual(n[-1]['start_us'],11333333)
        self.assertEqual(n[0]['runtime_tick'],33554432)
        self.assertEqual(n[4]['runtime_tick'],67108864)
        self.assertEqual(n[8]['runtime_tick'],134217728)
        self.assertEqual(n[2]['native_duration_us'],1000000)
        self.assertEqual(n[2]['sustain_us'],1000000)
        self.assertEqual(n[0]['sustain_us'],0)
        self.assertGreater(n[0]['native_duration_us'],0)

    def test_invalid_lanes_offsets_order_and_duplicates(self):
        for field,value in [('lane',4),('lane',None),('lane',True),('source_lane',7),
                            ('kind','open'),('start_us',-2000001),('end_us',MAX_SONG_US+1),('duration_us',999)]:
            s=source();s['tracks'][0]['notes'][0][field]=value
            with self.subTest(field=field,value=value),self.assertRaises((ValueError,TypeError)):prepare(s)
        s=source();s['tracks'][0]['notes'].reverse()
        with self.assertRaises(ValueError):prepare(s)
        s=source();s['tracks'][0]['notes'].insert(0,copy.deepcopy(s['tracks'][0]['notes'][0]))
        with self.assertRaises(ValueError):prepare(s)

    def test_wrong_selection_and_sysex(self):
        s=source()
        with self.assertRaises(ValueError):adapt(s,difficulty='Expert',instrument='five_fret_lead_guitar')
        s['tracks'][0]['special_events'].append({'type':'sysex'})
        with self.assertRaises(ValueError):prepare(s)

    def test_density_is_rejected_not_truncated(self):
        s=source();s['tracks'][0]['notes']=[dict(s['tracks'][0]['notes'][0],start_us=i*1000,end_us=i*1000+1,duration_us=1) for i in range(33)]
        with self.assertRaisesRegex(ValueError,'visible sprites'):prepare(s)

    def test_sustain_threshold_and_overlaps(self):
        s=source();n=s['tracks'][0]['notes'][0];n.update(duration_ticks=63)
        self.assertFalse(prepare(s)['notes'][0]['genuine_sustain'])
        n.update(duration_ticks=64)
        self.assertTrue(prepare(s)['notes'][0]['genuine_sustain'])
        n.update(duration_us=2000000,end_us=2000000)
        self.assertGreater(prepare(s)['native_overlap_count'],0)

    def test_long_and_overflow(self):
        self.assertEqual(cycles(3600000000),60397977600)
        with self.assertRaises(ValueError):cycles(1<<64)
        s=source();s['tracks'][0]['notes'][-1].update(start_us=MAX_SONG_US+1,end_us=MAX_SONG_US+2)
        with self.assertRaises(ValueError):prepare(s)

    def test_one_command_prepare_success_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'runtime'
            command=[sys.executable,'tools/prepare_easy.py','tests/fixtures/runtime/easy.chart','--output-dir',str(out)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((out/'imported_chart.hpp').exists())
            self.assertTrue((out/'source/easy/song.json').exists())
            command[2]='tests/fixtures/charts/constant.chart'
            # Constant fixture may contain Easy; force an invalid source file instead.
            bad=Path(temp)/'bad.mid';bad.write_bytes(b'bad');command[2]=str(bad)
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            self.assertFalse((out/'imported_chart.hpp').exists())

    def test_rounding_deterministic_cli_invalid_cleanup(self):
        a=prepare(source());self.assertEqual(header(a),header(prepare(source())))
        for us in [0,1,2000000,333333,7200000000]:
            self.assertLessEqual(abs(cycles(us)*1000000-us*16777216),500000)
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);inp=p/'song.json';inp.write_text(json.dumps(source()))
            cmd=[sys.executable,'tools/adapt_chart.py',str(inp),'--difficulty','Easy','--instrument','five_fret_lead_guitar','--output-dir',str(p/'out'),'--synthetic']
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            inp.write_text('{}')
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertFalse((p/'out/imported_chart.hpp').exists())
            self.assertFalse((p/'out/adapted.json').exists())


if __name__=='__main__':unittest.main()
