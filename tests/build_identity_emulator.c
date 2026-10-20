// Verify the complete profile label is actually composed, not just stored in ROM.
#include <mgba/core/core.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(int argc,char** argv){
    assert(argc==3);
    const char* text=argv[2];assert(strlen(text)<=24);
    struct mCore* c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
    color_t pixels[240*160]={0};c->setVideoBuffer(c,pixels,240);
    assert(mCoreLoadFile(c,argv[1]));c->reset(c);
    for(int f=0;f<90;++f)c->runFrame(c);
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
