#ifndef __SPRITE__
#define __SPRITE__

#include "tonc.h"
#include "mode7.hpp"
#include "noteManager.hpp"
#ifndef GBA_PUBLIC_DEMO
#include "careless.h"
#endif

#define SPR_COUNT	32

#ifndef GBA_PUBLIC_DEMO
extern NoteManager<careless_expertsingle_count>* nm;
#endif
extern int first_sprite;
extern volatile int recent_sprite;

void init_sprite(int ii, noteSprite sprite, u32 note_index);
void init_sprites();
void update_sprites();


#endif