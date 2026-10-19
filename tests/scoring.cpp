#include "scoring.hpp"
#include "importedRuntime.hpp"
#include "guitarGate.hpp"
#include "importedCompletion.hpp"
#include <cassert>
#include <cstdio>
#include <vector>
static GameplayEvent e(GameplayEventKind kind,uint32_t i=UINT32_MAX) {return {kind,i,1,0,0};}
static void basic() {
    NoteScore<40> s;
    for(unsigned n=1;n<=40;++n) {
        assert(s.consume(e(GameplayEventKind::PerfectHit,n-1)));
        unsigned expected=n<10?n*10:n<20?90+(n-9)*20:n<30?290+(n-19)*30:590+(n-29)*40;
        assert(s.snapshot().score==expected);assert(s.snapshot().multiplier==ScoreRules::multiplier(n));
    }
    assert(!s.consume(e(GameplayEventKind::Miss,1)));assert(s.snapshot().score==1030);
    s.consume(e(GameplayEventKind::WrongInput));assert(s.snapshot().combo==0&&s.snapshot().maxCombo==40&&s.snapshot().multiplier==1);
    assert(s.finalize());assert(s.snapshot().accuracy==10000&&!s.snapshot().fullCombo&&!s.snapshot().allPerfect);
    assert(!s.consume(e(GameplayEventKind::WrongInput)));s.reset();assert(!s.finalize()&&s.snapshot().score==0);
    for(unsigned i=0;i<40;++i){s.consume(e(GameplayEventKind::GoodHit,i));unsigned n=i+1;unsigned perfect=n<10?n*10:n<20?90+(n-9)*20:n<30?290+(n-19)*30:590+(n-29)*40;assert(s.snapshot().score==perfect/2);}
    assert(s.snapshot().score==515);s.finalize();assert(s.snapshot().fullCombo&&!s.snapshot().allPerfect);
    s.reset();s.consume(e(GameplayEventKind::Miss,0));s.consume(e(GameplayEventKind::PerfectHit,1));assert(s.snapshot().score==10&&s.snapshot().combo==1);
    assert(!s.consume(e(GameplayEventKind::PerfectHit,1))&&!s.consume(e(GameplayEventKind::PerfectHit,40)));
}
template<unsigned N> struct Session {
    NoteScore<N> score;GuitarGate gate;
    static void sink(void* p,const GameplayEvent& v){auto& c=*static_cast<Session*>(p);c.score.consume(v);c.gate.event(v);}
};
static void engineEvents() {
    const Note notes[]={{0,0,0},{0,1,0},{2000000,2,0},{4000000,0,0},{6000000,1,0}};
    NoteJudgment<5> j(notes,ImportedTiming::FRAME);Session<5> c;j.setEventSink(Session<5>::sink,&c);
    j.step(0,3);assert(c.score.snapshot().score==20&&c.score.snapshot().combo==2); // real chord
    j.step(0,3);assert(c.score.snapshot().score==20); // held
    j.step(0,0);j.step(0,1);assert(c.score.snapshot().wrong==1&&!c.gate.audible); // repeated press
    j.step(2000000,0);j.step(2000000+500000,4); // Good, recovers
    assert(c.score.snapshot().good==1&&c.score.snapshot().score==25&&c.gate.audible);
    j.step(6000000,2); // previous note Miss, then Perfect at this time
    assert(c.score.snapshot().missed==1&&c.score.snapshot().combo==1&&c.gate.audible);
    assert(c.score.coherent(j.stats())&&c.score.finalize());assert(c.score.snapshot().accuracy==8000);
    j.reset();c.score.reset();c.gate.reset();j.step(0,3|4); // chord hits then wrong extra
    assert(c.score.snapshot().perfect==2&&c.score.snapshot().wrong==1&&c.score.snapshot().combo==0&&!c.gate.audible);
    j.step(10000000,0);assert(c.score.snapshot().missed==3&&c.score.snapshot().maxCombo==2&&!c.gate.audible);
}
static void reference() {
    std::vector<Note> notes;for(unsigned i=0;i<395;++i)notes.push_back({uint64_t(i)*2000000,i%3,0});
    NoteJudgment<395> j(notes.data(),ImportedTiming::FRAME);Session<395> c;j.setEventSink(Session<395>::sink,&c);
    for(unsigned i=0;i<395;++i){j.step(notes[i].tick,0);j.step(notes[i].tick,1<<(i%3));}
    // Independent threshold buckets from the owner's reference calculation.
    const unsigned reference=9*10+10*20+10*30+366*40;
    assert(reference==15230&&c.score.snapshot().score==reference&&c.score.coherent(j.stats()));
    assert(c.score.finalize());const auto v=c.score.snapshot();assert(v.perfect==395&&v.good==0&&v.missed==0&&v.wrong==0&&v.maxCombo==395&&v.highestMultiplier==4&&v.accuracy==10000&&v.fullCombo&&v.allPerfect);
    NoteScore<8192> longChart;for(unsigned i=0;i<8192;++i)longChart.consume(e(GameplayEventKind::PerfectHit,i));
    assert(longChart.finalize()&&longChart.snapshot().score==9*10+10*20+10*30+(8192-29)*40);
    assert(ScoreRules::add(UINT32_MAX-5,40)==UINT32_MAX&&ScoreRules::add(UINT32_MAX,1)==UINT32_MAX);
    assert(ScoreRules::multiplier(UINT32_MAX)==4);
    assert(ScoreRules::accuracy(300,395)==7595&&ScoreRules::accuracy(1,3)==3333&&ScoreRules::accuracy(2,3)==6667);
    NoteScore<0> empty;assert(empty.finalize()&&empty.snapshot().accuracy==0&&!empty.snapshot().fullCombo&&!empty.snapshot().allPerfect);
}
static void completion() {
    using namespace ImportedCompletion;
    const auto end=silentEnd(1000000,true);
    assert(poll(true,PcmClock::Playing,UINT64_MAX,0,true)==Playing); // all notes alone never ends audio
    assert(poll(true,PcmClock::Ended,0,0,true)==Complete);
    assert(poll(true,PcmClock::Ended,100,0,true,101)==Playing);
    assert(poll(true,PcmClock::Ended,101,0,true,101)==Complete);
    assert(poll(true,PcmClock::Ended,101,0,false,101)==Inconsistent);
    assert(poll(true,PcmClock::Fault,100,0,true,101)==AudioError);
    assert(poll(true,PcmClock::Ended,0,0,false)==Inconsistent);
    assert(poll(true,PcmClock::Fault,0,0,true)==AudioError);
    assert(poll(true,PcmClock::Disabled,0,0,true)==AudioError);
    assert(poll(false,PcmClock::Disabled,end-1,end,true)==Playing);
    assert(poll(false,PcmClock::Disabled,end,end,true)==Complete);
    assert(poll(false,PcmClock::Disabled,end,end,false)==Inconsistent);
    uint32_t waited=0;
    for(unsigned i=0;i<119;++i)assert(boundedPoll(true,PcmClock::Ended,100,0,true,101,waited)==Playing);
    assert(boundedPoll(true,PcmClock::Ended,100,0,true,101,waited)==Inconsistent);
    assert(boundedPoll(true,PcmClock::Ended,101,0,true,101,waited)==Complete&&waited==0);
    assert(boundedPoll(true,PcmClock::Ended,101,0,false,101,waited)==Inconsistent);
    assert(silentEnd(0,false)==PRE_ROLL&&silentEnd(UINT64_MAX,true)==UINT64_MAX);
}
int main(){basic();engineEvents();reference();completion();puts("PASS: scoring10/20/30 thresholds, Good/Perfect, identity dedup, real held/chord/miss/hit/wrong order with audio gate,395Perfect=15230,8192notes, saturation, accuracy, empty charts, finalization, replay reset, audio end/fault/silent consistency");}
