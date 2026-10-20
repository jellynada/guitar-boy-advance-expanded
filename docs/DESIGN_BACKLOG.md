# Approved directions for later missions — not implemented in Mission012

## Physical lane order and input conflicts

Imported Easy currently maps **Left / A / B**, unchanged in Mission012. The owner
reports the physical B button sits between the D-pad and A. Proposed next mapping:

- Easy: **Left / B / A**.
- Medium: **Left / Right / B / A**.
- Hard: **Left / (Up or Down) / Right / B / A**.

Up and Down would be alternative physical buttons for **one logical lane**, never
two distinct notes. Before implementation, specify input-edge behavior when
switching Up to Down during a sustain, whether overlap keeps a hold alive, and
what conflicting directions mean. Remap chart adaptation, diagnostics, sprites,
judgment inputs and tests together in an explicitly approved gameplay mission.

## Sustain and near-fret feedback

Future behavior: lane-colored head, dim lane-colored approaching tail, white
subtly glowing/pulsing tail only during a valid active hold. Early release breaks
and removes the remaining tail; successful completion proceeds normally. Add
clear success feedback near the relevant fret. No such effects are implemented.

## Audio and cartridge capacity

The current roughly four-minute real song uses about9MB with dual signed8 PCM
streams (about8.87MB for the two imported streams alone). Ten similar songs will
not fit in a conventional32MiB GBA ROM. Investigate compression, CPU/DMA costs,
random access, synchronization, stem gating and packaging before designing a song
library. No codec, mixer, sample rate, on-device ZIP/MIDI parser or multi-song menu
change belongs in Mission012.

First priorities: validate the Windows launcher with the owner, investigate the
remaining emulator comparisons and hardware stack/timing margins, then scope
physical-order remapping. Stable-release licensing remains a separate gate.
