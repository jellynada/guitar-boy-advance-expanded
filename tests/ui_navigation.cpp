#include "uiNavigation.hpp"
#include <cassert>
#include <cstring>
using namespace UiNav;
static Song song={"stable","Fixture","",75,7,true,1};
static Catalog cat{&song,1};
static Action press(Controller& c,uint16_t key,Catalog list=cat){c.poll(list,0);auto a=c.poll(list,key);return a;}
int main(){
 Controller c;assert(c.screen==Screen::Title);c.poll(cat,A);assert(c.screen==Screen::Title);press(c,START);assert(c.screen==Screen::Main);
 for(int n=0;n<50;++n){c.poll(cat,START);}assert(c.screen==Screen::Main);
 press(c,A);assert(c.screen==Screen::Songs);press(c,A);assert(c.screen==Screen::Difficulty);press(c,DOWN);assert(c.cursor==1);assert(press(c,A)==Action::Start&&c.difficulty==1);
 c.enter(Screen::Pause,A|START);c.poll(cat,A|START);assert(c.screen==Screen::Pause);c.poll(cat,A);assert(c.poll(cat,A|START)==Action::Resume); // held A never double-confirms
 c.enter(Screen::Pause,0);press(c,DOWN);assert(press(c,A)==Action::Restart);press(c,DOWN);assert(press(c,A)==Action::Quit);press(c,B);assert(c.cursor==0);assert(press(c,START)==Action::Resume);
 for(unsigned choice=0;choice<4;++choice){c.enter(Screen::Results,A);for(unsigned i=0;i<choice;++i)press(c,DOWN);auto action=press(c,A);assert(action==(choice?Action::Quit:Action::Restart));if(choice==1)assert(c.screen==Screen::Difficulty);if(choice==2)assert(c.screen==Screen::Songs);if(choice==3)assert(c.screen==Screen::Main);}
 c.enter(Screen::Main,0);press(c,DOWN);press(c,A);assert(c.screen==Screen::Options);press(c,B);press(c,DOWN);press(c,DOWN);press(c,A);assert(c.screen==Screen::Credits);press(c,B);press(c,B);assert(c.screen==Screen::Title);
 for(int loop=0;loop<500;++loop){press(c,START);press(c,A);press(c,A);assert(press(c,A)==Action::Start);c.enter(Screen::Results,0);press(c,B);assert(c.screen==Screen::Songs);press(c,B);press(c,B);assert(c.screen==Screen::Title);}
 Song entries[8];for(unsigned i=0;i<8;++i)entries[i]=song;entries[2].available=false;entries[4].assetReference=0;Catalog many{entries,8};assert(many.size()==6);c.songs(many,0);for(unsigned i=0;i<5;++i)press(c,DOWN,many);assert(c.cursor==5&&c.first==1);press(c,A,many);assert(c.song==7);press(c,B,many);assert(c.screen==Screen::Songs&&c.cursor==5);press(c,DOWN,many);assert(c.cursor==0&&c.first==0);
 c.enter(Screen::Songs,0);c.cursor=200;assert(press(c,A)==Action::None);c.song=200;c.difficulties(cat,0);assert(c.screen==Screen::Songs);Catalog empty{nullptr,0};assert(empty.size()==0);assert(press(c,A,empty)==Action::None);
 c.enter(Screen::Main,0);c.poll(cat,UP|DOWN);assert(c.cursor==0);c.poll(cat,0);c.poll(cat,A|B);assert(c.screen==Screen::Main);c.poll(cat,0);c.poll(cat,A|DOWN);assert(c.screen==Screen::Main&&c.cursor==1);
 char title[8];bounded(title,sizeof title,"A VERY LONG TITLE");assert(!strcmp(title,"A VERY "));char zero='x';bounded(&zero,0,"bad");assert(zero=='x');bounded(title,sizeof title,nullptr);assert(!*title);
 entries[0].difficulties=4;Catalog hard{entries,1};c.song=0;c.difficulty=0;c.difficulties(hard,0);assert(c.difficulty==2);assert(press(c,A,hard)==Action::Start&&c.difficulty==2);
 Catalog invalid{entries,33};assert(!invalid.size());
}
