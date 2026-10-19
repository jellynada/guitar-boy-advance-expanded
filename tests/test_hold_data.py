import unittest
from tools.validate_holds import validate
from tools.adapt_chart import adapt,header
from tools.chart_importer import normalize
from pathlib import Path

class HoldDataTests(unittest.TestCase):
    def fixture(self):
        song=normalize(Path('tests/fixtures/runtime/easy.chart').read_text())
        return header(adapt(song,difficulty='Easy',instrument='five_fret_lead_guitar',synthetic=True))
    def test_fixture_contains_only_six_genuine_holds(self):self.assertEqual(validate(self.fixture()),(25,6))
    def test_mismatched_parallel_arrays_rejected(self):
        with self.assertRaises(ValueError):validate(self.fixture().replace('imported_note_count = 25','imported_note_count = 26'))
    def test_bad_easy_lane_rejected(self):
        text=self.fixture().replace('0U, 0U}', '3U, 0U}',1)
        with self.assertRaises(ValueError):validate(text)
    def test_too_short_audio_rejected(self):
        with self.assertRaises(ValueError):validate(self.fixture(),100)
    def test_duration_bound_rejected(self):
        text=self.fixture().replace('1000000ULL,','7200000001ULL,',1)
        with self.assertRaises(ValueError):validate(text)
