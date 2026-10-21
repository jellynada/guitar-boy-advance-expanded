#include "gameControls.hpp"
#include <cassert>
#include <cstdio>
#include <type_traits>

using PhysicalInput::map;
using PhysicalInput::sample;
// Independent expectations also check the production difficulty bindings.
constexpr uint16_t medium[]={KEY_LEFT,KEY_RIGHT,KEY_B,KEY_A};
constexpr uint16_t hard[]={KEY_LEFT,KEY_UP|KEY_DOWN,KEY_RIGHT,KEY_B,KEY_A};

int main(){
    static_assert(std::is_trivially_copyable<PhysicalInput::State>::value);
    static_assert(sizeof(PhysicalInput::State)==3);
    static_assert(map(KEY_B,EASY_BUTTONS)==2 && map(KEY_A,EASY_BUTTONS)==4);
    unsigned cases=0;
    for(uint16_t keys=0;keys<1024;++keys){
        // Expectations use GBA hardware bit values, independent of binding arrays.
        const uint8_t easy=((keys&32)?1:0)|((keys&2)?2:0)|((keys&1)?4:0);
        const uint8_t original=((keys&32)?1:0)|((keys&16)?2:0)|((keys&1)?4:0)|((keys&2)?8:0);
        assert(easyLaneMaskFromButtons(keys)==easy);
        assert(laneMaskFromButtons(keys)==original);
        assert(importedLaneMaskFromButtons(keys,4)==map(keys,medium));
        assert(importedLaneMaskFromButtons(keys,5)==map(keys,hard));
        assert(map(keys,medium)==(((keys&32)?1:0)|((keys&16)?2:0)|((keys&2)?4:0)|((keys&1)?8:0)));
        assert(map(keys,hard)==(((keys&32)?1:0)|((keys&192)?2:0)|((keys&16)?4:0)|((keys&2)?8:0)|((keys&1)?16:0)));
        for(uint8_t previous=0;previous<8;++previous){
            auto s=sample(keys,previous,EASY_BUTTONS);
            assert(s.held==easy && s.pressed==(easy&~previous) && s.released==(previous&~easy));++cases;
        }
    }
    // Independent overlapping LEFT/B/A holds, then rapid B taps while LEFT stays held.
    uint8_t previous=0;
    const uint16_t keys[]={32,34,35,33,32,34,32,34,32,34,0};
    const uint8_t held[]={1,3,7,5,1,3,1,3,1,3,0};
    const uint8_t pressed[]={1,2,4,0,0,2,0,2,0,2,0};
    const uint8_t released[]={0,0,0,2,4,0,2,0,2,0,3};
    for(unsigned i=0;i<sizeof(keys)/sizeof(keys[0]);++i){
        auto s=sample(keys[i],previous,EASY_BUTTONS);
        assert(s.held==held[i]&&s.pressed==pressed[i]&&s.released==released[i]);previous=s.held;
        auto repeat=sample(keys[i],previous,EASY_BUTTONS);assert(!repeat.pressed&&!repeat.released);
    }
    // Future alias handoff, including direct UP->DOWN without any all-released sample.
    previous=0;
    const uint16_t aliases[]={64,192,128,64,192,128,0};
    for(unsigned i=0;i<7;++i){
        auto s=sample(aliases[i],previous,hard);
        assert(s.held==(i==6?0:2));assert(s.pressed==(i==0?2:0));assert(s.released==(i==6?2:0));previous=s.held;
    }
    // Reset seeds logical held state: entering with A/B already down is not a new press.
    auto reset=sample(3,map(3,EASY_BUTTONS),EASY_BUTTONS);assert(reset.held==6&&!reset.pressed&&!reset.released);
    puts("PASS:1024 raw masks,8192 logical edge cases; LEFT/B/A chords/overlaps/rapid taps/reset; Original unchanged; future aliases coalesce");
}
