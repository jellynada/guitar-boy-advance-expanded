import unittest
from tools.release_status import status

class ReleaseGates(unittest.TestCase):
    def setUp(self):
        self.identity=dict(source_commit='a'*40,rom_sha256='b'*64)
        self.build=dict(self.identity,status='success');self.game=dict(self.identity,result='passed');self.digital=dict(self.identity,passed=True)
        self.output=dict(self.identity,release_gate='passed',passed=15,total=15)
    def test_all_technical_pass_is_not_owner_approval(self):
        r=status(self.build,self.game,self.digital,self.output)
        self.assertTrue(all(r[k]for k in ['build_succeeded','gameplay_passed','digital_passed','audio_output_passed']))
        self.assertFalse(r['owner_accepted']);self.assertFalse(r['release_approved'])
    def test_audio_failure_cannot_hide_behind_build_success(self):
        r=status(self.build,self.game,self.digital,dict(self.identity,release_gate='blocked',passed=9,total=15))
        self.assertTrue(r['build_succeeded']);self.assertFalse(r['audio_output_passed']);self.assertFalse(r['release_approved'])
    def test_stale_digital_identity_cannot_pass(self):
        self.digital['rom_sha256']='c'*64
        r=status(self.build,self.game,self.digital,self.output);self.assertFalse(r['digital_passed']);self.assertFalse(r['release_approved'])
    def test_partial_matrix_cannot_pass(self):
        r=status(self.build,self.game,self.digital,dict(self.identity,release_gate='passed',passed=9,total=9));self.assertFalse(r['audio_output_passed'])

    def test_stale_output_cannot_pass(self):
        self.output['source_commit']='d'*40
        r=status(self.build,self.game,self.digital,self.output);self.assertFalse(r['audio_output_passed'])
