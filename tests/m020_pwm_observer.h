// Host-only stock mGBA AV callback observer. Never compiled into a GBA ROM.
#include <mgba/internal/gba/gba.h>
static struct mCore* m020Core;
static FILE* m020Pwm;
static uint64_t m020Discarded;
static uint64_t m020Ordinal;
static FILE* m020PwmEvents;
static void m020Frame(struct mAVStream* stream, int16_t left, int16_t right) {
 (void)stream; (void)right;
 assert(fwrite(&left, sizeof(left), 1, m020Pwm)==1);
 struct GBA* gba=m020Core->board;
 uint64_t endpoint=mTimingGlobalTime(&gba->timing)+(int32_t)(gba->audio.lastSample-1024+(m020Ordinal%2+1)*512-mTimingCurrentTime(&gba->timing));
 // Full bounded 35..38-second wall-clock window, including scene count-in.
 if(endpoint>35ULL*16777216&&endpoint<39ULL*16777216)
  fprintf(m020PwmEvents,"%llu,%llu,%d\n",(unsigned long long)m020Ordinal,(unsigned long long)endpoint,left);
 ++m020Ordinal;
}
static struct mAVStream m020Stream={.postAudioFrame=m020Frame};
static void m020Init(struct mCore* c, const char* prefix) {
 char path[1024];snprintf(path,sizeof(path),"%s.pwm16",prefix);
 m020Pwm=fopen(path,"wb");assert(m020Pwm);m020Core=c;
 snprintf(path,sizeof(path),"%s.pwm-events.csv",prefix);m020PwmEvents=fopen(path,"w");assert(m020PwmEvents);fprintf(m020PwmEvents,"ordinal,cycle,value\n");
 c->setAVStream(c,&m020Stream);
}
static void m020Offset(const char* prefix) {
 char path[1024];snprintf(path,sizeof(path),"%s.pwm-offset.txt",prefix);
 FILE* f=fopen(path,"w");assert(f);
 fprintf(f,"%llu\n",(unsigned long long)m020Discarded);fclose(f);
}
