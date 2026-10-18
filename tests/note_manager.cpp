#include "noteManager.hpp"
#include "gameControls.hpp"
#include <cassert>
#include <cstdio>
#include <vector>

using Engine = NoteJudgment<1>;
constexpr u32 BPM = 83330;
constexpr u64 TARGET = u64(BPM) * 100;

static void capture(void* context, const GameplayEvent& event) {
    static_cast<std::vector<GameplayEvent>*>(context)->push_back(event);
}

static void windowCase(u64 now, u8 lane, NoteState expected, u32 wrong) {
    const Note notes[] = {{TARGET, 0, 0}};
    Engine engine(notes, BPM);
    std::vector<GameplayEvent> events;
    engine.setEventSink(capture, &events);
    engine.step(now, lane);
    assert(engine.state(0) == expected);
    assert(engine.stats().wrongInputs == wrong);
    assert(engine.stats().judged() <= 1);
}

int main() {
    const Note one[] = {{TARGET, 0, 0}};
    Engine limits(one, BPM);
    const u64 early = limits.windowTicks(Engine::GOOD_EARLY_US);
    const u64 late = limits.windowTicks(Engine::GOOD_LATE_US);
    const u64 perfect = limits.windowTicks(Engine::PERFECT_US);
    // Independent check using the actual GBA clock/cycles, not a BPM-derived
    // guess about milliseconds. Cycle rounding differs by less than 1 CPU cycle.
    assert(early == u64(BPM) * (16777216ull * 50000 / 1000000) / 280896);
    assert(late == u64(BPM) * (16777216ull * 85000 / 1000000) / 280896);
    windowCase(TARGET, 1, NoteState::Perfect, 0);
    windowCase(TARGET - perfect, 1, NoteState::Perfect, 0);
    windowCase(TARGET + perfect, 1, NoteState::Perfect, 0);
    windowCase(TARGET - perfect - 1, 1, NoteState::Good, 0);
    windowCase(TARGET + perfect + 1, 1, NoteState::Good, 0);
    windowCase(TARGET - early, 1, NoteState::Good, 0);
    windowCase(TARGET + late, 1, NoteState::Good, 0);
    windowCase(TARGET - early - 1, 1, NoteState::Pending, 1);
    windowCase(TARGET + late + 1, 1, NoteState::Missed, 1);

    Engine noInput(one, BPM);
    noInput.step(TARGET + late, 0);
    assert(noInput.state(0) == NoteState::Pending);
    noInput.step(TARGET + late + 1, 0);
    noInput.step(TARGET + 10 * late, 0);
    assert(noInput.stats().missed == 1 && noInput.stats().wrongInputs == 0);

    // A Perfect window is the same real duration at different BPM values.
    for (u32 tempo : {60000u, 120000u, 160000u}) {
        Engine tempoEngine(one, tempo);
        const u64 ticks = tempoEngine.windowTicks(Engine::PERFECT_US);
        const u64 scaledTime = ticks * 280896ull * 1000000;
        assert(scaledTime <= 25000ull * tempo * 16777216);
        assert(scaledTime >= 24999ull * tempo * 16777216);
    }

    // An unrelated wrong key cannot consume a still-valid note.
    Engine wrong(one, BPM);
    std::vector<GameplayEvent> events;
    wrong.setEventSink(capture, &events);
    wrong.step(TARGET, 2);
    assert(wrong.state(0) == NoteState::Pending);
    assert(events.size() == 1 && events[0].kind == GameplayEventKind::WrongInput);
    assert(events[0].noteIndex == Engine::NO_NOTE && events[0].laneMask == 2);
    wrong.step(TARGET + 1, 3); // Newly press lane 0 while holding the wrong key.
    assert(wrong.state(0) == NoteState::Perfect && wrong.stats().wrongInputs == 1);
    assert(events[1].kind == GameplayEventKind::PerfectHit && events[1].noteIndex == 0);
    assert(events[1].chartTick == TARGET && events[1].gameplayTick == TARGET + 1);
    wrong.step(TARGET + 2, 0);
    wrong.step(TARGET + 3, 1); // Repressing cannot award the note twice.
    assert(wrong.stats().hits() == 1 && wrong.stats().wrongInputs == 2);

    // Valid + extra input produces BOTH a hit and a separate mistake event.
    Engine extra(one, BPM);
    extra.step(TARGET, 0x0f);
    assert(extra.stats().perfect == 1 && extra.stats().wrongInputs == 1);

    const Note chord[] = {{TARGET, 0, 0}, {TARGET, 1, 0}, {TARGET, 3, 0}};
    NoteJudgment<3> together(chord, BPM);
    together.step(TARGET, 0x0b);
    assert(together.stats().perfect == 3 && together.stats().wrongInputs == 0);
    together.step(TARGET + late + 1, 0x0b);
    assert(together.stats().missed == 0 && together.stats().judged() == 3);

    // Partial chords are judged individually, including a missing chord member.
    NoteJudgment<3> partial(chord, BPM);
    partial.step(TARGET - perfect, 1);
    partial.step(TARGET + late, 3);
    partial.step(TARGET + late + 1, 3);
    assert(partial.stats().perfect == 1 && partial.stats().good == 1);
    assert(partial.stats().missed == 1 && partial.stats().judged() == 3);

    const Note repeated[] = {{TARGET, 0, 0}, {TARGET + 20 * BPM, 0, 0}};
    NoteJudgment<2> held(repeated, BPM);
    held.step(TARGET, 1);
    held.step(TARGET + 20 * BPM, 1); // Held key is not a fresh press.
    held.step(TARGET + 20 * BPM + late + 1, 1);
    assert(held.stats().perfect == 1 && held.stats().missed == 1);
    assert(held.stats().wrongInputs == 0);

    // One edge never hits two close notes in the same lane.
    const Note close[] = {{TARGET, 0, 0}, {TARGET + BPM, 0, 0}};
    NoteJudgment<2> closeEngine(close, BPM);
    closeEngine.step(TARGET, 1);
    assert(closeEngine.stats().hits() == 1);
    closeEngine.step(TARGET + BPM / 2, 0);
    closeEngine.step(TARGET + BPM, 1);
    assert(closeEngine.stats().hits() == 2);

    // No unsigned early-window underflow for a chart that begins at zero.
    const Note zero[] = {{0, 0, 0}};
    Engine startsAtZero(zero, BPM);
    startsAtZero.step(0, 1);
    assert(startsAtZero.stats().perfect == 1);

    // Reset clears all states/statistics/edge history, retains the subscription.
    wrong.reset(1);
    assert(wrong.state(0) == NoteState::Pending && wrong.stats().judged() == 0);
    assert(wrong.stats().wrongInputs == 0);
    wrong.step(TARGET, 1); // A button already held at reset is not a new press.
    assert(wrong.stats().hits() == 0);
    wrong.step(TARGET + 1, 0);
    wrong.step(TARGET + 2, 1);
    assert(wrong.stats().perfect == 1 && events.back().kind == GameplayEventKind::PerfectHit);

    // Empty and finished charts remain bounded after many late updates.
    NoteJudgment<0> empty(nullptr, BPM);
    empty.step(TARGET, 1);
    assert(empty.stats().judged() == 0 && empty.stats().wrongInputs == 1);
    for (u32 frame = 101; frame < 10000; ++frame) {
        wrong.step(u64(frame) * BPM, frame & 1);
        assert(wrong.stats().judged() == 1);
    }

    // The user's physical-button order is shared by judgment and animations.
    assert(LANE_BUTTONS[0] == KEY_LEFT && LANE_BUTTONS[1] == KEY_RIGHT);
    assert(LANE_BUTTONS[2] == KEY_A && LANE_BUTTONS[3] == KEY_B);
    assert(laneMaskFromButtons(KEY_LEFT | KEY_A) == 5);
    assert(laneMaskFromButtons(KEY_RIGHT | KEY_B) == 10);
    assert(laneMaskFromButtons(KEY_L | KEY_R) == 0);

    NoteManager<3> manager(chord, BPM);
    assert(manager.getNoteCount() == 3);
    assert(manager.update(100, 0x0b) == 3);
    assert(manager.wasHit(0) && manager.wasHit(1) && manager.wasHit(2));
    for (u32 frame = 101; frame < 10000; ++frame) {
        assert(manager.update(frame, frame & 1) == 3);
        assert(manager.judgment().stats().judged() == 3);
    }
    manager.reset();
    assert(manager.judgment().stats().judged() == 0 && !manager.wasHit(0));
    assert(!manager.wasHit(3));
    std::puts("PASS: timing boundaries, misses, wrong/extra input, chords, holds, repeat prevention, reset, final/empty charts, controls");
}
