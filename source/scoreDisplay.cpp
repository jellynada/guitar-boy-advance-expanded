#include "scoreDisplay.hpp"
#include "importedCompletion.hpp"
#include "tonc.h"
#include "gameControls.hpp"
#include "gameSession.hpp"
#include "buttons.h"
#include <tonc_tte.h>
// Tonc system font: readable 8x8 glyphs, using reserved BG tiles only.
namespace ScoreDisplay {
constexpr unsigned FIRST_TILE=128;
static unsigned map=31;
static constexpr unsigned controlCells[]={16*32+4,16*32+5,16*32+6,16*32+7,16*32+14,16*32+23};
static u16 savedControlTiles[6];
static u16 savedLabelRow[32];
static bool controlsDrawn=false;
static_assert(buttonsTilesLen<=128*32,"Pause/font tiles must not overlap receptor graphics");
constexpr unsigned PAUSE_TILE=224,PAUSE_X=5,PAUSE_Y=5,PAUSE_W=20,PAUSE_H=5;
EWRAM_DATA static u16 pauseTiles[PAUSE_W*PAUSE_H];
static bool pauseDrawn=false;
static void pauseText(unsigned x,unsigned y,const char* value){
    while(*value){unsigned c=static_cast<unsigned char>(*value++);
        se_mem[30][y*32+x++]=(PAUSE_TILE+c-31)|SE_PALBANK(15);}
}
void pauseShow(){
    if(pauseDrawn)return;
    for(unsigned y=0;y<PAUSE_H;++y)for(unsigned x=0;x<PAUSE_W;++x){
        const unsigned i=y*PAUSE_W+x,offset=(PAUSE_Y+y)*32+PAUSE_X+x;
        pauseTiles[i]=se_mem[30][offset];se_mem[30][offset]=(PAUSE_TILE+1)|SE_PALBANK(15);
    }
    pauseText(11,5,"PAUSED");pauseText(8,7,"START: RESUME");pauseText(8,9,"SELECT: EXIT");pauseDrawn=true;
}
void pauseHide(){
    if(!pauseDrawn)return;
    for(unsigned y=0;y<PAUSE_H;++y)for(unsigned x=0;x<PAUSE_W;++x)
        se_mem[30][(PAUSE_Y+y)*32+PAUSE_X+x]=pauseTiles[y*PAUSE_W+x];
    pauseDrawn=false;
}
void preparePauseFont(){
    for(unsigned glyph=0;glyph<96;++glyph)for(unsigned y=0;y<8;++y) {
        unsigned bits=reinterpret_cast<const u8*>(sys8Glyphs)[glyph*8+y];
        u32 row=0;for(unsigned x=0;x<8;++x)if(bits&(1u<<x))row|=1u<<(x*4);
        tile_mem[0][FIRST_TILE+glyph+1].data[y]=row;
        tile_mem[1][FIRST_TILE+glyph+1].data[y]=row;
    }
    const char* label=" PAUSEDSTART: RESUMESELECT: EXIT";
    while(*label){const unsigned c=static_cast<unsigned char>(*label++);
        for(unsigned y=0;y<8;++y){const unsigned bits=reinterpret_cast<const u8*>(sys8Glyphs)[(c-32)*8+y];
            u32 row=0;for(unsigned x=0;x<8;++x)row|=u32(bits&(1u<<x)?1:2)<<(x*4);
            tile_mem[1][PAUSE_TILE+c-31].data[y]=row;}
    }
}
static void text(unsigned x,unsigned y,const char* value,unsigned maximum=30) {
    while(*value&&x<30&&maximum--) {
        const unsigned char c=*value++;
        se_mem[map][y*32+x++]=(FIRST_TILE+((c>=32&&c<=126)?c-31:'?'-31))|SE_PALBANK(15);
    }
}
static void number(unsigned x,unsigned y,uint32_t value) {
    char buffer[11];unsigned n=0;
    do {buffer[n++]=char('0'+value%10);value/=10;}while(value);
    for(unsigned i=0;i<n/2;++i){char c=buffer[i];buffer[i]=buffer[n-1-i];buffer[n-1-i]=c;}
    buffer[n]=0;text(x,y,buffer);
}
static void row(unsigned y,const char* label,uint32_t value) {text(1,y,label);number(18,y,value);}
void page(){map=31;memset16(&se_mem[31],FIRST_TILE,1024);}
void line(unsigned x,unsigned y,const char* value){if(y<20)text(x,y,value);}
void value(unsigned x,unsigned y,uint32_t value){if(y<20)number(x,y,value);}
void clear() {
    pauseHide();
    // Restore the existing black depth mask and only the HUD rows of BG0.
    memset16(&tile_mem[0][1],0x6666,16);memset16(&se_mem[31],1,1024);
    memset16(&se_mem[30],0x004F,96);
    if(controlsDrawn){
        if(importedLaneCount==3){for(unsigned i=0;i<6;++i)se_mem[30][controlCells[i]]=savedControlTiles[i];}
        else for(unsigned i=0;i<32;++i)se_mem[30][16*32+i]=savedLabelRow[i];
        controlsDrawn=false;
    }
}
void initialize() {
    // Expand the bundled Tonc 1bpp font to opaque 4bpp white-on-black.
    // Use a dedicated palette bank so the highway palettes cannot obscure it.
    memset32(&tile_mem[0][FIRST_TILE],0,8);
    memset32(&tile_mem[1][FIRST_TILE],0,8);
    pal_bg_mem[15*16+1]=RGB15(31,31,31);
    pal_bg_mem[15*16+2]=RGB15(0,0,0);
    // Small opaque-font overlay, prepared once before playback. Original
    // transparent HUD/font tiles and highway BG1/BG2 are never modified.
    REG_BG1CNT=BG_BUILD(0,31,0,0,0,0,0);REG_BG1HOFS=REG_BG1VOFS=0;
    clear();
    for(unsigned i=0;i<6;++i)savedControlTiles[i]=se_mem[30][controlCells[i]];
    map=30;
    if(importedLaneCount==3){text(4,16,EASY_LABELS[0]);text(14,16,EASY_LABELS[1]);text(23,16,EASY_LABELS[2]);}
    else {for(unsigned i=0;i<32;++i)savedLabelRow[i]=se_mem[30][16*32+i];
        for(unsigned i=0;i<importedLaneCount;++i){const char* label=importedLabel(i,importedLaneCount);unsigned length=0;while(label[length])++length;
            text(receptorX(i,importedLaneCount)+(receptorWidth(importedLaneCount)-length)/2,16,label,receptorWidth(importedLaneCount));}}
    controlsDrawn=true;
}
void hud(const ScoreSnapshot& s,const char* judgment,const char* guitar) {
    map=30;memset16(&se_mem[30][0],FIRST_TILE,96);
    text(0,0,"SCORE:");number(6,0,s.score);
    text(0,1,"COMBO:");number(6,1,s.combo);text(16,1,"MULT:");number(21,1,s.multiplier);text(23,1,"X");
    text(0,2,judgment,10);text(17,2,guitar,13);
}
void results(const ScoreSnapshot& s,const char* title,uint32_t sessionState,uint32_t diagnostic) {
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
    if(diagnostic)text(1,14,diagnostic==1?"CLOCK DID NOT SETTLE":diagnostic==2?"UNRESOLVED NOTES":"STATS MISMATCH");
    row(12,"HOLDS DONE",s.holdsCompleted);if(!diagnostic)row(14,"EARLY RELEASES",s.holdsReleased);row(15,"HOLD BONUS",s.sustainBonus);
    text(1,16,"A / START: REPLAY");text(1,18,"B / SELECT: MODE SELECT");
}
}
