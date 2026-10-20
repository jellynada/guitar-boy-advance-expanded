"""Original two-stem 80s fixture with valid and impossible physical chords."""
from pathlib import Path
try:
    from .generate_song_examples import audio
except ImportError:
    from generate_song_examples import audio


def generate(output):
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    (output / 'song.ini').write_text('[song]\nname = Original Arcade75 Exercise\nartist = Project synthetic generator\n')
    text = '[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 120000\n}\n'
    for difficulty, lanes in [('Easy', 3), ('Medium', 4), ('Hard', 5)]:
        notes = [(i * 384, i % lanes, 192 if i % 9 == 1 else 1) for i in range(80) if i not in (10, 12, 20, 30, 40, 41)]
        for second, chord in [(10, [0, 1] if lanes == 4 else [0, 2] if lanes == 5 else [0, 1]),
                              (12, list(range(lanes))),
                              (20, [0, lanes-2, lanes-1]),
                              (30, list(range(lanes))),
                              (40, [1]), (41, [0, 2] if lanes == 5 else [2])]:
            notes += [(second * 384, lane, 768 if second == 40 else 192 if second in (12, 30) else 1) for lane in chord]
        # Exact source cutoff, plus existing notes beyond it, exercises exclusion.
        notes += [(28799, lanes-1, 192)]  # 74.997396s, clipped hold and late-window EOF
        text += '[' + difficulty + 'Single]\n{\n' + ''.join(f'{t} = N {lane} {duration}\n' for t, lane, duration in sorted(notes)) + '}\n'
    (output / 'notes.chart').write_text(text)
    audio(output / 'guitar.wav', 80, 220); audio(output / 'backing.wav', 80, 110)
    return output


def prepare_example(output):
    import tempfile
    try:
        from .song_pipeline import prepare
    except ImportError:
        from song_pipeline import prepare
    with tempfile.TemporaryDirectory(prefix='gba-original-arcade-') as tmp:
        source = generate(Path(tmp) / 'source')
        return prepare(source, output, difficulty='All', guitar='guitar.wav', backing=['backing.wav'], max_duration=75, handheld=True)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('output', type=Path)
    prepare_example(p.parse_args().output)
