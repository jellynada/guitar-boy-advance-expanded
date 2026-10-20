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

inline constexpr u16 MEDIUM_BUTTONS[4] = {KEY_LEFT, KEY_RIGHT, KEY_B, KEY_A};
inline constexpr u16 HARD_BUTTONS[5] = {KEY_LEFT, KEY_UP | KEY_DOWN, KEY_RIGHT, KEY_B, KEY_A};
inline constexpr const char* MEDIUM_LABELS[4] = {"LEFT", "RIGHT", "B", "A"};
inline constexpr const char* HARD_LABELS[5] = {"LEFT", "U/D", "RIGHT", "B", "A"};
inline const u16* importedButtons(unsigned lanes) {
    return lanes==5?HARD_BUTTONS:lanes==4?MEDIUM_BUTTONS:EASY_BUTTONS;
}
inline const char* importedLabel(unsigned lane,unsigned lanes) {
    return lanes==5?HARD_LABELS[lane]:lanes==4?MEDIUM_LABELS[lane]:EASY_LABELS[lane];
}
inline u16 importedGameButtons(unsigned lanes) {
    u16 mask=0;for(unsigned i=0;i<lanes;++i)mask|=importedButtons(lanes)[i];return mask;
}
inline u8 importedLaneMaskFromButtons(u16 buttons,unsigned lanes) {
    return lanes==5?PhysicalInput::map(buttons,HARD_BUTTONS):
           lanes==4?PhysicalInput::map(buttons,MEDIUM_BUTTONS):PhysicalInput::map(buttons,EASY_BUTTONS);
}
inline constexpr int receptorX(unsigned lane,unsigned lanes) {
    return lanes==3?int(lane)*9+3:lanes==4?int(lane)*6+3:int(lane)*5+2;
}
inline constexpr unsigned receptorWidth(unsigned lanes) {return lanes==5?5:6;}
#endif
