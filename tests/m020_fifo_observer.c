// Extend the existing read-only tap with bounded event-time metadata.
#include <assert.h>
#define GBAAudioSampleFIFO M019_GBAAudioSampleFIFO
#include "hardware_tap.c"
#undef GBAAudioSampleFIFO
static FILE* m020Events;
void GBAAudioSampleFIFO(struct GBAAudio* audio,int fifoId,int32_t cycles) {
 init();
 if(fifoId==0&&segment==1&&sampleNumber>=590000&&sampleNumber<600000){
  if(!m020Events){char path[1024];snprintf(path,sizeof(path),"%s.m020-events.csv",getenv("GBA_HARDWARE_TAP"));m020Events=fopen(path,"w");assert(m020Events);fprintf(m020Events,"index,cycle,late,until,value,slot0,slot1\n");}
  struct GBAAudioFIFO* ch=&audio->chA;uint32_t value=ch->internalSample;
  if(!ch->internalRemaining&&ch->fifoWrite!=ch->fifoRead)value=ch->fifo[ch->fifoRead];
  fprintf(m020Events,"%u,%llu,%d,%d,%d,%d,%d\n",sampleNumber,(unsigned long long)(mTimingGlobalTime(&audio->p->timing)-cycles),cycles,mTimingUntil(&audio->p->timing,&audio->sampleEvent),(int8_t)value,ch->samples[0],ch->samples[1]);
 }
 M019_GBAAudioSampleFIFO(audio,fifoId,cycles);
}
