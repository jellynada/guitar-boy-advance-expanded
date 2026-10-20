#include "inputDiagnostic.hpp"
#include "gameControls.hpp"
#include <cassert>
#include <cstdio>
using namespace InputDiagnostic;
static Session run(int scenario){
    Session s;s.reset(0);
    for(unsigned frame=0;frame<LEAD+COUNT*GAP;++frame){
        uint8_t held=0;
        for(unsigned i=0;i<NOTES;++i){
            unsigned onset=notes[i].tick/ImportedTiming::FRAME;
            unsigned duration=lengths[i]?90:1;
            if(i==18)duration=30; // Deliberate release B while A continues.
            if(frame>=onset&&frame<onset+duration)held|=1u<<notes[i].lane;
        }
        if(scenario==1&&frame==LEAD+3*GAP)held=1; // B absent in Left+B.
        if(scenario==2&&frame==LEAD+4*GAP)held=7; // Unmatched extra B.
        if(scenario==3&&frame>=LEAD+9*GAP+20&&frame<LEAD+9*GAP+90)held=0;
        if(scenario==4&&frame>=LEAD+11*GAP&&frame<=LEAD+11*GAP+20)held=2; // no fresh edges
        if(scenario==5&&frame>=LEAD+5*GAP&&frame<LEAD+5*GAP+10)held=0;
        s.update(frame,held);
    }
    return s;
}
int main(){
    for(unsigned mask=0;mask<8;++mask){u16 keys=0;for(unsigned lane=0;lane<3;++lane)if(mask&(1u<<lane))keys|=EASY_BUTTONS[lane];assert(easyLaneMaskFromButtons(keys)==mask);}
    auto s=run(0);for(unsigned i=0;i<COUNT;++i)assert(s.result(i)==Result::Pass);
    assert(s.state.completed==4&&s.state.released==1&&s.state.bonus>0);
    assert(run(1).result(3)==Result::Partial);assert(run(2).result(4)==Result::Wrong);
    assert(run(3).result(9)==Result::HoldEarly);assert(run(4).result(11)==Result::Partial);assert(run(5).result(5)==Result::Miss);
    s.reset(7);s.update(0,7);assert(s.state.pressed==0&&s.state.bonus==0&&s.state.active==0);
    puts("PASS: diagnostic chords, missing/extra inputs, no held-key retriggers, independent holds, deliberate release and reset");
}
