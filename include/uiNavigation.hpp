#ifndef UI_NAVIGATION_HPP
#define UI_NAVIGATION_HPP
#include <cstdint>
// UI policy only: no chart, judgment, audio, allocation or hardware access.
namespace UiNav {
enum class Screen:uint32_t {Title,Main,Songs,Difficulty,Playing,Pause,Results,Options,Credits,Diagnostic,Legacy};
enum class Action:uint8_t {None,Start,Resume,Restart,Quit,Diagnostic,Legacy};
constexpr uint16_t A=1,B=2,SELECT=4,START=8,UP=64,DOWN=128;
constexpr unsigned MAX_SONGS=32,VISIBLE_ROWS=5;
struct Song {const char* id;const char* title;const char* artist;uint32_t durationSeconds;uint8_t difficulties;bool available;uint16_t assetReference;};
struct Catalog {
 const Song* entries;unsigned count;
 bool valid(unsigned i)const{return entries&&count<=MAX_SONGS&&i<count&&entries[i].id&&*entries[i].id&&entries[i].title&&*entries[i].title&&entries[i].available&&entries[i].assetReference&&entries[i].difficulties&&(entries[i].difficulties&~7u)==0;}
 unsigned size()const{unsigned n=0;for(unsigned i=0;i<count&&i<MAX_SONGS;++i)n+=valid(i);return n;}
 unsigned index(unsigned position)const{for(unsigned i=0;i<count&&i<MAX_SONGS;++i)if(valid(i)){if(!position)return i;--position;}return MAX_SONGS;}
 unsigned position(unsigned index)const{unsigned n=0;for(unsigned i=0;i<index&&i<count&&i<MAX_SONGS;++i)n+=valid(i);return n;}
};
struct Input {
 uint16_t previous=0,blocked=0;
 void seed(uint16_t held){previous=blocked=held;}
 uint16_t poll(uint16_t held){blocked&=held;uint16_t fresh=held&~previous&~blocked;previous=held;return fresh;}
};
inline unsigned difficultyCount(uint8_t mask){return unsigned(!!(mask&1))+unsigned(!!(mask&2))+unsigned(!!(mask&4));}
inline unsigned difficultyAt(uint8_t mask,unsigned position){for(unsigned i=0;i<3;++i)if(mask&(1u<<i)){if(!position)return i;--position;}return 3;}
inline void bounded(char* out,unsigned capacity,const char* in){if(!capacity)return;unsigned i=0;while(in&&in[i]&&i+1<capacity){unsigned char c=in[i];out[i]=(c>=32&&c<=126)?char(c):'?';++i;}out[i]=0;}
struct Controller {
 Screen screen=Screen::Title;unsigned cursor=0,song=0,difficulty=0,first=0;Input input;
 void enter(Screen next,uint16_t held){screen=next;cursor=first=0;input.seed(held);}
 void songs(Catalog c,uint16_t held){enter(Screen::Songs,held);cursor=c.valid(song)?c.position(song):0;first=cursor>=VISIBLE_ROWS?cursor-VISIBLE_ROWS+1:0;}
 void difficulties(Catalog c,uint16_t held){if(!c.valid(song)){songs(c,held);return;}enter(Screen::Difficulty,held);uint8_t mask=c.entries[song].difficulties;if(!(mask&(1u<<difficulty)))difficulty=difficultyAt(mask,0);for(unsigned i=0;i<difficultyCount(mask);++i)if(difficultyAt(mask,i)==difficulty)cursor=i;}
 Action poll(Catalog c,uint16_t held,bool legacyAvailable=false){
  const uint16_t fresh=input.poll(held);const bool confirm=fresh&(A|START),back=fresh&B;
  if((confirm&&back)||((held&(START|SELECT))==(START|SELECT)))return Action::None;
  if(screen==Screen::Title){if(fresh&START)enter(Screen::Main,held);return Action::None;}
  if(screen==Screen::Playing||screen==Screen::Diagnostic||screen==Screen::Legacy)return Action::None;
  if(screen==Screen::Pause&&(fresh&START))return Action::Resume;
  if(screen==Screen::Pause&&(fresh&SELECT))return Action::Quit; // retained explicit paused shortcut
  if(back){switch(screen){
   case Screen::Main:enter(Screen::Title,held);break;
   case Screen::Songs:enter(Screen::Main,held);break;
   case Screen::Difficulty:songs(c,held);break;
   case Screen::Pause:cursor=0;break; // cancel destructive selection, stay paused
   case Screen::Results:songs(c,held);return Action::Quit;
   case Screen::Options:case Screen::Credits:enter(Screen::Main,held);break;
   default:break;}return Action::None;}
  unsigned n=0;
  switch(screen){case Screen::Main:n=3;break;case Screen::Songs:n=c.size();break;case Screen::Difficulty:n=c.valid(song)?difficultyCount(c.entries[song].difficulties):0;break;case Screen::Pause:n=3;break;case Screen::Results:n=4;break;default:break;}
  if((held&(UP|DOWN))!=(UP|DOWN)&&(fresh&(UP|DOWN))){if(n){cursor=(cursor%n+n+((fresh&DOWN)?1:-1))%n;if(cursor<first)first=cursor;if(cursor>=first+VISIBLE_ROWS)first=cursor-VISIBLE_ROWS+1;}return Action::None;}
  if(screen==Screen::Options){if(fresh&A)return Action::Diagnostic;if(legacyAvailable&&(fresh&SELECT))return Action::Legacy;return Action::None;}
  if(!confirm)return Action::None;
  switch(screen){
   case Screen::Main:if(cursor==0)songs(c,held);else if(cursor<3)enter(cursor==1?Screen::Options:Screen::Credits,held);break;
   case Screen::Songs:if(cursor<c.size()){song=c.index(cursor);difficulties(c,held);}break;
   case Screen::Difficulty:if(c.valid(song)&&cursor<difficultyCount(c.entries[song].difficulties)){difficulty=difficultyAt(c.entries[song].difficulties,cursor);enter(Screen::Playing,held);return Action::Start;}break;
   case Screen::Pause:if(cursor<3)return cursor==0?Action::Resume:cursor==1?Action::Restart:Action::Quit;break;
   case Screen::Results:if(cursor==0)return Action::Restart;if(cursor==1){difficulties(c,held);return Action::Quit;}if(cursor==2){songs(c,held);return Action::Quit;}if(cursor==3){enter(Screen::Main,held);return Action::Quit;}break;
   default:break;
  }
  return Action::None;
 }
};
}
#endif
