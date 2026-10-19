#ifndef PCM_PLAYBACK_HPP
#define PCM_PLAYBACK_HPP
#include "tonc.h"
#include "audioClock.hpp"
#include "noteJudgment.hpp"
extern volatile u32 audioState;
extern volatile u32 audioSamplesConsumed;
extern volatile u32 audioFaultCode;
extern volatile u32 guitarAudible,guitarGain;
extern volatile u32 audioRefillCount,audioRefillMaxCycles,audioUnderruns;
extern volatile u64 audioRefillTotalCycles;
void pcmGameplayEvent(const GameplayEvent&);
void pcmStart();
void pcmStop();
void pcmService();
u64 pcmSnapshotTick();
extern bool legacyAudioReady;
void legacyAudioInit();
#endif
