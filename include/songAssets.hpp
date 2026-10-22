#pragma once
#include "uiNavigation.hpp"
#include "importedChoice.hpp"
#include "pcmSource.hpp"
// ROM-resident descriptor. Catalog metadata has one generated authority.
struct SongAssets {
 const UiNav::Song* metadata;
 const ImportedChartChoice* charts;
 uint32_t chartCount;
 PcmSource pcm;
 bool cut;
 const char* identity;
};
