// Actual-key, read-only-observation pause regression for libmgba 0.10.1.
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/core/blip_buf.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void quiet(struct mLogger*l,int c,enum mLogLevel v,const char*f,va_list a){(void)l;(void)c;(void)v;(void)f;(void)a;}
static unsigned sym(const char* f,const char* n){FILE* p=fopen(f,"r");assert(p);char line[256],s[180],t;unsigned a,r=0;while(fgets(line,sizeof line,p))if(sscanf(line,"%x %c %179s",&a,&t,s)==3&&!strcmp(s,n)){r=a;break;}fclose(p);assert(r);return r;}
static uint64_t r64(struct mCore*c,unsigned a){return c->busRead32(c,a)|((uint64_t)c->busRead32(c,a+4)<<32);}
static FILE* captured,*captureCsv;
static uint64_t captureWritten;static unsigned captureState,captureCount,captureClock,captureFrame;
static void step(struct mCore*c,unsigned k){
 c->setKeys(c,k);c->runFrame(c);short b[4096];
 for(int i=0;i<2;i++){int n;while((n=blip_read_samples(c->getAudioChannel(c,i),b,4096,0))>0)if(!i&&captured){fwrite(b,2,n,captured);captureWritten+=n;}}
 if(captureCsv){unsigned state=c->busRead32(c,captureState),hw=c->busRead32(c,captureCount);
  if(state==1||state==4){unsigned raw=((unsigned)c->busRead16(c,0x4000108)<<4)|(c->busRead16(c,0x4000104)-65520);unsigned current=(hw&~((1u<<20)-1))|raw;if(current<hw)current+=1u<<20;hw=current;}
  fprintf(captureCsv,"%u,%llu,%u,%u,%llu,0,0,0,%u,0,0,0,0\n",captureFrame++,(unsigned long long)r64(c,captureClock),c->busRead32(c,captureCount),hw,(unsigned long long)captureWritten,state);
 }
}
static void shot(const char*prefix,const char*tag,color_t*p){char n[1024];snprintf(n,sizeof n,"%s.%s.ppm",prefix,tag);FILE*f=fopen(n,"wb");assert(f);fprintf(f,"P6\n240 160\n255\n");for(unsigned i=0;i<240*160;i++){unsigned char b[]={p[i]&255,(p[i]>>8)&255,(p[i]>>16)&255};fwrite(b,1,3,f);}fclose(f);}
#ifdef GBA_STACK_INSTRUMENT
#define address sym
#include "stack_probe.h"
#undef address
#endif
int main(int argc,char**argv){assert(argc==8);const char*sy=argv[2];unsigned count=atoi(argv[3]),limit=atoi(argv[4]),test=atoi(argv[5]),duration=atoi(argv[6]);
#define A(n) unsigned n=sym(sy,#n)
 A(gameMode);A(importedTransport);A(importedNowCycles);A(gameplayFrames);A(audioSamplesConsumed);A(audioState);A(audioRefillCount);A(audioPausedFill);A(guitarGain);A(guitarAudible);A(guitarEventSerial);A(displayedScore);A(displayedStats);A(imported_notes);A(imported_sustain_us);A(importedSessionState);A(importedPauseCount);A(importedResumeCount);A(audioUnderruns);A(guitarEventTrace);
#undef A
 struct mLogger logger={.log=quiet};mLogSetDefaultLogger(&logger);
 struct mCore*c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);color_t pixels[240*160];c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);for(int ch=0;ch<2;ch++)blip_set_rates(c->getAudioChannel(c,ch),c->frequency(c),32768);assert(mCoreLoadFile(c,argv[1]));c->reset(c);
 for(unsigned i=0;i<90;i++){step(c,0);}
#ifdef GBA_STACK_INSTRUMENT
 initProbe(c,sy);
#endif
 step(c,128);step(c,0);step(c,8);step(c,0);assert(c->busRead32(c,gameMode)==2);
 char file[1024];snprintf(file,sizeof file,"%s.raw",argv[7]);captured=fopen(file,"wb");assert(captured);snprintf(file,sizeof file,"%s.csv",argv[7]);captureCsv=fopen(file,"w");assert(captureCsv);fprintf(captureCsv,"frame,tick,consumed,hardware_consumed,capture_samples,perfect,good,miss,state,gate,gain,refills,underruns\n");captureState=audioState;captureCount=audioSamplesConsumed;captureClock=importedNowCycles;snprintf(file,sizeof file,"%s.events.csv",argv[7]);FILE* events=fopen(file,"w");assert(events);fprintf(events,"serial,sample,kind,gain,gameplay_tick\n");unsigned event=0;
 uint64_t until[3]={0};unsigned next=0,buttons[]={32,2,1},pauses=0,resumes=0,cycles=test==19?0:test==12?8:1;int exiting=test>=13&&test<=17;unsigned pauseAt=test==0?8:test==1?100:test==2?220:test==3?420:test==18?limit-90:180;uint64_t first=r64(c,imported_notes);if(test==1)pauseAt=first/280896-3;if(test==12)pauseAt=first/280896+120;if(test==18)pauseAt=r64(c,imported_notes+(count-1)*16)/280896;
 unsigned long frozenChecks=0;unsigned postSnapshotFrame=~0u;
 for(unsigned frame=0;frame<limit;frame++){
  uint64_t now=r64(c,importedNowCycles);unsigned keys=0;
  for(unsigned l=0;l<3;l++)if(until[l]>now)keys|=buttons[l];
  if(next<count){unsigned l=c->busRead32(c,imported_notes+next*16+8);uint64_t t=r64(c,imported_notes+next*16);if(t>now+280896&&t<=now+561792&&(keys&buttons[l])){keys&=~buttons[l];until[l]=0;}}
  while(next<count){uint64_t t=r64(c,imported_notes+next*16);if(t>now+280896)break;unsigned l=c->busRead32(c,imported_notes+next*16+8);assert(l<3);if(test!=4){keys|=buttons[l];until[l]=t+(r64(c,imported_sustain_us+next*8)*16777216ULL+500000)/1000000;}next++;}
  int trigger=frame>=pauseAt&&pauses<cycles&&c->busRead32(c,importedTransport)==1;
  if(test==4)trigger=trigger&&!c->busRead32(c,guitarAudible)&&!c->busRead32(c,guitarGain);
  if(test==20){assert(getenv("GBA_PAUSE_PLAYBACK_SAMPLES"));trigger=trigger&&c->busRead32(c,audioSamplesConsumed)>=strtoul(getenv("GBA_PAUSE_PLAYBACK_SAMPLES"),0,10)-4096;}
  if(test==2||test==3){unsigned l=test==2?1:2;trigger=trigger&&until[l]>now+561792;}
  if(test==8)trigger=trigger&&(until[0]>now+561792||until[1]>now+561792||until[2]>now+561792);
  if(frame==postSnapshotFrame)shot(argv[7],"two-seconds-later",pixels);
  if(trigger){
   shot(argv[7],"before",pixels);
   if(test==13){step(c,12);assert(c->busRead32(c,gameMode)==0);pauses++;break;}
   if(test==15){step(c,4);step(c,0);step(c,8);assert(c->busRead32(c,gameMode)==0);pauses++;break;}
   step(c,keys|8);step(c,(test==11?keys|8:keys));assert(c->busRead32(c,importedTransport)==2);pauses++;
   assert(c->busRead32(c,audioState)==(getenv("GBA_PAUSE_SILENT")?0:4));assert(!(c->busRead16(c,0x04000102)&128));
   if(test==14||test==16){step(c,test==14?4:12);assert(c->busRead32(c,gameMode)==0);break;}
   shot(argv[7],"paused",pixels);
   unsigned addresses[]={gameplayFrames,audioSamplesConsumed,audioRefillCount,audioPausedFill,guitarGain,guitarAudible,guitarEventSerial,displayedScore,displayedScore+4,displayedScore+8,displayedStats,displayedStats+4,displayedStats+8,displayedStats+12,importedNowCycles,importedNowCycles+4};unsigned frozen[sizeof addresses/sizeof *addresses];for(unsigned j=0;j<sizeof addresses/sizeof *addresses;j++)frozen[j]=c->busRead32(c,addresses[j]);
   step(c,keys|(test==11?8:0));color_t image[240*160];memcpy(image,pixels,sizeof image);
   for(unsigned p=0;p<duration;p++){unsigned held=test==5?2:test==6?1:test==7?3:test==8?0:test==9?32:keys;step(c,held|(test==11?8:0));assert(c->busRead32(c,importedTransport)==2);for(unsigned j=0;j<sizeof addresses/sizeof *addresses;j++)assert(c->busRead32(c,addresses[j])==frozen[j]);assert(!memcmp(image,pixels,sizeof image));assert(!(c->busRead16(c,0x04000102)&128));frozenChecks++;}
   if(test==17){step(c,4);assert(c->busRead32(c,gameMode)==0);break;}
   fprintf(stderr,"before timers %x %x %x consumed %u frozen %u fill %u\n",c->busRead16(c,0x4000102),c->busRead16(c,0x4000106),c->busRead16(c,0x400010a),c->busRead32(c,audioSamplesConsumed),c->busRead32(c,sym(sy,"audioPausedSamples")),c->busRead32(c,audioPausedFill));unsigned resumeKeys=test==5?2:test==6?1:test==7?3:test==8?0:test==9?32:keys;step(c,resumeKeys);step(c,resumeKeys|8);step(c,resumeKeys|8);fprintf(stderr,"resume phase=%u audio=%u mode=%u fault=%u\n",c->busRead32(c,importedTransport),c->busRead32(c,audioState),c->busRead32(c,gameMode),c->busRead32(c,sym(sy,"audioFaultCode")));assert(c->busRead32(c,importedTransport)==1);assert(c->busRead32(c,audioState)==(getenv("GBA_PAUSE_SILENT")?0:1));resumes++;step(c,keys);shot(argv[7],"resumed",pixels);pauseAt=frame+10;postSnapshotFrame=frame+120;
  }else step(c,keys);
  unsigned serial=c->busRead32(c,guitarEventSerial);assert(serial-event<=16);while(event<serial){unsigned a=guitarEventTrace+(event%16)*24;assert(c->busRead32(c,a+12)==event);fprintf(events,"%u,%u,%u,%u,%llu\n",event,c->busRead32(c,a),c->busRead32(c,a+4),c->busRead32(c,a+8),(unsigned long long)r64(c,a+16));event++;}
  if(c->busRead32(c,importedSessionState)!=0)break;
 }
 assert(pauses==cycles);if(!exiting){assert(resumes==cycles);assert(c->busRead32(c,audioUnderruns)==0);assert(c->busRead32(c,importedSessionState)==1);fprintf(stderr,"result score=%u P=%u G=%u M=%u W=%u holds=%u released=%u bonus=%u\n",c->busRead32(c,displayedScore),c->busRead32(c,displayedStats),c->busRead32(c,displayedStats+4),c->busRead32(c,displayedStats+8),c->busRead32(c,displayedStats+12),c->busRead32(c,displayedScore+60),c->busRead32(c,displayedScore+64),c->busRead32(c,displayedScore+56));if(test!=4){assert(c->busRead32(c,displayedStats)+c->busRead32(c,displayedStats+4)==count);assert(c->busRead32(c,displayedStats+8)==0);}shot(argv[7],"end",pixels);}
 printf("PASS case=%u pauses=%u resumes=%u frozen_checks=%lu score=%u heads=%u\n",test,pauses,resumes,frozenChecks,c->busRead32(c,displayedScore),next);assert(c->busRead32(c,importedPauseCount)==(exiting?c->busRead32(c,importedPauseCount):pauses));if(!exiting)assert(c->busRead32(c,importedResumeCount)==resumes);fclose(captured);fclose(captureCsv);fclose(events);
#ifdef GBA_STACK_INSTRUMENT
 endProbe(c);
#endif
 c->deinit(c);return 0;
}
