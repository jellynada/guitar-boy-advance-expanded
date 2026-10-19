#ifndef GAME_CONTROLS_HPP
#define GAME_CONTROLS_HPP

#include "tonc.h"

// Chart lane order: green, red, yellow, blue.
inline constexpr u16 LANE_BUTTONS[4] = {KEY_LEFT, KEY_RIGHT, KEY_A, KEY_B};
inline constexpr u16 GAME_BUTTONS = KEY_LEFT | KEY_RIGHT | KEY_A | KEY_B;

inline u8 laneMaskFromButtons(u16 buttons) {
    u8 lanes = 0;
    for (u32 lane = 0; lane < 4; ++lane)
        if (buttons & LANE_BUTTONS[lane]) lanes |= 1u << lane;
    return lanes;
}

inline constexpr u16 EASY_BUTTONS[3] = {KEY_LEFT, KEY_A, KEY_B};
inline constexpr u16 EASY_GAME_BUTTONS = KEY_LEFT | KEY_A | KEY_B;
inline u8 easyLaneMaskFromButtons(u16 buttons) {
    u8 lanes = 0;
    for (u32 lane = 0; lane < 3; ++lane)
        if (buttons & EASY_BUTTONS[lane]) lanes |= 1u << lane;
    return lanes;
}

#endif
