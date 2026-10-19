#include <cassert>
#include <cstdio>
#include <cstdlib>
#include "guitarGate.hpp"
#include "importedRuntime.hpp"
static GameplayEvent event(GameplayEventKind kind) { return {kind,0,1,0,0}; }
static void sink(void* p,const GameplayEvent& e) {static_cast<GuitarGate*>(p)->event(e);}
int main() {
    GuitarGate g;
    for(auto kind:{GameplayEventKind::PerfectHit,GameplayEventKind::GoodHit}) {g.event(event(kind));assert(g.audible&&g.sample(100,20)==120);}
    g.event(event(GameplayEventKind::Miss));assert(!g.audible);
    for(unsigned i=0;i<64;++i) {g.sample(100,20);assert(g.gain==256-(i+1)*4);}
    for(unsigned i=0;i<16384*10;++i)assert(g.sample(100,20)==20&&g.gain==0);
    for(auto kind:{GameplayEventKind::Miss,GameplayEventKind::WrongInput}) {g.event(event(kind));assert(g.sample(-100,-20)==-20);}
    for(auto kind:{GameplayEventKind::GoodHit,GameplayEventKind::PerfectHit}) {
        g.event(event(kind));for(unsigned i=0;i<64;++i)g.sample(100,20);assert(g.gain==256&&g.audible);
        g.event(event(GameplayEventKind::Miss));for(unsigned i=0;i<64;++i)g.sample(100,20);
    }
    // Fade reversal is bounded; current gain continues, not an amplitude jump.
    g.event(event(GameplayEventKind::GoodHit));for(int i=0;i<20;++i)g.sample(1,0);
    assert(g.gain==80);g.event(event(GameplayEventKind::WrongInput));g.sample(1,0);assert(g.gain==76);
    g.reset();assert(g.audible&&g.gain==256);
    // Real engine: overdue note misses before simultaneous later hit -> audible.
    const Note notes[]={{0,0,0},{2000000,1,0}};
    NoteJudgment<2> judge(notes,ImportedTiming::FRAME);judge.setEventSink(sink,&g);
    judge.step(2000000,2);assert(judge.stats().missed==1&&judge.stats().perfect==1&&g.audible);
    judge.reset();g.reset();judge.step(2000000,2|4);assert(judge.stats().wrongInputs==1&&!g.audible); // WrongInput after hit wins
    for(int x=-127;x<=127;++x)for(int b=-127;b<=127;++b)if(abs(x)+abs(b)<=127){g.reset();assert(g.sample(x,b)>=-127&&g.sample(x,b)<=127);}
    puts("PASS: gate Perfect/Good/Miss/WrongInput, true silence/no timeout,64sample fade/reversal, reset, same-update hit/miss/wrong event order, fixed-point bounds");
}
