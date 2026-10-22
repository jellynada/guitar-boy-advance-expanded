// Verify the complete profile label is actually composed, not just stored in ROM.
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static void log_message(struct mLogger* logger,int category,enum mLogLevel level,const char* format,va_list args){
    (void)logger;(void)category;
    if(level&(mLOG_FATAL|mLOG_ERROR|mLOG_WARN)){vfprintf(stderr,format,args);fputc('\n',stderr);}
}


static unsigned symbol(const char*path,const char*name){FILE*f=fopen(path,"r");assert(f);char line[256],n[180],t;unsigned a;while(fgets(line,sizeof line,f))if(sscanf(line,"%x %c %179s",&a,&t,n)==3&&!strcmp(n,name)){fclose(f);return a;}abort();}
static void press(struct mCore*c,unsigned k){c->setKeys(c,0);c->runFrame(c);c->setKeys(c,k);c->runFrame(c);c->setKeys(c,0);c->runFrame(c);}
static void glyphs(struct mCore*c,color_t*p,unsigned font,unsigned x,unsigned y,const char*s){for(;*s;++s,++x)for(unsigned r=0;r<8;++r){unsigned bits=c->busRead8(c,font+((unsigned)*s-32)*8+r);for(unsigned b=0;b<8;++b){unsigned rgb=p[(y*8+r)*240+x*8+b];int white=(rgb&255)>200&&((rgb>>8)&255)>200&&((rgb>>16)&255)>200;assert(white==!!(bits&(1u<<b)));}}}
int main(int argc,char** argv){
    assert(argc==3||argc==5);
    const char* text=argv[2];assert(strlen(text)<=24);
    struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);
    struct mCore* c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
    color_t pixels[240*160]={0};c->setVideoBuffer(c,pixels,240);
    assert(mCoreLoadFile(c,argv[1]));c->reset(c);
    for(int f=0;f<90;++f)c->runFrame(c);

    if(argc==5){
        unsigned font=symbol(argv[3],"sys8Glyphs"),screen=symbol(argv[3],"uiScreen");
        assert(c->busRead32(c,screen)==0);
        glyphs(c,pixels,font,10,4,"GUITAR BOY");glyphs(c,pixels,font,11,6,"ADVANCE");glyphs(c,pixels,font,11,9,"EXPANDED");
        press(c,8);assert(c->busRead32(c,screen)==1);press(c,128);press(c,1);assert(c->busRead32(c,screen)==7);
        char revision[30];assert(strlen(argv[4])==40);memcpy(revision,argv[4],29);revision[29]=0;
        glyphs(c,pixels,font,1,14,revision);
        puts("PASS: actual navigation title/main/options and visible source revision; full profile/SHA independently checked by artifact verifier");
        c->deinit(c);return 0;
    }
    unsigned ink=0;
    for(unsigned i=0;i<strlen(text);++i){
        unsigned base=0x07000000+(16+i)*8;
        unsigned a0=c->busRead16(c,base),a1=c->busRead16(c,base+2),a2=c->busRead16(c,base+4);
        assert((a0&0xFF)==28&&(a0&0x300)==0&&(a1>>14)==1);
        unsigned tile=((unsigned)text[i]-31)*4+0x201;
        assert((a2&1023)==tile);
        unsigned sx=a1&511,sy=a0&255;assert(sx<240);
        for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16&&sx+x<240;++x){
            unsigned address=0x06010000+(tile+(y/8)*2+x/8)*32+(y%8)*4+(x%8)/2;
            unsigned color=(c->busRead8(c,address)>>((x%2)*4))&15;
            if(!color)continue;
            unsigned palette=c->busRead16(c,0x05000200+(a2>>12)*32+color*2);
            // Spaces/transparent edges contribute no pass; visible ink must match.
            assert((pixels[(sy+y)*240+sx+x]&0xFFFFFF)==(mColorFrom555(palette)&0xFFFFFF));++ink;
        }
    }
    assert(ink>100);printf("PASS: complete visible profile '%s', %u matching ink pixels\n",text,ink);
    c->deinit(c);return 0;
}
