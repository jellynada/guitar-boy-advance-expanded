#!/usr/bin/env python3
"""Generate two original synthetic packages locally; no recordings are committed."""
import argparse
from pathlib import Path
import struct
import wave
import zipfile

RATE = 16384


def audio(path, seconds, frequency):
    # Integer triangle wave, deterministic PCM16 mono; no downloaded content.
    pcm = bytearray()
    for i in range(seconds * RATE):
        phase = i * frequency % RATE
        value = (phase if phase < RATE // 2 else RATE - phase) - RATE // 4
        pcm += struct.pack('<h', value * 2)
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm)


def vlq(value):
    result = [value & 127]
    while value >> 7:
        value >>= 7;result.insert(0, (value & 127) | 128)
    return bytes(result)


def track(events):
    previous, data = 0, bytearray()
    for tick, event in sorted(events, key=lambda e: e[0]):
        data += vlq(tick - previous) + event;previous = tick
    data += b'\0\xff\x2f\0'
    return b'MTrk' + struct.pack('>I', len(data)) + data


def generate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    pulse, drift = output / 'pulse', output / 'drift'
    pulse.mkdir();drift.mkdir()
    (pulse / 'song.ini').write_text('[song]\nname = Original Pulse\nartist = Project synthetic generator\n')
    (pulse / 'notes.chart').write_text('[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 120000\n}\n[EasySingle]\n{\n' +
        '\n'.join(f'{i*192} = N {i%3} {96 if i in (1,4) else 1}' for i in range(6)) + '\n}\n')
    audio(pulse / 'melody.wav', 6, 220)
    (drift / 'song.ini').write_text('[song]\nname = Original Tempo Drift\nartist = Project synthetic generator\ndelay = 125\n')
    tempos = [(0, b'\xff\x51\x03' + (500000).to_bytes(3, 'big')),
              (384, b'\xff\x51\x03' + (750000).to_bytes(3, 'big')),
              (960, b'\xff\x51\x03' + (400000).to_bytes(3, 'big'))]
    events = [(0, b'\xff\x03\x0bPART GUITAR')]
    for i in range(8):
        tick, pitch = i * 192, 60 + i % 3
        events += [(tick, bytes([0x90, pitch, 100])),
                   (tick + (96 if i in (1,3,5) else 1), bytes([0x80, pitch, 0]))]
    (drift / 'notes.midi').write_bytes(b'MThd' + struct.pack('>IHHH', 6, 1, 2, 192) + track(tempos) + track(events))
    audio(drift / 'lead.wav', 8, 330);audio(drift / 'accompaniment.wav', 8, 110)
    archive = output / 'drift.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(drift.iterdir()):
            entry = zipfile.ZipInfo(path.name, (1980, 1, 1, 0, 0, 0));entry.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(entry, path.read_bytes())
    return pulse, archive


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    for path in generate(p.parse_args().output):
        print(path)
