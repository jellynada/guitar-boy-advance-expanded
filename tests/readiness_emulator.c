// Independent GBA hardware inputs and actual receptor/map/framebuffer observations.
#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>



static void log_message(struct mLogger* l,int c,enum mLogLevel level,const char* f,va_list a){
    (void)l;(void)c;if(level&(mLOG_FATAL|mLOG_ERROR|mLOG_WARN)){vfprintf(stderr,f,a);fputc('\n',stderr);}
}
static unsigned address(const char* file,const char* name){
    FILE* f=fopen(file,"r");assert(f);char line[256],sym[180],kind;unsigned v;
    while(fgets(line,sizeof(line),f))if(sscanf(line,"%x %c %179s",&v,&kind,sym)==3&&!strcmp(sym,name)){fclose(f);return v;}
    abort();
}
static void frame(struct mCore* c,unsigned keys){
    c->setKeys(c,keys);c->runFrame(c);
    for(int ch=0;ch<2;++ch){short s[4096];while(blip_read_samples(c->getAudioChannel(c,ch),s,4096,0)>0){}}
}
static void glyphs(struct mCore* c,const color_t* pixels,unsigned font,unsigned x,const char* text){
    for(;*text;++text,++x)for(unsigned y=0;y<8;++y)for(unsigned bit=0;bit<8;++bit){
        unsigned bits=c->busRead8(c,font+((unsigned)*text-32)*8+y),rgb=pixels[(128+y)*240+x*8+bit];
        int white=(rgb&255)>200&&((rgb>>8)&255)>200&&((rgb>>16)&255)>200;
        assert(white==!!(bits&(1u<<bit)));
    }
}
static void press(struct mCore*c,unsigned keys){frame(c,keys);frame(c,0);}
int main(int argc,char**argv){
 assert(argc==3);struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);struct mCore*c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);color_t pixels[38400];c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);assert(mCoreLoadFile(c,argv[1]));c->reset(c);
 unsigned ready=address(argv[2],"importedReady"),mode=address(argv[2],"gameMode"),transport=address(argv[2],"importedTransport"),font=address(argv[2],"sys8Glyphs"),score=address(argv[2],"displayedScore");
 for(unsigned f=0;f<90;++f){frame(c,0);}assert(c->busRead32(c,ready)==0);press(c,128);
 for(unsigned epoch=0;epoch<20;++epoch){
  press(c,1);assert(c->busRead32(c,mode)==4&&c->busRead32(c,ready)==0);press(c,1);
  unsigned waited=0;while(!c->busRead32(c,ready)){assert(waited++<16);frame(c,0);}
  assert(c->busRead32(c,mode)==2&&c->busRead32(c,score)==0);frame(c,0); // compose the raster following the first committed table
  glyphs(c,pixels,font,4,"LEFT");glyphs(c,pixels,font,14,"B");glyphs(c,pixels,font,23,"A");
  press(c,8);assert(c->busRead32(c,transport)==2&&c->busRead32(c,ready)==1);press(c,8);assert(c->busRead32(c,transport)==1);
  press(c,12);assert(c->busRead32(c,mode)==0&&c->busRead32(c,ready)==0);
 }
 puts("PASS:20deterministic ready/start/label/pause/resume/short-exit epochs; no startup observation before readiness");c->deinit(c);return 0;
}
