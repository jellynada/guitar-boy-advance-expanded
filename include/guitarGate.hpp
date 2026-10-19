#ifndef GUITAR_GATE_HPP
#define GUITAR_GATE_HPP
#include <cstdint>
#include "noteJudgment.hpp"
// Existing synchronous engine order is authoritative: expired misses, hits in
// lane order, then WrongInput. Last event wins, including identical timestamps.
class GuitarGate {
public:
    static constexpr uint32_t FULL=256, FADE_SAMPLES=64; // 3.90625ms at16384Hz
    bool audible=true;
    uint32_t gain=FULL;
    void reset() { audible=true;gain=FULL; }
    void event(const GameplayEvent& e) {
        audible=e.kind==GameplayEventKind::PerfectHit||e.kind==GameplayEventKind::GoodHit;
    }
    int sample(int guitar,int backing) {
        if (audible) {if(gain<FULL)gain+=FULL/FADE_SAMPLES;}
        else if(gain)gain-=FULL/FADE_SAMPLES;
        // Symmetric division toward zero, no unsigned negative or signed shifts.
        return backing+guitar*int(gain)/int(FULL);
    }
};
#endif
