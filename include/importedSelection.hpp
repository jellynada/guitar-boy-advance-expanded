#pragma once
#include "imported_chart.hpp"
#include "importedChoice.hpp"
#ifndef GBA_IMPORTED_CHOICES
inline constexpr ImportedChartChoice imported_choices[]={{imported_notes,imported_sustain_us,imported_note_count,3,"Easy"}};
#endif
inline constexpr unsigned imported_choice_count=sizeof(imported_choices)/sizeof(imported_choices[0]);
