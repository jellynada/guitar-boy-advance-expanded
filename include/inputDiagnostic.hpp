#ifndef INPUT_DIAGNOSTIC_HPP
#define INPUT_DIAGNOSTIC_HPP
#include "importedRuntime.hpp"
#include "sustain.hpp"
#include "physicalInput.hpp"

// Original, silent test data. Never used by the imported song or its audio clock.
namespace InputDiagnostic {
constexpr unsigned COUNT=13, GAP=240, LEAD=120;
constexpr uint64_t tick(unsigned frame){return uint64_t(frame)*ImportedTiming::FRAME;}
struct Target {const char* label;uint8_t mask;};
inline constexpr Target targets[COUNT]={
    {"LEFT",1},{"B",2},{"A",4},{"LEFT+B",3},{"LEFT+A",5},{"B+A",6},
    {"LEFT+B+A",7},{"LEFT THEN B",3},{"HOLD LEFT + TAP B",3},
    {"HOLD B+A",6},{"RELEASE B KEEP A",6},{"RAPID B B B",2},{"LEFT B A SEQUENCE",7}};
constexpr uint64_t at(unsigned test,unsigned offset=0){return tick(LEAD+test*GAP+offset);}
inline constexpr Note notes[]={
    {at(0),0,0},{at(1),1,0},{at(2),2,0},
    {at(3),0,0},{at(3),1,0},{at(4),0,0},{at(4),2,0},
    {at(5),1,0},{at(5),2,0},{at(6),0,0},{at(6),1,0},{at(6),2,0},
    {at(7),0,0},{at(7,30),1,0},
    {at(8),0,0},{at(8,45),1,0},
    {at(9),1,0},{at(9),2,0},{at(10),1,0},{at(10),2,0},
    {at(11),1,0},{at(11,10),1,0},{at(11,20),1,0},
    {at(12),0,0},{at(12,20),1,0},{at(12,40),2,0}};
constexpr unsigned NOTES=sizeof(notes)/sizeof(notes[0]);
inline constexpr uint64_t lengths[NOTES]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,1500000,0,1500000,1500000,1500000,1500000,0,0,0,0,0,0};
inline constexpr unsigned first[COUNT+1]={0,1,2,3,5,7,9,12,14,16,18,20,23,26};
enum class Result:uint32_t {Waiting,Pass,Partial,Miss,Wrong,HoldEarly};
struct Snapshot {
    uint32_t frame=0,test=0,held=0,pressed=0,expected=0,hit=0,missing=0,active=0;
    uint32_t result=0,lastLane=0,lastKind=0,bonus=0,completed=0,released=0;
};
class Session {
    NoteJudgment<NOTES> judgment_{notes,ImportedTiming::FRAME};
    Sustain::Holds<NOTES> holds_{notes,lengths};
    NoteScore<NOTES> score_;
    uint8_t previous_=0;unsigned wrong_[COUNT]{};
    static void event(void* context,const GameplayEvent& e){
        auto& self=*static_cast<Session*>(context);
        self.score_.consume(e);self.holds_.event(e,self.score_.snapshot().multiplier);
        self.state.lastLane=e.laneMask;self.state.lastKind=uint32_t(e.kind);
        if(e.kind==GameplayEventKind::WrongInput)++self.wrong_[self.state.test];
    }
public:
    Snapshot state;
    void reset(uint8_t held){judgment_.reset(held);judgment_.setEventSink(event,this);holds_.reset();score_.reset();previous_=held;state={};for(auto& n:wrong_)n=0;}
    Result result(unsigned test)const{
        if(state.frame<LEAD+test*GAP+150)return Result::Waiting;
        unsigned hit=0;for(unsigned i=first[test];i<first[test+1];++i)if(judgment_.state(i)==NoteState::Perfect||judgment_.state(i)==NoteState::Good)++hit;
        if(wrong_[test])return Result::Wrong;
        if(hit!=first[test+1]-first[test])return hit?Result::Partial:Result::Miss;
        if(test==10){return holds_.state(18)==Sustain::State::ReleasedEarly&&holds_.state(19)==Sustain::State::Completed?Result::Pass:Result::HoldEarly;}
        for(unsigned i=first[test];i<first[test+1];++i)if(lengths[i]&&holds_.state(i)!=Sustain::State::Completed)return Result::HoldEarly;
        return Result::Pass;
    }
    void update(unsigned frame,uint8_t held){
        state.frame=frame;state.test=frame<LEAD?0:(frame-LEAD)/GAP;if(state.test>=COUNT)state.test=COUNT-1;
        state.held=held;state.pressed=PhysicalInput::edges(held,previous_).pressed;previous_=held;state.expected=targets[state.test].mask;
        score_.addSustainBonus(holds_.update(tick(frame),held));judgment_.step(tick(frame),held);
        state.hit=0;state.missing=0;state.active=0;
        for(unsigned i=first[state.test];i<first[state.test+1];++i){auto s=judgment_.state(i);if(s==NoteState::Perfect||s==NoteState::Good)state.hit|=1u<<notes[i].lane;else state.missing|=1u<<notes[i].lane;}
        for(unsigned l=0;l<3;++l)if(holds_.active(l)!=UINT32_MAX&&(held&(1u<<l)))state.active|=1u<<l;
        state.result=uint32_t(result(state.test));state.bonus=holds_.stats().bonus;state.completed=holds_.stats().completed;state.released=holds_.stats().released;
    }
    bool finished()const{return state.frame>LEAD+(COUNT-1)*GAP+180;}
};
bool finished();
void start(uint8_t held);
void update(unsigned frame,uint8_t held);
}
#endif
