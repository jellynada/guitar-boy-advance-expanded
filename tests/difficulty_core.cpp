#include "gameControls.hpp"
#include "importedRuntime.hpp"
#include "scoring.hpp"
#include "sustain.hpp"
#include <cassert>
#include <cstdio>
int main(){
    Note notes[]={{0,0,0},{0,1,0},{0,2,0},{0,3,0},{0,4,0}};
    NoteJudgment<8,5> judge(notes,280896);judge.configure(notes,5);
    judge.step(0,31);assert(judge.stats().perfect==5&&judge.stats().wrongInputs==0);
    // A fifth-lane note is judged; selecting fewer records does not miss unused capacity.
    judge.configure(notes+3,2);judge.step(0,24);assert(judge.stats().perfect==2);
    judge.step(100000000,0);assert(judge.stats().missed==0);
    NoteScore<8> score;score.reset(2);
    for(unsigned i=0;i<2;++i)score.consume({GameplayEventKind::PerfectHit,i,uint8_t(1u<<(3+i)),0,0});
    assert(score.finalize()&&score.snapshot().allPerfect&&score.snapshot().accuracy==10000&&score.snapshot().total==2);
    uint64_t lengths[]={500000,500000,500000,500000,500000,0,0,0};
    Sustain::Holds<8,5> holds(notes,lengths);holds.configure(notes,lengths,5);
    for(unsigned i=0;i<5;++i)holds.event({GameplayEventKind::PerfectHit,i,uint8_t(1u<<i),0,0},1);
    for(unsigned i=0;i<5;++i)assert(holds.active(i)==i);
    holds.update(Sustain::STEP,31);assert(holds.stats().bonus==5);
    holds.resumeInput(Sustain::STEP,31);holds.update(2*Sustain::STEP,31);assert(holds.resolved()&&holds.stats().completed==5);
    uint8_t previous=0;
    for(unsigned keys:{64u,192u,128u,64u,0u}){
        auto state=PhysicalInput::sample(keys,previous,HARD_BUTTONS);
        assert(state.pressed==(previous==0&&keys?2:0));
        previous=state.held;
    }
    assert(importedLaneMaskFromButtons(KEY_A,4)==8&&importedLaneMaskFromButtons(KEY_A,5)==16);
    assert(importedLaneMaskFromButtons(KEY_UP|KEY_DOWN,5)==2);
    puts("PASS: four/five lanes, bounded chart selection, fifth-lane judgment/holds/scoring and UP/DOWN alias handoff");
}
