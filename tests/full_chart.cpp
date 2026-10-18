#include "noteJudgment.hpp"
#include "chart_fixture.hpp"
#include <array>
#include <cassert>
#include <cstdio>

struct Events {
    std::array<unsigned, 699> perNote{};
    unsigned perfect = 0, good = 0, miss = 0, wrong = 0;
    static void receive(void* context, const GameplayEvent& event) {
        auto& counts = *static_cast<Events*>(context);
        if (event.kind == GameplayEventKind::WrongInput) { ++counts.wrong; return; }
        assert(event.noteIndex < counts.perNote.size());
        assert(++counts.perNote[event.noteIndex] == 1);
        if (event.kind == GameplayEventKind::PerfectHit) ++counts.perfect;
        else if (event.kind == GameplayEventKind::GoodHit) ++counts.good;
        else ++counts.miss;
    }
};

int main() {
    constexpr unsigned bpm = 83330;
    const unsigned frames = chart[698].tick / bpm + 1200;
    NoteJudgment<699> judgment(chart, bpm);
    Events events;
    judgment.setEventSink(Events::receive, &events);
    for (unsigned frame = 0; frame <= frames; ++frame) judgment.step(u64(frame) * bpm, 0);
    assert(judgment.stats().missed == 699 && judgment.stats().hits() == 0);
    assert(events.miss == 699 && events.wrong == 0);
    for (unsigned count : events.perNote) assert(count == 1);
    for (unsigned i = 0; i < 699; ++i) assert(judgment.state(i) == NoteState::Missed);

    judgment.reset();
    events = {};
    unsigned next = 0;
    for (unsigned frame = 0; frame <= frames; ++frame) {
        u8 lanes = 0;
        const u64 now = u64(frame) * bpm;
        while (next < 699 && chart[next].tick <= now) lanes |= 1u << chart[next++].lane;
        judgment.step(now, lanes);
        const auto& stats = judgment.stats();
        assert(stats.judged() <= 699 && stats.hits() == events.perfect + events.good);
    }
    assert(judgment.stats().perfect == 699 && judgment.stats().good == 0);
    assert(judgment.stats().missed == 0 && judgment.stats().wrongInputs == 0);
    assert(events.perfect == 699 && events.wrong == 0);
    for (unsigned count : events.perNote) assert(count == 1);
    for (unsigned i = 0; i < 699; ++i) assert(judgment.state(i) == NoteState::Perfect);
    std::puts("PASS: unchanged 699-note chart, all-miss and all-perfect runs, exactly one event per note, consistent stats");
}
