#ifndef NOTE_JUDGMENT_HPP
#define NOTE_JUDGMENT_HPP

#include <array>
#include <cstdint>
#include "note.h"

enum class NoteState : uint8_t { Pending, Perfect, Good, Missed };
enum class GameplayEventKind : uint8_t { PerfectHit, GoodHit, Miss, WrongInput };

struct GameplayEvent {
    GameplayEventKind kind;
    uint32_t noteIndex; // NO_NOTE for WrongInput.
    uint8_t laneMask;   // Chart lanes, not hardware button bits.
    uint64_t chartTick;
    uint64_t gameplayTick;
};

struct JudgmentStats {
    uint32_t perfect = 0;
    uint32_t good = 0;
    uint32_t missed = 0;
    uint32_t wrongInputs = 0; // One event per poll with unmatched new presses.
    uint32_t hits() const { return perfect + good; }
    uint32_t judged() const { return hits() + missed; }
};

// No rendering, hardware input, audio control or dynamic allocation in this engine.
// Call step once per input poll with monotonic gameplay ticks and HELD lane bits.
template <uint32_t N>
class NoteJudgment {
public:
    static constexpr uint32_t NO_NOTE = UINT32_MAX;
    static constexpr uint32_t PERFECT_US = 25000;
    static constexpr uint32_t GOOD_EARLY_US = 50000;
    static constexpr uint32_t GOOD_LATE_US = 85000;
    static constexpr uint32_t GBA_CLOCK_HZ = 16777216;
    static constexpr uint32_t FRAME_CYCLES = 280896;
    using EventSink = void (*)(void*, const GameplayEvent&);

    NoteJudgment(const Note* notes, uint32_t ticksPerFrame)
        : notes_(notes), ticksPerFrame_(ticksPerFrame) {
        reset();
    }

    // Rounds the real-time window down to CPU cycles, then chart-clock ticks.
    uint64_t windowTicks(uint32_t microseconds) const {
        const uint64_t cycles = uint64_t(GBA_CLOCK_HZ) * microseconds / 1000000;
        return uint64_t(ticksPerFrame_) * cycles / FRAME_CYCLES;
    }

    void setEventSink(EventSink sink, void* context = nullptr) {
        sink_ = sink;
        context_ = context;
    }

    // Retains the event subscription. Supply held buttons to avoid a phantom
    // press if a future in-game restart occurs while a button is already down.
    void reset(uint8_t heldLanes = 0) {
        states_.fill(NoteState::Pending);
        stats_ = {};
        firstPending_ = 0;
        previousHeld_ = heldLanes & 0x0f;
    }

    const JudgmentStats& stats() const { return stats_; }
    NoteState state(uint32_t index) const { return states_[index]; }

    void step(uint64_t now, uint8_t heldLanes) {
        const uint64_t early = windowTicks(GOOD_EARLY_US);
        const uint64_t late = windowTicks(GOOD_LATE_US);
        const uint64_t perfect = windowTicks(PERFECT_US);
        heldLanes &= 0x0f;
        uint8_t pressed = heldLanes & ~previousHeld_;
        previousHeld_ = heldLanes;

        // Late boundary is inclusive. Every expired pending record emits a miss,
        // including when no keys are pressed or several frames were skipped.
        while (firstPending_ < N) {
            if (states_[firstPending_] != NoteState::Pending) {
                ++firstPending_;
                continue;
            }
            const uint64_t target = notes_[firstPending_].tick;
            if (now <= target || now - target <= late) break;
            judge(firstPending_, NoteState::Missed, now);
            ++firstPending_;
        }

        uint8_t unmatched = pressed;
        for (uint32_t lane = 0; lane < 4; ++lane) {
            const uint8_t mask = 1u << lane;
            if (!(pressed & mask)) continue;
            // Earliest eligible pending note in THIS lane. Other lanes cannot
            // consume it. Each press can hit at most one note.
            for (uint32_t i = firstPending_; i < N; ++i) {
                const uint64_t target = notes_[i].tick;
                if (target > now && target - now > early) break;
                if (states_[i] != NoteState::Pending || notes_[i].lane != lane) continue;
                if (now > target && now - target > late) continue;
                const uint64_t distance = now >= target ? now - target : target - now;
                judge(i, distance <= perfect ? NoteState::Perfect : NoteState::Good, now);
                unmatched &= ~mask;
                break;
            }
        }
        if (unmatched) {
            ++stats_.wrongInputs;
            emit({GameplayEventKind::WrongInput, NO_NOTE, unmatched, 0, now});
        }
    }

private:
    void emit(const GameplayEvent& event) {
        if (sink_) sink_(context_, event); // Synchronous; no lossy event queue.
    }

    void judge(uint32_t index, NoteState state, uint64_t now) {
        states_[index] = state; // Only called for Pending records.
        GameplayEventKind kind;
        if (state == NoteState::Perfect) { ++stats_.perfect; kind = GameplayEventKind::PerfectHit; }
        else if (state == NoteState::Good) { ++stats_.good; kind = GameplayEventKind::GoodHit; }
        else { ++stats_.missed; kind = GameplayEventKind::Miss; }
        emit({kind, index, uint8_t(1u << notes_[index].lane), notes_[index].tick, now});
    }

    const Note* notes_;
    uint32_t ticksPerFrame_;
    std::array<NoteState, N> states_{};
    JudgmentStats stats_{};
    uint32_t firstPending_ = 0;
    uint8_t previousHeld_ = 0;
    EventSink sink_ = nullptr;
    void* context_ = nullptr;
};

#endif
