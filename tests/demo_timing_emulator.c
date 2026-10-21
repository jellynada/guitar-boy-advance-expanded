#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Called only at a known fresh custom-song menu entry, never on a song clock.
static void selectDefaultDifficulty(struct mCore* c,unsigned mode){
    if(c->busRead32(c,mode)!=4)return;
    c->setKeys(c,0);c->runFrame(c);unsigned choice=getenv("GBA_DIFFICULTY")?atoi(getenv("GBA_DIFFICULTY")):0;for(unsigned i=0;i<choice;i++){c->setKeys(c,128);c->runFrame(c);c->setKeys(c,0);c->runFrame(c);}c->setKeys(c,1);c->runFrame(c);c->setKeys(c,0);c->runFrame(c);
}


static int crashed;
static void crash(void* context){(void)context;crashed=1;}
static void log_message(struct mLogger* logger,int category,enum mLogLevel level,const char* format,va_list args){
    (void)logger;(void)category;if(level&(mLOG_FATAL|mLOG_ERROR|mLOG_WARN)){vfprintf(stderr,format,args);fputc('\n',stderr);}
}
static unsigned address(const char* filename,const char* name){
    FILE* in=fopen(filename,"r");assert(in);char line[256],symbol[180],kind;unsigned value=0,result=0;
    while(fgets(line,sizeof(line),in))if(sscanf(line,"%x %c %179s",&value,&kind,symbol)==3&&!strcmp(symbol,name)){result=value;break;}
    fclose(in);assert(result);return result;
}
static uint64_t read64(struct mCore* c,unsigned a){return c->busRead32(c,a)|((uint64_t)c->busRead32(c,a+4)<<32);}
static void frame(struct mCore* c,unsigned keys){c->setKeys(c,keys);c->runFrame(c);assert(!crashed);}
static void drain(struct mCore* c){for(int ch=0;ch<2;++ch){short v[4096];while(blip_read_samples(c->getAudioChannel(c,ch),v,4096,0)>0){}}}
static void screenshot(const char* prefix,const char* suffix,const color_t* pixels){
    char name[1024];snprintf(name,sizeof(name),"%s.%s.ppm",prefix,suffix);FILE* out=fopen(name,"wb");assert(out);fprintf(out,"P6\n240 160\n255\n");
    for(unsigned i=0;i<240*160;++i){unsigned char rgb[]={pixels[i]&255,(pixels[i]>>8)&255,(pixels[i]>>16)&255};fwrite(rgb,1,3,out);}fclose(out);
}

static unsigned optional_address(const char* filename,const char* name){
    FILE* in=fopen(filename,"r");assert(in);char line[256],symbol[180],kind;unsigned value=0;
    while(fgets(line,sizeof(line),in))if(sscanf(line,"%x %c %179s",&value,&kind,symbol)==3&&!strcmp(symbol,name)){fclose(in);return value;}
    fclose(in);return 0;
}
// Only count highway-colored pixels where the perspective texture predicts a
// different color. This detects displaced floor outside its correct geometry;
// it is not a general screenshot similarity or arbitrary black-region test.
static unsigned defects(struct mCore* c,const color_t* pixels,unsigned table,unsigned* floorPixels){
    unsigned fill=c->busRead8(c,0x06008000+6*64+1);
    color_t fillColor=mColorMix5Bit(1,0,15,mColorFrom555(c->busRead16(c,0x05000000+fill*2)))&0xFFFFFF;
    unsigned bad=0;
    for(unsigned y=60;y<152;++y){
        int pa=(int16_t)c->busRead16(c,table+y*16),pc=(int16_t)c->busRead16(c,table+y*16+4);
        int dx=(int32_t)c->busRead32(c,table+y*16+8),dy=(int32_t)c->busRead32(c,table+y*16+12);
        for(unsigned x=0;x<240;++x){
            if((pixels[y*240+x]&0xFFFFFF)!=fillColor)continue;
            ++*floorPixels;
            unsigned tx=((dx+pa*(int)x)>>8)&511,ty=((dy+pc*(int)x)>>8)&511;
            unsigned tile=c->busRead8(c,0x0600C000+(ty/8)*64+tx/8);
            unsigned color=c->busRead8(c,0x06008000+tile*64+(ty%8)*8+tx%8);
            color_t expected=mColorMix5Bit(1,0,15,mColorFrom555(c->busRead16(c,0x05000000+color*2)))&0xFFFFFF;
            bad+=expected!=fillColor;
        }
    }
    return bad;
}
int main(int argc,char** argv){
    assert(argc==8);const char* syms=argv[2];unsigned count=strtoul(argv[3],0,10),frames=strtoul(argv[4],0,10);int original=!strcmp(argv[5],"original"),quiet=!strcmp(argv[5],"quiet"),oracle=atoi(argv[7]);
    unsigned mode=address(syms,"gameMode"),clock=address(syms,"importedNowCycles"),chart=address(syms,"imported_notes"),lengths=address(syms,"imported_sustain_us");
    unsigned maxWork=address(syms,"importedFrameWorkMaxCycles"),totalWork=address(syms,"importedFrameWorkTotalCycles"),workCount=address(syms,"importedFrameWorkCount");
    unsigned tail=address(syms,"sustainTailSprites"),underruns=address(syms,"audioUnderruns"),refillMax=address(syms,"audioRefillMaxCycles"),refillCount=address(syms,"audioRefillCount"),refillTotal=address(syms,"audioRefillTotalCycles");
    unsigned deadline=optional_address(syms,"scanlineDeadlineMisses"),latest=optional_address(syms,"scanlineVblankLatestLine"),armCost=optional_address(syms,"scanlineVblankMaxCycles");
    unsigned table=address(syms,"m7_bgaffs"),activeTable=optional_address(syms,"scanlineActiveData");
    struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);struct mCore* c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
    color_t pixels[240*160]={0};c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);
    for(int ch=0;ch<2;++ch)blip_set_rates(c->getAudioChannel(c,ch),c->frequency(c),32768);
    struct mCoreCallbacks cb={.coreCrashed=crash};c->addCoreCallbacks(c,&cb);assert(mCoreLoadFile(c,argv[1]));c->reset(c);
    for(unsigned f=0;f<90;++f){frame(c,0);drain(c);}
    if(!original){frame(c,0);}
    unsigned next=0,buttons[5]={32,2,1,0,0},lanes=3;uint64_t heldUntil[5]={0};unsigned checked=0,badFrames=0,worst=0,peakTails=0,totalFloor=0;uint64_t totalBad=0;
    char name[1024];snprintf(name,sizeof(name),"%s.frames.csv",argv[6]);FILE* csv=fopen(name,"w");assert(csv);fprintf(csv,"frame,tick,tails,displaced_floor_pixels\n");
    for(unsigned f=0;f<frames;++f){
        unsigned keys=f<2?8:0;uint64_t now=read64(c,clock);
        if(!original&&!quiet&&f>2){
            for(unsigned l=0;l<lanes;++l)if(heldUntil[l]>now)keys|=buttons[l];
            if(next<count){unsigned l=c->busRead32(c,chart+next*16+8);uint64_t target=read64(c,chart+next*16);if(target>now+280896&&target<=now+2*280896&&(keys&buttons[l])){keys&=~buttons[l];heldUntil[l]=0;}}
            while(next<count){uint64_t target=read64(c,chart+next*16);if(target>now+280896)break;unsigned l=c->busRead32(c,chart+next*16+8);assert(l<lanes);keys|=buttons[l];heldUntil[l]=target+(read64(c,lengths+next*8)*16777216ULL+500000)/1000000;++next;}
        }
        frame(c,keys);if(f==2){selectDefaultDifficulty(c,mode);chart=c->busRead32(c,address(syms,"activeImportedNotes"));lengths=c->busRead32(c,address(syms,"activeImportedSustains"));lanes=c->busRead32(c,address(syms,"importedLaneCount"));if(lanes==4){unsigned b[]={32,16,2,1};memcpy(buttons,b,sizeof b);}if(lanes==5){unsigned b[]={32,64,16,2,1};memcpy(buttons,b,sizeof b);}}drain(c);if(f>4)assert(c->busRead32(c,mode)==(original?1:2));
        if(!original&&activeTable&&f>30&&(c->busRead16(c,0x04000000)&1024)&&!getenv("GBA_TEST_DISABLE_SCANLINE_DMA")){
            assert(c->busRead32(c,0x040000b8)&0x80000000u);assert(c->busRead32(c,0x040000dc)&0x80000000u);
        }
        unsigned tails=c->busRead32(c,tail);if(tails>peakTails)peakTails=tails;unsigned bad=0;
        if(!original&&oracle&&f>30&&(c->busRead16(c,0x04000000)&1024)){
            unsigned current=activeTable?c->busRead32(c,activeTable):0;if(!current)current=table;
            bad=defects(c,pixels,current,&totalFloor);++checked;badFrames+=bad!=0;totalBad+=bad;if(bad>worst)worst=bad;
        }
        fprintf(csv,"%u,%llu,%u,%u\n",f,(unsigned long long)read64(c,clock),tails,bad);
        if((f==180)||(f>=420&&f<480)||(f>=900&&f<960)||(f>=1500&&f<1560)||(f>=4800&&f<4860)||(f>=9000&&f<9060)||(f>=15000&&f<15060)||(f>=15800&&f<15860)){
            char suffix[64];snprintf(suffix,sizeof(suffix),"frame-%05u",f);screenshot(argv[6],suffix,pixels);
        }
    }
    fclose(csv);unsigned wc=c->busRead32(c,workCount),rc=c->busRead32(c,refillCount);
    snprintf(name,sizeof(name),"%s.timing.json",argv[6]);FILE* out=fopen(name,"w");assert(out);
    fprintf(out,"{\"frames\":%u,\"frames_checked\":%u,\"defect_frames\":%u,\"worst_displaced_pixels\":%u,\"total_displaced_pixels\":%llu,\"floor_pixels\":%u,\"peak_tails\":%u,\"foreground_max\":%u,\"foreground_mean\":%.3f,\"refill_max\":%u,\"refill_mean\":%.3f,\"underruns\":%u}\n",frames,checked,badFrames,worst,(unsigned long long)totalBad,totalFloor,peakTails,c->busRead32(c,maxWork),wc?read64(c,totalWork)/(double)wc:0,c->busRead32(c,refillMax),rc?read64(c,refillTotal)/(double)rc:0,c->busRead32(c,underruns));fclose(out);
    if(deadline){printf("DMA rearm: missed%u latest_VCOUNT%u maximum%u CPUcycles\n",c->busRead32(c,deadline),c->busRead32(c,latest),c->busRead32(c,armCost));assert(c->busRead32(c,deadline)==0);}
    assert(c->busRead32(c,underruns)==0);if(getenv("GBA_REQUIRE_CLEAN_HIGHWAY")){assert(checked>100&&totalFloor>100000&&badFrames==0);}
    printf("PASS: observation completed; checked%u defect_frames%u worst_pixels%u tails%u\n",checked,badFrames,worst,peakTails);c->deinit(c);return 0;
}
