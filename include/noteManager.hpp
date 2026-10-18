#ifndef __NOTE_MANAGER__
#define __NOTE_MANAGER__

#include "tonc.h"
#include "noteJudgment.hpp"

struct noteSprite {
    VECTOR pos;
    u8 pal;
};

#define ENABLED true

// Keep the original note-position formulas and ten-frame sprite lookahead.
// Judgment and presentation are deliberately separate.
template <u32 N>
class NoteManager {
public:
    NoteManager(const Note* song_notes, u32 song_bpm)
        : song_notes(song_notes), song_bpm(song_bpm), judgment_(song_notes, song_bpm) {
        prepSprites();
    }

    void reset(u8 heldLanes = 0) {
        current_note_index = 0;
        judgment_.reset(heldLanes);
    }

    u32 update(u32 frame, u8 heldLanes) {
        const u64 tick = u64(frame) * song_bpm;
        judgment_.step(tick, heldLanes);
        const u64 lookahead = u64(song_bpm) * 10;
        const u64 visualTick = frame ? tick - song_bpm : 0; // Mission 001 pre-increment lookahead.
        while (current_note_index < N) {
            const u64 target = song_notes[current_note_index].tick;
            if (target > visualTick && target - visualTick > lookahead) break;
            ++current_note_index;
        }
        return current_note_index;
    }

    u32 getNoteCount() const { return N; }
    noteSprite* getNoteSprites() { return note_sprites; }
    NoteJudgment<N>& judgment() { return judgment_; }
    const NoteJudgment<N>& judgment() const { return judgment_; }
    bool wasHit(u32 index) const {
        if (index >= N) return false;
        NoteState state = judgment_.state(index);
        return state == NoteState::Perfect || state == NoteState::Good;
    }

private:
        void prepSprites(){
            for(u32 i = 0; i < N; i++){
                VECTOR pos = {};
                note_sprites[i].pal = 0;
                pos.y = 0;
                switch(song_notes[i].lane){
                    case 0:
                        note_sprites[i].pal = 1;
                        pos.x = 0x0E300;
                        break;
                    case 1:
                        note_sprites[i].pal = 2;
                        pos.x = 0x0F400;
                        break;
                    case 2:
                        note_sprites[i].pal = 3;
                        pos.x = 0x10400;
                        break;
                    case 3:
                        note_sprites[i].pal = 4;
                        pos.x = 0x11600;
                        break;
                }
                s64 temp_tick = -static_cast<s64>(song_notes[i].tick);
                pos.z = (((256 * temp_tick / 871) - 640000)>>4)-25000; //this is a placeholder, will need to be converted to actual z position based on tempo and speed of highway
                note_sprites[i].pos = pos;
            }
        }
        
        const Note* song_notes;
        u32 song_bpm;
        noteSprite note_sprites[N];
        NoteJudgment<N> judgment_;
        u32 current_note_index = 0;
};

#endif
