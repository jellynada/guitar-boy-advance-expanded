#include "scoreDisplay.hpp"
#include "importedCompletion.hpp"
#include "tonc.h"
#include "text.h"
// Existing8x8 font, one glyph per map entry; no new assets or sprite budget.
namespace ScoreDisplay {
constexpr unsigned FIRST_TILE=128;
static unsigned map=31;
static void text(unsigned x,unsigned y,const char* value,unsigned maximum=30) {
    while(*value&&x<30&&maximum--) {
        const unsigned char c=*value++;
        se_mem[map][y*32+x++]=FIRST_TILE+((c>=32&&c<=126)?c-31:'?'-31);
    }
}
static void number(unsigned x,unsigned y,uint32_t value) {
    char buffer[11];unsigned n=0;
    do {buffer[n++]=char('0'+value%10);value/=10;}while(value);
    for(unsigned i=0;i<n/2;++i){char c=buffer[i];buffer[i]=buffer[n-1-i];buffer[n-1-i]=c;}
    buffer[n]=0;text(x,y,buffer);
}
static void row(unsigned y,const char* label,uint32_t value) {text(1,y,label);number(18,y,value);}
void clear() {
    // Restore the existing black depth mask and only the HUD rows of BG0.
    memset16(&tile_mem[0][1],0x6666,16);memset16(&se_mem[31],1,1024);
    memset16(&se_mem[30],0x004F,64);
}
void initialize() {
    memcpy32(&tile_mem[0][FIRST_TILE],textTiles,96*sizeof(TILE)/4);
    memcpy32(&tile_mem[1][FIRST_TILE],textTiles,96*sizeof(TILE)/4);
    REG_BG1CNT=BG_BUILD(0,31,0,0,0,0,0);REG_BG1HOFS=REG_BG1VOFS=0;
    clear();
}
void hud(const ScoreSnapshot& s,const char* judgment,const char* guitar) {
    map=30;memset16(&se_mem[30][0],FIRST_TILE,64);
    text(0,0,"S:");number(2,0,s.score);text(15,0,"C:");number(17,0,s.combo);
    text(0,1,"X:");number(2,1,s.multiplier);text(6,1,judgment,10);text(17,1,guitar,13);
}
void results(const ScoreSnapshot& s,const char* title,uint32_t sessionState) {
    map=31;memset16(&se_mem[31],FIRST_TILE,1024);
    text(1,0,sessionState==ImportedCompletion::Complete?"RESULTS":sessionState==ImportedCompletion::AudioError?"AUDIO ERROR":"DATA ERROR");
    text(1,2,title,28);
    row(4,sessionState==ImportedCompletion::Complete?"SCORE":"PARTIAL SCORE",s.score);
    text(1,5,"ACCURACY");number(18,5,s.accuracy/100);text(s.accuracy>=10000?21:s.accuracy>=1000?20:19,5,".");
    const unsigned dot=s.accuracy>=10000?21:s.accuracy>=1000?20:19;
    char decimals[]={char('0'+s.accuracy/10%10),char('0'+s.accuracy%10),'%',0};text(dot+1,5,decimals);
    row(6,"PERFECT",s.perfect);row(7,"GOOD",s.good);row(8,"MISS",s.missed);row(9,"WRONG INPUT",s.wrong);
    row(10,"MAX COMBO",s.maxCombo);row(11,"HIGHEST X",s.highestMultiplier);
    if(sessionState==ImportedCompletion::Complete) {
        if(s.allPerfect)text(1,13,"ALL PERFECT / FULL COMBO");
        else if(s.fullCombo)text(1,13,"FULL COMBO");
        else text(1,13,"SONG COMPLETE");
    } else text(1,13,sessionState==ImportedCompletion::AudioError?"SESSION INTERRUPTED":"UNRESOLVED / STATS MISMATCH");
    text(1,16,"A / START: REPLAY");text(1,18,"B / SELECT: MODE SELECT");
}
}
