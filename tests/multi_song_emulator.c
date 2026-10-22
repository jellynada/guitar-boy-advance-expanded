#include <mgba/core/core.h>
#include <mgba/core/timing.h>
#include <mgba/core/log.h>
#include <mgba/core/blip_buf.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static void quiet(struct mLogger*l,int c,enum mLogLevel v,const char*f,va_list a){(void)l;(void)c;(void)v;(void)f;(void)a;}
static unsigned symbol(const char* path,const char*name){FILE*f=fopen(path,"r");assert(f);unsigned a;char t,n[180],line[256];while(fgets(line,sizeof line,f))if(sscanf(line,"%x %c %179s",&a,&t,n)==3&&!strcmp(n,name)){fclose(f);return a;}abort();}
static unsigned screen,mode,phase,stats,score,clockAddr,session,ready,countAddr,lanesAddr,pausedCount;
static void step(struct mCore*c,unsigned keys){c->setKeys(c,keys);c->runFrame(c);short b[4096];for(int i=0;i<2;i++)while(blip_read_samples(c->getAudioChannel(c,i),b,4096,0)>0){}}
static void press(struct mCore*c,unsigned keys){step(c,0);step(c,keys);step(c,0);}
static uint64_t r64(struct mCore*c,unsigned a){return c->busRead32(c,a)|((uint64_t)c->busRead32(c,a+4)<<32);}
static void expect(struct mCore*c,unsigned s){if(c->busRead32(c,screen)!=s)fprintf(stderr,"UI expected=%u actual=%u mode=%u ready=%u\n",s,c->busRead32(c,screen),c->busRead32(c,mode),c->busRead32(c,ready));assert(c->busRead32(c,screen)==s);}
static void menusSilent(struct mCore*c){assert(!(c->busRead16(c,0x4000102)&128));assert(!(c->busRead16(c,0x4000106)&128));assert(!(c->busRead16(c,0x400010a)&128));assert(!(c->busRead32(c,0x40000b8)&0x80000000));assert(!(c->busRead32(c,0x40000dc)&0x80000000));if(c->busRead16(c,0x4000200)&(2|16))fprintf(stderr,"MENU RESOURCE screen=%u IE=%x mode=%u\n",c->busRead32(c,screen),c->busRead16(c,0x4000200),c->busRead32(c,mode));assert(!(c->busRead16(c,0x4000200)&(2|16)));assert(!(c->busRead16(c,0x4000000)&(1024|4096)));}
static void glyph(struct mCore*c,color_t*p,unsigned font,unsigned x,unsigned y,const char*s){for(;*s;s++,x++)for(unsigned row=0;row<8;row++){unsigned bits=c->busRead8(c,font+((unsigned)*s-32)*8+row);for(unsigned col=0;col<8;col++){unsigned rgb=p[(y*8+row)*240+x*8+col];int white=(rgb&255)>200&&((rgb>>8)&255)>200&&((rgb>>16)&255)>200;assert(white==!!(bits&(1u<<col)));}}}
static void shot(const char*prefix,const char*name,color_t*p){char file[1024];snprintf(file,sizeof file,"%s.%s.ppm",prefix,name);FILE*f=fopen(file,"wb");assert(f);fprintf(f,"P6\n240 160\n255\n");for(unsigned i=0;i<38400;i++){unsigned char b[]={p[i]&255,(p[i]>>8)&255,(p[i]>>16)&255};fwrite(b,1,3,f);}fclose(f);}
static void songs(struct mCore*c){unsigned s=c->busRead32(c,screen);if(s==0){press(c,8);s=1;}if(s==1){press(c,1);s=2;}if(s==3){press(c,2);s=2;}assert(s==2);expect(c,2);menusSilent(c);}

struct Row {unsigned song,difficulty,count,samples,chart,holds,guitar,backing,source,storage;};
static void startRow(struct mCore*c,const struct Row*r,const char*sy){
 songs(c);unsigned cursor=symbol(sy,"uiCursor");
 for(unsigned n=0;c->busRead32(c,cursor)!=r->song;++n){assert(n<32);press(c,128);}
 press(c,1);expect(c,3);
 unsigned mask=c->busRead32(c,symbol(sy,"collectionCatalog")+r->song*20+16)&255;
 unsigned position=0;for(unsigned d=0;d<r->difficulty;++d)position+=!!(mask&(1u<<d));
 for(unsigned n=0;c->busRead32(c,cursor)!=position;++n){assert(n<3);press(c,128);}
 step(c,0);uint64_t transitionBegin=mTimingGlobalTime(c->timing);step(c,1);
 for(unsigned n=0;n<16&&!c->busRead32(c,ready);++n)step(c,1);
 printf("TRANSITION song=%u difficulty=%u cycles_to_ready_frame=%llu\n",r->song,r->difficulty,(unsigned long long)(mTimingGlobalTime(c->timing)-transitionBegin));
 expect(c,4);
 assert(c->busRead32(c,ready)&&c->busRead32(c,mode)==2);
 assert(c->busRead32(c,symbol(sy,"activeSongIndex"))==r->song);
 assert(c->busRead32(c,symbol(sy,"activeSongDifficulty"))==r->difficulty);
 assert(c->busRead32(c,countAddr)==r->count&&c->busRead32(c,lanesAddr)==r->difficulty+3);
 assert(c->busRead32(c,symbol(sy,"activeImportedNotes"))==r->chart);
 assert(c->busRead32(c,symbol(sy,"activeImportedSustains"))==r->holds);
 unsigned pcm=symbol(sy,"activePcm");
 assert(c->busRead32(c,pcm)==r->guitar&&c->busRead32(c,pcm+4)==r->backing);
 assert(c->busRead32(c,pcm+8)==r->source&&c->busRead32(c,pcm+12)==r->samples&&c->busRead32(c,pcm+16)==r->storage);
 assert(c->busRead32(c,score)==0&&c->busRead32(c,stats)==0&&c->busRead32(c,stats+8)==0);
 assert(r64(c,clockAddr)<16777216ULL);
}
static void waitReady(struct mCore*c){for(unsigned n=0;!c->busRead32(c,ready);++n){assert(n<16);step(c,0);}expect(c,4);assert(c->busRead32(c,mode)==2);}
static void quit(struct mCore*c){press(c,8);expect(c,5);press(c,128);press(c,128);press(c,1);expect(c,2);menusSilent(c);}
static void finish(struct mCore*c,unsigned count,unsigned limit,const char*sy){unsigned chart=c->busRead32(c,symbol(sy,"activeImportedNotes")),holds=c->busRead32(c,symbol(sy,"activeImportedSustains"));unsigned lanes=c->busRead32(c,lanesAddr),buttons[5]={32,2,1,0,0};if(lanes==4){unsigned b[]={32,16,2,1};memcpy(buttons,b,sizeof b);}if(lanes==5){unsigned b[]={32,64,16,2,1};memcpy(buttons,b,sizeof b);}uint64_t until[5]={0};unsigned next=0;
for(unsigned frame=0;frame<limit&&c->busRead32(c,screen)==4;frame++){uint64_t now=r64(c,clockAddr);unsigned keys=0;for(unsigned l=0;l<lanes;l++)if(until[l]>now)keys|=buttons[l];if(next<count){unsigned lane=c->busRead32(c,chart+next*16+8);uint64_t t=r64(c,chart+next*16);if(t>now+280896&&t<=now+561792&&(keys&buttons[lane])){keys&=~buttons[lane];until[lane]=0;}}while(next<count){uint64_t t=r64(c,chart+next*16);if(t>now+280896)break;unsigned lane=c->busRead32(c,chart+next*16+8);keys|=buttons[lane];until[lane]=t+(r64(c,holds+next*8)*16777216ULL+500000)/1000000;next++;}step(c,keys);}expect(c,6);assert(c->busRead32(c,session)==1);assert(c->busRead32(c,stats)+c->busRead32(c,stats+4)==count);assert(c->busRead32(c,stats+8)==0);assert(c->busRead32(c,stats+12)==0);assert(c->busRead32(c,score+44)==1);assert(c->busRead32(c,symbol(sy,"audioUnderruns"))==0);}

int main(int argc,char**argv){
 assert(argc==5);const char*sy=argv[2];struct Row rows[96];unsigned rowCount=0;FILE*f=fopen(argv[3],"r");assert(f);
 while(rowCount<96&&fscanf(f,"%u %u %u %u %x %x %x %x %u %u",&rows[rowCount].song,&rows[rowCount].difficulty,&rows[rowCount].count,&rows[rowCount].samples,&rows[rowCount].chart,&rows[rowCount].holds,&rows[rowCount].guitar,&rows[rowCount].backing,&rows[rowCount].source,&rows[rowCount].storage)==10)++rowCount;
 fclose(f);assert(rowCount>=2);
 struct mLogger logger={.log=quiet};mLogSetDefaultLogger(&logger);struct mCore*c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
 color_t pixels[38400];c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);for(int i=0;i<2;i++)blip_set_rates(c->getAudioChannel(c,i),c->frequency(c),32768);
 assert(mCoreLoadFile(c,argv[1]));c->reset(c);
#define S(v,n) v=symbol(sy,n)
 S(screen,"uiScreen");S(mode,"gameMode");S(phase,"importedTransport");S(stats,"displayedStats");S(score,"displayedScore");S(clockAddr,"importedNowCycles");S(session,"importedSessionState");S(ready,"importedReady");S(countAddr,"importedChartCount");S(lanesAddr,"importedLaneCount");S(pausedCount,"importedPauseCount");
 for(unsigned i=0;i<90;++i)step(c,0);expect(c,0);menusSilent(c);shot(argv[4],"title",pixels);
 step(c,8);for(unsigned i=0;i<30;++i)step(c,8);expect(c,1);menusSilent(c);step(c,0);songs(c);
 step(c,1);for(unsigned i=0;i<30;++i)step(c,1);expect(c,3);step(c,0);press(c,2);shot(argv[4],"songs",pixels);
 // Every packaged difficulty, correct ROM identities, freeze/resume and restart.
 for(unsigned r=0;r<rowCount;++r){
  const struct Row*x=&rows[r];unsigned limit=(uint64_t)x->samples*1024/280896+601;
  for(unsigned choice=0;choice<4;++choice){
   startRow(c,x,sy);
   for(unsigned i=0;i<20;++i)step(c,1);
   assert(c->busRead32(c,stats+12)==0);press(c,8);expect(c,5);
   uint64_t frozen=r64(c,clockAddr);unsigned pts=c->busRead32(c,score);
   for(unsigned i=0;i<60;++i)step(c,0);
   assert(r64(c,clockAddr)==frozen&&c->busRead32(c,score)==pts);
   press(c,8);expect(c,4);press(c,8);expect(c,5);press(c,128);press(c,1);waitReady(c);
   assert(c->busRead32(c,score)==0&&c->busRead32(c,pausedCount)==0);
   finish(c,x->count,limit,sy);
   assert(c->busRead32(c,symbol(sy,"audioSamplesConsumed"))==x->samples);
   unsigned final=c->busRead32(c,score);for(unsigned i=0;i<30;++i)step(c,0);assert(c->busRead32(c,score)==final);
   menusSilent(c);
   for(unsigned i=0;i<choice;++i)press(c,128);press(c,1);
   if(choice==0){waitReady(c);assert(c->busRead32(c,symbol(sy,"activeSongIndex"))==x->song);assert(c->busRead32(c,score)==0);quit(c);}
   else if(choice==1){expect(c,3);press(c,2);}
   else if(choice==2){expect(c,2);}
   else{expect(c,1);songs(c);}
   printf("PASS song=%u difficulty=%u full_completion results_action=%u score=%u\n",x->song,x->difficulty,choice,final);fflush(stdout);
  }
 }
 // Alternating both directions, difficulties, and pause-quit without a reboot.
 for(unsigned i=0;i<40;++i){const struct Row*x=&rows[(i%4==0||i%4==3)?0:rowCount-1];startRow(c,x,sy);quit(c);}
 // Invalid catalog index cannot launch chart/audio.
 press(c,1);expect(c,3);c->busWrite32(c,symbol(sy,"uiSong"),32);
 // Controller is independent of observer uiSong; exercise actual controller.song.
 unsigned controller=symbol(sy,"_ZN9UiScreens10controllerE");
 c->busWrite32(c,controller+8,32);press(c,1);assert(c->busRead32(c,mode)!=2);menusSilent(c);
 printf("PASS multi-song: all identities, difficulties, results actions, full completions, 40 alternating switches, held keys, invalid index; no reboot\n");
 c->deinit(c);return 0;
}
