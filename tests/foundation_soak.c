// Single-core, no-reset scene soak. Actual ROM keys; no writes to game RAM.
#define main prior_timing_probe_main
#include "demo_timing_emulator.c"
#undef main
#include <mgba/internal/gba/gba.h>
#include <sys/resource.h>
static uint64_t framesRun,nonzero,checkedFrames,displaced,playingCycles,pausedCycles,menuCycles,resultCycles;static uint64_t judgments[4];
static unsigned peakHeads,peakTails,peakWork,peakRefill,sceneCount,pauseCount,transientFrames;
static unsigned modeA,sessionA,phaseA,clockA,countA,lanesA,readyA,statsA,scoreA,headFirstA,headEndA,tailA,workA,refillA,underrunA,deadlineA;
static color_t pixelsSoak[38400];
static uint64_t ticks(struct mCore*c){return mTimingGlobalTime(&((struct GBA*)c->board)->timing);}
static void stepSoak(struct mCore*c,unsigned keys){
 uint64_t begin=ticks(c);unsigned scene=c->busRead32(c,modeA),phase=c->busRead32(c,phaseA);frame(c,keys);++framesRun;uint64_t elapsed=ticks(c)-begin;if(scene==1||(scene==2&&phase==1))playingCycles+=elapsed;else if(scene==2&&phase==2)pausedCycles+=elapsed;else if(scene==2&&phase==3)resultCycles+=elapsed;else menuCycles+=elapsed;
 for(int ch=0;ch<2;ch++){short v[4096];int n;while((n=blip_read_samples(c->getAudioChannel(c,ch),v,4096,0))>0)if(!ch)for(int i=0;i<n;i++)nonzero+=v[i]!=0;}
 if(c->busRead32(c,modeA)==2){
  unsigned heads=c->busRead32(c,headEndA)-c->busRead32(c,headFirstA),tails=c->busRead32(c,tailA),work=c->busRead32(c,workA),refill=c->busRead32(c,refillA);
  assert(heads<=32&&tails<=96&&work<280896);if(heads>peakHeads)peakHeads=heads;if(tails>peakTails)peakTails=tails;if(work>peakWork)peakWork=work;if(refill>peakRefill)peakRefill=refill;
  assert(!c->busRead32(c,underrunA)&&!c->busRead32(c,deadlineA));
  if(!c->busRead32(c,readyA))++transientFrames;
  if(framesRun%64==0&&c->busRead32(c,readyA)&&c->busRead32(c,phaseA)==1&&(c->busRead16(c,0x04000000)&1024)){
   unsigned table=c->busRead32(c,address(getenv("SOAK_SYMBOLS"),"scanlineActiveData"));assert(table);unsigned floor=0,bad=defects(c,pixelsSoak,table,&floor);++checkedFrames;displaced+=bad;if(bad){fprintf(stderr,"SOAK_FLOOR_FAILURE frame=%llu scene=%u bad=%u mode=%u ready=%u phase=%u tick=%llu vcount=%u dispcnt=%x dma=%x/%x\n",(unsigned long long)framesRun,sceneCount,bad,c->busRead32(c,modeA),c->busRead32(c,readyA),c->busRead32(c,phaseA),(unsigned long long)read64(c,clockA),c->busRead16(c,0x4000006),c->busRead16(c,0x4000000),c->busRead32(c,0x40000b8),c->busRead32(c,0x40000dc));screenshot(getenv("SOAK_OUTPUT"),"failure",pixelsSoak);}assert(!bad);
  }
 }
}
static void pressSoak(struct mCore*c,unsigned keys){stepSoak(c,0);stepSoak(c,keys);stepSoak(c,0);}
static void waitReady(struct mCore*c){for(unsigned w=0;w<16&&!c->busRead32(c,readyA);w++)stepSoak(c,0);assert(c->busRead32(c,readyA));}
int main(int argc,char**argv){assert(argc==6);const char*sy=argv[2],*profile=argv[4];unsigned seconds=strtoul(argv[3],0,10);assert(seconds>0&&seconds<=7200);int privateProfile=!strcmp(profile,"private"),legacy=!strcmp(profile,"legacy");assert(privateProfile||legacy||!strcmp(profile,"public"));assert(setenv("SOAK_SYMBOLS",sy,1)==0);assert(setenv("SOAK_OUTPUT",argv[5],1)==0);
#define SA(field,name) field=address(sy,name)
 SA(modeA,"gameMode");SA(sessionA,"importedSessionState");SA(phaseA,"importedTransport");SA(clockA,"importedNowCycles");SA(countA,"importedChartCount");SA(lanesA,"importedLaneCount");SA(readyA,"importedReady");SA(statsA,"displayedStats");SA(scoreA,"displayedScore");SA(headFirstA,"importedFirstVisible");SA(headEndA,"importedEndVisible");SA(tailA,"sustainTailSprites");SA(workA,"importedFrameWorkMaxCycles");SA(refillA,"audioRefillMaxCycles");SA(underrunA,"audioUnderruns");SA(deadlineA,"scanlineDeadlineMisses");
#undef SA
 struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);struct mCore*c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);c->setVideoBuffer(c,pixelsSoak,240);c->setAudioBufferSize(c,4096);for(int ch=0;ch<2;ch++)blip_set_rates(c->getAudioChannel(c,ch),c->frequency(c),32768);struct mCoreCallbacks cb={.coreCrashed=crash};c->addCoreCallbacks(c,&cb);assert(mCoreLoadFile(c,argv[1]));c->reset(c);uint64_t begin=ticks(c),target=(uint64_t)seconds*16777216;unsigned completed[3]={0},perfectRuns=0,missRuns=0,mixedRuns=0,exits=0;uint64_t referenceScore[3]={0};
 for(unsigned f=0;f<90;f++)stepSoak(c,0);
 if(legacy){pressSoak(c,1);assert(c->busRead32(c,modeA)==1);while(ticks(c)-begin<target){stepSoak(c,0);assert(c->busRead32(c,modeA)==1);}assert(c->busRead32(c,statsA+8)==699);}
 else while(ticks(c)-begin<target){
  assert(c->busRead32(c,modeA)==0);for(unsigned idle=0;idle<(sceneCount==0?3600u:sceneCount%7==0?600u:3u);idle++)stepSoak(c,0);
  if(privateProfile&&sceneCount==0)pressSoak(c,128);
  pressSoak(c,1);assert(c->busRead32(c,modeA)==4);
  unsigned difficulty=privateProfile?0:sceneCount%3;unsigned choice=c->busRead32(c,address(sy,"_ZL19difficultySelection"));for(unsigned turns=0;choice!=difficulty&&turns<3;turns++){pressSoak(c,128);choice=c->busRead32(c,address(sy,"_ZL19difficultySelection"));}assert(choice==difficulty);pressSoak(c,1);assert(c->busRead32(c,modeA)==2);waitReady(c);assert(c->busRead32(c,scoreA)==0&&c->busRead32(c,statsA)==0&&c->busRead32(c,statsA+12)==0);
  unsigned count=c->busRead32(c,countA),lanes=c->busRead32(c,lanesA),notes=c->busRead32(c,address(sy,"activeImportedNotes")),lengths=c->busRead32(c,address(sy,"activeImportedSustains")),buttons[5]={32,2,1,0,0};assert(count==(privateProfile?395:difficulty==0?86:difficulty==1?171:335));if(lanes==4){unsigned b[]={32,16,2,1};memcpy(buttons,b,sizeof b);}if(lanes==5){unsigned b[]={32,64,16,2,1};memcpy(buttons,b,sizeof b);}
  unsigned pattern=(sceneCount/3)%3,next=0,pauses=0;uint64_t until[5]={0},previous=0;unsigned budget=privateProfile?17500:5100;
  for(unsigned f=0;f<budget&&c->busRead32(c,sessionA)==0;f++){
   uint64_t now=read64(c,clockA);assert(now>=previous);previous=now;unsigned keys=0;
   for(unsigned l=0;l<lanes;l++)if(until[l]>now)keys|=buttons[l];
   if(next<count){unsigned l=c->busRead32(c,notes+next*16+8);uint64_t t=read64(c,notes+next*16);if(t>now+280896&&t<=now+561792&&(keys&buttons[l])){keys&=~buttons[l];until[l]=0;}}
   while(next<count){uint64_t t=read64(c,notes+next*16);if(t>now+280896)break;if(pattern==2&&next%5==0&&now<t+587202)break;unsigned l=c->busRead32(c,notes+next*16+8);assert(l<lanes);if(pattern!=1&&(pattern!=2||next%3!=1)){keys|=buttons[l];until[l]=t+(read64(c,lengths+next*8)*16777216ULL+500000)/1000000;}next++;}
   if(pattern==2&&f>10&&f%30==0)keys=lanes==3?35:lanes==4?(f%60?35:19):(f%60?35:82);
   if(lanes==5&&(keys&192))keys=(keys&~192)|(f%2?64:128);
   assert((keys&48)!=48&&(keys&192)!=192);
   if((f==70||f==180||f==600)&&pauses<3){
    stepSoak(c,keys|8);stepSoak(c,keys);assert(c->busRead32(c,phaseA)==2);uint64_t frozen=read64(c,clockA);unsigned score=c->busRead32(c,scoreA),events=c->busRead32(c,address(sy,"guitarEventSerial"));
    unsigned wait=sceneCount%5==0?600:6;for(unsigned w=0;w<wait;w++){stepSoak(c,keys);assert(read64(c,clockA)==frozen&&c->busRead32(c,scoreA)==score&&c->busRead32(c,address(sy,"guitarEventSerial"))==events);}
    stepSoak(c,keys);stepSoak(c,keys|8);stepSoak(c,keys|8);assert(c->busRead32(c,phaseA)==1);stepSoak(c,keys);++pauses;++pauseCount;
   }else stepSoak(c,keys);
  }
  assert(c->busRead32(c,sessionA)==1);assert(c->busRead32(c,statsA)+c->busRead32(c,statsA+4)+c->busRead32(c,statsA+8)==count);assert(c->busRead32(c,address(sy,"audioState"))==2);++completed[difficulty];for(unsigned j=0;j<4;j++)judgments[j]+=c->busRead32(c,statsA+j*4);
  if(pattern==0){assert(c->busRead32(c,statsA)+c->busRead32(c,statsA+4)==count&&c->busRead32(c,statsA+8)==0&&c->busRead32(c,statsA+12)==0);++perfectRuns;referenceScore[difficulty]=c->busRead32(c,scoreA);}else if(pattern==1){assert(c->busRead32(c,statsA+8)==count&&c->busRead32(c,scoreA)==0);++missRuns;}else{assert(c->busRead32(c,statsA+8)>0&&c->busRead32(c,statsA+12)>0);++mixedRuns;}
  if(sceneCount%4==0){pressSoak(c,1);assert(c->busRead32(c,modeA)==2&&c->busRead32(c,sessionA)==0);waitReady(c);assert(c->busRead32(c,scoreA)==0);pressSoak(c,8);assert(c->busRead32(c,phaseA)==2);pressSoak(c,4);assert(c->busRead32(c,modeA)==0);++exits;}else{pressSoak(c,2);assert(c->busRead32(c,modeA)==0);}
  ++sceneCount;printf("progress scenes=%u frames=%llu seconds=%.3f\n",sceneCount,(unsigned long long)framesRun,(ticks(c)-begin)/16777216.);fflush(stdout);
 }
 struct rusage usage;assert(getrusage(RUSAGE_SELF,&usage)==0);assert(ticks(c)-begin>=target&&nonzero>1000);FILE*out=fopen(argv[5],"w");assert(out);fprintf(out,"{\"profile\":\"%s\",\"requested_seconds\":%u,\"emulated_cycles\":%llu,\"emulated_seconds\":%.9f,\"playing_cycles\":%llu,\"paused_cycles\":%llu,\"menu_cycles\":%llu,\"result_cycles\":%llu,\"judgments_P_G_M_W\":[%llu,%llu,%llu,%llu],\"runFrame_calls\":%llu,\"complete_songs\":[%u,%u,%u],\"perfect_runs\":%u,\"all_miss_runs\":%u,\"mixed_runs\":%u,\"pause_cycles\":%u,\"replay_then_exit\":%u,\"startup_frames_observed_not_reference_valid\":%u,\"framebuffer_frames_checked\":%llu,\"displaced_pixels\":%llu,\"visible_head_peak\":%u,\"tail_peak\":%u,\"foreground_peak\":%u,\"refill_peak\":%u,\"host_peak_rss_kib\":%ld,\"nonzero_audio_samples\":%llu,\"reference_scores\":[%llu,%llu,%llu],\"result\":\"passed\"}\n",profile,seconds,(unsigned long long)(ticks(c)-begin),(ticks(c)-begin)/16777216.,(unsigned long long)playingCycles,(unsigned long long)pausedCycles,(unsigned long long)menuCycles,(unsigned long long)resultCycles,(unsigned long long)judgments[0],(unsigned long long)judgments[1],(unsigned long long)judgments[2],(unsigned long long)judgments[3],(unsigned long long)framesRun,completed[0],completed[1],completed[2],perfectRuns,missRuns,mixedRuns,pauseCount,exits,transientFrames,(unsigned long long)checkedFrames,(unsigned long long)displaced,peakHeads,peakTails,peakWork,peakRefill,usage.ru_maxrss,(unsigned long long)nonzero,(unsigned long long)referenceScore[0],(unsigned long long)referenceScore[1],(unsigned long long)referenceScore[2]);fclose(out);c->deinit(c);return 0;}
