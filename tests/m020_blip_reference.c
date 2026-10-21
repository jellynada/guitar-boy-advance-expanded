// Independent replay of observed PWM values through an isolated stock blip.
// No waveform alignment or fitted gain. Capture offset is measured by probe.
#include <mgba/core/blip_buf.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char**argv) {
 assert(argc==3);FILE* in=fopen(argv[1],"rb");FILE* out=fopen(argv[2],"wb");assert(in&&out);
 struct blip_t* b=blip_new(4096);assert(b);blip_set_rates(b,16777216,32768);
 int last=0;unsigned clock=0;int16_t sample,buffer[4096];
 while(fread(&sample,2,1,in)==1){
  blip_add_delta(b,clock,(int)sample-last);last=sample;clock+=512;
  if(clock==2048){blip_end_frame(b,2048);clock=0;int n;
   while((n=blip_read_samples(b,buffer,4096,0))>0)assert(fwrite(buffer,2,n,out)==(size_t)n);
  }
 }
 fclose(in);fclose(out);blip_delete(b);return 0;
}
