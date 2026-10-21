#ifndef AUDIO_CLOCK_HPP
#define AUDIO_CLOCK_HPP
#include <cstdint>
namespace PcmClock {
constexpr uint32_t RATE=16384, PERIOD=1024, PRE_ROLL=32768;
// This is timer-derived FIFO output-request position, not speaker feedback.
inline uint64_t tick(uint32_t consumed) { return uint64_t(consumed ? consumed-1 : 0)*PERIOD; }
inline uint32_t bounded(uint32_t count,uint32_t end) { return count>end ? end : count; }
enum State : uint32_t { Disabled=0,Playing=1,Ended=2,Fault=3,Paused=4 };
}
#endif
