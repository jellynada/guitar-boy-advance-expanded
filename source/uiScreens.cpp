#include "tonc.h"
#include "uiScreens.hpp"
#include "gameSession.hpp"
#include "scoreDisplay.hpp"
#include "imported_chart.hpp"
#include "importedSelection.hpp"
#include "imported_audio.hpp"
#include "ui_song.hpp"
#include "build_identity.hpp"
#include "importedCompletion.hpp"
#ifdef GBA_MULTI_SONG
#include "song_collection.hpp"
#endif
namespace UiScreens {
EWRAM_DATA UiNav::Controller controller;
#ifndef GBA_MULTI_SONG
static constexpr uint8_t mask(){uint8_t result=0;for(unsigned i=0;i<imported_choice_count;++i)if(imported_choices[i].lanes>=3&&imported_choices[i].lanes<=5)result|=1u<<(imported_choices[i].lanes-3);return result;}
static const UiNav::Song songs[]={{UI_SONG_ID,UI_SONG_TITLE?UI_SONG_TITLE:imported_title,UI_SONG_ARTIST,imported_audio_source_samples/imported_audio_rate,mask(),true,1}};
UiNav::Catalog catalog(){return {songs,1};}
#else
UiNav::Catalog catalog(){return {collectionCatalog,collectionSongCount};}
#endif
void sync(){uiScreen=unsigned(controller.screen);uiCursor=controller.cursor;uiSong=controller.song;uiDifficulty=controller.difficulty;}
static void centered(unsigned row,const char* value){char bounded[31];UiNav::bounded(bounded,sizeof bounded,value);unsigned n=0;while(bounded[n])++n;ScoreDisplay::line((30-n)/2,row,bounded);}
static void item(unsigned row,unsigned index,const char* text){ScoreDisplay::line(1,row,controller.cursor==index?">":" ");ScoreDisplay::line(3,row,text);}
void draw(const ScoreSnapshot& s,unsigned completion,unsigned diagnostic){
 sync();using UiNav::Screen;const auto screen=controller.screen;
 if(screen==Screen::Difficulty)gameMode=4;else if(screen!=Screen::Playing&&screen!=Screen::Pause&&screen!=Screen::Results)gameMode=0;
 if(screen==Screen::Pause){ScoreDisplay::pauseMenu(controller.cursor);return;}
 pal_bg_mem[0]=0;pal_bg_mem[241]=RGB15(31,31,31);pal_bg_mem[242]=0;
 REG_BG1CNT=BG_BUILD(0,31,0,0,0,0,0);REG_BG1HOFS=REG_BG1VOFS=0;REG_BLDCNT=0;REG_DISPCNT=DCNT_BG1|DCNT_MODE0;
 ScoreDisplay::page();
 if(screen==Screen::Title){centered(4,"GUITAR BOY");centered(6,"ADVANCE");centered(9,"EXPANDED");centered(14,"PRESS START");return;}
 if(screen==Screen::Main){centered(2,"GUITAR BOY ADVANCE");centered(4,"EXPANDED");item(8,0,"PLAY");item(10,1,"OPTIONS");item(12,2,"CREDITS");ScoreDisplay::line(1,18,"A/START: SELECT   B: TITLE");return;}
 const auto cat=catalog();const auto* song=cat.valid(controller.song)?&cat.entries[controller.song]:nullptr;
 if(screen==Screen::Songs){if(controller.cursor<cat.size())song=&cat.entries[cat.index(controller.cursor)];centered(1,"SELECT A SONG");for(unsigned row=0;row<UiNav::VISIBLE_ROWS;++row){unsigned p=controller.first+row;if(p>=cat.size())break;item(5+row*2,p,cat.entries[cat.index(p)].title);}if(!cat.size())centered(8,"NO PLAYABLE CONTENT");if(song){ScoreDisplay::line(1,15,song->artist?song->artist:"");ScoreDisplay::line(1,16,"DURATION SECONDS:");ScoreDisplay::value(20,16,song->durationSeconds);}ScoreDisplay::line(1,18,"A: SELECT   B: MAIN MENU");return;}
 if(screen==Screen::Difficulty){centered(1,song?song->title:"UNAVAILABLE");centered(3,"CHOOSE DIFFICULTY");if(song){const char* names[]={"EASY  LEFT B A","MEDIUM  L R B A","HARD  L U/D R B A"};for(unsigned i=0;i<UiNav::difficultyCount(song->difficulties);++i)item(7+i*2,i,names[UiNav::difficultyAt(song->difficulties,i)]);}ScoreDisplay::line(1,16,"U/D = UP OR DOWN ALIAS");ScoreDisplay::line(1,18,"A: PLAY   B: SONG SELECT");return;}
 if(screen==Screen::Options){centered(1,"CONTROLS / BUILD INFO");ScoreDisplay::line(1,4,"EASY: LEFT B A");ScoreDisplay::line(1,6,"MEDIUM: LEFT RIGHT B A");ScoreDisplay::line(1,8,"HARD: LEFT UP/DOWN RIGHT B A");ScoreDisplay::line(1,10,"START: PAUSE / RESUME");ScoreDisplay::line(1,11,"PAUSED SELECT: SONG SELECT");
#ifdef GBA_MULTI_SONG
 ScoreDisplay::line(1,13,"M022 DEVELOPMENT REVIEW");
#else
 ScoreDisplay::line(1,13,"M021 DEVELOPMENT REVIEW");
#endif
 ScoreDisplay::line(1,14,GBA_SOURCE_REVISION);ScoreDisplay::line(1,16,"A: INPUT TEST");
#ifndef GBA_PUBLIC_DEMO
 ScoreDisplay::line(1,17,"SELECT: LEGACY DEMO TEST");
#endif
 ScoreDisplay::line(1,19,"B: MAIN MENU");return;}
 if(screen==Screen::Credits){centered(1,"GUITAR BOY ADVANCE");centered(3,"EXPANDED");ScoreDisplay::line(1,6,"BASED ON GUITAR-BOY-ADVANCE");ScoreDisplay::line(1,8,"ORIGINAL PROJECT: STARTFLIING");ScoreDisplay::line(1,11,"EXPANDED SOURCE:");ScoreDisplay::line(1,12,"JELLYNADA / GITHUB");ScoreDisplay::line(1,15,"MUSIC: SEE SOURCE PACKAGE");ScoreDisplay::line(1,18,"B: MAIN MENU");return;}
 if(screen==Screen::Results){centered(0,completion==ImportedCompletion::Complete?"SONG COMPLETE!":"SESSION INTERRUPTED");centered(2,song?song->title:"");const char* names[]={"EASY","MEDIUM","HARD"};centered(3,names[controller.difficulty<3?controller.difficulty:0]);ScoreDisplay::line(1,5,"SCORE:");ScoreDisplay::value(19,5,s.score);ScoreDisplay::line(1,6,"ACCURACY:");ScoreDisplay::value(19,6,s.accuracy/100);ScoreDisplay::line(s.accuracy>=10000?22:s.accuracy>=1000?21:20,6,".");unsigned dot=s.accuracy>=10000?22:s.accuracy>=1000?21:20;char frac[]={char('0'+s.accuracy/10%10),'%',0};ScoreDisplay::line(dot+1,6,frac);ScoreDisplay::line(1,7,"MAX COMBO:");ScoreDisplay::value(19,7,s.maxCombo);ScoreDisplay::line(1,8,"PERFECT / GOOD / MISS");ScoreDisplay::value(1,9,s.perfect);ScoreDisplay::value(11,9,s.good);ScoreDisplay::value(21,9,s.missed);if(diagnostic)ScoreDisplay::line(1,10,"CHECK BUILD DIAGNOSTICS");else ScoreDisplay::line(1,10,s.fullCombo?"FULL COMBO":"A/START SELECT  B SONGS");item(12,0,"RETRY");item(14,1,"CHANGE DIFFICULTY");item(16,2,"SONG SELECT");item(18,3,"MAIN MENU");}
}
}
extern "C" {EWRAM_DATA volatile uint32_t uiScreen=0,uiCursor=0,uiSong=0,uiDifficulty=0;}
