#ifndef SUSTAIN_DISPLAY_HPP
#define SUSTAIN_DISPLAY_HPP
#include <cstdint>
#include "sustain.hpp"
Sustain::State sustainState(uint32_t index);
uint32_t sustainActiveNote(unsigned lane);
namespace SustainDisplay {void initialize();void draw(uint64_t now);}
#endif
