// Host-only mGBA0.10.1 observation. No GBA instructions or emulated cycles added.
#define _GNU_SOURCE
// Windows static-link wrappers; no changes to stock emulator or ROM.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/gba/io.h>
#include <mgba/core/timing.h>
static FILE *fifoLog,*sampleLog,*pwmLog,*metaLog;
static FILE *transportLog;
static uint64_t pausedFifoRequests;
static uint32_t sampleNumber;
static int capturePcm=1,capturePwm=1;
static unsigned modeAddress,stateAddress,fillAddress,countAddress,segment,graphicsMode=2,ioDepth;
static uint64_t affineWrites,lateWrites,lineWrites[160],lateLines[160],lastWordWrites,lateLastWords,blendWrites,lateBlendWrites;
static int32_t blankRemainingMin=0x7fffffff;
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
    capturePcm=getenv("GBA_TAP_NO_PCM")==NULL;capturePwm=getenv("GBA_TAP_NO_PWM")==NULL;
    modeAddress=strtoul(getenv("GBA_TAP_MODE_ADDR"),0,16);
    stateAddress=strtoul(getenv("GBA_TAP_STATE_ADDR"),0,16);
    fillAddress=strtoul(getenv("GBA_TAP_FILL_ADDR"),0,16);
    if(getenv("GBA_TAP_COUNT_ADDR"))countAddress=strtoul(getenv("GBA_TAP_COUNT_ADDR"),0,16);
    char path[1024];snprintf(path,sizeof(path),"%s.fifo",prefix);fifoLog=fopen(path,"wb");
    snprintf(path,sizeof(path),"%s.samples",prefix);sampleLog=fopen(path,"wb");
    snprintf(path,sizeof(path),"%s.pwm",prefix);pwmLog=fopen(path,"wb");
    snprintf(path,sizeof(path),"%s.samplemeta",prefix);metaLog=fopen(path,"wb");
    snprintf(path,sizeof(path),"%s.transport.csv",prefix);transportLog=fopen(path,"w");
    if(transportLog)fprintf(transportLog,"cycle,enabled,consumed,fill,state\n");
    if(!fifoLog||!sampleLog||!pwmLog||!metaLog)abort();
    setvbuf(fifoLog,NULL,_IOFBF,1048576);setvbuf(sampleLog,NULL,_IOFBF,1048576);
}
#pragma pack(push,1)
struct Write {uint32_t segment,end,word;uint64_t cycle;};
struct Meta {uint32_t index;int32_t late,until,sampleIndex,lastSample;uint64_t cycle;};
struct Pwm {uint32_t segment;uint64_t cycle;int16_t left,right;};
struct Sample {uint32_t segment;int8_t value;uint64_t cycle;};
#pragma pack(pop)
uint32_t __real_GBAAudioWriteFIFO(struct GBAAudio* audio,int address,uint32_t value);
uint32_t __wrap_GBAAudioWriteFIFO(struct GBAAudio* audio,int address,uint32_t value){
    static uint32_t (*real)(struct GBAAudio*,int,uint32_t);
    if(!real)real=__real_GBAAudioWriteFIFO;
    init();
    if(capturePcm&&fifoLog&&address==REG_FIFO_A_LO&&ram(audio->p,modeAddress)==2&&ram(audio->p,stateAddress)==1){
        struct Write w={segment,ram(audio->p,fillAddress),value,mTimingGlobalTime(&audio->p->timing)};
        fwrite(&w,sizeof(w),1,fifoLog);
    }
    return real(audio,address,value);
}
void __real_GBAAudioSampleFIFO(struct GBAAudio* audio,int fifoId,int32_t cycles);
void __wrap_GBAAudioSampleFIFO(struct GBAAudio* audio,int fifoId,int32_t cycles){
    static void (*real)(struct GBAAudio*,int,int32_t);
    if(!real)real=__real_GBAAudioSampleFIFO;
    init();
    if(fifoId==0&&ram(audio->p,modeAddress)==2&&ram(audio->p,stateAddress)==4)++pausedFifoRequests;
    if(capturePcm&&sampleLog&&fifoId==0&&ram(audio->p,modeAddress)==2&&ram(audio->p,stateAddress)==1){
        struct GBAAudioFIFO* ch=&audio->chA;
        uint32_t value=ch->internalSample;
        if(!ch->internalRemaining&&ch->fifoWrite!=ch->fifoRead)value=ch->fifo[ch->fifoRead];
        struct Sample s={segment,(int8_t)value,mTimingGlobalTime(&audio->p->timing)-cycles};
        if(segment==1&&sampleNumber>=3811900&&sampleNumber<3813200){struct Meta m={sampleNumber,cycles,mTimingUntil(&audio->p->timing,&audio->sampleEvent),audio->sampleIndex,audio->lastSample,mTimingGlobalTime(&audio->p->timing)};fwrite(&m,sizeof(m),1,metaLog);}
        if(segment==1)++sampleNumber;
        fwrite(&s,sizeof(s),1,sampleLog);
    }
    // Optional diagnostic correction of mGBA0.10.1's uncompensated FIFO
    // event lateness. Not enabled for normal observations or delivered ROMs.
    int32_t oldWhen=audio->sampleEvent.when;
    int correct=getenv("GBA_TAP_CORRECT_FIFO_LATENESS")&&ram(audio->p,modeAddress)==2&&ram(audio->p,stateAddress)==1;
    if(correct)audio->sampleEvent.when=(int32_t)((uint32_t)oldWhen+(uint32_t)cycles);
    real(audio,fifoId,cycles);
    if(correct)audio->sampleEvent.when=oldWhen;
}
void __real_GBAAudioSample(struct GBAAudio* audio,int32_t timestamp);
void __wrap_GBAAudioSample(struct GBAAudio* audio,int32_t timestamp){
    static void (*real)(struct GBAAudio*,int32_t);
    if(!real)real=__real_GBAAudioSample;
    init();int begin=audio->sampleIndex;int32_t old=audio->lastSample;
    real(audio,timestamp);
    if(capturePcm&&capturePwm&&pwmLog&&ram(audio->p,modeAddress)==2&&ram(audio->p,stateAddress)==1){
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
    if(address==REG_TM0CNT_HI&&ram(gba,modeAddress)==2){
        if(transportLog)fprintf(transportLog,"%llu,%u,%u,%u,%u\n",(unsigned long long)mTimingGlobalTime(&gba->timing),!!(value&0x80),ram(gba,countAddress),ram(gba,fillAddress),ram(gba,stateAddress));
        if(value&0x80){if(!getenv("GBA_TAP_SINGLE_PLAYBACK")||!segment)++segment;}
    }
    if(ram(gba,modeAddress)==graphicsMode&&(address==REG_BG2Y_LO||address==REG_BLDALPHA)){
        unsigned line=gba->memory.io[REG_VCOUNT/2];
        if(line<160){
            int hblank=gba->memory.io[REG_DISPSTAT/2]&2;
            if(address==REG_BG2Y_LO){++lastWordWrites;lateLastWords+=!hblank;}
            else {++blendWrites;lateBlendWrites+=!hblank;}
            if(hblank){int32_t remaining=mTimingUntil(&gba->timing,&gba->video.event);if(remaining<blankRemainingMin)blankRemainingMin=remaining;}
        }
    }
    if(ram(gba,modeAddress)==graphicsMode&&address==REG_BG2X_LO){
        unsigned line=gba->memory.io[REG_VCOUNT/2];
        if(line<160){++affineWrites;++lineWrites[line];if(!(gba->memory.io[REG_DISPSTAT/2]&2)){++lateWrites;++lateLines[line];}}
    }
}
void __real_GBAIOWrite(struct GBA* gba,uint32_t address,uint16_t value);
void __wrap_GBAIOWrite(struct GBA* gba,uint32_t address,uint16_t value){
    static void (*real)(struct GBA*,uint32_t,uint16_t);
    if(!real)real=__real_GBAIOWrite;
    init();if(!ioDepth)observe(gba,address,value);real(gba,address,value);
}
void __real_GBAIOWrite32(struct GBA* gba,uint32_t address,uint32_t value);
void __wrap_GBAIOWrite32(struct GBA* gba,uint32_t address,uint32_t value){
    static void (*real)(struct GBA*,uint32_t,uint32_t);
    if(!real)real=__real_GBAIOWrite32;
    init();
    if(address==REG_DMA0SAD_LO&&getenv("GBA_TEST_SHIFT_SCANLINE_DMA"))value+=16;
    if(address==REG_DMA0CNT_LO&&getenv("GBA_TEST_DISABLE_SCANLINE_DMA"))value&=~0x80000000u;
    observe(gba,address,value);++ioDepth;real(gba,address,value);--ioDepth;
}
__attribute__((destructor)) static void finish(void){
    const char* prefix=getenv("GBA_HARDWARE_TAP");if(!prefix||!fifoLog)return;
    fclose(fifoLog);fclose(sampleLog);fclose(pwmLog);fclose(metaLog);if(transportLog)fclose(transportLog);char path[1024];snprintf(path,sizeof(path),"%s.hardware.json",prefix);FILE* out=fopen(path,"w");if(!out)abort();
    fprintf(out,"{\"affine_writes\":%llu,\"late_affine_writes\":%llu,\"late_by_line\":[",(unsigned long long)affineWrites,(unsigned long long)lateWrites);
    for(unsigned i=0;i<160;++i)fprintf(out,"%s%llu",i?",":"",(unsigned long long)lateLines[i]);
    fprintf(out,"],\"last_word_writes\":%llu,\"late_last_words\":%llu,\"blend_writes\":%llu,\"late_blend_writes\":%llu,\"minimum_hblank_remaining_cycles\":%d,\"paused_fifo_requests\":%llu}\n",(unsigned long long)lastWordWrites,(unsigned long long)lateLastWords,(unsigned long long)blendWrites,(unsigned long long)lateBlendWrites,blankRemainingMin,(unsigned long long)pausedFifoRequests);fclose(out);
}
