#include "inputDiagnostic.hpp"
#include "scoreDisplay.hpp"
#include "gameControls.hpp"
#include <tonc.h>
namespace InputDiagnostic {
static Session session;
static unsigned recentPress=0;
extern "C" {Snapshot diagnosticSnapshot;uint32_t diagnosticResults[COUNT];}
static const char* label(Result r){switch(r){case Result::Waiting:return "WAIT";case Result::Pass:return "PASS";case Result::Partial:return "PARTIAL";case Result::Miss:return "MISS";case Result::Wrong:return "WRONG";case Result::HoldEarly:return "HOLD FAIL";}return "?";}
static void mask(unsigned y,const char* title,unsigned value){
    ScoreDisplay::line(0,y,title);ScoreDisplay::line(11,y,value&1?EASY_LABELS[0]:"----");ScoreDisplay::line(17,y,value&2?EASY_LABELS[1]:"-");ScoreDisplay::line(21,y,value&4?EASY_LABELS[2]:"-");
}
bool finished(){return session.finished();}
void start(uint8_t held){session.reset(held);recentPress=0;ScoreDisplay::initialize();REG_BLDCNT=0;REG_DISPCNT=DCNT_BG1|DCNT_MODE0;pal_bg_mem[0]=0;}
void update(unsigned frame,uint8_t held){
    session.update(frame,held);diagnosticSnapshot=session.state;
    for(unsigned i=0;i<COUNT;++i)diagnosticResults[i]=uint32_t(session.result(i));
    ScoreDisplay::page();ScoreDisplay::line(0,0,"INPUT / CHORD TEST - M014");
    if(session.finished()){
        for(unsigned i=0;i<COUNT;++i){ScoreDisplay::line(0,i+2,targets[i].label);ScoreDisplay::line(21,i+2,label(session.result(i)));}
        ScoreDisplay::line(0,16,"A/START RETRY B/SELECT EXIT");return;
    }
    ScoreDisplay::line(0,2,targets[session.state.test].label);
    const unsigned target=LEAD+session.state.test*GAP;
    if(frame<target){ScoreDisplay::line(0,3,"PRESS IN:");ScoreDisplay::value(10,3,(target-frame+59)/60);}
    else if(frame<target+6)ScoreDisplay::line(0,3,"PRESS NOW");
    else ScoreDisplay::line(0,3,label(session.result(session.state.test)));
    mask(5,"GBA HELD",held);mask(6,"NEW PRESS",session.state.pressed);
    if(session.state.pressed)recentPress=session.state.pressed;
    mask(7,"LAST PRESS",recentPress);
    mask(8,"EXPECTED",session.state.expected);mask(9,"HEAD HIT",session.state.hit);mask(10,"NOT HIT",session.state.missing);
    mask(12,"VALID HOLD",session.state.active);
    ScoreDisplay::line(0,13,"BONUS:");ScoreDisplay::value(7,13,session.state.bonus);
    ScoreDisplay::line(15,13,"DONE:");ScoreDisplay::value(21,13,session.state.completed);
    mask(14,"EVENT LANE",session.state.lastLane);
    ScoreDisplay::line(0,15,!session.state.lastLane?"READY":session.state.lastKind==0?"PERFECT":session.state.lastKind==1?"GOOD":session.state.lastKind==2?"MISS":"WRONG");
    const unsigned t=session.state.test;
    ScoreDisplay::line(0,16,t==7?"LEFT NOW B AFTER 0.5S":t==8?"HOLD LEFT 1.5S TAP B +0.75S":t==9?"HOLD BOTH FOR 1.5S":t==10?"RELEASE B +0.5S KEEP A 1.5S":t==11?"TAP B AT 0 / 0.17 / 0.34S":t==12?"LEFT B A EACH 0.34S":"TAP TARGET AT ZERO");
    ScoreDisplay::line(0,18,"START+SELECT: EXIT");
}
}
