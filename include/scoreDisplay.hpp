#ifndef SCORE_DISPLAY_HPP
#define SCORE_DISPLAY_HPP
#include "scoring.hpp"
namespace ScoreDisplay {
void initialize();
void clear();
void page();
void line(unsigned x,unsigned y,const char* text);
void value(unsigned x,unsigned y,uint32_t number);
void preparePauseFont();
void pauseShow();
void pauseHide();
void hud(const ScoreSnapshot&,const char* judgment,const char* guitar);
void results(const ScoreSnapshot&,const char* title,uint32_t sessionState,uint32_t diagnostic=0);
}
#endif
