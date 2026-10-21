"""Original score/synth source for Mission017; no recordings or external assets.

This does not clear inherited game code/art or authorize a public ROM upload.
The immutable source arrangement is 42 bars; Arcade75 retains its first40.
"""
import argparse
import hashlib
import json
from pathlib import Path
import wave
import numpy as np

TITLE = 'Copper Circuit'
RATE, BPM, PPQ = 16384, 128, 192
BEAT_SAMPLES = RATE * 60 // BPM  #7680, exact
BARS = 42
COUNT = BARS * 4 * BEAT_SAMPLES
ROOTS = (40, 36, 43, 38)  # E minor / C / G / D, original arrangement
MELODY = ((52, 59, 55, 59, 62, 59, 55, 54),
          (48, 55, 52, 55, 60, 59, 55, 52),
          (55, 62, 59, 62, 67, 66, 62, 59),
          (50, 57, 54, 57, 62, 60, 57, 54))


def frequency(pitch):
    return 440 * 2 ** ((pitch - 69) / 12)


def arrange():
    events = []
    charts = {'Easy': [], 'Medium': [], 'Hard': []}
    def head(d, tick, lanes, duration=1):
        for lane in lanes: charts[d].append((tick, lane, duration))
    for bar in range(BARS):
        chord = (bar // 2) % 4
        for eighth in range(8):
            tick = bar * 4 * PPQ + eighth * PPQ // 2
            pitch = MELODY[chord][eighth]
            # B section raises the phrase; outro returns to the root.
            if 16 <= bar < 24 and eighth in (2, 6): pitch += 12
            if bar >= 39: pitch = ROOTS[chord] + (12 if eighth % 2 == 0 else 19)
            duration = PPQ if eighth == 7 and bar % 4 == 3 else PPQ // 2
            events.append(dict(role='guitar', tick=tick, pitch=pitch, duration_ticks=duration,
                               accent=eighth % 2 == 0))
            events.append(dict(role='bass', tick=tick, pitch=ROOTS[chord], duration_ticks=PPQ//2))
            events.append(dict(role='hat', tick=tick, duration_ticks=PPQ//4))
            if eighth % 2 == 0: events.append(dict(role='kick', tick=tick, duration_ticks=PPQ//2))
            if eighth in (2, 6): events.append(dict(role='snare', tick=tick, duration_ticks=PPQ//2))
        if bar < 40:
            for beat in (0, 2):
                lane = (bar + beat // 2) % 3
                lanes = (1, 2) if bar % 8 == 7 and beat == 2 else (lane,)
                head('Easy', (bar*4+beat)*PPQ, lanes, PPQ if beat == 0 and bar % 4 == 0 else 1)
            for beat, lane in enumerate((0, 2, 1, 3)):
                lanes = ((0, 2) if bar % 8 == 3 else (1, 3)) if bar % 4 == 3 and beat == 2 else (lane,)
                head('Medium', (bar*4+beat)*PPQ, lanes, PPQ*3//2 if beat == 3 and bar % 4 == 3 else 1)
            for eighth, lane in enumerate((0, 3, 1, 4, 2, 3, 1, 4)):
                lanes = (0, 3, 4) if bar % 8 == 7 and eighth == 4 else (0, 1) if bar % 8 == 3 and eighth == 0 else (lane,)
                head('Hard', bar*4*PPQ+eighth*PPQ//2, lanes, PPQ if eighth == 7 and bar % 4 == 3 else 1)
    # Resolve final chord before the source ring-out; holds cross the75s cut.
    for difficulty in charts:
        onset = 39*4*PPQ + 7*PPQ//2
        charts[difficulty] = [n for n in charts[difficulty] if n[0] != onset]
        head(difficulty, onset, (2 if difficulty=='Easy' else 3 if difficulty=='Medium' else 4,), PPQ*2)
        charts[difficulty].sort()
    return events, charts


def render(events):
    guitar = np.zeros(COUNT, dtype=np.float64)
    backing = np.zeros(COUNT, dtype=np.float64)
    def add(target, start, signal):
        count = min(len(signal), len(target)-start)
        if count > 0: target[start:start+count] += signal[:count]
    for e in events:
        start = e['tick'] * BEAT_SAMPLES // PPQ
        duration = e['duration_ticks'] * BEAT_SAMPLES // PPQ
        role = e['role']; length = duration + (RATE//12 if role=='guitar' else 0)
        t = np.arange(length, dtype=np.float64)/RATE
        attack = np.minimum(1., t*800)
        release = np.minimum(1., np.maximum(0., (length/RATE-t)*100))
        if role=='guitar':
            f = frequency(e['pitch'])
            tone = sum(np.sin(2*np.pi*f*h*t) * (0.66**(h-1))/h for h in range(1, 7))
            body = np.tanh(2.4*tone) * np.exp(-t*7)
            signal = body * attack * release * (.30 if e['accent'] else .22)
            add(guitar, start, signal)
        elif role=='bass':
            f = frequency(e['pitch']); signal=(np.sin(2*np.pi*f*t)+.15*np.sin(4*np.pi*f*t))*np.exp(-t*6)*attack*release*.25
            add(backing, start, signal)
        elif role=='kick':
            phase = 2*np.pi*(45*t+55*(1-np.exp(-t*40))/40)
            add(backing,start,np.sin(phase)*np.exp(-t*25)*attack*.35)
        else:
            # Stateless integer noise: no downloaded sample or random-seed state.
            indices=np.arange(length,dtype=np.uint64)+np.uint64(start)
            hashed=(indices+0x9e3779b9)&0xffffffff
            hashed=((hashed^(hashed>>16))*0x85ebca6b)&0xffffffff
            hashed=((hashed^(hashed>>13))*0xc2b2ae35)&0xffffffff
            hashed=hashed^(hashed>>16)
            noise=(hashed>>16).astype(np.float64)/32768-1
            # Band-limit source percussion for the GBA's8-bit/16kHz output.
            # This is part of the original instrument, not a runtime effect.
            noise=np.convolve(noise,np.array([1.,2.,3.,2.,1.])/9,mode='same')
            decay=40 if role=='hat' else 22
            amp=.035 if role=='hat' else .12
            add(backing,start,noise*np.exp(-t*decay)*attack*amp)
    # Fixed, documented synthesis gain; never normalize quiet passages upward.
    return guitar*.80, backing*.80


def generate(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    events, charts=arrange();guitar,backing=render(events)
    hashes={}
    for name,values in [('guitar.wav',guitar),('backing.wav',backing)]:
        if np.max(np.abs(values))>=1: raise ValueError('Source synthesis clipped')
        pcm=np.rint(values*32767).astype('<i2').tobytes()
        with wave.open(str(output/name),'wb')as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm)
        hashes[name]=hashlib.sha256((output/name).read_bytes()).hexdigest()
    (output/'song.ini').write_text('[song]\nname = '+TITLE+'\nartist = Guitar Boy Advance Expanded original demo\n')
    text='[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 128000\n}\n'
    for difficulty,notes in charts.items():
        text+='['+difficulty+'Single]\n{\n'+''.join(f'{tick} = N {lane} {duration}\n'for tick,lane,duration in notes)+'}\n'
    (output/'notes.chart').write_text(text)
    provenance=dict(title=TITLE,tempo_bpm=BPM,source_bars=BARS,source_samples=COUNT,source_seconds=COUNT/RATE,
        playable_bars=40,playable_seconds=75,origin='New score, melody, arrangement, charts and deterministic synthesizer written for Mission017; no external recordings or copied chart data.',
        rights_scope='New composition/source generation only; no license is asserted for inherited game code or artwork.',
        sections=['opening/riff','A development','upper-register B','A return','closing/ring-out'],
        stems=hashes,source_chart_heads={d:len(n)for d,n in charts.items()},synthesis='Plucked harmonic drive guitar; tonal bass; synthesized kick, noise snare and hats. Separate guitar/backing roles.')
    (output/'composition-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return provenance


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args();print(json.dumps(generate(a.output),indent=2))
