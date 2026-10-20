#include "playTransport.hpp"
#include "noteJudgment.hpp"
#include "sustain.hpp"
#include "gameControls.hpp"
#include <cassert>
#include <cstdio>
using namespace PlayTransport;

int main(){
    Controller c;c.begin(START);assert(c.poll(START)==Command::None);
    c.poll(0);assert(c.poll(START)==Command::Pause);assert(c.apply(Command::Pause));
    assert(!c.apply(Command::Pause));
    for(unsigned f=0;f<36000;++f)assert(c.poll(START)==Command::None); //10min held START
    c.poll(0);assert(c.poll(START)==Command::Resume);assert(c.apply(Command::Resume));assert(!c.apply(Command::Resume));
    assert(c.poll(START)==Command::None);
    for(unsigned order=0;order<2;++order)for(unsigned gap=1;gap<=CHORD_POLLS;++gap){
        c.begin(0);auto first=order?SELECT:START,second=order?START:SELECT;
        auto a=c.poll(first);if(a==Command::Pause)c.apply(a);
        for(unsigned i=1;i<gap;++i)c.poll(0);
        assert(c.poll(second)==Command::Exit);assert(c.apply(Command::Exit));
    }
    c.begin(0);assert(c.poll(SYSTEM)==Command::Exit);
    c.begin(0);c.poll(SELECT);for(unsigned i=0;i<CHORD_POLLS;++i)c.poll(0);
    assert(c.poll(START)==Command::Pause);c.apply(Command::Pause);c.poll(0);assert(c.poll(SELECT)==Command::Exit);
    c.finish();assert(c.poll(START)==Command::None&&c.phase==Phase::Results);c.reset();assert(c.phase==Phase::Selector);
    // Seeding input preserves all note state and does not create free menu hits.
    const Note notes[]={{1000,0,0},{2000,1,0},{3000,2,0}};
    NoteJudgment<3> judgment(notes,280896);
    judgment.step(1000,1);assert(judgment.stats().perfect==1);
    judgment.seedInput(7);judgment.step(2000,7);assert(judgment.stats().perfect==1&&judgment.stats().wrongInputs==0);
    judgment.step(2000,5);judgment.step(2000,7);assert(judgment.stats().perfect==2); // fresh B after release
    judgment.step(3000,3);judgment.step(3000,7);assert(judgment.stats().perfect==3);
    // Two genuine overlapping holds: frozen time produces zero bonus; missing B
    // at resume uses the unchanged release grace while held A keeps accumulating.
    const Note holds[]={{0,1,0},{0,2,0}};const uint64_t lengths[]={2000000,2000000};
    Sustain::Holds<2> h(holds,lengths);
    h.event({GameplayEventKind::PerfectHit,0,2,0,0},4);h.event({GameplayEventKind::PerfectHit,1,4,0,0},4);
    const uint64_t now=Sustain::STEP*2;assert(h.update(now,6)==16);
    for(unsigned f=0;f<36000;++f)assert(h.stats().bonus==16&&h.stats().completed==0);
    h.resumeInput(now,4);assert(h.stats().bonus==16);assert(h.update(now,4)==0);
    h.update(now+Sustain::GRACE+1,4);assert(h.state(0)==Sustain::State::ReleasedEarly&&h.state(1)==Sustain::State::Active);
    h.update(now+Sustain::STEP,4);assert(h.stats().bonus==20);
    // Releasing/reholding while paused earns nothing: only resume-held matters.
    Sustain::Holds<2> keep(holds,lengths);keep.event({GameplayEventKind::PerfectHit,0,2,0,0},3);
    assert(keep.update(now,2)==6);keep.resumeInput(now,2);assert(keep.update(now,2)==0&&keep.stats().bonus==6);
    puts("PASS: pause states, held/rapid/system-chord priority,10min UI clock, no synthetic presses, frozen/independent holds and normal grace");
}
