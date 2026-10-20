#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/core/blip_buf.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned sym(const char* file,const char* name){FILE* f=fopen(file,"r");assert(f);char line[256],n[180],kind;unsigned a;while(fgets(line,sizeof line,f))if(sscanf(line,"%x %c %179s",&a,&kind,n)==3&&!strcmp(n,name)){fclose(f);return a;}assert(0);return 0;}
static void quiet(struct mLogger*l,int c,enum mLogLevel v,const char*f,va_list a){(void)l;(void)c;(void)v;(void)f;(void)a;}
static void step(struct mCore*c,unsigned keys){c->setKeys(c,keys);c->runFrame(c);short buffer[4096];for(int i=0;i<2;++i)while(blip_read_samples(c->getAudioChannel(c,i),buffer,4096,0)>0){}}
static void press(struct mCore*c,unsigned k){step(c,k);step(c,0);}
int main(int argc,char**argv){
 assert(argc==3);struct mLogger logger={.log=quiet};mLogSetDefaultLogger(&logger);
 struct mCore*c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);color_t pixels[240*160];c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);
 for(int i=0;i<2;++i)blip_set_rates(c->getAudioChannel(c,i),c->frequency(c),32768);
 assert(mCoreLoadFile(c,argv[1]));c->reset(c);unsigned mode=sym(argv[2],"gameMode"),lanes=sym(argv[2],"importedLaneCount"),count=sym(argv[2],"importedChartCount"),session=sym(argv[2],"importedSessionState");
 for(unsigned i=0;i<90;++i)step(c,0);
 press(c,128);step(c,1);assert(c->busRead32(c,mode)==4);
 for(unsigned i=0;i<10;++i){step(c,1);}assert(c->busRead32(c,mode)==4); // held confirm cannot skip screen
 step(c,0);press(c,128);press(c,2);assert(c->busRead32(c,mode)==0); // B back
 press(c,64);press(c,1);assert(c->busRead32(c,mode)==1); // Original bypasses difficulty menu
 for(unsigned i=0;i<12;++i){step(c,0);}
 press(c,12);for(unsigned i=0;i<3;++i)step(c,0);assert(c->busRead32(c,mode)==0);
 press(c,128);press(c,1);assert(c->busRead32(c,mode)==4);
 press(c,128);press(c,1);assert(c->busRead32(c,mode)==2);assert(c->busRead32(c,lanes)==5&&c->busRead32(c,count)==13);
 for(unsigned i=0;i<650;++i){step(c,0);}assert(c->busRead32(c,session)==1);
 press(c,1);assert(c->busRead32(c,mode)==2&&c->busRead32(c,lanes)==5&&c->busRead32(c,session)==0); // replay same chart
 for(unsigned i=0;i<12;++i){step(c,0);}
 press(c,8);assert(c->busRead32(c,sym(argv[2],"importedTransport"))==2);press(c,4);assert(c->busRead32(c,mode)==0);
 press(c,1);assert(c->busRead32(c,mode)==4);press(c,64);press(c,64);press(c,1);
 assert(c->busRead32(c,mode)==2&&c->busRead32(c,lanes)==3&&c->busRead32(c,count)==6);
 for(unsigned i=0;i<650;++i){step(c,0);}assert(c->busRead32(c,session)==1); // switching does not judge stale capacity
 puts("PASS: held-confirm guard, B-back, Original flow, Hard selection/replay/pause/exit, then Easy count/state reset");c->deinit(c);return 0;
}
