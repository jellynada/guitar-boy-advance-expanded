# Original synthetic MIDI fixture

Written for this project, not transcribed from a song. No audio is included.
`tests/test_song_package.py:fixture` constructs the same bytes in memory.

PPQ 192; MIDI tempo changes at ticks 0/384/576 use 500000/1000000/250000
microseconds per quarter note. All four guitar difficulties are present.
Medium contains a 192..768 sustain and a chord at tick384.

Before INI delay: starts .5/1/1/2 seconds, first sustain ends2.25seconds and
lasts1.75seconds. INI delay+250ms produces starts .75/1.25/1.25/2.25seconds
and sustain end2.5seconds, unchanged duration. Short one-tick release lengths
are deliberately retained; no player-specific sustain cutoff is applied.

Try: `python3 tools/import_song.py tests/fixtures/midi`
Open `imports/output/packages/midi/report.txt`. Missing-audio warning is expected.
