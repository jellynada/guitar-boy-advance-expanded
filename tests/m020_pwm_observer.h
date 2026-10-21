// Host-only stock mGBA AV callback observer. Never compiled into a GBA ROM.
#include <mgba/internal/gba/gba.h>
static struct mCore* m020Core;
static FILE* m020Pwm;
static uint64_t m020Discarded;
static void m020Frame(struct mAVStream* stream, int16_t left, int16_t right) {
 (void)stream; (void)right;
 assert(fwrite(&left, sizeof(left), 1, m020Pwm)==1);
}
static struct mAVStream m020Stream={.postAudioFrame=m020Frame};
static void m020Init(struct mCore* c, const char* prefix) {
 char path[1024];snprintf(path,sizeof(path),"%s.pwm16",prefix);
 m020Pwm=fopen(path,"wb");assert(m020Pwm);m020Core=c;
 c->setAVStream(c,&m020Stream);
}
static void m020Offset(const char* prefix) {
 char path[1024];snprintf(path,sizeof(path),"%s.pwm-offset.txt",prefix);
 FILE* f=fopen(path,"w");assert(f);
 fprintf(f,"%llu\n",(unsigned long long)m020Discarded);fclose(f);
}
