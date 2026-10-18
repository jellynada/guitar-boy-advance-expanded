// Stub only the hardware text renderer; exercise the real note-manager code.
#define __TERMINAL__
#define __TEXT_DISPLAY__
#include "tonc.h"
struct textDisplay {
    textDisplay(u16, u16, u16, bool = true) {}
    void update(u32) {}
    void update(u32, u32) {}
};
#include "noteManager.hpp"
#include <cassert>

int main() {
    const Note notes[] = {{100, 0, 0}, {100, 1, 0}, {200, 3, 0}};
    NoteManager<3> manager(notes, 1);
    manager.init();
    assert(manager.getNoteCount() == 3);
    for (int frame = 0; frame < 90; ++frame) assert(manager.update() == 0);
    assert(manager.update() == 2); // A chord advances both records.
    for (int frame = 91; frame < 197; ++frame) manager.update();
    assert(manager.checkHit(KEY_R) == 2); // Final note remains hittable.
    for (int frame = 197; frame < 10000; ++frame) {
        assert(manager.update() == 3); // Cursor stops at the array boundary.
        if (frame > 210) assert(manager.checkHit(KEY_R) == -1);
    }
    const Note single[] = {{100, 0, 0}};
    NoteManager<1> one(single, 1);
    for (int frame = 0; frame < 1000; ++frame) one.update();
    assert(one.checkHit(KEY_L) == -1);
}
