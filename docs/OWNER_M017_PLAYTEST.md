# Your Copper Circuit handheld playtest

This is a playable test candidate, not an accepted release. A strict emulator
audio comparison still fails; please pay special attention to music timing.

1. Download the `.gba` directly, or download the ZIP and choose **Extract All**
   in Windows. Open `Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC1.gba` in mGBA
   or copy that exact file onto your compatible GBA flash cartridge. No build
   tools are needed. Existing mGBA users can use File → Load ROM.
2. Select **Copper Circuit** with A. Choose Easy first, then Medium and Hard.
   Easy is LEFT/B/A; Medium LEFT/RIGHT/B/A; Hard LEFT/UP-or-DOWN/RIGHT/B/A.
   On an emulator, map those GBA buttons in its controller settings first.
3. Press each note as it reaches the line. Each new note needs a new press.
   Keep long notes held. Try chords and overlapping holds. In Hard, move from
   Up to both Up+Down to Down: the shared lane should stay held.
4. Intentionally miss several notes: guitar should disappear while drums/bass
   continue. Hit a later note: guitar should return. Listen through the ending.
5. Press START during a hold. Wait10seconds: score, notes and music must freeze.
   Resume with START. Try keeping a button held, releasing it while paused and
   repressing after resume. Report extra WrongInput or unexpected sustain loss.
   Repeat near the final notes. SELECT while paused returns to selection.
6. Finish all75seconds. Results must appear. A/START replays; B/SELECT returns.
   Restart several times and check that the first notes still respond.
7. Check readability, flicker, missing tails, stutter, clicks or drifting music.
   Tell me your console/flash cartridge (or mGBA version), difficulty, what
   happened and roughly when. A short recording helps if convenient.

Please report pass/fail for each difficulty and the pause/repress test. Only
**your** real-handheld results can establish owner acceptance. No acceptance
has been assumed from automated tests.
