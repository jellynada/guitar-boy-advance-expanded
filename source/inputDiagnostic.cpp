#include "inputDiagnostic.hpp"
#include "scoreDisplay.hpp"
#include <tonc.h>
namespace InputDiagnostic {
static Session session;
static unsigned recentPress=0;
extern "C" {Snapshot diagnosticSnapshot;uint32_t diagnosticResults[COUNT];}
static const char* label(Result r){switch(r){case Result::Waiting:return "WAIT";case Result::Pass:return "PASS";case Result::Partial:return "PARTIAL";case Result::Miss:return "MISS";case Result::Wrong:return "WRONG";case Result::HoldEarly:return "HOLD FAIL";}return "?";}
static void mask(unsigned y,const char* title,unsigned value){
    ScoreDisplay::line(0,y,title);ScoreDisplay::line(11,y,value&1?"LEFT":"----");ScoreDisplay::line(17,y,value&2?"A":"-");ScoreDisplay::line(21,y,value&4?"B":"-");
}
bool finished(){return session.finished();}
void start(uint8_t held){session.reset(held);recentPress=0;ScoreDisplay::initialize();REG_BLDCNT=0;REG_DISPCNT=DCNT_BG1|DCNT_MODE0;pal_bg_mem[0]=0;}
void update(unsigned frame,uint8_t held){
    session.update(frame,held);diagnosticSnapshot=session.state;
    for(unsigned i=0;i<COUNT;++i)diagnosticResults[i]=uint32_t(session.result(i));
    ScoreDisplay::page();ScoreDisplay::line(0,0,"INPUT / CHORD TEST - M010");
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
    ScoreDisplay::line(0,14,"LAST HIT LANE:");ScoreDisplay::value(15,14,session.state.lastLane);
    ScoreDisplay::line(19,14,session.state.lastKind==0?"PERFECT":session.state.lastKind==1?"GOOD":session.state.lastKind==2?"MISS":"WRONG");
    const unsigned t=session.state.test;
    ScoreDisplay::line(0,16,t==7?"LEFT NOW A AFTER 0.5S":t==8?"HOLD LEFT 1.5S TAP A +0.75S":t==9?"HOLD BOTH FOR 1.5S":t==10?"RELEASE A +0.5S KEEP B 1.5S":t==11?"TAP A AT 0 / 0.17 / 0.34S":t==12?"LEFT A B EACH 0.34S":"TAP TARGET AT ZERO");
    ScoreDisplay::line(0,18,"START+SELECT: EXIT");
}
}
