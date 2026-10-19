#include "scoreDisplay.hpp"
#include "importedCompletion.hpp"
#include "tonc.h"
#include <tonc_tte.h>
// Tonc system font: readable 8x8 glyphs, using reserved BG tiles only.
namespace ScoreDisplay {
constexpr unsigned FIRST_TILE=128;
static unsigned map=31;
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
void clear() {
    // Restore the existing black depth mask and only the HUD rows of BG0.
    memset16(&tile_mem[0][1],0x6666,16);memset16(&se_mem[31],1,1024);
    memset16(&se_mem[30],0x004F,96);
}
void initialize() {
    // Expand the bundled Tonc 1bpp font to opaque 4bpp white-on-black.
    // Use a dedicated palette bank so the highway palettes cannot obscure it.
    memset32(&tile_mem[0][FIRST_TILE],0,8);
    memset32(&tile_mem[1][FIRST_TILE],0,8);
    pal_bg_mem[15*16+1]=RGB15(31,31,31);
    for(unsigned glyph=0;glyph<96;++glyph)for(unsigned y=0;y<8;++y) {
        unsigned bits=reinterpret_cast<const u8*>(sys8Glyphs)[glyph*8+y];
        u32 row=0;for(unsigned x=0;x<8;++x)if(bits&(1u<<x))row|=1u<<(x*4);
        tile_mem[0][FIRST_TILE+glyph+1].data[y]=row;
        tile_mem[1][FIRST_TILE+glyph+1].data[y]=row;
    }
    REG_BG1CNT=BG_BUILD(0,31,0,0,0,0,0);REG_BG1HOFS=REG_BG1VOFS=0;
    clear();
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
