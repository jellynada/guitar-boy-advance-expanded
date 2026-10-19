#include "sustain.hpp"
#include "guitarGate.hpp"
#include <cassert>
#include <cstdio>
using namespace Sustain;
static GameplayEvent hit(unsigned i,uint64_t tick=0){return {GameplayEventKind::PerfectHit,i,uint8_t(1u<<i),tick,tick};}
int main(){
 const Note notes[]={{0,0,0},{0,1,0},{0,2,0}};const uint64_t lengths[]={1000000,1000000,1000000};
 Holds<3> h(notes,lengths);h.event(hit(0),2);assert(h.update(STEP-1,1)==0);assert(h.update(STEP,1)==2);assert(h.update(STEP,1)==0);
 assert(h.update(2*STEP,1)==2);assert(h.update(3*STEP,1)==2);assert(h.update(4*STEP,1)==2);assert(h.state(0)==State::Completed&&h.stats().bonus==8);assert(h.update(10*STEP,1)==0);
 h.reset();h.event(hit(0),1);h.update(4*STEP-GRACE,0);h.update(5*STEP,0);assert(h.state(0)==State::Completed&&h.stats().bonus==3); // end tolerance survives a skipped poll
 h.reset();h.event(hit(0),2);assert(h.update(STEP,0)==2);h.update(STEP+GRACE+1,0);assert(h.state(0)==State::ReleasedEarly&&h.stats().bonus==2);
 h.reset();h.event(hit(0),4);assert(h.update(STEP,1)==4);assert(h.update(STEP+1,0)==0);assert(h.update(STEP+GRACE+2,0)==0);assert(h.state(0)==State::ReleasedEarly);assert(h.update(4*STEP,1)==0&&h.stats().bonus==4);
 h.reset();h.event(hit(0),1);h.update(STEP,1);h.update(STEP+100,0);h.update(STEP+GRACE,1);assert(h.state(0)==State::Active);h.update(4*STEP,1);assert(h.state(0)==State::Completed&&h.stats().bonus==3); // no points during tolerated gap
 h.reset();h.event(hit(0),1);h.event(hit(1),2);h.event(hit(2),4);assert(h.update(STEP,7)==7);assert(h.update(4*STEP,7)==21);assert(h.stats().completed==3&&h.resolved());
 h.reset();auto miss=hit(0);miss.kind=GameplayEventKind::Miss;h.event(miss,1);assert(h.state(0)==State::MissedOnset);h.event(hit(0),4);assert(h.update(4*STEP,7)==0);
 const Note overlap[]={{0,0,0},{STEP,0,0}};const uint64_t ol[]={1000000,500000};Holds<2> o(overlap,ol);o.event(hit(0),1);o.update(STEP,1);o.event(hit(1,STEP),2);assert(o.state(0)==State::ReleasedEarly&&o.state(1)==State::Active);o.event(hit(0),4);assert(o.state(1)==State::Active);o.update(3*STEP,1);assert(o.stats().bonus==5&&o.stats().completed==1);
 // The real judgment engine still needs a fresh press; early hold release does
 // not touch head scoring, combo, FC or the audio gate.
 NoteScore<3> score;GuitarGate gate;h.reset();for(unsigned i=0;i<3;++i){auto e=hit(i);score.consume(e);gate.event(e);h.event(e,score.snapshot().multiplier);}score.addSustainBonus(h.update(STEP,7));h.update(STEP+1,0);h.update(STEP+GRACE+2,0);assert(score.snapshot().combo==3&&gate.audible);assert(score.finalize()&&score.snapshot().fullCombo);assert(score.snapshot().score==33);
 const Note one[]={{0,0,0}};NoteJudgment<1> j(one,280896);j.step(0,1);j.step(STEP,1);assert(j.stats().perfect==1&&j.stats().wrongInputs==0);
 // Bonus rate is captured at onset even if a later head changes the multiplier.
 Holds<3> frozen(notes,lengths);frozen.event(hit(0),2);frozen.event(hit(1),4);assert(frozen.update(STEP,3)==6);
 auto wrong=hit(0);wrong.kind=GameplayEventKind::WrongInput;wrong.noteIndex=UINT32_MAX;
 frozen.event(wrong,1);assert(frozen.update(2*STEP,3)==6); // captured rates survive wrong-input combo changes
 const Note sameLane[]={{0,0,0},{STEP,0,0}};NoteJudgment<2> fresh(sameLane,280896);
 fresh.step(0,1);fresh.step(STEP,1);assert(fresh.stats().perfect==1);
 fresh.step(STEP+fresh.windowTicks(85000)+1,1);assert(fresh.stats().perfect==1&&fresh.stats().missed==1&&fresh.stats().wrongInputs==0);
 const uint64_t tapLengths[]={1000000,0};Holds<2> tap(sameLane,tapLengths);tap.event(hit(0),1);tap.update(STEP,1);tap.event(hit(1,STEP),2);
 assert(tap.state(0)==State::ReleasedEarly&&tap.resolved()&&tap.update(4*STEP,1)==0);
 const Note future[]={{2*STEP,0,0}};const uint64_t fl[]={1000000};Holds<1> early(future,fl);
 early.event(hit(0,STEP),1);assert(early.update(2*STEP,1)==0);assert(early.update(3*STEP,1)==1);
 Holds<0> empty(nullptr,nullptr);assert(empty.resolved()&&empty.update(STEP,7)==0);
 h.reset();assert(h.stats().bonus==0&&h.stats().completed==0&&h.stats().released==0);
 puts("PASS: exact quarter-second bonuses, captured multipliers, duplicate prevention, gaps, grace, permanent release, three simultaneous holds, missed onset, same-lane replacement, combo/FC/audio independence, reset");
}
