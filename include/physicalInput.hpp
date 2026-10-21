#ifndef PHYSICAL_INPUT_HPP
#define PHYSICAL_INPUT_HPP
#include <cstddef>
#include <cstdint>

// Fixed-size bit masks only: no heap, hardware reads, clock or judgment policy.
// Multiple physical buttons in one binding are OR aliases of ONE logical lane.
namespace PhysicalInput {
struct State { uint8_t held, pressed, released; };
constexpr State edges(uint8_t current, uint8_t previous) {
    return {current, uint8_t(current & ~previous), uint8_t(previous & ~current)};
}
template<std::size_t N>
constexpr uint8_t map(uint16_t physical, const uint16_t (&bindings)[N]) {
    static_assert(N > 0 && N <= 8, "Logical lane masks fit in one byte");
    uint8_t logical = 0;
    for (std::size_t lane = 0; lane < N; ++lane)
        if (physical & bindings[lane]) logical |= uint8_t(1u << lane);
    return logical;
}
template<std::size_t N>
constexpr State sample(uint16_t physical, uint8_t previousLogical, const uint16_t (&bindings)[N]) {
    // Edges are computed AFTER alias coalescing, never from raw key_hit/key_released.
    return edges(map(physical, bindings), previousLogical);
}
}
#endif
