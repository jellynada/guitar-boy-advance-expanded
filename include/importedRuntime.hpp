#ifndef IMPORTED_RUNTIME_HPP
#define IMPORTED_RUNTIME_HPP
#include <cstdint>
#include "noteJudgment.hpp"

// Exact hardware cycles are engine ticks: same judgment, no BPM multiplication.
namespace ImportedTiming {
constexpr uint32_t HZ = 16777216;
constexpr uint32_t FRAME = 280896;
constexpr uint64_t PRE_ROLL_US = 2000000;
constexpr uint64_t MAX_US = 7202000000ULL;
constexpr uint64_t AHEAD = uint64_t(HZ); // one second
constexpr uint64_t BEHIND = uint64_t(HZ) / 5; // 200 ms
constexpr uint32_t MAX_FRAME = uint64_t(MAX_US + 1000000) * HZ / (1000000ULL * FRAME);
inline uint64_t frameTick(uint32_t frame) { return uint64_t(frame) * FRAME; }
inline bool toCycles(uint64_t microseconds, uint64_t& out) {
    if (microseconds > MAX_US) return false;
    out = (microseconds * HZ + 500000) / 1000000;
    return true;
}
// Relative coordinates only: clamp BEFORE multiply/cast, independent of song age.
inline int relativeZ(int64_t deltaCycles) {
    if (deltaCycles < -int64_t(BEHIND)) deltaCycles = -int64_t(BEHIND);
    if (deltaCycles > int64_t(AHEAD)) deltaCycles = int64_t(AHEAD);
    return -21000 - int(deltaCycles * 83330 * 16 / (int64_t(FRAME) * 871));
}
// The floor follows the same snapshot as notes, including stop/fault/EOF.
inline int floorZ(uint64_t tick) {
    const uint64_t maximum=frameTick(MAX_FRAME);
    if (tick>maximum) tick=maximum;
    return -40000-int((tick*83330*16/(uint64_t(FRAME)*871))%(512*256));
}
inline int laneX(uint32_t lane, unsigned lanes=3) {
    constexpr int positions[3] = {0x0E380, 0x0FC00, 0x11480};
    if(lanes==3)return lane<3?positions[lane]:0;
    // Same highway width, centers of four/five equal texture-space lanes.
    const int center=lanes==4?48+int(lane)*48:36+int(lane)*40;
    return lane<lanes?0x0FC00+(center-120)*6272/72:0;
}
}

template <uint32_t N, unsigned LANES = 3>
class ImportedRuntime {
public:
    explicit ImportedRuntime(const Note* notes) : notes_(notes), judgment_(notes, ImportedTiming::FRAME) {}
    void configure(const Note* notes,uint32_t count){notes_=notes;count_=count<=N?count:N;judgment_.configure(notes,count_);reset();}
    void reset(uint8_t held = 0) {
        judgment_.reset(held); first_ = end_ = 0; now_ = 0; previousFrame_ = 0;
    }
    void update(uint32_t frame, uint8_t held) {
        // A mode reset starts a new epoch. Regressing clocks never move backward.
        if (frame < previousFrame_) frame = previousFrame_;
        if (frame > ImportedTiming::MAX_FRAME) frame = ImportedTiming::MAX_FRAME;
        previousFrame_ = frame;
        now_ = ImportedTiming::frameTick(frame);
        updateTick(now_, held);
    }
    void updateTick(uint64_t tick, uint8_t held) {
        if (tick < now_) tick = now_;
        now_ = tick;
        judgment_.step(now_, held);
        while (first_ < count_ && now_ > notes_[first_].tick && now_ - notes_[first_].tick > ImportedTiming::BEHIND) ++first_;
        if (end_ < first_) end_ = first_;
        while (end_ < count_ && (notes_[end_].tick <= now_ || notes_[end_].tick - now_ <= ImportedTiming::AHEAD)) ++end_;
    }
    NoteJudgment<N,LANES>& judgment() { return judgment_; }
    const JudgmentStats& stats() const { return judgment_.stats(); }
    bool wasHit(uint32_t i) const {
        return i < count_ && (judgment_.state(i) == NoteState::Perfect || judgment_.state(i) == NoteState::Good);
    }
    uint32_t firstVisible() const { return first_; }
    uint32_t endVisible() const { return end_; }
    uint64_t now() const { return now_; }
private:
    const Note* notes_;
    NoteJudgment<N,LANES> judgment_;
    uint32_t count_=N;
    uint64_t now_ = 0;
    uint32_t first_ = 0, end_ = 0, previousFrame_ = 0;
};
#endif
