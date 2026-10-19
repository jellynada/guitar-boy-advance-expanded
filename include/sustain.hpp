#ifndef SUSTAIN_HPP
#define SUSTAIN_HPP
#include <array>
#include <cstdint>
#include "noteJudgment.hpp"
#include "scoring.hpp"
namespace Sustain {
constexpr uint64_t STEP=4194304; // exactly 250ms at 16,777,216Hz
constexpr uint64_t GRACE=16777216ULL*50000/1000000; //50ms, no points during gaps
inline uint64_t duration(uint64_t us){return (us*16777216ULL+500000)/1000000;}
enum class State:uint8_t { None,Pending,Active,Completed,ReleasedEarly,MissedOnset };
struct Stats {uint32_t total=0,completed=0,released=0,missed=0,bonus=0;};
template<unsigned N> class Holds {
    struct Lane {uint32_t id=UINT32_MAX,multiplier=1;uint64_t previous=0,held=0,releasedAt=0;bool down=true;};
    const Note* notes_;const uint64_t* lengths_;
    std::array<State,N> states_{};std::array<Lane,3> lanes_{};Stats stats_{};
    void finish(Lane& lane,State state){states_[lane.id]=state;if(state==State::Completed)++stats_.completed;else ++stats_.released;lane.id=UINT32_MAX;}
public:
    Holds(const Note* notes,const uint64_t* lengths):notes_(notes),lengths_(lengths){reset();}
    void reset(){stats_={};for(auto& l:lanes_)l=Lane{};for(unsigned i=0;i<N;++i){states_[i]=lengths_[i]?State::Pending:State::None;stats_.total+=lengths_[i]!=0;}}
    State state(unsigned i)const{return i<N?states_[i]:State::None;}
    uint32_t active(unsigned lane)const{return lane<3?lanes_[lane].id:UINT32_MAX;}
    const Stats& stats()const{return stats_;}
    bool resolved()const {return stats_.completed+stats_.released+stats_.missed==stats_.total;}
    uint64_t end(unsigned i)const{return notes_[i].tick+duration(lengths_[i]);}
    void event(const GameplayEvent& e,uint32_t multiplier){
        if(e.kind==GameplayEventKind::WrongInput||e.noteIndex>=N)return;
        const unsigned i=e.noteIndex,lane=notes_[i].lane;if(lane>=3)return;
        if(e.kind==GameplayEventKind::Miss){if(states_[i]==State::Pending){states_[i]=State::MissedOnset;++stats_.missed;}return;}
        if(lengths_[i]&&states_[i]!=State::Pending)return;
        // A fresh head on the same lane retires its previous hold. Holding the
        // button alone never hits that head; the unchanged judgment engine owns it.
        auto& l=lanes_[lane];if(l.id!=UINT32_MAX&&l.id!=i)finish(l,end(l.id)<=e.gameplayTick+GRACE?State::Completed:State::ReleasedEarly);
        if(states_[i]!=State::Pending)return;
        states_[i]=State::Active;l=Lane{};l.id=i;l.multiplier=multiplier;
        l.previous=e.gameplayTick>notes_[i].tick?e.gameplayTick:notes_[i].tick;
    }
    uint32_t update(uint64_t now,uint8_t held){
        uint32_t bonus=0;
        for(unsigned lane=0;lane<3;++lane){auto& l=lanes_[lane];if(l.id==UINT32_MAX)continue;
            const uint64_t deadline=end(l.id),tick=now<deadline?now:deadline;
            const bool down=held&(1u<<lane);
            if(!l.down&&now-l.releasedAt>GRACE){finish(l,deadline<=l.releasedAt+GRACE?State::Completed:State::ReleasedEarly);continue;}
            if(tick>l.previous&&l.down){
                const uint64_t before=l.held/STEP;l.held+=tick-l.previous;
                bonus=ScoreRules::add(bonus,uint32_t(l.held/STEP-before)*l.multiplier);
            }
            if(!down&&l.down)l.releasedAt=now;
            l.down=down;if(tick>l.previous)l.previous=tick;
            if(now>=deadline)finish(l,State::Completed);
        }
        stats_.bonus=ScoreRules::add(stats_.bonus,bonus);return bonus;
    }
    // At EOF a hold extending beyond available audio is an error, not a made-up
    // completion. Caller displays DATA ERROR and resets safely on replay.
};
}
#endif
