#pragma once
#include <cstdint>
struct PcmSource {
 const unsigned char* guitar;
 const unsigned char* backing;
 uint32_t sourceSamples,playbackSamples,storageSamples;
};
#ifdef GBA_MULTI_SONG
extern PcmSource activePcm;
// Called only while stopped. Never called by the sample IRQ.
bool pcmSelect(const PcmSource&);
#endif
