"""Original synthetic MIDI/package tests. No third-party charts or music."""
import contextlib
from fractions import Fraction
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.chart_importer import InvalidChart, normalize
from tools.midi_importer import normalize_midi, parse_midi
from tools.song_package import inspect, Package
from tools.import_song import import_song


def vlq(n):
    result = [n & 127]
    while n >> 7:
        n >>= 7
        result.insert(0, (n & 127) | 128)
    return bytes(result)


def meta(kind, data):
    return bytes((255, kind)) + vlq(len(data)) + data


def midi(tracks, resolution=192, fmt=1):
    chunks = []
    for events in tracks:
        previous, body = 0, bytearray()
        for tick, payload in events:
            body += vlq(tick - previous) + payload
            previous = tick
        body += b'\x00\xff\x2f\x00'
        chunks.append(b'MTrk' + struct.pack('>I', len(body)) + body)
    return b'MThd' + struct.pack('>IHHH', 6, fmt, len(tracks), resolution) + b''.join(chunks)


def tempo(us):
    return meta(0x51, us.to_bytes(3, 'big'))


def name(text):
    return meta(3, text.encode())


def on(pitch, channel=0, velocity=100):
    return bytes((0x90 | channel, pitch, velocity))


def off(pitch, channel=0):
    return bytes((0x80 | channel, pitch, 0))


def fixture():
    # Independent arithmetic at PPQ192: 192 ticks at .5s/q = .5s;
    # 384..576 at 1s/q = 1s; 576..768 at .25s/q = .25s.
    return midi([[(0, tempo(500000)), (0, meta(0x58, bytes((4,2,24,8)))),
                  (384, tempo(1000000)), (576, tempo(250000))],
                 [(0, name('PART GUITAR')), (0, on(60)), (0, on(84)),
                  (0, on(96)), (1, off(60)), (1, off(84)), (1, off(96)),
                  (192, on(72)), (384, on(73)), (384, on(74)),
                  (384, on(77)), (385, off(73)), (385, off(74)), (385, off(77)),
                  (576, on(75)), (577, off(75)), (768, off(72))]])


class MidiTests(unittest.TestCase):
    def test_checked_in_fixture_matches_generator(self):
        self.assertEqual(Path("tests/fixtures/midi/tempo_changes.mid").read_bytes(), fixture())

    def test_four_difficulties_exact_tempo_and_sustain(self):
        song = normalize_midi(fixture())
        self.assertEqual([t['difficulty'] for t in song['tracks']], ['Easy','Medium','Hard','Expert'])
        notes = song['tracks'][1]['notes']
        self.assertEqual([n['start_us'] for n in notes], [500000,1000000,1000000,2000000])
        self.assertEqual(notes[0]['end_us'], 2250000)
        self.assertEqual(notes[0]['duration_us'], 1750000)
        self.assertEqual([p['time_us'] for p in song['tempo_map']], [0,1000000,2000000])
        self.assertEqual(song['tracks'][1]['modifiers'][0]['kind'], 'force_hopo')
        self.assertEqual(len(notes), 4)  # forcing marker must not become a note

    def test_type_zero_running_status_zero_velocity(self):
        raw = midi([[(0, name('PART GUITAR')), (0, tempo(500000)),
                     (0,on(72)), (0,bytes((73,100))),
                     (192,bytes((72,0))), (192,bytes((73,0)))]], fmt=0)
        notes = normalize_midi(raw)['tracks'][1]['notes']
        self.assertEqual([n['duration_us'] for n in notes], [500000,500000])

    def test_exact_nonintegral_bpm(self):
        raw = midi([[(0,tempo(500001))],[(0,name('PART GUITAR')),
                    (1,on(96)),(2,off(96))]], resolution=3)
        n = normalize_midi(raw)['tracks'][3]['notes'][0]
        self.assertEqual(n['start_us_exact'], {'numerator':166667,'denominator':1})
        self.assertEqual(n['duration_us'],166667)

    def test_channels_paired_separately(self):
        raw=midi([[(0,tempo(500000))],[(0,name('PART GUITAR')),
                  (0,on(96,0)),(192,off(96,0)),(192,on(96,1)),(384,off(96,1))]])
        self.assertEqual([n['source_channel'] for n in normalize_midi(raw)['tracks'][3]['notes']], [0,1])

    def test_markers_instruments_and_unknowns(self):
        raw=midi([[(0,tempo(500000))],[(0,name('PART GUITAR')),
                  (0,on(96)),(0,on(104)),(0,on(116)),(0,on(110)),
                  (192,off(96)),(192,off(104)),(192,off(116)),(192,off(110))],
                  [(0,name('PART DRUMS')),(0,on(96)),(192,off(96))],
                  [(0,name('PART BASS')),(0,on(84)),(192,off(84))]])
        diagnostics=[]; song=normalize_midi(raw,diagnostics=diagnostics)
        self.assertEqual(sum(len(t['notes']) for t in song['tracks']),2)
        kinds={e.get('kind') for e in song['tracks'][3]['special_events']}
        self.assertTrue({'tap','star_power','uninterpreted_midi_note'} <= kinds)
        self.assertIn('2:PART DRUMS',song['unsupported_sections'])
        self.assertTrue(any(d['code']=='MIDI_UNKNOWN_PITCH' for d in diagnostics))

    def test_enhanced_opens_required(self):
        for enabled in (False,True):
            ev=[(0,name('PART GUITAR'))]
            if enabled: ev += [(0,meta(1,b'[ENHANCED_OPENS]'))]
            ev += [(0,on(59)),(0,on(96)),(192,off(59)),(192,off(96))]
            song=normalize_midi(midi([[(0,tempo(500000))],ev]))
            self.assertEqual(len(song['tracks'][0]['notes']),int(enabled))
            if enabled: self.assertIsNone(song['tracks'][0]['notes'][0]['lane'])

    def test_sysex_preserved_not_fake_notes(self):
        payload=b'PS\x00\x00\x03\x04\x01\xf7'
        ev=[(0,name('PART GUITAR')),(0,b'\xf0'+vlq(len(payload))+payload),
            (0,on(96)),(192,off(96))]
        diagnostics=[];song=normalize_midi(midi([[(0,tempo(500000))],ev]),diagnostics=diagnostics)
        self.assertEqual(len(song['tracks'][3]['notes']),1)
        self.assertTrue(any(e.get('recognized_marker')=='tap_phrase' for e in song['tracks'][3]['special_events']))
        self.assertTrue(any(d['code']=='MIDI_SYSEX_RETAINED' for d in diagnostics))

    def test_equivalent_chart_and_midi_independent_values(self):
        text='''[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 120000\n384 = B 60000\n576 = B 240000\n}\n[MediumSingle]\n{\n192 = N 0 576\n384 = N 1 1\n384 = N 2 1\n576 = N 3 1\n}\n'''
        a=normalize(text)['tracks'][0]['notes'];b=normalize_midi(fixture())['tracks'][1]['notes']
        projection=lambda notes:[(n['tick'],n['lane'],n['start_us'],n['end_us']) for n in notes]
        self.assertEqual(projection(a),projection(b))
        self.assertEqual(projection(a),[(192,0,500000,2250000),(384,1,1000000,1005208),(384,2,1000000,1005208),(576,3,2000000,2001302)])

    def test_event_limit_and_invalid_data_bytes(self):
        with patch('tools.midi_importer.MAX_EVENTS', 2), self.assertRaises(InvalidChart) as err:
            parse_midi(fixture())
        self.assertEqual(err.exception.code, 'MIDI_EVENTS')
        for event in (b'\x90\x80\x01', b'\xf1\x00', b'\xff\x80\x00'):
            with self.subTest(event=event), self.assertRaises(InvalidChart):
                parse_midi(midi([[(0, event)]]))

    def test_extended_header_and_single_byte_channel_events(self):
        raw=midi([[(0,tempo(500000))],[(0,name('PART GUITAR')),
                  (0,b'\xc0\x05'),(0,b'\xd0\x01'),(0,on(96)),(192,off(96))]])
        raw=raw[:4]+struct.pack('>I',8)+raw[8:14]+b'xx'+raw[14:]
        self.assertEqual(normalize_midi(raw)['tracks'][3]['notes'][0]['duration_us'],500000)

    def test_duplicate_instrument_and_ambiguous_channels(self):
        guitar=[(0,name('PART GUITAR')),(0,on(96)),(192,off(96))]
        for tracks in ([[(0,tempo(500000))],guitar,guitar],
                       [[(0,tempo(500000))],[(0,name('PART GUITAR')),(0,on(96,0)),(0,on(96,1)),(192,off(96,0)),(192,off(96,1))]]):
            with self.assertRaises(InvalidChart):normalize_midi(midi(tracks))

    def test_missing_tempo_and_bad_names(self):
        for raw,code in [(midi([[(0,name('PART GUITAR')),(0,on(96)),(1,off(96))]]),'MISSING_INITIAL_TEMPO'),
                         (midi([[(0,tempo(500000))],[(0,name('DRUMS')),(0,on(96)),(1,off(96))]]),'NO_SUPPORTED_NOTES')]:
            with self.assertRaises(InvalidChart) as error: normalize_midi(raw)
            self.assertEqual(error.exception.code,code)

    def test_malformed_pairing(self):
        cases=[([(0,on(96)),(1,on(96)),(2,off(96))],'MIDI_OVERLAPPING_NOTE'),
               ([(0,off(96))],'MIDI_UNPAIRED_OFF'), ([(0,on(96))],'MIDI_UNCLOSED_NOTE')]
        for events,code in cases:
            with self.subTest(code=code),self.assertRaises(InvalidChart) as error:
                normalize_midi(midi([[(0,tempo(500000))],[(0,name('PART GUITAR'))]+events]))
            self.assertEqual(error.exception.code,code)

    def test_truncated_every_prefix(self):
        raw=fixture()
        for length in range(len(raw)):
            with self.subTest(length=length),self.assertRaises(InvalidChart): parse_midi(raw[:length])

    def test_bad_structures(self):
        raw=fixture()
        for data in [b'garbage',raw+b'junk', raw[:8]+struct.pack('>HHH',2,2,192)+raw[14:],
                     raw[:12]+b'\xe7\x28'+raw[14:],
                     midi([[(0,b'\xff\x51\x02\x01\x01')]]),
                     midi([[(0,b'\xff\x51\x03\x00\x00\x00')]]),
                     midi([[(0,tempo(500000)),(0,tempo(600000))]]),
                     midi([[(0,tempo(500000)),(0,meta(0x58,b'\x04\x02'))]]),
                     midi([[(0,tempo(500000)),(0,meta(0x58,b'\x00\x02\x18\x08'))]]),
                     midi([[(0,tempo(500000)),(0,meta(0x54,b'\x00'*5))]])]:
            with self.subTest(data=data[:20]),self.assertRaises(InvalidChart): normalize_midi(data)

    def test_running_status_reset_and_vlq(self):
        ev=[(0,on(96)),(0,meta(1,b'text')),(1,bytes((96,0)))]
        with self.assertRaises(InvalidChart) as err: parse_midi(midi([ev]))
        self.assertEqual(err.exception.code,'MIDI_RUNNING_STATUS')
        raw=midi([[(0,tempo(500000))]])
        bad=raw[:18]+struct.pack('>I',5)+b'\x81\x81\x81\x81\x00'
        with self.assertRaises(InvalidChart): parse_midi(bad)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.song=self.root/'synthetic';self.song.mkdir()
        (self.song/'notes.mid').write_bytes(fixture())
        (self.song/'song.ini').write_text('[song]\nname = Synthetic Song\nartist = Test Author\ncharter = Fixture\ndelay = 250\ndiff_guitar = 3\n',encoding='utf8')
        for stem in ('song','guitar','rhythm','preview'):
            (self.song/(stem+'.opus')).write_bytes(b'not audio; discovery test only')

    def tearDown(self): self.temp.cleanup()

    def inspect(self,source=None,**kwargs):
        diagnostics=[];song,tracks=inspect(source or self.song,diagnostics,**kwargs)
        return song,tracks,diagnostics

    def test_metadata_stems_offsets_counts_and_compatibility(self):
        song,tracks,_=self.inspect()
        self.assertEqual(song['metadata']['Name'],'Synthetic Song')
        self.assertEqual(song['package']['song_ini']['charter'],'Fixture')
        self.assertEqual(song['package']['song_ini']['diff_guitar'],'3')
        n=song['tracks'][1]['notes'][0]
        self.assertEqual((n['start_us'],n['end_us'],n['duration_us']),(750000,2500000,1750000))
        streams=song['package']['audio_streams']
        self.assertEqual(len(streams),4)
        self.assertEqual(sum(s['selected_for_future_adapter'] for s in streams),3)
        self.assertEqual(tracks[1]['note_count'],4)
        self.assertEqual(tracks[1]['chord_count'],1)
        self.assertFalse(any(t['playable_now'] for t in tracks))

    def test_shared_markers_not_shifted_four_times(self):
        (self.song/'notes.mid').write_bytes(midi([[(0,tempo(500000))],[(0,name('PART GUITAR')),
                           (0,on(96)),(0,on(116)),(192,off(96)),(192,off(116))]]))
        song,_,_=self.inspect()
        self.assertEqual(song['tracks'][3]['special_events'][0]['start_us'],250000)

    def test_negative_half_microsecond_offset(self):
        (self.song/'song.ini').write_text('[song]\ndelay = -0.0005\n')
        song,_,_=self.inspect()
        self.assertEqual(song['tracks'][0]['notes'][0]['start_us'],-1)
        self.assertEqual(song['tracks'][0]['notes'][0]['start_us_exact'],{'numerator':-1,'denominator':2})

    def test_sustain_dpad_overlap_and_release_boundary(self):
        raw=midi([[(0,tempo(500000))],[(0,name('PART GUITAR')),
                  (0,on(72)),(192,on(73)),(384,off(72)),(384,off(73))]])
        (self.song/'notes.mid').write_bytes(raw)
        _,tracks,warnings=self.inspect()
        self.assertEqual(tracks[1]['sustain_dpad_conflicts'][0]['kind'],'opposing_directions')
        self.assertTrue(any(w['code']=='DPAD_SUSTAIN_OVERLAP' for w in warnings))
        raw=midi([[(0,tempo(500000))],[(0,name('PART GUITAR')),
                  (0,on(72)),(192,off(72)),(192,on(73)),(384,off(73))]])
        (self.song/'notes.mid').write_bytes(raw)
        self.assertEqual(self.inspect()[1][1]['sustain_dpad_conflicts'],[])

    def test_other_audio_formats_and_unknown_name(self):
        for n in ('guitar.opus','song.opus','rhythm.opus'):(self.song/n).unlink()
        for n in ('guitar.wav','rhythm.mp3','song.ogg'):(self.song/n).write_bytes(b'discovery only')
        self.assertEqual({s['format'] for s in self.inspect()[0]['package']['audio_streams']},{'opus','ogg','wav','mp3'})
        (self.song/'unknown.opus').write_bytes(b'unknown role')
        with self.assertRaises(InvalidChart):self.inspect()

    def test_zip_nested_folder_and_size_limits(self):
        z=self.root/'nested.zip'
        with zipfile.ZipFile(z,'w') as out:
            for p in sorted(self.song.iterdir()):out.write(p,'Song/'+p.name)
        self.assertEqual(self.inspect(z)[0]['package']['chart_file'],'Song/notes.mid')
        with patch('tools.song_package.MAX_ENTRIES',2),self.assertRaises(InvalidChart):self.inspect(z)
        with patch('tools.song_package.MAX_TOTAL',10),self.assertRaises(InvalidChart):self.inspect(z)
        with Package(z) as package,self.assertRaises(InvalidChart):package.read('Song/notes.mid',2)

    def test_ini_encoding_and_no_audio_read(self):
        (self.song/'song.ini').write_bytes('[song]\nname = Caf\xe9\ndelay = 0\n'.encode('latin1'))
        # A corrupt audio stream must not be decoded or confused with a valid codec.
        song,_,warnings=self.inspect()
        self.assertEqual(song['metadata']['Name'],'Café')
        self.assertTrue(any(w['code']=='INI_ENCODING' for w in warnings))
        self.assertFalse(any(s['decoded'] for s in song['package']['audio_streams']))

    def test_zip_and_folder_equivalence(self):
        z=self.root/'synthetic.zip'
        with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
            for p in sorted(self.song.iterdir()): out.write(p,p.name)
        self.assertEqual(self.inspect()[0],self.inspect(z)[0])

    def test_explicit_chart_selection(self):
        (self.song/'another.mid').write_bytes(fixture())
        with self.assertRaises(InvalidChart) as error:self.inspect()
        self.assertEqual(error.exception.code,'CHART_SELECTION')
        self.assertEqual(self.inspect(chart='notes.mid')[0]['source_name'],'notes.mid')

    def test_audio_ambiguity_and_selection(self):
        (self.song/'song.ogg').write_bytes(b'dummy')
        with self.assertRaises(InvalidChart) as error:self.inspect()
        self.assertEqual(error.exception.code,'AUDIO_SELECTION')
        song,_,_=self.inspect(audio=['song.opus','guitar.opus'])
        self.assertEqual(sum(s['selected_for_future_adapter'] for s in song['package']['audio_streams']),2)

    def test_preview_only_not_gameplay(self):
        for stem in ('song','guitar','rhythm'):(self.song/(stem+'.opus')).unlink()
        song,_,warnings=self.inspect()
        self.assertIn('gameplay audio',song['package']['missing_files'])
        self.assertTrue(any(w['code']=='MISSING_AUDIO' for w in warnings))

    def test_chart_offsets_require_choice(self):
        (self.song/'notes.mid').unlink()
        (self.song/'notes.chart').write_text('[Song]\n{\nResolution = 192\nOffset = .5\n}\n[SyncTrack]\n{\n0 = B 120000\n}\n[MediumSingle]\n{\n192 = N 0 0\n}\n')
        with self.assertRaises(InvalidChart) as err:self.inspect()
        self.assertEqual(err.exception.code,'OFFSET_SELECTION')
        for policy,expected in [('add',1250000),('ini',750000),('chart',1000000)]:
            song,_,_=self.inspect(offset_policy=policy)
            self.assertEqual(song['tracks'][0]['notes'][0]['start_us'],expected)

    def test_ini_errors(self):
        for text in ['[song]\ndelay = nan\n','[song]\nname=a\nname=b\n','[other]\nname=a\n']:
            (self.song/'song.ini').write_text(text)
            with self.assertRaises((InvalidChart,ValueError,__import__('configparser').Error)):self.inspect()

    def test_deterministic_outputs_and_invalid_removes_stale(self):
        out=self.root/'output'
        with contextlib.redirect_stdout(io.StringIO()):self.assertTrue(import_song(self.song,out))
        first={p.name:p.read_bytes() for p in (out/'synthetic').iterdir()}
        with contextlib.redirect_stdout(io.StringIO()):self.assertTrue(import_song(self.song,out))
        self.assertEqual(first,{p.name:p.read_bytes() for p in (out/'synthetic').iterdir()})
        (self.song/'notes.mid').write_bytes(b'bad')
        with contextlib.redirect_stdout(io.StringIO()):self.assertFalse(import_song(self.song,out))
        self.assertFalse((out/'synthetic/song.json').exists())
        self.assertFalse(json.loads((out/'synthetic/report.json').read_text())['playable_now'])

    def test_cli_single_mid(self):
        result=subprocess.run([sys.executable,'tools/import_song.py',str(self.song/'notes.mid'),'--output-dir',str(self.root/'out')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Playable in current GBA engine: NO',result.stdout)

    def test_zip_unsafe_paths_and_symlinks(self):
        for path in ['../escape','/absolute','C:/escape','a/../../escape','a\\escape','a//b','./a']:
            z=self.root/'unsafe.zip'
            with zipfile.ZipFile(z,'w') as out:out.writestr(path,b'x')
            with self.subTest(path=path),self.assertRaises(InvalidChart):self.inspect(z)
        z=self.root/'symlink.zip';info=zipfile.ZipInfo('link');info.create_system=3;info.external_attr=0o120777<<16
        with zipfile.ZipFile(z,'w') as out:out.writestr(info,'../../escape')
        with self.assertRaises(InvalidChart):self.inspect(z)
        (self.song/'unsafe').symlink_to(self.song/'notes.mid')
        with self.assertRaises(InvalidChart):self.inspect()

    def test_zip_ratio_duplicates_collisions_truncated(self):
        z=self.root/'bad.zip'
        with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:out.writestr('bomb',b'0'*2_000_000)
        with self.assertRaises(InvalidChart) as err:self.inspect(z)
        self.assertEqual(err.exception.code,'ZIP_SIZE')
        for names in [('Notes.mid','notes.mid'),('a','a/notes.mid')]:
            with zipfile.ZipFile(z,'w') as out:
                for n in names:out.writestr(n,b'x')
            with self.assertRaises(InvalidChart):self.inspect(z)
        z.write_bytes(b'PK\x03\x04bad')
        with self.assertRaises(zipfile.BadZipFile):self.inspect(z)


if __name__=='__main__': unittest.main()
