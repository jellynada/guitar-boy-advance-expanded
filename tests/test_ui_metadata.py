import unittest
from tools.write_song_ui import header
from pathlib import Path
class UiMetadata(unittest.TestCase):
 def test_public_name_has_fixed_original_identity(self):
  s=header('public-demo');self.assertIn('Synth Demo"',s);self.assertIn('copper-circuit',s);self.assertNotIn('Synth Demo 2',s)
 def test_public_cannot_take_package_metadata(self):
  with self.assertRaises(ValueError):header('public-demo',{'metadata':{'Name':'untrusted'}})
 def test_other_existing_fixture_has_honest_separate_name(self):self.assertIn('Synth Demo 2',header('public-synthetic'))
 def test_private_display_names_are_bounded_and_escaped(self):
  s=header('song-private',{'metadata':{'Name':'A"\\\n'+'x'*200,'Artist':'Artist'}});self.assertIn('\\"',s);self.assertNotIn('x'*64,s)
 def test_no_invented_private_title(self):
  self.assertIn('nullptr',header('song-private'))
  with self.assertRaises(ValueError):header('song-private',{'metadata':{}})
 def test_adapters_keep_frozen_assertions(self):
  import tempfile
  from build_ui_probes import generate
  with tempfile.TemporaryDirectory()as d:
   out=generate(Path(__file__).resolve().parents[1],d)
   s=(out/'pause.c').read_text();self.assertIn('assert(!memcmp(image,pixels,sizeof image))',s);self.assertIn('assert(c->busRead32(c,audioUnderruns)==0)',s);self.assertIn('assert(c->busRead32(c,displayedStats+8)==0)',s)
