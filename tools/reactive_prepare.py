"""Two aligned, independently controllable signed8 streams; host only."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import tempfile
try:
    from .audio_prepare import RATE, PRE_ROLL, TAIL, GUARD, MAX_SAMPLES, MAX_ROM_AUDIO, decode, decoder_version
except ImportError:
    from audio_prepare import RATE, PRE_ROLL, TAIL, GUARD, MAX_SAMPLES, MAX_ROM_AUDIO, decode, decoder_version


def save_reactive(guitar, backing, report, destination):
    if not guitar or len(guitar)!=len(backing) or len(guitar)>MAX_SAMPLES:
        raise ValueError('Reactive streams must have equal, nonzero, bounded sample counts.')
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    blobs=[]
    for pcm in (guitar,backing):
        blob=bytes(PRE_ROLL)+bytes(pcm)+bytes(TAIL+GUARD)
        blob+=bytes((-len(blob))%16);blobs.append(blob)
    if sum(map(len,blobs))>MAX_ROM_AUDIO:raise ValueError('Two-stream audio exceeds30MiB; song not shortened or downsampled.')
    report.update(schema_version='gba-reactive-audio-v1',format='signed8_pcm',sample_rate=RATE,channels=1,
                  source_samples=len(guitar),source_duration_seconds=len(guitar)/RATE,
                  pre_roll_samples=PRE_ROLL,tail_samples=TAIL,guard_samples=GUARD,
                  playback_samples=PRE_ROLL+len(guitar)+TAIL,byte_size=len(blobs[0]),
                  total_byte_size=sum(map(len,blobs)),pcm_sha256=hashlib.sha256(blobs[0]).hexdigest(),
                  backing_sha256=hashlib.sha256(blobs[1]).hexdigest(),
                  origin='No trimming; codec pre-skip honored; same32768sample pre-roll for both; shorter ends zero padded.')
    (destination/'imported_audio.bin').write_bytes(blobs[0]);(destination/'imported_backing.bin').write_bytes(blobs[1])
    (destination/'audio.json').write_text(json.dumps(report,indent=2)+'\n')
    (destination/'audio_report.txt').write_text(f"Two synchronized mono signed8 streams at{RATE}Hz; {len(guitar)} source samples ({len(guitar)/RATE:.6f}s).\nTotal ROM audio:{report['total_byte_size']}bytes.\n{report['mix_rule']}\nOnly the candidate guitar stream is gated. Backing never follows judgment state. Instrument isolation needs human confirmation.\n")
    return report


def convert_reactive(guitar_paths,backing_paths,destination):
    paths=[Path(p) for p in guitar_paths+backing_paths]
    if len(guitar_paths)!=1 or not backing_paths or len(paths)>8:
        raise ValueError('Select exactly one guitar stream and1–7backing streams explicitly.')
    if len(set(p.resolve() for p in paths))!=len(paths):raise ValueError('A file cannot be selected twice or in both roles.')
    version=decoder_version();sources=[]
    with tempfile.TemporaryDirectory(prefix='gba-reactive-') as tmp:
        streams=[]
        for i,p in enumerate(paths):
            values,info=decode(p,Path(tmp),i);info['playback_role']='guitar' if i==0 else 'backing'
            streams.append(values);sources.append(info)
        count=max(map(len,streams));g=array('d',[0])*count;b=array('d',[0])*count
        # Same N-source averaging as Mission006, before separating the roles.
        for n,values in enumerate(streams):
            target=g if n==0 else b
            for i,x in enumerate(values):target[i]+=x/len(paths)
        peak=max(abs(x)+abs(y) for x,y in zip(g,b))
        gain=.85/max(1.,peak);outputs=[];snrs=[]
        for values in (g,b):
            pcm=bytearray(count);signal=noise=0.
            for i,x in enumerate(values):
                value=x*gain*127;q=math.floor(value+.5) if value>=0 else math.ceil(value-.5)
                q=max(-127,min(127,q));pcm[i]=q&255;signal+=value*value;noise+=(value-q)**2
            outputs.append(pcm);snrs.append(round(10*math.log10(signal/noise),3) if signal and noise else None)
        signed=lambda x:x if x<128 else x-256
        maxsum=max(abs(signed(x))+abs(signed(y)) for x,y in zip(*outputs))
        if maxsum>127:raise ValueError('Unsafe guitar/backing peak; no clipped output accepted.')
        return save_reactive(*outputs,dict(synthetic=False,sources=sources,ffmpeg_version=version,
            mix_rule='Downmix mono, sum/N selected source files by explicit role; shared gain0.85/max(1,max(abs(guitar)+abs(backing))); separately round signed8; zero-pad ends; no trimming/no dither.',
            gain=gain,absolute_sum_peak=peak,quantized_absolute_sum_peak=maxsum,
            quantization_snr_db=dict(guitar=snrs[0],backing=snrs[1]),
            role_verification='Roles are explicit candidate assignments, not automatic instrument isolation. See private stem inspection and human listening limitations.'),destination)


def synthetic_reactive(song,destination):
    notes=next(t['notes'] for t in song['tracks'] if t['difficulty']=='Easy' and t['instrument']=='five_fret_lead_guitar')
    count=max(12*RATE,(max(n['start_us'] for n in notes)*RATE+999999)//1000000+RATE)
    g=bytearray(count);b=bytearray(count);next_note=0;freq=262;phase=0;seed=1
    for i in range(count):
        while next_note<len(notes) and i*1000000>=notes[next_note]['start_us']*RATE:
            freq=(262,330,392)[notes[next_note]['lane']];next_note+=1
        phase=(phase+freq*65536//RATE)&65535
        tri=(phase if phase<32768 else 65535-phase)-16384
        # Sustained, bright test voice; not sustain-note gameplay.
        g[i]=(tri*48//16384)&255
        bassphase=(i*97*65536//RATE)&65535
        bass=((bassphase if bassphase<32768 else 65535-bassphase)-16384)*24//16384
        seed=(1664525*seed+1013904223)&0xffffffff
        pulse=i%(RATE//2)
        drum=((seed>>24)-128)*max(0,512-pulse)//8192
        b[i]=max(-36,min(36,bass+drum))&255
    return save_reactive(g,b,dict(synthetic=True,sources=[],mix_rule='Original continuous triangle lead and distinct97Hz bass/noise percussion. Guitar peak48, backing peak36; no third-party recording.'),destination)
