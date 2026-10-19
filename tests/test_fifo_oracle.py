"""Deliberate signal corruptions must not pass the exact digital oracle."""
import csv
import tempfile
import unittest
from pathlib import Path
import numpy as np
from analyze_fifo import analyze


class FifoOracleTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name);self.prefix=self.root/'capture';self.advance=3
        self.guitar=np.array([0 if i<128 else i%19-9 for i in range(4096)],dtype=np.int8)
        self.backing=np.array([0 if i<128 else (i*7)%17-8 for i in range(4096)],dtype=np.int8)
        events=[];pcm=[];gain=256;audible=True
        for i,(g,b) in enumerate(zip(self.guitar,self.backing)):
            if i in (256,512,768,1024):
                kind=2 if i in (256,768) else 0;events.append(dict(sample=i,kind=kind,gain=gain));audible=kind==0
            gain=min(256,gain+4) if audible else max(0,gain-4)
            product=int(g)*gain;scaled=abs(product)//256
            pcm.append(int(b)+(-scaled if product<0 else scaled))
        self.expected=np.array(pcm,dtype=np.int8)
        (self.root/'imported_audio.bin').write_bytes(self.guitar.tobytes());(self.root/'imported_backing.bin').write_bytes(self.backing.tobytes())
        with Path(str(self.prefix)+'.events.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=['sample','kind','gain']);writer.writeheader();writer.writerows(events)
        self.samples=np.zeros(2048,dtype=[('segment','<u4'),('value','i1'),('cycle','<u8')]);self.samples['segment']=1;self.samples['value']=self.expected[3:2051];self.samples['cycle']=4096+np.arange(2048)*1024
        starts=np.arange(32,2080,4);self.words=np.zeros(len(starts),dtype=[('segment','<u4'),('end','<u4'),('word','<u4'),('cycle','<u8')]);self.words['segment']=1;self.words['end']=starts+4
        for j,start in enumerate(starts):self.words['word'][j]=int.from_bytes(self.expected[start:start+4].tobytes(),'little')
        self.write()

    def write(self):
        self.samples.tofile(str(self.prefix)+'.samples');self.words.tofile(str(self.prefix)+'.fifo')

    def rejected(self):
        self.write()
        with self.assertRaises(ValueError):analyze(self.root,self.prefix,self.advance)

    def test_correct_original_signal(self):
        self.assertEqual(analyze(self.root,self.prefix,3)['digital_mismatches'],0)

    def test_one_consumed_byte(self):
        self.samples['value'][500]^=1;self.rejected()

    def test_one_written_byte(self):
        self.words['word'][200]^=1;self.rejected()

    def test_repeated_sample(self):
        self.samples['value'][400:]=self.samples['value'][399:-1];self.rejected()

    def test_clock_discontinuity(self):
        self.samples['cycle'][1000:]+=1024;self.rejected()

    def test_full_mix_instead_of_muting(self):
        self.samples['value']=self.guitar[3:2051]+self.backing[3:2051];self.rejected()

    def test_backing_disappears(self):
        self.samples['value'][340:450]=0;self.rejected()

    def test_wrong_fixed_startup_offset(self):
        with self.assertRaises(ValueError):analyze(self.root,self.prefix,4)

    def test_source_corruption(self):
        self.guitar[600]^=1;(self.root/'imported_audio.bin').write_bytes(self.guitar.tobytes());self.rejected()

    def test_missing_observation(self):
        self.samples=self.samples[:10];self.rejected()


if __name__=='__main__':unittest.main()
