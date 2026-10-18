"""Original synthetic chart fixtures; no copyrighted song or audio inputs."""
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from tools.chart_importer import InvalidChart, compatibility, cpp_assets, normalize

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/charts"


def chart(notes="0 = N 0 0", sync="0 = B 120000", resolution="192", offset="0", track="MediumSingle"):
    return f"[Song]\n{{\nResolution = {resolution}\nOffset = {offset}\n}}\n[SyncTrack]\n{{\n{sync}\n}}\n[{track}]\n{{\n{notes}\n}}\n"


def load(text, messages=None):
    return normalize(text, diagnostics=messages)["tracks"][0]["notes"]


class ImporterTests(unittest.TestCase):
    def assert_invalid(self, text, code):
        with self.assertRaises(InvalidChart) as result:
            normalize(text)
        self.assertEqual(result.exception.code, code)

    def test_hand_calculated_fixture_outputs(self):
        expected = json.loads((FIXTURES / "expected.json").read_text())
        for name, values in expected.items():
            with self.subTest(name=name):
                song = normalize((FIXTURES / name).read_text())
                track = next(t for t in song["tracks"] if t["section"] == values["track"])
                self.assertEqual([n["start_us"] for n in track["notes"]], values["start_us"])
                self.assertEqual([n["duration_us"] for n in track["notes"]], values["duration_us"])

    def test_multiple_tempo_boundaries_and_sustain(self):
        song = normalize((FIXTURES / "tempo_changes.chart").read_text())
        self.assertEqual([p["time_us"] for p in song["tempo_map"]], [250000, 1250000, 2250000])
        sustain = song["tracks"][1]["notes"][0]
        # .5 s at 120 BPM + 1 s at 60 BPM + .25 s at 240 BPM.
        self.assertEqual(sustain["duration_us"], 1750000)
        self.assertEqual(sustain["end_us"], 2500000)
        self.assertEqual(song["time_signatures"][1], dict(tick=384, numerator=3, denominator=4))

    def test_exact_tempo_boundary_uses_new_segment_after_boundary(self):
        notes = load(chart("192 = N 0 0\n193 = N 1 0\n384 = N 2 0", "0 = B 120000\n192 = B 60000"))
        self.assertEqual([n["start_us"] for n in notes], [500000, 505208, 1500000])
        self.assertEqual(notes[1]["start_us_exact"], dict(numerator=1515625, denominator=3))

    def test_resolution_changes_do_not_change_musical_time(self):
        for resolution in [96, 192, 480, 960]:
            with self.subTest(resolution=resolution):
                notes = load(chart(f"{resolution} = N 0 {resolution}", resolution=str(resolution)))
                self.assertEqual((notes[0]["start_us"], notes[0]["duration_us"]), (500000, 500000))

    def test_exact_rational_no_per_segment_rounding_drift(self):
        sync = "\n".join(f"{i} = B {120000 if i % 2 == 0 else 90000}" for i in range(100))
        note = load(chart("100 = N 0 0", sync, "3"))[0]
        # 50/3 beats at 120 BPM plus 50/3 beats at 90 BPM.
        self.assertEqual(note["start_us_exact"], dict(numerator=175000000, denominator=9))
        self.assertEqual(note["start_us"], 19444444)

    def test_offsets_are_explicit_and_applied_once(self):
        for offset, expected in [("0.25", 250000), ("-0.25", -250000), (".125", 125000), ("+1.5", 1500000)]:
            with self.subTest(offset=offset):
                note = load(chart("0 = N 0 192", offset=offset))[0]
                self.assertEqual((note["start_us"], note["duration_us"], note["end_us"]), (expected, 500000, expected + 500000))
        implicit = normalize(chart().replace("Offset = 0\n", ""))
        self.assertFalse(implicit["timing"]["offset_explicit"])
        self.assertEqual(implicit["timing"]["offset_seconds"], "0")

    def test_fractional_negative_offsets_and_rounding_endpoints(self):
        note = load(chart("0 = N 0 1", resolution="1", offset="-0.0000005"))[0]
        self.assertEqual(note["start_us"], -1)
        self.assertEqual(note["end_us"], 500000)
        self.assertEqual(note["duration_us"], 500001)  # rounded_end - rounded_start
        self.assertEqual(note["duration_us_exact"], dict(numerator=500000, denominator=1))

    def test_simultaneous_notes_stay_in_source_order(self):
        notes = load(chart("192 = N 3 0\n192 = N 0 192\n192 = N 2 96"))
        self.assertEqual([n["lane"] for n in notes], [3, 0, 2])
        self.assertEqual([n["source_order"] for n in notes], [0, 1, 2])
        self.assertEqual([n["start_us"] for n in notes], [500000] * 3)

    def test_difficulties_independent_and_expert_not_relabeled(self):
        messages = []
        song = normalize((FIXTURES / "tempo_changes.chart").read_text(), diagnostics=messages)
        report = compatibility(song, messages)
        self.assertEqual([t["difficulty"] for t in song["tracks"]], ["Easy", "Medium", "Hard", "Expert"])
        self.assertEqual([t["note_count"] for t in report], [3, 5, 3, 2])
        self.assertTrue(all(not t["playable_now"] for t in report))
        self.assertIsNone(report[3]["planned_button_layout"])
        self.assertIn("EXPERT_NOT_REMAPPED", [m["code"] for m in messages])

    def test_lanes_are_not_collapsed_to_fit_future_layout(self):
        messages = []
        song = normalize(chart("0 = N 4 0", track="EasySingle"), diagnostics=messages)
        report = compatibility(song, messages)
        self.assertEqual(song["tracks"][0]["notes"][0]["lane"], 4)
        self.assertEqual(report[0]["fret_slots_required"], 5)
        self.assertIn("PLANNED_LAYOUT_TOO_SMALL", [m["code"] for m in messages])

    def test_modifiers_open_notes_and_special_phrases_preserved(self):
        song = normalize((FIXTURES / "tempo_changes.chart").read_text())
        expert = song["tracks"][3]
        self.assertEqual([m["kind"] for m in expert["modifiers"]], ["hopo_flip", "tap"])
        self.assertEqual(len(expert["notes"]), 2)  # markers are NOT extra notes
        self.assertEqual(expert["notes"][1]["source_lane"], 7)
        self.assertIsNone(expert["notes"][1]["lane"])
        self.assertEqual(expert["special_events"][0]["phrase_id"], 2)
        self.assertEqual(expert["special_events"][1]["text"], "soloend")
        self.assertEqual(song["global_events"][0]["payload"], '"section Synthetic section"')

    def test_range_modifiers_are_retained_and_warned(self):
        messages = []
        song = normalize(chart("0 = N 0 0\n0 = N 5 192"), diagnostics=messages)
        self.assertEqual(song["tracks"][0]["modifiers"][0]["duration_us"], 500000)
        self.assertIn("RANGE_MODIFIER", [m["code"] for m in messages])
        self.assert_invalid(chart("0 = N 5 0\n192 = N 0 0"), "ORPHAN_MODIFIER")

    def test_dpad_opposition_and_diagonal_reports(self):
        for difficulty, notes, expected in [
            ("MediumSingle", "0 = N 0 0\n0 = N 1 0", "opposing_directions"),
            ("HardSingle", "0 = N 0 0\n0 = N 2 0", "opposing_directions"),
            ("HardSingle", "0 = N 0 0\n0 = N 1 0", "diagonal_requires_playtest"),
        ]:
            messages = []
            song = normalize(chart(notes, track=difficulty), diagnostics=messages)
            report = compatibility(song, messages)
            self.assertEqual(report[0]["dpad_conflicts"][0]["kind"], expected)

    def test_negative_times_report_preroll(self):
        messages = []
        song = normalize(chart(offset="-1"), diagnostics=messages)
        compatibility(song, messages)
        self.assertIn("NEGATIVE_TIME", [m["code"] for m in messages])

    def test_bad_bpm_resolution_and_offset(self):
        for bpm in ["0", "-120000", "nan", "4294967296"]:
            with self.subTest(bpm=bpm), self.assertRaises(InvalidChart):
                normalize(chart(sync=f"0 = B {bpm}"))
        for resolution in ["0", "-1", "1.5", "4294967296"]:
            with self.subTest(resolution=resolution), self.assertRaises(InvalidChart):
                normalize(chart(resolution=resolution))
        for offset in ["NaN", "Infinity", "1e5", "abc"]:
            with self.subTest(offset=offset):
                self.assert_invalid(chart(offset=offset), "INVALID_OFFSET")

    def test_missing_sections_and_initial_tempo(self):
        self.assert_invalid("[Song]\n{\nResolution = 192\n}", "MISSING_SECTION")
        self.assert_invalid("[SyncTrack]\n{\n0 = B 120000\n}", "MISSING_SECTION")
        self.assert_invalid(chart().replace("Resolution = 192\n", ""), "MISSING_RESOLUTION")
        self.assert_invalid(chart(sync="192 = B 120000"), "MISSING_INITIAL_TEMPO")
        self.assert_invalid(chart(notes=""), "NO_SUPPORTED_NOTES")

    def test_unknown_tracks_retained_not_treated_as_guitar(self):
        messages = []
        song = normalize(chart() + "[ExpertDrums]\n{\n0 = N 1 0\n}\n", diagnostics=messages)
        self.assertEqual(song["unsupported_sections"]["ExpertDrums"][0]["text"], "0 = N 1 0")
        self.assertEqual(len(song["tracks"]), 1)
        self.assertIn("UNSUPPORTED_TRACK", [m["code"] for m in messages])

    def test_unknown_note_ids_and_events_rejected(self):
        for event in ["0 = N 8 0", "0 = N -1 0", "0 = N 0 -1", "0 = N 0", "0 = X 1 0"]:
            with self.subTest(event=event), self.assertRaises(InvalidChart):
                normalize(chart(event))
        self.assert_invalid(chart(sync="0 = B 120000\n1 = X 2"), "UNSUPPORTED_SYNC")

    def test_duplicate_and_unsorted_events_rejected(self):
        self.assert_invalid(chart("1 = N 0 0\n1 = N 0 192"), "DUPLICATE_NOTE")
        self.assert_invalid(chart("2 = N 0 0\n1 = N 1 0"), "UNSORTED_EVENTS")
        self.assert_invalid(chart(sync="0 = B 120000\n0 = B 60000"), "DUPLICATE_SYNC")
        self.assert_invalid(chart(sync="0 = B 120000\n20 = B 60000\n10 = B 180000"), "UNSORTED_EVENTS")
        self.assert_invalid(chart() + "[MediumSingle]\n{\n}\n", "DUPLICATE_SECTION")
        self.assert_invalid(chart().replace("Resolution = 192", "Resolution = 192\nResolution = 480"), "DUPLICATE_METADATA")

    def test_time_signatures_do_not_change_timing(self):
        signatures = normalize(chart("192 = N 0 0", "0 = TS 7 3\n0 = B 120000\n96 = TS 3"))
        self.assertEqual(signatures["time_signatures"], [dict(tick=0, numerator=7, denominator=8), dict(tick=96, numerator=3, denominator=4)])
        self.assertEqual(signatures["tracks"][0]["notes"][0]["start_us"], 500000)
        for ts in ["0 -1", "0 2", "4 32"]:
            with self.subTest(ts=ts), self.assertRaises(InvalidChart):
                normalize(chart(sync=f"0 = TS {ts}\n0 = B 120000"))

    def test_editor_anchors_do_not_override_tempo_timing(self):
        for time, conflict in [(500000, False), (600000, True)]:
            messages = []
            song = normalize(chart("192 = N 0 0", f"0 = B 120000\n192 = A {time}"), diagnostics=messages)
            self.assertEqual(song["tracks"][0]["notes"][0]["start_us"], 500000)
            self.assertEqual(song["anchors"][0]["audio_time_us"], time)
            self.assertEqual("ANCHOR_CONFLICT" in [m["code"] for m in messages], conflict)

    def test_large_timestamps_and_overflow(self):
        self.assert_invalid(chart(f"{2**64} = N 0 0"), "NUMBER_RANGE")
        self.assert_invalid(chart(f"{2**64-1} = N 0 1"), "TICK_OVERFLOW")
        self.assert_invalid(chart(f"{2**64-1} = N 0 0", "0 = B 1"), "TIME_OVERFLOW")
        self.assert_invalid(chart(offset="9223372036855"), "TIME_OVERFLOW")
        note = load(chart(f"{2**64-1} = N 4 0", "0 = B 4000000000", "4000000000"))[0]
        exact = Fraction((2**64-1) * 60_000_000_000, 4000000000**2)
        self.assertEqual(note["start_us_exact"], dict(numerator=exact.numerator, denominator=exact.denominator))
        self.assertLess(note["start_us"], 2**63)

    def test_parser_comments_bom_quotes_and_malformed_braces(self):
        text = '\ufeff' + chart().replace("Resolution = 192", 'Name = "Synthetic https://example.test/π" // comment\nResolution = 192')
        self.assertEqual(normalize(text)["metadata"]["Name"], "Synthetic https://example.test/π")
        self.assert_invalid(chart()[:-2], "UNCLOSED_SECTION")
        self.assert_invalid(chart().replace("[Song]\n{", "[Song]\nResolution = 1"), "MISSING_BRACE")

    def check_headers_with_compiler(self, compiler, flags=()):
        texts = [(FIXTURES / "tempo_changes.chart").read_text(), chart(offset="-0.0000005"),
                 chart(f"{2**64-1} = N 4 0", "0 = B 4000000000", "4000000000"),
                 chart(offset="-9223372036854.775808"), chart(offset="9223372036854.775807")]
        for text in texts:
            digest = hashlib.sha256(text.encode()).hexdigest()
            song = normalize(text)
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp)
                (path / "song_data.hpp").write_text(cpp_assets(song, digest))
                (path / "check.cpp").write_text('#include "song_data.hpp"\n')
                result = subprocess.run([compiler, *flags, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(path / "check.cpp")], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_generated_headers_compile_with_host_compiler(self):
        compiler = shutil.which("g++")
        self.assertIsNotNone(compiler, "g++ is required for header checks")
        self.check_headers_with_compiler(compiler)

    def test_generated_headers_compile_with_gba_compiler(self):
        devkit = Path(os.environ.get("DEVKITARM", str(ROOT.parent / ".cloud-setup/gba/devkitpro/devkitARM")))
        compiler = devkit / "bin/arm-none-eabi-g++"
        if not compiler.exists():
            self.skipTest("devkitARM not present; only host header compilation checked")
        self.check_headers_with_compiler(str(compiler), ("-mcpu=arm7tdmi", "-mthumb"))

    def test_cli_determinism_sidecar_and_failed_reimport(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            source = path / "test.chart"
            source.write_bytes((FIXTURES / "constant.chart").read_bytes())
            (path / "song.ini").write_text("[song]\ndelay=123\n")
            def run(folder):
                return subprocess.run(["python3", str(ROOT / "tools/import_chart.py"), str(source), "--output-dir", str(path / folder)], capture_output=True, text=True)
            self.assertEqual(run("a").returncode, 0)
            self.assertEqual(run("b").returncode, 0)
            for name in ["song.json", "song_data.hpp", "report.json", "report.txt"]:
                self.assertEqual((path / "a/test" / name).read_bytes(), (path / "b/test" / name).read_bytes())
            report = json.loads((path / "a/test/report.json").read_text())
            self.assertEqual(report["status"], "prepared_not_playable")
            self.assertEqual(report["tempo_point_count"], 1)
            self.assertEqual(report["tempo_change_count"], 0)
            self.assertIn("SIDECAR_INI_NOT_APPLIED", [m["code"] for m in report["diagnostics"]])
            (path / "a/test/keep.txt").write_text("user file")
            source.write_text(chart(resolution="0"))
            self.assertEqual(run("a").returncode, 1)
            self.assertFalse((path / "a/test/song_data.hpp").exists())
            self.assertFalse((path / "a/test/song.json").exists())
            self.assertEqual((path / "a/test/keep.txt").read_text(), "user file")
            self.assertFalse(json.loads((path / "a/test/report.json").read_text())["valid"])

    def test_batch_workflow_continues_past_invalid_charts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tools").mkdir()
            (root / "imports/incoming").mkdir(parents=True)
            for name in ["import_chart.py", "chart_importer.py"]:
                shutil.copyfile(ROOT / "tools" / name, root / "tools" / name)
            command = ["python3", str(root / "tools/import_chart.py")]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            (root / "imports/incoming/a_bad.chart").write_text("invalid")
            (root / "imports/incoming/b_good.chart").write_text(chart())
            result = subprocess.run(command, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertTrue((root / "imports/output/b_good/song_data.hpp").exists())
            self.assertFalse((root / "imports/output/a_bad/song_data.hpp").exists())

    def test_duplicate_global_events_rejected(self):
        self.assert_invalid(chart() + '[Events]\n{\n0 = E "section A"\n0 = E "section A"\n}\n', "DUPLICATE_EVENT")

    def test_non_chart_inputs_and_invalid_utf8_report_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            for name, data, code in [("not_audio.mp3", b"synthetic bytes, not actual audio", "WRONG_EXTENSION"), ("bad.chart", b"\xff", "READ_OR_WRITE_ERROR")]:
                source = path / name
                source.write_bytes(data)
                result = subprocess.run(["python3", str(ROOT / "tools/import_chart.py"), str(source), "--output-dir", str(path / "out")], capture_output=True)
                self.assertEqual(result.returncode, 1)
                report = json.loads((path / "out" / source.stem / "report.json").read_text())
                self.assertIn(code, [item["code"] for item in report["diagnostics"]])
                self.assertNotIn(b"Traceback", result.stderr)

    def test_dot_only_filenames_cannot_escape_output_root(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            source = path / "...chart"
            source.write_text(chart())
            result = subprocess.run(["python3", str(ROOT / "tools/import_chart.py"), str(source), "--output-dir", str(path / "out")], capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse((path / "song.json").exists())
            self.assertIn(b"Rename", result.stderr)

    def test_empty_difficulty_is_reported_not_prepared(self):
        messages = []
        song = normalize(chart() + "[EasySingle]\n{\n}\n", diagnostics=messages)
        tracks = compatibility(song, messages)
        self.assertFalse(tracks[1]["prepared"])
        self.assertEqual(tracks[1]["note_count"], 0)
        self.assertIn("EMPTY_TRACK", [m["code"] for m in messages])

    def test_original_demo_is_valid_without_legacy_timing_changes(self):
        text = (ROOT / "charts/careless.chart").read_text(encoding="utf-8-sig")
        notes = load(text)
        self.assertEqual(len(notes), 699)
        self.assertEqual({n["lane"] for n in notes}, {0, 1, 2, 3})
        self.assertTrue(all(n["duration_us"] == 0 for n in notes))
        # First note is 2688 / 192 = 14 beats at 83.330 BPM.
        self.assertEqual(notes[0]["start_us_exact"], dict(numerator=84000000000, denominator=8333))


if __name__ == "__main__":
    unittest.main()
