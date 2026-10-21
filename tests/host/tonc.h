// Only the types needed to test NoteManager on a desktop; no GBA hardware emulation.
#pragma once
#include <cstdint>
using u8 = uint8_t;
using u16 = uint16_t;
using u32 = uint32_t;
using u64 = uint64_t;
using s64 = int64_t;
struct VECTOR { int x, y, z; };
constexpr u32 KEY_A = 1, KEY_B = 2, KEY_R = 256, KEY_L = 512, KEY_RIGHT = 16, KEY_LEFT = 32;
constexpr u32 KEY_UP = 64, KEY_DOWN = 128;
