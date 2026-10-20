#include "noteJudgment.hpp"
#include "scoring.hpp"
#include "sustain.hpp"
#include <cassert>
#include <cstdio>
struct Song {
    Note notes[2]={{16777216ULL,0,0},{16777216ULL+10,1,0}};
    uint64_t lengths[2]={1000000,0};
    NoteJudgment<2,3> judgment{notes,280896};
    NoteScore<2> score;
    Sustain::Holds<2,3> holds{notes,lengths};
    static void event(void* p,const GameplayEvent& e){auto& s=*static_cast<Song*>(p);s.score.consume(e);s.holds.event(e,s.score.snapshot().multiplier);}
    Song(){judgment.setEventSink(event,this);}
};
int main(){
    Song a;a.judgment.step(16777216ULL,1);a.score.addSustainBonus(a.holds.update(33554432ULL,1));
    a.judgment.finishAtEof(33554432ULL);assert(a.score.finalize());assert(a.holds.resolved());
    assert(a.score.snapshot().perfect==1&&a.score.snapshot().missed==1&&a.holds.stats().completed==1);
    auto score=a.score.snapshot().score;a.judgment.finishAtEof(33554432ULL);assert(a.score.snapshot().score==score);
    Song b;b.judgment.step(16777216ULL+10,0);assert(b.judgment.stats().missed==0);
    b.judgment.finishAtEof(16777216ULL+11);assert(b.judgment.stats().missed==2&&b.holds.resolved());
    assert(b.score.finalize()&&!b.score.snapshot().fullCombo&&!b.score.snapshot().allPerfect);
    // Newly activated hold whose head/end are both in the final poll.
    Song d;d.notes[0].tick=33554000ULL;d.notes[1].tick=33554100ULL;d.lengths[0]=25;d.holds.reset();
    d.holds.update(33554432ULL,1);d.judgment.step(33554432ULL,1);
    d.judgment.finishAtEof(33554432ULL);assert(!d.holds.resolved());
    d.holds.update(33554432ULL,1);assert(d.holds.resolved()&&d.holds.stats().completed==1);
    std::puts("PASS: finite EOF emits each pending miss once, settles holds, no free hits or score");
}
