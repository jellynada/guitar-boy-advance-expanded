#ifndef GAME_CONTROLS_HPP
#define GAME_CONTROLS_HPP

#include "tonc.h"
#include "physicalInput.hpp"

// Chart lane order: green, red, yellow, blue.
inline constexpr u16 LANE_BUTTONS[4] = {KEY_LEFT, KEY_RIGHT, KEY_A, KEY_B};
inline constexpr u16 GAME_BUTTONS = KEY_LEFT | KEY_RIGHT | KEY_A | KEY_B;

inline u8 laneMaskFromButtons(u16 buttons) {
    return PhysicalInput::map(buttons, LANE_BUTTONS);
}

inline constexpr u16 EASY_BUTTONS[3] = {KEY_LEFT, KEY_B, KEY_A};
inline constexpr const char* EASY_LABELS[3] = {"LEFT", "B", "A"};
inline constexpr u16 EASY_GAME_BUTTONS = KEY_LEFT | KEY_A | KEY_B;
inline u8 easyLaneMaskFromButtons(u16 buttons) {
    return PhysicalInput::map(buttons, EASY_BUTTONS);
}

#endif
