# Pause/repress event — explained without changing the input contract

The original RC1 case8 still fails its old blanket zero-WrongInput assertion;
that log is retained. New read-only `pause_trace_emulator.c` observes physical
keys, actual Tonc current/previous polled keys, Easy logical lane mask, transport,
musical tick, event serial, score/combo, gate and hold-release counters.

At host frame696 resume completes with START held and no fret held. Resume seeds
judgment input with that actual held state. The tick remains159663104. At frame697
the driver supplies raw2 (B), physical fresh2 and logical lane bit2, in active
play. Tick159925248 produces exactly one WrongInput. Combo9→0, guitar audible→
muted; the old head is not awarded again. There is no new pending note for that
lane in its judgment window. Thus the test driver performs a genuine post-resume
press outside a note opportunity; the game does not manufacture an edge.

This is existing behavior, not an owner-requested change to scoring or input.
A held sustain may continue/recover under the existing50ms release grace, but
a new physical press does not re-award its already judged head or exempt that
press from ordinary WrongInput rules. No extra resume grace or broad input
suppression has been added. Musical time/bonuses do not advance while paused.

Focused actual-ROM cases:8 release paused/repress after resume (one explained
WrongInput);24 release and repress while paused (zero);25 continuously held
(zero);27 release while paused and keep released through resume (zero, normal
hold release). Existing host policy tests cover two independent holds, releasing
B while A continues, LEFT with B, legitimate fresh hits, system-chord sequences
and10-minute held START. Full-ROM old matrix retains repeated pauses, paused
exit, near-EOF, results/replay and Hard alias handoffs. All original assertions
remain intact in tests/pause_emulator.c; the new probe has explicit expectations
for its independently traced case8 rather than silently changing that test.

Medium's final same-lane hold replacement remains unchanged by explicit owner
choice in Mission018. No new chart, timing, scoring or global sustain policy is
introduced. Owner RC2 handheld checks remain required.
