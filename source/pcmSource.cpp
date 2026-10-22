#ifdef GBA_MULTI_SONG
#include "pcmSource.hpp"
#include "pcmPlayback.hpp"
EWRAM_DATA PcmSource activePcm{};
bool pcmSelect(const PcmSource& source) {
 if(audioState!=PcmClock::Disabled||!source.guitar||!source.backing||
    !source.sourceSamples||source.playbackSamples<source.sourceSamples||
    source.storageSamples<source.playbackSamples+16)return false;
 activePcm=source;return true;
}
#endif
