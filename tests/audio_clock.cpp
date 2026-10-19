#include "audioClock.hpp"
#include "importedRuntime.hpp"
#include <cassert>
#include <cstdio>
int main(){
    using namespace PcmClock;
    assert(tick(0)==0&&tick(1)==0&&tick(2)==1024);
    assert(tick(PRE_ROLL+1)==33554432); // first source sample at chart origin
    assert(tick(16384*3600+1)==60397977600ULL);
    assert(tick(UINT32_MAX)==uint64_t(UINT32_MAX-1)*1024);
    assert(bounded(100,90)==90&&bounded(80,90)==80);
    // Sample-grid timestamps, no repeated per-frame rounding or BPM scale.
    for(uint32_t sample:{0U,PRE_ROLL,PRE_ROLL+1234567,100000000U}){
        assert(tick(sample+1)==uint64_t(sample)*16777216/16384);
    }
    Note notes[]={{tick(PRE_ROLL+1),0,0},{tick(PRE_ROLL+16384+1),1,0},{tick(PRE_ROLL+10*16384+1),2,0}};
    ImportedRuntime<3> engine(notes);
    for(unsigned i=0;i<3;++i){engine.updateTick(notes[i].tick-1024,0);engine.updateTick(notes[i].tick,1<<i);engine.updateTick(notes[i].tick,1<<i);}
    assert(engine.stats().perfect==3&&engine.stats().judged()==3);
    uint64_t last=engine.now();engine.updateTick(0,0);assert(engine.now()==last);
    engine.reset();engine.updateTick(notes[2].tick+2000000,0);assert(engine.stats().missed==3);
    puts("PASS: sample clock zero/pre-roll/hour-long exact timing, overflow bounds, shared judgment, frozen/backward snapshots");
}
