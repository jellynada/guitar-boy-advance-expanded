#include "scanline.hpp"
#include "mode7.hpp"
#include <cstddef>

namespace {
// Existing BG_AFFINE layout is copied to the four BG2 register words by DMA.
static_assert(sizeof(BG_AFFINE)==16&&offsetof(BG_AFFINE,dx)==8&&offsetof(BG_AFFINE,dy)==12);
struct alignas(4) Frame {BG_AFFINE affine[SCREEN_HEIGHT+1];u16 blend[SCREEN_HEIGHT+1];};
EWRAM_DATA Frame frames[2];
volatile bool enabled=false,ready=false;
volatile unsigned active=0;
void build(unsigned index){
    auto& target=frames[index];
    // Above the horizon the existing depth mask is fully opaque. Initialize
    // those entries anyway, rather than retaining a previous scene's table.
    unsigned horizon=m7_level.horizon<0?0:m7_level.horizon>SCREEN_HEIGHT?SCREEN_HEIGHT:m7_level.horizon;
    memset32(target.affine,0,horizon*4);
    memcpy32(target.affine+horizon,m7_level.bgaff+horizon,(SCREEN_HEIGHT-horizon)*4);
    target.affine[SCREEN_HEIGHT]=target.affine[0];
    for(unsigned line=0;line<=SCREEN_HEIGHT;++line){
        // The old HBlank(vc) writes blend for vc+1. Preserve its exclusive
        // clamp upper bound: the floor's existing maximum coefficient is15.
        const int ey=clamp(int(line)-1-m7_level.horizon,0,16);
        target.blend[line]=BLDA_BUILD(16-ey,ey);
    }
}
}
extern "C" {
const BG_AFFINE* volatile scanlineActiveData=nullptr;
volatile u32 scanlineFrameCommits=0,scanlineVblankMaxCycles=0,scanlineDeadlineMisses=0,scanlineVblankLatestLine=0;
}
namespace Scanline {
void stop(){
    const u16 previous=REG_IME;REG_IME=0;
    if(enabled){REG_DMA0CNT=0;REG_DMA3CNT=0;}
    enabled=false;ready=false;scanlineActiveData=nullptr;
    REG_IME=previous;
}
void start(){
    stop();active=0;ready=false;scanlineFrameCommits=scanlineVblankMaxCycles=scanlineDeadlineMisses=scanlineVblankLatestLine=0;
    build(0);scanlineActiveData=frames[0].affine;
    const u16 previous=REG_IME;REG_IME=0;
    irq_disable(II_HBLANK);REG_IF=IRQ_HBLANK;
    enabled=true;REG_IME=previous;
}
void prepare(){
    // If a completed table has not yet been consumed, leave it alone. With
    // ready false VBlank cannot swap active while this buffer is being filled.
    if(!enabled||ready)return;
    build(active^1u);
    asm volatile("":::"memory");
    ready=true;
}
void vblank(){
    if(!enabled)return;
    const u16 begin=REG_TM3D;
    const u32 line=REG_VCOUNT;
    if(line<SCREEN_HEIGHT){++scanlineDeadlineMisses;REG_DMA0CNT=0;REG_DMA3CNT=0;return;}
    if(line>scanlineVblankLatestLine)scanlineVblankLatestLine=line;
    REG_DMA0CNT=0;REG_DMA3CNT=0;
    if(ready){active^=1u;ready=false;++scanlineFrameCommits;}
    auto& frame=frames[active];scanlineActiveData=frame.affine;
    REG_BG_AFFINE[2]=frame.affine[0];REG_BLDALPHA=frame.blend[0];
    // Line0 is loaded now; each visible HBlank installs line(y+1). The extra
    // entry at160 makes the final visible-line trigger safe on real hardware.
    REG_DMA0SAD=reinterpret_cast<u32>(frame.affine+1);REG_DMA0DAD=reinterpret_cast<u32>(&REG_BG_AFFINE[2]);
    REG_DMA0CNT=4|DMA_32|DMA_REPEAT|DMA_DST_RELOAD|DMA_AT_HBLANK|DMA_ENABLE;
    REG_DMA3SAD=reinterpret_cast<u32>(frame.blend+1);REG_DMA3DAD=reinterpret_cast<u32>(&REG_BLDALPHA);
    REG_DMA3CNT=1|DMA_16|DMA_REPEAT|DMA_DST_FIXED|DMA_AT_HBLANK|DMA_ENABLE;
    const u32 cost=u16(REG_TM3D-begin)*64u;
    if(cost>scanlineVblankMaxCycles)scanlineVblankMaxCycles=cost;
}
}
