#include "sprite.hpp"
#include "gameSession.hpp"

#include "notes.h"

u8 sort_ids[SPR_COUNT];
int sort_keys[SPR_COUNT];
static u32 loaded_notes[SPR_COUNT];

int first_sprite = SPR_COUNT;
volatile int recent_sprite = 0;

void init_sprite(int ii, noteSprite sprite, u32 note_index){
	loaded_notes[ii] = note_index;
	M7_SPRITE *spr= &m7_level.sprites[ii];
	spr->pos= sprite.pos;
	spr->anchor.x= 16;
	spr->anchor.y= 30;
	obj_set_attr(&spr->obj, 
		ATTR0_SQUARE | ATTR0_AFF_DBL | ATTR0_BLEND,
		ATTR1_SIZE_64x32 | ATTR1_AFF_ID(ii), 
		ATTR2_ID(1) | ATTR2_PRIO(2) | ATTR2_PALBANK(sprite.pal));

	spr->obj_id= ii;
	spr->aff_id= ii;
	spr->tiles = (TILE*)notesTiles;
	//Terminal::log("Init sprite %% at z: %%", ii, spr->pos.z);
};

void update_sprites()
{
	int ii;

	M7_SPRITE *spr= m7_level.sprites;

	const int recent = recent_sprite; // Main-thread visual lookahead cursor.
	const int count = activeNoteCount();
	//check the next 30 sprites,
	if (gameMode == 2) {
        for (ii=0; ii<SPR_COUNT; ++ii) {
            loaded_notes[ii] = UINT32_MAX;
            obj_hide(&spr[ii].obj);
        }
        // Adaptation rejects charts exceeding this complete visible-window budget.
        for (u32 index=importedFirstVisible; index<importedEndVisible && index-importedFirstVisible<SPR_COUNT; ++index)
            init_sprite(index-importedFirstVisible, importedSprite(index), index);
    } else if(first_sprite != recent+SPR_COUNT-2){
		noteSprite* positions = nm->getNoteSprites();
		for(ii=first_sprite; ii<recent+SPR_COUNT-2 && ii<count; ii++){
			init_sprite(ii%SPR_COUNT, positions[ii], ii);
		}
		first_sprite = recent;
	}

	for(ii=0; ii<SPR_COUNT; ii++)
	{
        // Keep the chart identity of each recycled slot. A judged note may be
        // behind the lookahead cursor and therefore not reloaded this frame.
        if (loaded_notes[ii] < (u32)count) {
            const u32 tile = activeWasHit(loaded_notes[ii]) ? 65 : 1;
            spr[ii].obj.attr2 = (spr[ii].obj.attr2 & ~ATTR2_ID_MASK) | ATTR2_ID(tile);
            m7_prep_sprite(&m7_level, &spr[ii]);
        } else {
            obj_hide(&spr[ii].obj);
        }

		// Create sort key
		if(BFN_GET2(spr[ii].obj.attr0, ATTR0_MODE) != ATTR0_HIDE){
			sort_keys[ii]= spr[ii].pos2.z;
		} else
			sort_keys[ii]= INT_MAX;
	}

	id_sort_shell(sort_keys, sort_ids, SPR_COUNT);

	// Update real OAM
	for(ii=0; ii<SPR_COUNT; ii++)
		obj_copy(&oam_mem[ii], &spr[sort_ids[ii]].obj, 1);
}

void init_sprites()
{
	int ii;
	noteSprite* pos = nm->getNoteSprites();
	// Notes
	for(ii=0; ii<SPR_COUNT; ii++)
	{
		if(gameMode != 2 && ii < (int)nm->getNoteCount()) init_sprite(ii, pos[ii], ii);
        else {
            loaded_notes[ii] = UINT32_MAX;
            obj_hide(&m7_level.sprites[ii].obj);
        }
	}

	// Setup sorting list
	for(ii=0; ii<SPR_COUNT; ii++)
		sort_ids[ii]= ii;
}