#ifndef UI_SCREENS_HPP
#define UI_SCREENS_HPP
#include "uiNavigation.hpp"
#include "scoring.hpp"
namespace UiScreens {
extern UiNav::Controller controller;
UiNav::Catalog catalog();
void sync();
void draw(const ScoreSnapshot&,unsigned completion,unsigned diagnostic);
}
extern "C" {extern volatile uint32_t uiScreen,uiCursor,uiSong,uiDifficulty;}
#endif
