"""Bounded host decoding and deterministic signed8 mono ROM audio preparation."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

RATE=16384
PRE_ROLL=2*RATE
TAIL=RATE//2
GUARD=RATE  # more than a full VBlank of reads, never logical music
MAX_SAMPLES=1800*RATE
MAX_ROM_AUDIO=30*1024*1024


def decoder_version():
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ValueError('Install FFmpeg and ffprobe. Ubuntu/WSL: sudo apt install ffmpeg. Check: ffmpeg -version; ffprobe -version.')
    return subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]


def decode(path, work, index):
    probe=subprocess.run(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-format_whitelist','ogg,mp3,wav,flac','-select_streams','a','-show_entries','stream=codec_name,sample_rate,channels:format=duration','-of','json',str(path)],capture_output=True,text=True,timeout=30)
    if probe.returncode:
        raise ValueError(f'Cannot decode {path.name}: {probe.stderr.strip()}')
    info=json.loads(probe.stdout)
    streams=info.get('streams',[])
    if len(streams)!=1:
        raise ValueError(f'{path.name}: require exactly one audio stream, found {len(streams)}.')
    duration=float(info.get('format',{}).get('duration','0'))
    if not math.isfinite(duration) or duration>1800:
        raise ValueError(f'{path.name}: unsupported duration (maximum30minutes).')
    output=work/f'decoded-{index}.f32'
    command=['ffmpeg','-nostdin','-v','error','-threads','1','-bitexact','-protocol_whitelist','file,pipe','-format_whitelist','ogg,mp3,wav,flac','-i',str(path),'-map','0:a:0','-vn',
             '-ac','1','-ar',str(RATE),'-af','aresample=resampler=swr:dither_method=none',
             '-fs',str((MAX_SAMPLES+1)*4),'-f','f32le','-y',str(output)]
    result=subprocess.run(command,capture_output=True,text=True,timeout=180)
    if result.returncode:
        raise ValueError(f'FFmpeg failed for {path.name}: {result.stderr.strip()}')
    raw=output.read_bytes()
    if len(raw)%4 or not raw or len(raw)//4>MAX_SAMPLES:
        raise ValueError(f'{path.name}: decoded samples are empty/invalid/over30minutes; nothing is truncated for a build.')
    samples=array('f');samples.frombytes(raw)
    if sys.byteorder!='little':samples.byteswap()
    if any(not math.isfinite(x) for x in samples):raise ValueError('Non-finite decoded audio.')
    return samples,dict(source_file=path.name,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        codec=streams[0].get('codec_name'),source_rate=streams[0].get('sample_rate'),
                        source_channels=streams[0].get('channels'),decoded_mono_samples=len(samples),
                        source_duration_seconds=duration)


def save_audio(pcm, report, destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    if not pcm or len(pcm)>MAX_SAMPLES:raise ValueError('Empty/overlong audio.')
    playback=bytes(PRE_ROLL)+pcm+bytes(TAIL)
    blob=playback+bytes(GUARD)
    blob+=bytes((-len(blob))%16)
    if len(blob)>MAX_ROM_AUDIO:raise ValueError('Audio exceeds30MiB budget; select a lower-rate future format or shorter song.')
    report.update(schema_version='gba-audio-v1',format='signed8_pcm',sample_rate=RATE,channels=1,
                  source_samples=len(pcm),source_duration_seconds=len(pcm)/RATE,pre_roll_samples=PRE_ROLL,
                  tail_samples=TAIL,playback_samples=len(playback),guard_samples=GUARD,
                  byte_size=len(blob),pcm_sha256=hashlib.sha256(blob).hexdigest(),
                  origin='No leading-silence trim. Decoded source sample zero follows32768zero samples. Decoder applies source codec pre-skip.',
                  source_pcm_sha256=hashlib.sha256(pcm).hexdigest())
    (destination/'imported_audio.bin').write_bytes(blob)
    (destination/'audio.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=[f"Format: signed8 PCM, mono {RATE}Hz",f"Source samples:{len(pcm)}, duration:{len(pcm)/RATE:.6f}s",
           f"ROM audio bytes:{len(blob)}; pre-roll2s, tail0.5s, safety guard1s (not musical duration)",
           f"Sources:{[s['source_file'] for s in report.get('sources',[])]}",f"Conversion:{report.get('mix_rule','original generated synthetic audio')}",
           f"Quantization SNR:{report.get('quantization_snr_db','n/a')}dB; output peak:{report.get('output_peak',0)} /127",
           'No guitar muting, runtime mixing or audio decoding on GBA.']
    (destination/'audio_report.txt').write_text('\n'.join(lines)+'\n')
    return report


def convert_files(paths, destination):
    if not paths:raise ValueError('Select at least one authorized file explicitly.')
    if len(paths)>8:raise ValueError('Maximum8selected stems.')
    if len({Path(p).resolve() for p in paths})!=len(paths):raise ValueError('Duplicate audio selection.')
    version=decoder_version()
    with tempfile.TemporaryDirectory(prefix='gba-audio-') as tmp:
        work=Path(tmp);acc=array('d');sources=[]
        for index,path in enumerate(paths):
            samples,info=decode(Path(path),work,index);sources.append(info)
            if len(samples)>len(acc):acc.extend(array('d',[0.0])*(len(samples)-len(acc)))
            for i,value in enumerate(samples):acc[i]+=value/len(paths)
        peak=max(abs(x) for x in acc)
        gain=0.85/max(1.0,peak) # only reduce; never normalize a quiet source upward
        pcm=bytearray(len(acc));noise=signal=0.0;out_peak=0
        for i,value in enumerate(acc):
            y=value*gain*127
            q=math.floor(y+0.5) if y>=0 else math.ceil(y-0.5)
            q=max(-127,min(127,q));pcm[i]=q&255;out_peak=max(out_peak,abs(q))
            signal+=y*y;noise+=(y-q)**2
        snr=round(10*math.log10(signal/noise),3) if noise and signal else None
        report=dict(synthetic=False,sources=sources,ffmpeg_version=version,
                    mix_rule='Mono downmix each source; average N explicitly selected stems; zero-pad shorter ends; gain0.85/max(1,mix_peak); no trimming/no dither; nearest signed8',
                    gain=gain,mix_peak=peak,output_peak=out_peak,quantization_snr_db=snr,
                    duration_policy='Preserve decoded sample zero; longest selected stem defines end; retain original codec pre-skip via FFmpeg')
        return save_audio(bytes(pcm),report,destination)


def synthetic_audio(song, destination):
    notes=next(t['notes'] for t in song['tracks'] if t['difficulty']=='Easy' and t['instrument']=='five_fret_lead_guitar')
    count=max(12*RATE, (max(n['start_us'] for n in notes)*RATE+999999)//1000000+RATE)
    values=[0]*count
    # Original three-note exercise, integer triangle voices and soft bass pulse.
    for note in notes:
        begin=(note['start_us']*RATE+500000)//1000000
        frequency=(262,330,392)[note['lane']]
        length=RATE//5
        for j in range(min(length,count-begin)):
            phase=(j*frequency*65536//RATE)&65535
            triangle=(phase if phase<32768 else 65535-phase)-16384
            envelope=min(j*64,32768,(length-j)*16)
            values[begin+j]+=triangle*envelope*90//(16384*32768)
    pcm=bytes(max(-108,min(108,x))&255 for x in values)
    return save_audio(pcm,dict(synthetic=True,sources=[],mix_rule='Original integer-generated triangle melody; matching25note synthetic chart; no external recording',output_peak=max(abs(x) for x in values)),destination)
