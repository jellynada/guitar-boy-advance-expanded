#include "pcmPlayback.hpp"
#include "guitarGate.hpp"
#include "maxmod.h"
#include "soundbank_bin.h"
#include "imported_audio.hpp"
#include "imported_audio_bin.h"
#include "imported_backing_bin.h"

volatile u32 audioState=PcmClock::Disabled;
volatile u32 audioSamplesConsumed=0;
volatile u32 audioFaultCode=0;
volatile u32 guitarAudible=1,guitarGain=256;
volatile u32 audioRefillCount=0,audioRefillMaxCycles=0,audioUnderruns=0;
volatile u64 audioRefillTotalCycles=0;
volatile u32 audioPauseCount=0,audioResumeCount=0,audioPausedSamples=0,audioPausedFill=0;
static u16 pausedRouting=0;
struct GuitarEventRecord {u32 sample,kind,gain,serial;u64 gameplayTick;};
EWRAM_DATA GuitarEventRecord guitarEventTrace[16];
volatile u32 guitarEventSerial=0;
static GuitarGate gate;
static u32 fillPosition=0,previousBlock=0,countEpoch=0,previousRaw=0;
// Retained original Maxmod storage; no allocations during mode changes.
alignas(4) static u8 mixMemory[MM_MIXLEN_16KHZ];
alignas(4) EWRAM_DATA static u8 waveMemory[MM_MIXLEN_16KHZ];
alignas(4) EWRAM_DATA static u8 moduleChannels[16*MM_SIZEOF_MODCH];
alignas(4) EWRAM_DATA static u8 activeChannels[16*MM_SIZEOF_ACTCH];
alignas(4) EWRAM_DATA static u8 mixingChannels[16*MM_SIZEOF_MIXCH];
bool legacyAudioReady=false;
static void hardwareStop() {
    REG_TM0CNT=0;REG_TM1CNT=0;REG_TM2CNT=0;
    irq_disable(II_TIMER1);REG_IF=IRQ_TIMER1;
    REG_DMA1CNT=0;REG_DMA2CNT=0;
    REG_SNDDSCNT=SDS_ARESET|SDS_BRESET;REG_FIFO_A=0;
}
void legacyAudioInit() {
    legacyAudioReady=false;hardwareStop();
    memset32(moduleChannels,0,sizeof(moduleChannels)/4);
    memset32(activeChannels,0,sizeof(activeChannels)/4);
    memset32(mixingChannels,0,sizeof(mixingChannels)/4);
    memset32(mixMemory,0,sizeof(mixMemory)/4);
    mm_gba_system setup={MM_MIX_16KHZ,16,16,moduleChannels,activeChannels,mixingChannels,mixMemory,waveMemory,(mm_addr)soundbank_bin};
    mmInit(&setup);legacyAudioReady=true;
}
// Timer1 reloads after16 sample requests; Timer2 counts those blocks. Software
// extends the20-bit count, serviced1024times/sec, including >64second tracks.
static u32 consumed() {
    u16 high,low,again;
    do {high=REG_TM2D;low=REG_TM1D;again=REG_TM2D;}while(high!=again);
    const u32 raw=(u32(high)<<4)|(u32(low)-65520);
    if(raw<previousRaw)countEpoch+=1u<<20;
    previousRaw=raw;return countEpoch+raw;
}
static void fault(u32 code) {
    audioFaultCode=code;audioState=PcmClock::Fault;hardwareStop();
}
// Four32-bit writes append16 samples to FIFO A. No ring, DMA cursor, decoder,
// heap or independent stream position. Both samples always use fillPosition.
static IWRAM_CODE void append16() {
    for(u32 word=0;word<4;++word) {
        u32 packed=0;
        for(u32 byte=0;byte<4;++byte,++fillPosition) {
            int value=0;
            if(fillPosition<imported_audio_playback_samples) {
                const int g=reinterpret_cast<const signed char*>(imported_audio_bin)[fillPosition];
                if(imported_audio_reactive) {
                    const int b=reinterpret_cast<const signed char*>(imported_backing_bin)[fillPosition];
                    value=gate.sample(g,b);
                } else value=g; // Mission006 fixed mixes remain supported.
            }
            packed|=u32(value&255)<<(byte*8);
        }
        REG_FIFO_A=packed;
    }
    guitarGain=gate.gain;
}
static IWRAM_CODE void refill() {
    if(audioState!=PcmClock::Playing)return;
    const u16 begin=REG_TM3D;
    const u32 count=consumed(),block=count>>4;
    if(block-previousBlock!=1) {++audioUnderruns;fault(3);return;}
    previousBlock=block;
    audioSamplesConsumed=PcmClock::bounded(count,imported_audio_playback_samples);
    if(count>=imported_audio_playback_samples) {audioState=PcmClock::Ended;hardwareStop();return;}
    append16();
    const u32 cost=u16(REG_TM3D-begin)*64u;
    ++audioRefillCount;audioRefillTotalCycles+=cost;
    if(cost>audioRefillMaxCycles)audioRefillMaxCycles=cost;
}
void pcmStop() {
    const u16 irq=REG_IME;REG_IME=0;
    legacyAudioReady=false;hardwareStop();audioState=PcmClock::Disabled;audioSamplesConsumed=0;audioFaultCode=0;
    gate.reset();guitarAudible=1;guitarGain=256;guitarEventSerial=0;
    fillPosition=previousBlock=countEpoch=previousRaw=0;
    REG_IME=irq;
}
void pcmStart() {
    pcmStop();audioRefillCount=audioRefillMaxCycles=audioUnderruns=0;audioRefillTotalCycles=0;
    audioPauseCount=audioResumeCount=audioPausedSamples=audioPausedFill=0;pausedRouting=0;
    if(!imported_audio_enabled)return;
    const u16 irq=REG_IME;REG_IME=0;
    REG_SNDSTAT=SSTAT_ENABLE;REG_SNDDMGCNT=0;
    REG_SNDDSCNT=SDS_A100|SDS_AL|SDS_AR|SDS_ARESET|SDS_BRESET;
    append16();append16(); // prime32samples:16sample IRQ deadline slack
    REG_TM1D=65520;REG_TM2D=0;
    REG_TM2CNT=TM_ENABLE|TM_CASCADE;
    REG_TM1CNT=TM_ENABLE|TM_CASCADE|TM_IRQ;
    irq_set(II_TIMER1,refill,0);REG_IF=IRQ_TIMER1;irq_enable(II_TIMER1);
    REG_TM0D=65536-PcmClock::PERIOD;audioState=PcmClock::Playing;REG_TM0CNT=TM_ENABLE;
    REG_IME=irq;
}
bool pcmPause() {
    const u16 irq=REG_IME;REG_IME=0;
    pcmService();
    if(audioState!=PcmClock::Playing){REG_IME=irq;return false;}
    // Stop ONLY the source timer. Keep FIFO contents, cascade counters, mixer
    // cursor, gain/ramp and count-extension epoch. hardwareStop resets FIFO.
    REG_TM0CNT=0;
    const u32 count=consumed();
    // A Timer1 overflow may have become pending just before IME was cleared.
    // Service that one normal refill now, then acknowledge it exactly once.
    if((count>>4)!=previousBlock)refill();
    if(audioState!=PcmClock::Playing){REG_IME=irq;return false;}
    audioSamplesConsumed=PcmClock::bounded(count,imported_audio_playback_samples);
    if(count>=imported_audio_playback_samples){audioState=PcmClock::Ended;hardwareStop();REG_IME=irq;return false;}
    irq_disable(II_TIMER1);REG_IF=IRQ_TIMER1;
    pausedRouting=REG_SNDDSCNT&~(SDS_ARESET|SDS_BRESET);
    REG_SNDDSCNT=pausedRouting&~(SDS_AL|SDS_AR);
    audioPausedSamples=audioSamplesConsumed;audioPausedFill=fillPosition;++audioPauseCount;
    audioState=PcmClock::Paused;REG_IME=irq;return true;
}
bool pcmResume() {
    const u16 irq=REG_IME;REG_IME=0;
    if(audioState!=PcmClock::Paused){REG_IME=irq;return false;}
    if(REG_TM0CNT!=0||REG_TM1CNT!=(TM_ENABLE|TM_CASCADE)||
       REG_TM2CNT!=(TM_ENABLE|TM_CASCADE)||!(REG_SNDSTAT&SSTAT_ENABLE)||
       consumed()!=audioPausedSamples||fillPosition!=audioPausedFill){fault(4);REG_IME=irq;return false;}
    // Do not reset/reprime FIFO or rewrite Timer1/2. Timer0 restarts a full
    // 1024-cycle period; only its interrupted fractional DAC interval is lost.
    // No source sample is consumed/replayed, and chart time uses this SAME count.
    REG_IF=IRQ_TIMER1;irq_enable(II_TIMER1);
    REG_SNDDSCNT=pausedRouting;audioState=PcmClock::Playing;
    REG_TM0CNT=TM_ENABLE;++audioResumeCount;REG_IME=irq;return true;
}
void pcmService() {
    if(audioState!=PcmClock::Playing)return;
    if(REG_TM0CNT!=TM_ENABLE||REG_TM1CNT!=(TM_ENABLE|TM_CASCADE|TM_IRQ)||REG_TM2CNT!=(TM_ENABLE|TM_CASCADE)||
       !(REG_IE&IRQ_TIMER1)||!(REG_SNDSTAT&SSTAT_ENABLE)||
       (REG_SNDDSCNT&(SDS_AL|SDS_AR|SDS_ATMR1))!=(SDS_AL|SDS_AR)) {fault(1);return;}
    const u32 count=consumed();
    if(count<audioSamplesConsumed) {fault(2);return;}
    audioSamplesConsumed=PcmClock::bounded(count,imported_audio_playback_samples);
    if(count>=imported_audio_playback_samples) {audioState=PcmClock::Ended;hardwareStop();}
}
u64 pcmSnapshotTick() {
    const u16 irq=REG_IME;REG_IME=0;pcmService();const u32 count=audioSamplesConsumed;REG_IME=irq;
    return PcmClock::tick(count);
}
void pcmGameplayEvent(const GameplayEvent& event) {
    if(!imported_audio_reactive)return;
    const u16 irq=REG_IME;REG_IME=0;
    gate.event(event);guitarAudible=gate.audible;
    const u32 serial=guitarEventSerial;
    guitarEventTrace[serial%16]={fillPosition,u32(event.kind),gate.gain,serial,event.gameplayTick};
    guitarEventSerial=serial+1;REG_IME=irq;
}
