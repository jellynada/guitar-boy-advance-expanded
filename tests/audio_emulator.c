#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
int main(int argc,char** argv){
    assert(argc==7);const char* syms=argv[2];unsigned count=strtoul(argv[3],0,10),frames=strtoul(argv[4],0,10);const char* mode=argv[5];int isFault=!strncmp(mode,"fault",5);
    unsigned modeaddr=address(syms,"gameMode"),clockaddr=address(syms,"importedNowCycles"),statsaddr=address(syms,"displayedStats"),chartaddr=address(syms,"imported_notes");
    unsigned stateaddr=address(syms,"audioState"),consaddr=address(syms,"audioSamplesConsumed"),maxaddr=address(syms,"importedFrameWorkMaxCycles"),totaladdr=address(syms,"importedFrameWorkTotalCycles"),workcount=address(syms,"importedFrameWorkCount");
    struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);
    struct mCore* c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
    color_t pixels[240*160]={0};c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);
    for(int ch=0;ch<2;++ch)blip_set_rates(c->getAudioChannel(c,ch),c->frequency(c),32768);
    struct mCoreCallbacks cb={.coreCrashed=crash};c->addCoreCallbacks(c,&cb);assert(mCoreLoadFile(c,argv[1]));c->reset(c);
    for(unsigned i=0;i<90;++i){frame(c,0);drain(c);}assert(c->busRead32(c,modeaddr)==0);
    for(unsigned i=0;i<2;++i){frame(c,128);drain(c);}frame(c,0);drain(c);
    char filename[1024];snprintf(filename,sizeof(filename),"%s.raw",argv[6]);FILE* audio=fopen(filename,"wb");assert(audio);
    snprintf(filename,sizeof(filename),"%s.csv",argv[6]);FILE* csv=fopen(filename,"w");assert(csv);fprintf(csv,"frame,tick,consumed,hardware_consumed,capture_samples,perfect,good,miss,state\n");
    unsigned firstaddr=address(syms,"importedFirstVisible"),endaddr=address(syms,"importedEndVisible");
    int lineSeen[5]={0};unsigned refIds[5]={0,1,2,count/2,count-1};
    uint64_t written=0,previous=0;unsigned next=0,nonzero=0,lastJudged=0;uint64_t frozen=0;unsigned frozenJudged=0;unsigned buttons[]={32,1,2};
    for(unsigned f=0;f<frames;++f){
        unsigned keys=f<2?8:0;
        uint64_t now=read64(c,clockaddr);
        if(!strcmp(mode,"perfect")&&f>2)while(next<count){uint64_t target=read64(c,chartaddr+next*16);if(target>now+280896)break;unsigned lane=c->busRead32(c,chartaddr+next*16+8);assert(lane<3);keys|=buttons[lane];++next;}
        if(isFault&&f==400){
            if(!strcmp(mode,"fault_dma"))c->busWrite32(c,0x040000c4,0);
            else if(!strcmp(mode,"fault_sound"))c->busWrite16(c,0x04000084,0);
            else c->busWrite16(c,0x04000102,0);
        }
        if(isFault&&f>405&&f%2)keys=32|1|2; // inputs cannot judge after an audio fault
        frame(c,keys);
        if(f>4)assert(c->busRead32(c,modeaddr)==2);
        short left[4096],right[4096];int n=blip_read_samples(c->getAudioChannel(c,0),left,4096,0),r=blip_read_samples(c->getAudioChannel(c,1),right,4096,0);assert(n==r);
        for(int i=0;i<n;++i){assert(left[i]==right[i]);nonzero+=left[i]!=0;}
        fwrite(left,2,n,audio);written+=n;
        uint64_t tick=read64(c,clockaddr);assert(tick>=previous);previous=tick;
        unsigned p=c->busRead32(c,statsaddr),g=c->busRead32(c,statsaddr+4),m=c->busRead32(c,statsaddr+8),state=c->busRead32(c,stateaddr);
        assert(p+g+m<=count);
        unsigned hw=c->busRead16(c,0x04000104)|(unsigned)c->busRead16(c,0x04000108)<<16;
        fprintf(csv,"%u,%llu,%u,%u,%llu,%u,%u,%u,%u\n",f,(unsigned long long)tick,c->busRead32(c,consaddr),hw,(unsigned long long)written,p,g,m,state);
        for(unsigned ref=0;ref<5;++ref) if(!lineSeen[ref]) {
            unsigned index=refIds[ref];if(index>=count){lineSeen[ref]=1;continue;}
            unsigned first=c->busRead32(c,firstaddr),end=c->busRead32(c,endaddr);
            uint64_t target=read64(c,chartaddr+index*16);
            if(index>=first&&index<end&&tick+5*280896>=target) {
                unsigned slot=index-first;
                for(unsigned obj=0;obj<32;++obj){
                    unsigned a0=c->busRead16(c,0x07000000+obj*8),a1=c->busRead16(c,0x07000002+obj*8);
                    if((a0&0x300)!=0x300||((a1>>9)&31)!=slot)continue;
                    int x=a1&511,y=a0&255;if(x>=256)x-=512;if(y>=160)y-=256;x+=64;y+=64;
                    if(y>=116){
                        uint64_t distance=tick>target?tick-target:target-tick;
                        unsigned lane=c->busRead32(c,chartaddr+index*16+8);
                        assert(distance<=280896);assert(abs(x-(48+72*(int)lane))<=9);assert(y<=124);
                        lineSeen[ref]=1;
                        if(ref==0){char imageName[1024];snprintf(imageName,sizeof(imageName),"%s.ppm",argv[6]);FILE* image=fopen(imageName,"wb");assert(image);fprintf(image,"P6\n240 160\n255\n");for(unsigned pixel=0;pixel<240*160;++pixel){unsigned char rgb[]={pixels[pixel]&255,(pixels[pixel]>>8)&255,(pixels[pixel]>>16)&255};fwrite(rgb,1,3,image);}fclose(image);}
                        printf("LINE index%u expected_tick%llu displayed_tick%llu error_ms%.6f center_x%d center_y%d\n",index,(unsigned long long)target,(unsigned long long)tick,(tick>target?tick-target:target-tick)*1000.0/16777216,x,y);}
                }
            }
        }
        if(p+g+m>lastJudged){unsigned index=p+g+m-1;if(index==0||index==count/2||index==count-1){uint64_t target=read64(c,chartaddr+index*16);printf("REFERENCE index%u expected_tick%llu actual_tick%llu abs_error_ms%.6f\n",index,(unsigned long long)target,(unsigned long long)tick,(tick>target?tick-target:target-tick)*1000.0/16777216);}lastJudged=p+g+m;}
        if(isFault&&f==405){frozen=tick;frozenJudged=p+g+m;}
        if(isFault&&f>405){assert(state==3);assert(tick==frozen);assert(p+g+m==frozenJudged);assert(c->busRead32(c,statsaddr+12)==0);}
    }
    fclose(audio);fclose(csv);
    if(!strcmp(mode,"perfect")||!strcmp(mode,"miss")||!strcmp(mode,"silent"))for(unsigned r=0;r<5;++r)assert(lineSeen[r]);
    unsigned p=c->busRead32(c,statsaddr),g=c->busRead32(c,statsaddr+4),m=c->busRead32(c,statsaddr+8),w=c->busRead32(c,statsaddr+12),state=c->busRead32(c,stateaddr);
    if(!strcmp(mode,"perfect"))assert(p==count&&g==0&&m==0&&w==0);
    if(!strcmp(mode,"miss"))assert(m==count&&p==0&&g==0&&w==0);
    if(isFault)assert(state==3&&p+g+m<count);
    else if(!strcmp(mode,"silent"))assert(state==0&&nonzero==0);
    else assert(state==2&&nonzero>1000);
    printf("PASS: %s frames%u notes%u Perfect%u Good%u Miss%u Wrong%u nonzero_samples%u audio_state%u; foreground max%u avg%.1f CPUcycles/frame\n",mode,frames,count,p,g,m,w,nonzero,state,c->busRead32(c,maxaddr),read64(c,totaladdr)/(double)c->busRead32(c,workcount));
    // Rapid return/replay: exact counts start at0, timer position starts near0.
    for(unsigned repeat=0;repeat<4;++repeat){
        for(unsigned i=0;i<2;++i){frame(c,12);}frame(c,0);assert(c->busRead32(c,modeaddr)==0);
        for(unsigned i=0;i<2;++i){frame(c,128);}frame(c,0); // Original
        for(unsigned i=0;i<2;++i){frame(c,8);}frame(c,0);assert(c->busRead32(c,modeaddr)==1);
        unsigned sounding=0;for(unsigned i=0;i<90;++i){frame(c,0);short samples[4096];int n=blip_read_samples(c->getAudioChannel(c,0),samples,4096,0);for(int j=0;j<n;++j)sounding+=samples[j]!=0;blip_clear(c->getAudioChannel(c,1));}assert(sounding>100);
        for(unsigned i=0;i<2;++i){frame(c,12);}frame(c,0);
        for(unsigned i=0;i<2;++i){frame(c,128);}frame(c,0);
        for(unsigned i=0;i<2;++i){frame(c,8);}frame(c,0);assert(c->busRead32(c,modeaddr)==2);
        assert(c->busRead32(c,statsaddr)==0&&c->busRead32(c,statsaddr+8)==0);
        assert(c->busRead32(c,consaddr)<1500);drain(c);
    }
    printf("PASS:4rapid original/imported replay cycles, original sound, reset counters/position, no crash\n");
    c->deinit(c);mLogSetDefaultLogger(NULL);return 0;
}
