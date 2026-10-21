"""Negative checks for the narrowly approved development/release separation."""
import copy
import unittest
from tools.foundation_development_gate import check, RC2, HASH

class FoundationGate(unittest.TestCase):
    def setUp(self):
        self.statuses={x:'success'for x in ['build','gameplay','digital','soak','focused-audio']}
        self.statuses['audio-output']='failure'
        self.source=dict(runtime_build_inputs_identical=True,runtime_identity=RC2,
            expected_rom_sha256=HASH,owner_foundation_accepted=True,pr_merge_approved=False,
            candidate_commit='candidate',candidate_tree='tree')
        self.audio=dict(source_commit=RC2,rom_sha256=HASH,passed=9,total=15,release_gate='blocked',
            results=[dict(difficulty=d,case=c,exit_code=int(c in [4,22]))for d in range(3)for c in [19,4,22,0,12]])
    def test_known_limitation_does_not_approve_merge_release_or_graphics(self):
        r=check(self.audio,self.statuses,self.source)
        self.assertEqual(r['development_integration_checks'],'passed')
        for k in ['pr_merge_approved','release_approved','graphics_authorized','strict_audio_passed']:self.assertFalse(r[k])
    def test_transport_failure_blocks_development(self):
        self.statuses['digital']='failure'
        with self.assertRaises(ValueError):check(self.audio,self.statuses,self.source)
    def test_changed_rom_rejected(self):
        self.audio['rom_sha256']='a'*64
        with self.assertRaises(ValueError):check(self.audio,self.statuses,self.source)
    def test_new_audio_failure_rejected(self):
        self.audio['results'][0]['exit_code']=1
        with self.assertRaises(ValueError):check(self.audio,self.statuses,self.source)
    def test_relocated_audio_failure_rejected(self):
        self.audio['results'][0]['exit_code']=1;self.audio['results'][1]['exit_code']=0
        with self.assertRaises(ValueError):check(self.audio,self.statuses,self.source)
    def test_partial_matrix_rejected(self):
        self.audio['results'].pop()
        with self.assertRaises(ValueError):check(self.audio,self.statuses,self.source)
    def test_changed_candidate_source_rejected(self):
        self.source['runtime_build_inputs_identical']=False
        with self.assertRaises(ValueError):check(self.audio,self.statuses,self.source)
    def test_unreviewed_audio_improvement_requires_review(self):
        self.statuses['audio-output']='success'
        with self.assertRaises(ValueError):check(self.audio,self.statuses,self.source)
    def test_crash_cannot_replace_known_assertion_failure(self):
        self.audio['results'][1]['exit_code']=-11
        with self.assertRaises(ValueError):check(self.audio,self.statuses,self.source)
