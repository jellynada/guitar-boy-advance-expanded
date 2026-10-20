#include "affineTranslation.hpp"
#include <cassert>
#include <cstring>
#include <array>
struct Row {int16_t pa,pb,pc,pd;int32_t dx,dy;};
int main(){
 std::array<Row,161> rows{},expected{};for(unsigned i=0;i<161;i++)rows[i]={int16_t(i),1,2,3,int32_t(i*17),int32_t(i*891)-40000};
 auto original=rows;AffineTranslation::Key key={rows.data(),1,2,3,4,5,6,58};AffineTranslation::Cache cache;
 cache.remember(rows.data(),58,160,key,-40000);
 for(int z: {-40001,-171071,-40000,-50000,-50000}){
  expected=original;for(unsigned i=58;i<160;i++)expected[i].dy+=z+40000;
  assert(cache.translate(rows.data(),58,160,key,z));assert(!memcmp(rows.data(),expected.data(),sizeof rows));
 }
 for(unsigned k=0;k<8;k++){auto changed=key;switch(k){case 0:changed.table=expected.data();break;case 1:changed.x++;break;case 2:changed.y++;break;case 3:changed.ux++;break;case 4:changed.uz++;break;case 5:changed.vy++;break;case 6:changed.wy++;break;case 7:changed.horizon++;break;}
  auto before=rows;assert(!cache.translate(rows.data(),58,160,changed,-60000));assert(!memcmp(before.data(),rows.data(),sizeof rows));
 }
 assert(!cache.translate(rows.data(),59,160,key,-50000));cache.invalidate();assert(!cache.translate(rows.data(),58,160,key,-50000));
 rows[58].dy=INT32_MAX;cache.remember(rows.data(),58,160,key,0);auto before=rows;assert(!cache.translate(rows.data(),58,160,key,1));assert(!memcmp(before.data(),rows.data(),sizeof rows));
}
