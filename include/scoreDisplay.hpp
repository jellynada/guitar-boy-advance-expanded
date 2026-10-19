#ifndef SCORE_DISPLAY_HPP
#define SCORE_DISPLAY_HPP
#include "scoring.hpp"
namespace ScoreDisplay {
void initialize();
void clear();
void hud(const ScoreSnapshot&,const char* judgment,const char* guitar);
void results(const ScoreSnapshot&,const char* title,uint32_t sessionState);
}
#endif
