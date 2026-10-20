// Replay an external full-song capture's musical timestamps and independently
// reconstructed actual-key driver trace through the unchanged gameplay core.
// Compile with the matching private runtime header; never commit that header.
#include "imported_chart.hpp"
#include "importedRuntime.hpp"
#include "scoring.hpp"
#include "sustain.hpp"
#include <fstream>
#include <string>
#include <cstdio>
#include <cassert>
#include <cstring>
struct Replay {
    ImportedRuntime<imported_note_count,5> notes{imported_notes};
    NoteScore<imported_note_count> score;
    Sustain::Holds<imported_note_count,5> holds{imported_notes,imported_sustain_us};
    static void event(void* p,const GameplayEvent& e){auto& r=*static_cast<Replay*>(p);r.score.consume(e);r.holds.event(e,r.score.snapshot().multiplier);}
    Replay(){notes.judgment().setEventSink(event,this);}
};
int main(int argc,char**argv){
 assert(argc==3||(argc==4&&!std::strcmp(argv[3],"--clock-only")));std::ifstream file(argv[1]);assert(file);std::string line;std::getline(file,line);Replay r;uint64_t previous=0,until[3]={};unsigned next=0,frames=0;
 while(std::getline(file,line)){
  unsigned frame,consumed,hardware,p,g,m;unsigned long long tick,captured;
  assert(std::sscanf(line.c_str(),"%u,%llu,%u,%u,%llu,%u,%u,%u",&frame,&tick,&consumed,&hardware,&captured,&p,&g,&m)==8);
  unsigned keys=0;if(frame>2){for(unsigned lane=0;lane<3;++lane)if(until[lane]>previous)keys|=1u<<lane;
   if(next<imported_note_count){unsigned lane=imported_notes[next].lane;uint64_t target=imported_notes[next].tick;
    if(target>previous+280896&&target<=previous+561792&&(keys&(1u<<lane))){keys&=~(1u<<lane);until[lane]=0;}}
   while(next<imported_note_count){uint64_t target=imported_notes[next].tick;if(target>previous+280896)break;unsigned lane=imported_notes[next].lane;keys|=1u<<lane;until[lane]=target+Sustain::duration(imported_sustain_us[next]);++next;}}
  r.score.addSustainBonus(r.holds.update(tick,keys));r.notes.updateTick(tick,keys);previous=tick;
  if(argc==3)assert(r.notes.stats().perfect==p&&r.notes.stats().good==g&&r.notes.stats().missed==m);++frames;
 }
 assert(r.score.resolved()&&r.holds.resolved()&&r.notes.stats().perfect==imported_note_count);std::fprintf(stderr,"Reconstructed score=%u bonus=%u\n",r.score.snapshot().score,r.holds.stats().bonus);assert(r.score.snapshot().score==std::stoul(argv[2]));
 std::printf("PASS:%uframes, exact external trace score%u hold_bonus%u completed%u\n",frames,r.score.snapshot().score,r.holds.stats().bonus,r.holds.stats().completed);
}
