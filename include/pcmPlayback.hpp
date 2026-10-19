#ifndef PCM_PLAYBACK_HPP
#define PCM_PLAYBACK_HPP
#include "tonc.h"
#include "audioClock.hpp"
extern volatile u32 audioState;
extern volatile u32 audioSamplesConsumed;
extern volatile u32 audioFaultCode;
void pcmStart();
void pcmStop();
void pcmService();
u64 pcmSnapshotTick();
extern bool legacyAudioReady;
void legacyAudioInit();
#endif
