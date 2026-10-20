#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int crashed;
static void on_crash(void* context) { (void)context; crashed=1; }
static void log_message(struct mLogger* logger,int category,enum mLogLevel level,const char* format,va_list args) {
    (void)logger;(void)category;
    if(level & (mLOG_FATAL | mLOG_ERROR | mLOG_WARN)) {vfprintf(stderr,format,args);fputc('\n',stderr);}
}
static uint64_t read64(struct mCore* core, unsigned address) {
    return core->busRead32(core,address) | (uint64_t)core->busRead32(core,address+4)<<32;
}
static void frame(struct mCore* core, unsigned keys) {core->setKeys(core,keys);core->runFrame(core);assert(!crashed);}
static void screenshot(const char* filename, color_t* pixels) {
    FILE* out=fopen(filename,"wb");assert(out);fprintf(out,"P6\n240 160\n255\n");
    for(unsigned i=0;i<240*160;++i) {unsigned char rgb[]={pixels[i]&255,(pixels[i]>>8)&255,(pixels[i]>>16)&255};fwrite(rgb,1,3,out);}
    fclose(out);
}
int main(int argc,char** argv) {
    assert(argc==13);
    unsigned modeaddr=strtoul(argv[2],0,16),clockaddr=strtoul(argv[3],0,16),statsaddr=strtoul(argv[4],0,16);
    unsigned chartaddr=strtoul(argv[5],0,16),count=strtoul(argv[6],0,10),frames=strtoul(argv[7],0,10);
    unsigned erroraddr=strtoul(argv[9],0,16),eventsaddr=strtoul(argv[10],0,16),firstaddr=strtoul(argv[11],0,16),endaddr=strtoul(argv[12],0,16);
    struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);
    struct mCore* core=mCoreFind(argv[1]);assert(core&&core->init(core));mCoreInitConfig(core,NULL);
    color_t pixels[240*160]={0};core->setVideoBuffer(core,pixels,240);core->setAudioBufferSize(core,4096);
    for(int c=0;c<2;++c) blip_set_rates(core->getAudioChannel(core,c),core->frequency(core),32768);
    struct mCoreCallbacks callbacks={.coreCrashed=on_crash};core->addCoreCallbacks(core,&callbacks);
    assert(mCoreLoadFile(core,argv[1]));core->reset(core);
    for(unsigned f=0;f<90;++f)frame(core,0);
    assert(core->busRead32(core,modeaddr)==0);
    screenshot("/tmp/mission005-menu.ppm",pixels);
    for(unsigned f=0;f<2;++f){frame(core,128);} // Down
    for(unsigned f=0;f<2;++f){frame(core,0);}
    for(unsigned f=0;f<2;++f){frame(core,8);} // Start
    frame(core,0);assert(core->busRead32(core,modeaddr)==2);
    unsigned next=0;unsigned buttons[]={32,2,1};unsigned nonzero=0,visible=0;
    uint64_t previous=0;
    for(unsigned f=0;f<frames;++f) {
        uint64_t now=(uint64_t)core->busRead32(core,clockaddr)*280896;
        assert(now>=previous);previous=now;
        unsigned keys=0;
        if(!strcmp(argv[8],"perfect")) while(next<count) {
            uint64_t target=read64(core,chartaddr+next*16);
            if(target>now+280896)break;
            unsigned lane=core->busRead32(core,chartaddr+next*16+8);assert(lane<3);
            keys|=buttons[lane];++next;
        }
        // Right is ignored in Easy; cannot create WrongInput or consume a note.
        if(f%30==0)keys|=16;
        frame(core,keys);
        assert(core->busRead32(core,modeaddr)==2);
        unsigned first=core->busRead32(core,firstaddr),end=core->busRead32(core,endaddr);
        assert(first<=end&&end<=count&&end-first<=32);
        unsigned p=core->busRead32(core,statsaddr),g=core->busRead32(core,statsaddr+4),m=core->busRead32(core,statsaddr+8);
        assert(p+g+m<=count);
        for(unsigned i=0;i<32;++i) if((core->busRead16(core,0x07000000+i*8)&0x0300)!=0x0200)++visible;
        for(int c=0;c<2;++c) {short samples[4096];int n=blip_read_samples(core->getAudioChannel(core,c),samples,4096,0);for(int i=0;i<n;++i)nonzero+=samples[i]!=0;}
        if(f==120||f==450) {char name[128];snprintf(name,sizeof(name),"/tmp/mission005-imported-%u.ppm",f);screenshot(name,pixels);}
    }
    unsigned p=core->busRead32(core,statsaddr),g=core->busRead32(core,statsaddr+4),m=core->busRead32(core,statsaddr+8),w=core->busRead32(core,statsaddr+12);
    assert(p+g+m==count&&w==0&&nonzero==0&&visible>0);
    assert(core->busRead32(core,eventsaddr)==count);
    if(!strcmp(argv[8],"perfect"))assert(p==count&&g==0&&m==0);
    else assert(m==count);
    printf("PASS: imported %s, %u frames, Perfect%u Good%u Miss%u Wrong%u; visible sprite samples%u, nonzero audio%u; max measured hit error %.6f ms\n",argv[8],frames,p,g,m,w,visible,nonzero,read64(core,erroraddr)*1000.0/16777216);
    // Switch original/imported repeatedly, verifying clean fresh clock/stats,
    // then original audio and silence again (not just cold-start silence).
    for(unsigned repetition=0;repetition<3;++repetition) {
        for(unsigned f=0;f<2;++f){frame(core,12);} // Start+Select
        frame(core,0);assert(core->busRead32(core,modeaddr)==0);
        for(unsigned f=0;f<2;++f){frame(core,128);}frame(core,0);
        for(unsigned f=0;f<2;++f){frame(core,8);}frame(core,0);
        assert(core->busRead32(core,modeaddr)==1);
        assert(core->busRead32(core,statsaddr)==0&&core->busRead32(core,statsaddr+8)==0);
        unsigned sounding=0;
        for(unsigned f=0;f<120;++f) {frame(core,0);short samples[4096];int n=blip_read_samples(core->getAudioChannel(core,0),samples,4096,0);for(int i=0;i<n;++i)sounding+=samples[i]!=0;blip_clear(core->getAudioChannel(core,1));}
        assert(sounding>100);
        for(unsigned f=0;f<2;++f){frame(core,12);}frame(core,0);
        assert(core->busRead32(core,modeaddr)==0);
        for(unsigned f=0;f<2;++f){frame(core,128);}frame(core,0);
        for(unsigned f=0;f<2;++f){frame(core,8);}frame(core,0);
        assert(core->busRead32(core,modeaddr)==2);
        assert(core->busRead32(core,clockaddr)<10);
        assert(core->busRead32(core,statsaddr)==0&&core->busRead32(core,statsaddr+8)==0);
        // Drain old frontend samples before measuring newly produced silence.
        for(int c=0;c<2;++c)blip_clear(core->getAudioChannel(core,c));
        for(unsigned f=0;f<120;++f)frame(core,0);
        for(int c=0;c<2;++c)blip_clear(core->getAudioChannel(core,c));
        unsigned residual=0;
        for(unsigned f=0;f<30;++f) {frame(core,0);for(int c=0;c<2;++c){short samples[4096];int n=blip_read_samples(core->getAudioChannel(core,c),samples,4096,0);for(int i=0;i<n;++i)residual+=samples[i]!=0;}}
        assert(residual==0);
    }
    printf("PASS: three original/imported return cycles, original audio active, imported audio silent and counters/clock reset\n");
    core->deinit(core);mLogSetDefaultLogger(NULL);return 0;
}
