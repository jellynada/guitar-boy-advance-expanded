#ifndef AFFINE_TRANSLATION_HPP
#define AFFINE_TRANSLATION_HPP
#include <cstdint>
#include <climits>
// Exact reuse of an already computed affine table when ONLY camera Z changes.
// No interpolation, lower precision or skipped table publication.
namespace AffineTranslation {
struct Key {
    const void* table;
    int x,y,ux,uz,vy,wy,horizon;
    bool operator==(const Key& b)const{return table==b.table&&x==b.x&&y==b.y&&ux==b.ux&&uz==b.uz&&vy==b.vy&&wy==b.wy&&horizon==b.horizon;}
};
class Cache {
    Key key_{};int32_t z_=0,min_=0,max_=0;unsigned first_=0,end_=0;bool valid_=false;
public:
    void invalidate(){valid_=false;}
    template<class Row>void remember(Row* rows,unsigned first,unsigned end,const Key& key,int32_t z){
        key_=key;z_=z;first_=first;end_=end;valid_=first<end;
        if(!valid_)return;
        min_=max_=rows[first].dy;
        for(unsigned i=first+1;i<end;++i){if(rows[i].dy<min_)min_=rows[i].dy;if(rows[i].dy>max_)max_=rows[i].dy;}
    }
    template<class Row>bool translate(Row* rows,unsigned first,unsigned end,const Key& key,int32_t z){
        if(!valid_||!(key==key_)||first!=first_||end!=end_)return false;
        const int64_t delta=int64_t(z)-z_,lo=int64_t(min_)+delta,hi=int64_t(max_)+delta;
        if(delta<INT32_MIN||delta>INT32_MAX||lo<INT32_MIN||hi>INT32_MAX)return false;
        const int32_t d=int32_t(delta);
        for(unsigned i=first;i<end;++i)rows[i].dy+=d;
        min_=int32_t(lo);max_=int32_t(hi);z_=z;return true;
    }
};
}
#endif
