#ifndef IMPORTED_COMPLETION_HPP
#define IMPORTED_COMPLETION_HPP
#include <cstdint>
#include "audioClock.hpp"
namespace ImportedCompletion {
enum State : uint32_t { Playing=0,Complete=1,AudioError=2,Inconsistent=3 };
constexpr uint64_t LATE=16777216ULL*85000/1000000;
constexpr uint64_t FRAME=280896,PRE_ROLL=33554432;
inline uint64_t silentEnd(uint64_t lastTick,bool nonempty) {
    const uint64_t padding=LATE+FRAME;
    return !nonempty?PRE_ROLL:lastTick>UINT64_MAX-padding?UINT64_MAX:lastTick+padding;
}
inline State poll(bool enabled,uint32_t audio,uint64_t now,uint64_t silentDeadline,bool resolvedAndCoherent,uint64_t finalAudioTick=0) {
    if(audio==PcmClock::Fault||(enabled&&audio==PcmClock::Disabled))return AudioError;
    // An ISR can end playback after the foreground took its snapshot.
    // Let the next normal update catch up instead of freezing a stale clock.
    if(enabled&&audio==PcmClock::Ended&&now<finalAudioTick)return Playing;
    const bool ended=enabled?audio==PcmClock::Ended:now>=silentDeadline;
    return ended?(resolvedAndCoherent?Complete:Inconsistent):Playing;
}
}
#endif
