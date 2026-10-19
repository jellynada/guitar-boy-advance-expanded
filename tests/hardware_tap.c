// Host-only mGBA0.10.1 observation. No GBA instructions or emulated cycles added.
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/gba/io.h>
#include <mgba/core/timing.h>
static FILE *fifoLog,*sampleLog,*pwmLog,*metaLog;
static uint32_t sampleNumber;
static int capturePcm=1;
static unsigned modeAddress,stateAddress,fillAddress,segment,graphicsMode=2,ioDepth;
static uint64_t affineWrites,lateWrites,lineWrites[160],lateLines[160];
static int initialized;
static uint32_t ram(struct GBA* gba,unsigned a){
    if((a>>24)==3)return gba->memory.iwram[(a&32767)/4];
    if((a>>24)==2)return gba->memory.wram[(a&262143)/4];
    return 0;
}
static void init(void){
    if(initialized)return;
    initialized=1;
    const char* prefix=getenv("GBA_HARDWARE_TAP");if(!prefix)return;
    if(getenv("GBA_TAP_GRAPHICS_MODE"))graphicsMode=strtoul(getenv("GBA_TAP_GRAPHICS_MODE"),0,10);
    capturePcm=getenv("GBA_TAP_NO_PCM")==NULL;
    modeAddress=strtoul(getenv("GBA_TAP_MODE_ADDR"),0,16);
    stateAddress=strtoul(getenv("GBA_TAP_STATE_ADDR"),0,16);
    fillAddress=strtoul(getenv("GBA_TAP_FILL_ADDR"),0,16);
    char path[1024];snprintf(path,sizeof(path),"%s.fifo",prefix);fifoLog=fopen(path,"wb");
    snprintf(path,sizeof(path),"%s.samples",prefix);sampleLog=fopen(path,"wb");
    snprintf(path,sizeof(path),"%s.pwm",prefix);pwmLog=fopen(path,"wb");
    snprintf(path,sizeof(path),"%s.samplemeta",prefix);metaLog=fopen(path,"wb");
    if(!fifoLog||!sampleLog||!pwmLog||!metaLog)abort();
    setvbuf(fifoLog,NULL,_IOFBF,1048576);setvbuf(sampleLog,NULL,_IOFBF,1048576);
}
#pragma pack(push,1)
struct Write {uint32_t segment,end,word;uint64_t cycle;};
struct Meta {uint32_t index;int32_t late,until,sampleIndex,lastSample;uint64_t cycle;};
struct Pwm {uint32_t segment;uint64_t cycle;int16_t left,right;};
struct Sample {uint32_t segment;int8_t value;uint64_t cycle;};
#pragma pack(pop)
uint32_t GBAAudioWriteFIFO(struct GBAAudio* audio,int address,uint32_t value){
    static uint32_t (*real)(struct GBAAudio*,int,uint32_t);
    if(!real)real=dlsym(RTLD_NEXT,"GBAAudioWriteFIFO");
    init();
    if(capturePcm&&fifoLog&&address==REG_FIFO_A_LO&&ram(audio->p,modeAddress)==2&&ram(audio->p,stateAddress)==1){
        struct Write w={segment,ram(audio->p,fillAddress),value,mTimingGlobalTime(&audio->p->timing)};
        fwrite(&w,sizeof(w),1,fifoLog);
    }
    return real(audio,address,value);
}
void GBAAudioSampleFIFO(struct GBAAudio* audio,int fifoId,int32_t cycles){
    static void (*real)(struct GBAAudio*,int,int32_t);
    if(!real)real=dlsym(RTLD_NEXT,"GBAAudioSampleFIFO");
    init();
    if(capturePcm&&sampleLog&&fifoId==0&&ram(audio->p,modeAddress)==2&&ram(audio->p,stateAddress)==1){
        struct GBAAudioFIFO* ch=&audio->chA;
        uint32_t value=ch->internalSample;
        if(!ch->internalRemaining&&ch->fifoWrite!=ch->fifoRead)value=ch->fifo[ch->fifoRead];
        struct Sample s={segment,(int8_t)value,mTimingGlobalTime(&audio->p->timing)-cycles};
        if(segment==1&&sampleNumber>=3811900&&sampleNumber<3813200){struct Meta m={sampleNumber,cycles,mTimingUntil(&audio->p->timing,&audio->sampleEvent),audio->sampleIndex,audio->lastSample,mTimingGlobalTime(&audio->p->timing)};fwrite(&m,sizeof(m),1,metaLog);}
        if(segment==1)++sampleNumber;
        fwrite(&s,sizeof(s),1,sampleLog);
    }
    real(audio,fifoId,cycles);
}
void GBAAudioSample(struct GBAAudio* audio,int32_t timestamp){
    static void (*real)(struct GBAAudio*,int32_t);
    if(!real)real=dlsym(RTLD_NEXT,"GBAAudioSample");
    init();int begin=audio->sampleIndex;int32_t old=audio->lastSample;
    real(audio,timestamp);
    if(capturePcm&&pwmLog&&ram(audio->p,modeAddress)==2&&ram(audio->p,stateAddress)==1){
        int end=audio->lastSample!=old?2<<GBARegisterSOUNDBIASGetResolution(audio->soundbias):audio->sampleIndex;
        for(int i=begin;i<end;++i){
            uint64_t now=mTimingGlobalTime(&audio->p->timing);
            int32_t difference=(uint32_t)old+i*audio->sampleInterval-(uint32_t)mTimingCurrentTime(&audio->p->timing);
            struct Pwm p={segment,now+difference,audio->currentSamples[i].left,audio->currentSamples[i].right};
            fwrite(&p,sizeof(p),1,pwmLog);
        }
    }
}
static void observe(struct GBA* gba,uint32_t address,uint32_t value){
    if(!fifoLog)return;
    if(address==REG_TM0CNT_HI&&(value&0x80)&&ram(gba,modeAddress)==2)++segment;
    if(ram(gba,modeAddress)==graphicsMode&&address==REG_BG2X_LO){
        unsigned line=gba->memory.io[REG_VCOUNT/2];
        if(line<160){++affineWrites;++lineWrites[line];if(!(gba->memory.io[REG_DISPSTAT/2]&2)){++lateWrites;++lateLines[line];}}
    }
}
void GBAIOWrite(struct GBA* gba,uint32_t address,uint16_t value){
    static void (*real)(struct GBA*,uint32_t,uint16_t);
    if(!real)real=dlsym(RTLD_NEXT,"GBAIOWrite");
    init();if(!ioDepth)observe(gba,address,value);real(gba,address,value);
}
void GBAIOWrite32(struct GBA* gba,uint32_t address,uint32_t value){
    static void (*real)(struct GBA*,uint32_t,uint32_t);
    if(!real)real=dlsym(RTLD_NEXT,"GBAIOWrite32");
    init();observe(gba,address,value);++ioDepth;real(gba,address,value);--ioDepth;
}
__attribute__((destructor)) static void finish(void){
    const char* prefix=getenv("GBA_HARDWARE_TAP");if(!prefix||!fifoLog)return;
    fclose(fifoLog);fclose(sampleLog);fclose(pwmLog);fclose(metaLog);char path[1024];snprintf(path,sizeof(path),"%s.hardware.json",prefix);FILE* out=fopen(path,"w");if(!out)abort();
    fprintf(out,"{\"affine_writes\":%llu,\"late_affine_writes\":%llu,\"late_by_line\":[",(unsigned long long)affineWrites,(unsigned long long)lateWrites);
    for(unsigned i=0;i<160;++i)fprintf(out,"%s%llu",i?",":"",(unsigned long long)lateLines[i]);
    fprintf(out,"]}\n");fclose(out);
}
