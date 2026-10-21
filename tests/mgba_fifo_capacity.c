// Independent stock-library experiment: no game code or emulator patches.
#include <mgba/core/core.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/gba/audio.h>
#include <mgba/internal/gba/io.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(int argc,char**argv){assert(argc==2);struct mCore*c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);assert(mCoreLoadFile(c,argv[1]));c->reset(c);struct GBA*g=c->board;
for(unsigned words=7;words<=8;words++){memset(&g->audio.chA,0,sizeof(g->audio.chA));for(unsigned w=0;w<words;w++)GBAAudioWriteFIFO(&g->audio,REG_FIFO_A_LO,0x04030201+0x04040404*w);unsigned before=g->audio.chA.fifoWrite;GBAAudioSampleFIFO(&g->audio,0,0);unsigned first=g->audio.chA.internalSample&255;printf("prime_bytes=%u write=%u read=%u remaining=%u first_sample=%u expected_next=2\n",words*4,before,g->audio.chA.fifoRead,g->audio.chA.internalRemaining,first);assert(first==(words==7?2:0));}for(unsigned experiment=0;experiment<3;experiment++){
memset(&g->audio.chA,0,sizeof(g->audio.chA));g->audio.chA.internalSample=0x09090909;g->audio.chA.internalRemaining=4;g->audio.chA.samples[0]=5;g->audio.chA.samples[1]=5;
g->audio.sampleEvent.when=mTimingCurrentTime(&g->timing)+192+(experiment==2?600:0);
GBAAudioSampleFIFO(&g->audio,0,experiment?600:0);
printf("FIFO_timestamp_probe experiment=%u cyclesLate=%u output=%d,%d\n",experiment,experiment?600:0,g->audio.chA.samples[0],g->audio.chA.samples[1]);
assert(g->audio.chA.samples[0]==(experiment==2?9:5)&&g->audio.chA.samples[1]==9);
}c->deinit(c);return 0;}
