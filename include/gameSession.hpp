#ifndef GAME_SESSION_HPP
#define GAME_SESSION_HPP
#include "tonc.h"
#include "noteManager.hpp"
// Stable instrumentation values:0 selector,1 unchanged original,2 imported Easy.
extern volatile u32 gameMode;
extern u32 importedFirstVisible;
extern u32 importedEndVisible;
extern u64 importedNowCycles;
u32 activeNoteCount();
bool activeWasHit(u32 index);
noteSprite importedSprite(u32 index);
#endif
