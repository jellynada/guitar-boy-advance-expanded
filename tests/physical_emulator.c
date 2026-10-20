// Independent GBA hardware inputs and actual receptor/map/framebuffer observations.
#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "default_difficulty.h"

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
static unsigned receptor(struct mCore* c,unsigned lane,unsigned spacing){return c->busRead16(c,0x0600F000+(13*32+3+lane*spacing)*2);}
static void glyphs(struct mCore* c,const color_t* pixels,unsigned font,unsigned x,const char* text){
    for(;*text;++text,++x)for(unsigned y=0;y<8;++y)for(unsigned bit=0;bit<8;++bit){
        unsigned bits=c->busRead8(c,font+((unsigned)*text-32)*8+y),rgb=pixels[(128+y)*240+x*8+bit];
        int white=(rgb&255)>200&&((rgb>>8)&255)>200&&((rgb>>16)&255)>200;
        assert(white==!!(bits&(1u<<bit)));
    }
}
int main(int argc,char** argv){
    assert(argc==3);struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);
    struct mCore* c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
    color_t pixels[240*160]={0};c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);
    for(int ch=0;ch<2;++ch)blip_set_rates(c->getAudioChannel(c,ch),c->frequency(c),32768);
    assert(mCoreLoadFile(c,argv[1]));c->reset(c);unsigned mode=address(argv[2],"gameMode"),font=address(argv[2],"sys8Glyphs");
    for(unsigned f=0;f<90;++f)frame(c,0);
    const unsigned cells[]={16*32+4,16*32+5,16*32+6,16*32+7,16*32+14,16*32+23};unsigned originalTiles[6];
    for(unsigned i=0;i<6;++i)originalTiles[i]=c->busRead16(c,0x0600F000+cells[i]*2);
    frame(c,128);frame(c,0);frame(c,8);for(unsigned f=0;f<4;++f)frame(c,0);selectDefaultDifficulty(c,mode);assert(c->busRead32(c,mode)==2);
    glyphs(c,pixels,font,4,"LEFT");glyphs(c,pixels,font,14,"B");glyphs(c,pixels,font,23,"A");
    unsigned inactive[4];for(unsigned l=0;l<3;++l)inactive[l]=receptor(c,l,9);
    for(unsigned mask=0;mask<8;++mask){
        unsigned keys=((mask&1)?32:0)|((mask&2)?2:0)|((mask&4)?1:0);
        for(unsigned f=0;f<3;++f)frame(c,keys);
        for(unsigned l=0;l<3;++l)assert(receptor(c,l,9)==inactive[l]+((mask&(1u<<l))?18:0));
    }
    frame(c,3);frame(c,1);frame(c,1); // Release B while keeping A physically held.
    assert(receptor(c,1,9)==inactive[1]&&receptor(c,2,9)==inactive[2]+18);
    frame(c,0);frame(c,12);frame(c,0);assert(c->busRead32(c,mode)==0);
    for(unsigned i=0;i<6;++i)assert(c->busRead16(c,0x0600F000+cells[i]*2)==originalTiles[i]);
    frame(c,64);frame(c,0);frame(c,8);for(unsigned f=0;f<4;++f)frame(c,0);assert(c->busRead32(c,mode)==1);
    for(unsigned l=0;l<4;++l)inactive[l]=receptor(c,l,6);
    const unsigned buttons[]={32,16,1,2};
    for(unsigned l=0;l<4;++l){frame(c,0);for(unsigned f=0;f<3;++f)frame(c,buttons[l]);for(unsigned k=0;k<4;++k)assert(receptor(c,k,6)==inactive[k]+(k==l?18:0));}
    puts("PASS: visible LEFT/B/A labels,8 imported receptor masks, release-B/keep-A, exact tile restoration and Original LEFT/RIGHT/A/B feedback");
    c->deinit(c);return 0;
}
