#include "pcmPlayback.hpp"
#include "maxmod.h"
#include "soundbank_bin.h"
#include "imported_audio.hpp"
#include "imported_audio_bin.h"

volatile u32 audioState=PcmClock::Disabled;
volatile u32 audioSamplesConsumed=0;
volatile u32 audioFaultCode=0;

// Same mode/channel/buffer configuration as mmInitDefault, retained for replay.
// mmInitDefault allocates on each call; public mmInit reuses these buffers.
alignas(4) static u8 mixMemory[MM_MIXLEN_16KHZ];
alignas(4) EWRAM_DATA static u8 waveMemory[MM_MIXLEN_16KHZ];
alignas(4) EWRAM_DATA static u8 moduleChannels[16*MM_SIZEOF_MODCH];
alignas(4) EWRAM_DATA static u8 activeChannels[16*MM_SIZEOF_ACTCH];
alignas(4) EWRAM_DATA static u8 mixingChannels[16*MM_SIZEOF_MIXCH];

bool legacyAudioReady=false;
static void hardwareStop();
void legacyAudioInit() {
    legacyAudioReady=false;
    hardwareStop();
    memset32(moduleChannels,0,sizeof(moduleChannels)/4);
    memset32(activeChannels,0,sizeof(activeChannels)/4);
    memset32(mixingChannels,0,sizeof(mixingChannels)/4);
    memset32(mixMemory,0,sizeof(mixMemory)/4);
    mm_gba_system setup={MM_MIX_16KHZ,16,16,moduleChannels,activeChannels,mixingChannels,mixMemory,waveMemory,(mm_addr)soundbank_bin};
    mmInit(&setup);
    legacyAudioReady=true;
}
static void hardwareStop() {
    REG_TM0CNT=0;
    REG_DMA1CNT=0;REG_DMA2CNT=0;
    REG_TM1CNT=0;REG_TM2CNT=0;
    REG_SNDDSCNT=SDS_ARESET|SDS_BRESET;
    REG_FIFO_A=0;
}
void pcmStop() {
    const u16 irq=REG_IME;REG_IME=0;
    legacyAudioReady=false;hardwareStop();audioState=PcmClock::Disabled;audioSamplesConsumed=0;audioFaultCode=0;
    REG_IME=irq;
}
void pcmStart() {
    pcmStop();
    if (!imported_audio_enabled) return;
    const u16 irq=REG_IME;REG_IME=0;
    REG_SNDSTAT=SSTAT_ENABLE;
    REG_SNDDMGCNT=0;
    REG_SNDDSCNT=SDS_A100|SDS_AL|SDS_AR|SDS_ARESET|SDS_BRESET;
    REG_DMA1SAD=(u32)imported_audio_bin;
    REG_DMA1DAD=(u32)&REG_FIFO_A;
    REG_DMA1CNT=DMA_ENABLE|DMA_AT_FIFO|DMA_32|DMA_REPEAT|DMA_DST_FIXED;
    REG_TM1D=0;REG_TM2D=0;
    REG_TM2CNT=TM_ENABLE|TM_CASCADE;
    REG_TM1CNT=TM_ENABLE|TM_CASCADE;
    REG_TM0D=65536-PcmClock::PERIOD;
    audioState=PcmClock::Playing;
    REG_TM0CNT=TM_ENABLE;
    REG_IME=irq;
}
static u32 consumed() {
    u16 high,low,again;
    do { high=REG_TM2D;low=REG_TM1D;again=REG_TM2D; } while(high!=again);
    return (u32(high)<<16)|low;
}
void pcmService() {
    if (audioState!=PcmClock::Playing) return;
    if (REG_TM0CNT!=TM_ENABLE || !(REG_DMA1CNT&DMA_ENABLE) || !(REG_SNDSTAT&SSTAT_ENABLE) ||
        REG_TM1CNT!=(TM_ENABLE|TM_CASCADE) || REG_TM2CNT!=(TM_ENABLE|TM_CASCADE) ||
        (REG_SNDDSCNT&(SDS_AL|SDS_AR|SDS_ATMR1))!=(SDS_AL|SDS_AR)) {
        audioFaultCode=1;audioState=PcmClock::Fault;hardwareStop();return;
    }
    u32 count=consumed();
    if (count<audioSamplesConsumed) {audioFaultCode=2;audioState=PcmClock::Fault;hardwareStop();return;}
    audioSamplesConsumed=PcmClock::bounded(count,imported_audio_playback_samples);
    if (count>=imported_audio_playback_samples) {audioState=PcmClock::Ended;hardwareStop();}
}
u64 pcmSnapshotTick() {
    const u16 irq=REG_IME;REG_IME=0;
    pcmService();
    const u32 count=audioSamplesConsumed;
    REG_IME=irq;
    return PcmClock::tick(count);
}
