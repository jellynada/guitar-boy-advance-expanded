# Your Mission 019 handheld check

Use **Copper Circuit RC2**, unchanged from Mission018. This is a playtest, not
approval for new graphics or a final release. You do not need an all-Perfect run.

[Download the ROM directly](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/437410b45881119084cf675735b30cf3c841dad5/public-demo-downloads/Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.gba)
or [download the player ZIP](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/437410b45881119084cf675735b30cf3c841dad5/public-demo-downloads/Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.zip).
For the ZIP, right-click it in Windows and choose **Extract All**. Open
`Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.gba` in mGBA, or copy it to your
flash cartridge with the method you normally use. No coding or build setup.

| Difficulty | Buttons from the leftmost lane to the rightmost |
|---|---|
| Easy |LEFT, B, A |
| Medium |LEFT, RIGHT, B, A |
| Hard |LEFT, UP **or** DOWN, RIGHT, B, A |

Hard UP and DOWN are two choices for the same lane. Try a diagonal such as
UP+RIGHT; you never need to push opposite directions together.

- [ ] Record GBA model, flash cartridge and that you used **RC2**.
- [ ] Play one complete Easy song, then Medium and Hard. Try chords and diagonals.
- [ ] Hold several long notes; release one early while keeping another held.
- [ ] Miss deliberately: guitar should mute, backing should continue; hit again
      and check the guitar returns.
- [ ] Press START to pause/resume several times, including during a long note.
      Try keeping START held briefly; it should not repeatedly toggle.
- [ ] Keep a fret held through pause. Then try releasing/repressing while paused.
      Score/time should stay frozen. A new press **after** resume with no new note
      can legitimately show WRONG; it does not award the old note again.
- [ ] While paused, SELECT should return to the selector. START+SELECT exits.
- [ ] Finish, view results, replay with A/START, then return with B/SELECT.
      Switch difficulties and restart; old scores should clear.
- [ ] Play for roughly20–30 minutes if convenient. Report stutter, popping,
      noticeable drift, highway flicker, stuck input, freeze or crash, with the
      difficulty and whether it followed a pause/replay.

Medium's final note deliberately replaces an earlier same-button hold. That
existing pattern is preserved by your previous choice. Your positive RC1 report
remains useful history; this checklist has **not** been marked complete for you.

Reply in plain English, for example: “GBA SP, [cartridge], RC2. Easy/Medium/Hard
finished. Pause/replay worked. I heard [problem/no problem] after [action].”
Listening feedback cannot alone resolve the strict sub-millisecond emulator
comparison. Optional recording details are in [the audio plan](M019_AUDIO_GATE.md).

ROM SHA-256: `9c4af95ff97eddd266dca3d7491ac9a5b1256f417684aae51b7c126443afafde`.
ZIP SHA-256: `194c34e77deade95e2c60f4d57cc55c946dbd199cf56cf48cfb9fd1e2d08b77b`.
