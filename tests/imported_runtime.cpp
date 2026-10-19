#include "importedRuntime.hpp"
#include "gameControls.hpp"
#include <cassert>
#include <cstdio>
#include <climits>

int main() {
    using namespace ImportedTiming;
    uint64_t result;
    assert(toCycles(1000000, result) && result == 16777216);
    assert(toCycles(2000000, result) && result == 33554432);
    assert(toCycles(3600000000ULL, result) && result == 60397977600ULL);
    assert(!toCycles(UINT64_MAX, result));
    assert(!toCycles(MAX_US + 1, result));
    assert(frameTick(1) == 280896);
    assert(frameTick(1000000) == 280896000000ULL);
    assert(frameTick(UINT32_MAX) == uint64_t(UINT32_MAX) * 280896);
    assert(relativeZ(INT64_MAX) == relativeZ(AHEAD));
    assert(relativeZ(INT64_MIN) == relativeZ(-int64_t(BEHIND)));
    assert(relativeZ(0) == -21000);
    assert(floorZ(0) == -40000);
    assert(floorZ(UINT64_MAX) == floorZ(frameTick(MAX_FRAME)));
    assert(floorZ(frameTick(215016)) <= -40000 && floorZ(frameTick(215016)) > -171072);
    assert(laneX(0) < laneX(1) && laneX(1) < laneX(2));
    assert(laneX(99) == 0);
    assert(easyLaneMaskFromButtons(KEY_LEFT) == 1);
    assert(easyLaneMaskFromButtons(KEY_A) == 2);
    assert(easyLaneMaskFromButtons(KEY_B) == 4);
    assert(easyLaneMaskFromButtons(KEY_RIGHT | KEY_L | KEY_R) == 0);
    assert(laneMaskFromButtons(KEY_LEFT | KEY_RIGHT | KEY_A | KEY_B) == 15);
    // Independent reference events at beginning, middle, end of a one-hour chart.
    Note notes[] = {{frameTick(120),0,0},{frameTick(107508),1,0},{frameTick(215016),2,0}};
    ImportedRuntime<3> runtime(notes);
    for (uint32_t frame : {120U,107508U,215016U}) {
        const uint8_t lane = frame == 120 ? 1 : frame == 107508 ? 2 : 4;
        runtime.update(frame-1,0);
        runtime.update(frame,lane);
        runtime.update(frame+1,lane);
        runtime.update(frame+2,0);
    }
    assert(runtime.stats().perfect == 3 && runtime.stats().judged() == 3);
    runtime.update(215100,0);
    assert(runtime.firstVisible() == 3 && runtime.endVisible() == 3);
    runtime.update(0,0); // a stale read cannot rewind the monotonic clock
    assert(runtime.now() == frameTick(215100));
    for (unsigned repetition=0; repetition<5; ++repetition) {
        runtime.reset(7);
        assert(runtime.now() == 0 && runtime.firstVisible() == 0 && runtime.endVisible() == 0);
        assert(runtime.stats().judged() == 0);
        runtime.update(1,7); // held buttons at reset are not fresh presses
        assert(runtime.stats().wrongInputs == 0);
        runtime.update(220000,0); // skipped frames must miss every remaining note
        assert(runtime.stats().missed == 3 && runtime.stats().judged() == 3);
        runtime.update(UINT32_MAX,0);
        assert(runtime.now() == frameTick(MAX_FRAME));
    }
    const Note lastAllowed[] = {{(MAX_US * HZ + 500000) / 1000000, 0, 0}};
    ImportedRuntime<1> last(lastAllowed);
    last.update(UINT32_MAX, 0);
    assert(last.stats().missed == 1); // cap includes final late window and tail
    // Inclusive real-time judgment windows are reused, in CPU cycles.
    ImportedRuntime<1> single(notes);
    assert(single.judgment().windowTicks(25000) == 419430);
    assert(single.judgment().windowTicks(50000) == 838860);
    assert(single.judgment().windowTicks(85000) == 1426063);
    // Frame sampling, not tempo accumulation, bounds scheduled note error.
    uint64_t largestError = 0;
    for (uint64_t us : {2000000ULL,2500000ULL,4000000ULL,8000000ULL,3602000000ULL}) {
        assert(toCycles(us,result));
        const uint64_t frame = (result + FRAME - 1) / FRAME;
        const uint64_t error = frame * FRAME - result;
        assert(error < FRAME);
        if (error > largestError) largestError = error;
    }
    printf("PASS: imported clock/controls/judgment/reset/long-song bounds; reference frame error max %.6f ms (<16.743ms)\n",double(largestError)*1000/HZ);
}
