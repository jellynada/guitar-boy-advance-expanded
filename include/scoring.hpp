#ifndef SCORING_HPP
#define SCORING_HPP
#include <array>
#include <cstdint>
#include "noteJudgment.hpp"
namespace ScoreRules {
inline uint32_t add(uint32_t a,uint32_t b) {return b>UINT32_MAX-a?UINT32_MAX:a+b;}
inline uint32_t multiplier(uint32_t combo) {return combo>=30?4:combo>=20?3:combo>=10?2:1;}
inline uint32_t accuracy(uint32_t hits,uint32_t total) {return total?uint32_t((uint64_t(hits)*10000+total/2)/total):0;}
}
// Plain, stable instrumentation/renderer snapshot. Accuracy is hundredths of a percent.
struct ScoreSnapshot {
    uint32_t score=0,combo=0,maxCombo=0,multiplier=1,highestMultiplier=1;
    uint32_t perfect=0,good=0,missed=0,wrong=0,total=0,accuracy=0;
    uint32_t finalized=0,fullCombo=0,allPerfect=0;
    uint32_t sustainBonus=0,holdsCompleted=0,holdsReleased=0,holdsMissed=0,holdsTotal=0;
};
template<uint32_t N> class NoteScore {
public:
    void reset() {state_={};state_.total=N;seen_.fill(0);}
    NoteScore() {reset();}
    bool consume(const GameplayEvent& event) {
        if(state_.finalized)return false;
        if(event.kind==GameplayEventKind::WrongInput) {
            state_.wrong=ScoreRules::add(state_.wrong,1);breakCombo();return true;
        }
        const uint32_t i=event.noteIndex;
        if(i>=N||(seen_[i/8]&(1u<<(i%8))))return false;
        seen_[i/8]|=1u<<(i%8);
        if(event.kind==GameplayEventKind::Miss) {++state_.missed;breakCombo();return true;}
        if(event.kind==GameplayEventKind::PerfectHit)++state_.perfect;else ++state_.good;
        ++state_.combo; // Threshold is crossed BEFORE awarding this note.
        state_.multiplier=ScoreRules::multiplier(state_.combo);
        if(state_.combo>state_.maxCombo)state_.maxCombo=state_.combo;
        if(state_.multiplier>state_.highestMultiplier)state_.highestMultiplier=state_.multiplier;
        state_.score=ScoreRules::add(state_.score,(event.kind==GameplayEventKind::PerfectHit?10:5)*state_.multiplier);
        state_.accuracy=ScoreRules::accuracy(state_.perfect+state_.good,N);
        return true;
    }
    void addSustainBonus(uint32_t bonus) {if(!state_.finalized){state_.score=ScoreRules::add(state_.score,bonus);state_.sustainBonus=ScoreRules::add(state_.sustainBonus,bonus);}}
    bool coherent(const JudgmentStats& j) const {
        return state_.perfect==j.perfect&&state_.good==j.good&&state_.missed==j.missed&&state_.wrong==j.wrongInputs;
    }
    bool resolved() const {return uint64_t(state_.perfect)+state_.good+state_.missed==N;}
    bool finalize() {
        if(!resolved())return false;
        state_.finalized=1;state_.fullCombo=N&&state_.missed==0&&state_.wrong==0;
        state_.allPerfect=state_.fullCombo&&state_.perfect==N;return true;
    }
    const ScoreSnapshot& snapshot() const {return state_;}
private:
    void breakCombo() {state_.combo=0;state_.multiplier=1;}
    ScoreSnapshot state_{};
    std::array<uint8_t,(uint64_t(N)+7)/8> seen_{};
};
#endif
