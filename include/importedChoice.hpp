#pragma once
#include "note.h"
#include <cstdint>
struct ImportedChartChoice {const Note* notes;const uint64_t* sustains;uint32_t count,lanes;const char* difficulty;};
