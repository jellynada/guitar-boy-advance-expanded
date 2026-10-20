#include "sustainDisplay.hpp"
#include "imported_chart.hpp"
#include "importedRuntime.hpp"
#include "mode7.hpp"
#include "gameSession.hpp"
#include <tonc.h>
// Original note art occupies tiles0..128; sprite font starts513. Tiles192..383 are reserved for tails.
namespace SustainDisplay {
constexpr unsigned TILE_ID=192,FIRST_OBJ=32,LIMIT=128;
extern "C" {volatile uint32_t sustainTailSprites=0,sustainTailOverflow=0;}
void initialize(){sustainTailOverflow=0;}
struct Point {int x,y;};
static Point project(uint32_t lane,int64_t delta){
    const auto* cam=m7_level.camera;
    VECTOR vr={ImportedTiming::laneX(lane,importedLaneCount)-cam->pos.x,-cam->pos.y,ImportedTiming::relativeZ(delta)};
    const int x=vec_dot(&vr,&cam->u),y=-vec_dot(&vr,&cam->v),z=-vec_dot(&vr,&cam->w);
    if(z<=0)return {120,120};
    const int scale=DivSafe(M7_D<<16,z);
    // Exactly the center used by the existing 64x64 affine note sprites.
    return {120+int(int64_t(x+1024)*scale/65536),80+int(int64_t(y+128)*scale/65536)};
}
void draw(uint64_t now){
    unsigned slot=FIRST_OBJ;
    // At most32 visible heads plus3 older active holds. Long tails never
    // force a scan over historical chart records on every frame.
    const unsigned visible=importedEndVisible-importedFirstVisible;
    for(unsigned candidate=0;candidate<importedLaneCount+visible;++candidate){
        unsigned i;
        if(candidate<importedLaneCount){i=sustainActiveNote(candidate);if(i>=importedFirstVisible)continue;}
        else i=importedFirstVisible+candidate-importedLaneCount;
        if(i>=importedChartCount)continue;
        const auto& n=activeImportedNotes[i];if(n.tick>now&&n.tick-now>ImportedTiming::AHEAD)break;
        const auto state=sustainState(i);
        if(!activeImportedSustains[i]||(state!=Sustain::State::Pending&&state!=Sustain::State::Active))continue;
        const uint64_t end=n.tick+Sustain::duration(activeImportedSustains[i]);if(end<=now)continue;
        const uint64_t start=n.tick>now?n.tick:now;
        Point a=project(n.lane,int64_t(start)-int64_t(now)),b=project(n.lane,int64_t(end)-int64_t(now));
        if(a.y<=b.y)continue;
        const int top=b.y<28?28:b.y,bottom=a.y>120?120:a.y;
        const int step=(a.x-b.x)*256/(a.y-b.y);
        for(int y=top;y<bottom;y+=8){
            if(slot==LIMIT){++sustainTailOverflow;break;}
            const int fixed=b.x*256+step*(y-b.y),x1=fixed/256,x2=(fixed+step*7)/256;
            const int x=(x1<x2?x1:x2)-2;
            if(x<0||x>=224)continue;
            const unsigned tile=TILE_ID+(slot-FIRST_OBJ)*2;
            for(unsigned row=0;row<8;++row){
                const int offset=(fixed+step*int(row))/256-x-2;
                const uint64_t pixels=y+int(row)<bottom&&offset>=0&&offset<=12?uint64_t(0x1111)<<(offset*4):0;
                tile_mem_obj[0][tile].data[row]=uint32_t(pixels);
                tile_mem_obj[0][tile+1].data[row]=uint32_t(pixels>>32);
            }
            obj_set_attr(&oam_mem[slot++],ATTR0_WIDE|ATTR0_Y(y),ATTR1_SIZE_16x8|ATTR1_X(x),
                         ATTR2_ID(tile)|ATTR2_PRIO(2)|ATTR2_PALBANK(n.lane+1));
        }
    }
    sustainTailSprites=slot-FIRST_OBJ;
    while(slot<LIMIT)obj_hide(&oam_mem[slot++]);
}
}
