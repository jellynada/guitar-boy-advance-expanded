import copy,json,tempfile,unittest
from pathlib import Path
from tools.song_collection import validate,inspect_package
SPEC={'schema':'gba-song-collection-v1','profile':'public','entries':[{'id':'copper-circuit','package':'public:synth-demo'},{'id':'synthetic-easy-fixture','package':'public:synth-demo-2'}]}
class CollectionValidation(unittest.TestCase):
 def test_verifier_cli_needs_no_numpy(self):
  import subprocess,sys
  result=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve().parents[1]/'tools/song_collection.py'),'--help'],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stderr)
 def test_original_ordinary_windows_retained(self):
  s=(Path(__file__).resolve().parents[1]/'tools/test_collection.py').read_text()
  self.assertIn("'6.322,37.5,76.7'",s)
  self.assertIn('},265"',s)
 def test_explicit_public(self):self.assertEqual(validate(copy.deepcopy(SPEC)),SPEC)
 def reject(self,fn):
  s=copy.deepcopy(SPEC);fn(s)
  with self.assertRaises((ValueError,KeyError,TypeError)):validate(s)
 def test_duplicate_id(self):self.reject(lambda s:s['entries'][1].update(id='copper-circuit'))
 def test_duplicate_asset(self):self.reject(lambda s:s['entries'][1].update(package='public:synth-demo'))
 def test_private_in_public(self):self.reject(lambda s:s['entries'][1].update(package='private:prepared',prepared='unapproved'))
 def test_public_input_override(self):self.reject(lambda s:s['entries'][0].update(prepared='unapproved'))
 def test_malformed_id(self):self.reject(lambda s:s['entries'][0].update(id='../bad'))
 def test_missing_id(self):self.reject(lambda s:s['entries'][0].pop('id'))
 def test_unallowlisted(self):self.reject(lambda s:s['entries'][0].update(package='other'))
 def test_too_many(self):self.reject(lambda s:s.update(entries=s['entries']*17))
 def test_empty(self):self.reject(lambda s:s.update(entries=[]))
 def test_unknown_profile(self):self.reject(lambda s:s.update(profile='anything'))
 def test_wrong_public_identity(self):self.reject(lambda s:s['entries'][0].update(id='wrong'))
 def test_unknown_keys(self):self.reject(lambda s:s.update(directory='Playlist'))
if __name__=='__main__':unittest.main()
