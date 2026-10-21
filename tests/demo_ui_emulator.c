// Actual menu/control inputs; complete composed labels and results/replay.
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/core/blip_buf.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned sym(const char*f,const char*n){FILE*p=fopen(f,"r");assert(p);char s[180],line[256],t;unsigned a;while(fgets(line,sizeof line,p))if(sscanf(line,"%x %c %179s",&a,&t,s)==3&&!strcmp(s,n)){fclose(p);return a;}fclose(p);assert(0);return 0;}
static void quiet(struct mLogger*l,int c,enum mLogLevel v,const char*f,va_list a){(void)l;(void)c;(void)v;(void)f;(void)a;}
static void step(struct mCore*c,unsigned key){c->setKeys(c,key);c->runFrame(c);for(int j=0;j<2;++j){short b[4096];while(blip_read_samples(c->getAudioChannel(c,j),b,4096,0)>0){}}}
static void press(struct mCore*c,unsigned key){step(c,key);step(c,0);}
static void label(struct mCore*c,color_t*p,unsigned first,unsigned y,const char*s){unsigned ink=0;for(unsigned i=0;s[i];++i){unsigned a=0x07000000+(first+i)*8;unsigned a0=c->busRead16(c,a),a1=c->busRead16(c,a+2),a2=c->busRead16(c,a+4);assert((a0&255)==y);unsigned tile=((unsigned)s[i]-31)*4+0x201;assert((a2&1023)==tile);unsigned sx=a1&511;assert(sx<240);for(unsigned dy=0;dy<16&&y+dy<160;++dy)for(unsigned x=0;x<16&&sx+x<240;++x){unsigned address=0x06010000+(tile+dy/8*2+x/8)*32+dy%8*4+x%8/2;unsigned color=(c->busRead8(c,address)>>(x%2*4))&15;if(!color)continue;unsigned palette=c->busRead16(c,0x05000200+(a2>>12)*32+color*2);assert((p[(y+dy)*240+sx+x]&0xffffff)==(mColorFrom555(palette)&0xffffff));++ink;}}assert(ink>40);}
int main(int argc,char**argv){assert(argc==3);struct mLogger logger={.log=quiet};mLogSetDefaultLogger(&logger);struct mCore*c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);color_t pixels[38400];c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);assert(mCoreLoadFile(c,argv[1]));c->reset(c);
unsigned mode=sym(argv[2],"gameMode"),ready=sym(argv[2],"importedReady"),session=sym(argv[2],"importedSessionState"),score=sym(argv[2],"displayedScore"),count=sym(argv[2],"importedChartCount"),lanes=sym(argv[2],"importedLaneCount");
for(int i=0;i<90;++i){step(c,0);}
label(c,pixels,16,28,"GUITAR BOY ADVANCE");label(c,pixels,48,58,">Copper Circuit");
press(c,128);press(c,1);assert(c->busRead32(c,mode)==3);press(c,12);assert(c->busRead32(c,mode)==0);press(c,64);press(c,1);assert(c->busRead32(c,mode)==4);
press(c,64);for(int i=0;i<3;++i)step(c,0);label(c,pixels,88,106,">Hard L U/D R B A");label(c,pixels,0,146,"U/D=Up or Down");press(c,1);assert(c->busRead32(c,mode)==2&&c->busRead32(c,lanes)==5&&c->busRead32(c,count)==335);
for(int wait=0;wait<16&&!c->busRead32(c,ready);++wait){step(c,0);}assert(c->busRead32(c,ready));
press(c,8);assert(c->busRead32(c,sym(argv[2],"importedTransport"))==2);unsigned frozen=c->busRead32(c,sym(argv[2],"audioSamplesConsumed"));for(int i=0;i<600;++i)step(c,0);assert(c->busRead32(c,sym(argv[2],"audioSamplesConsumed"))==frozen);press(c,4);assert(c->busRead32(c,mode)==0);
press(c,1);assert(c->busRead32(c,mode)==4);press(c,128);press(c,1);assert(c->busRead32(c,count)==86);for(int i=0;i<4900&&c->busRead32(c,session)==0;++i)step(c,0);assert(c->busRead32(c,session)==1&&c->busRead32(c,score+44)==1&&c->busRead32(c,score+28)==86);press(c,1);assert(c->busRead32(c,session)==0);for(int wait=0;wait<16&&!c->busRead32(c,ready);++wait){step(c,0);}assert(c->busRead32(c,ready));
assert(c->busRead32(c,score)==0);press(c,8);press(c,4);assert(c->busRead32(c,mode)==0);assert(c->busRead32(c,sym(argv[2],"audioUnderruns"))==0);
puts("PASS: composed boot/song/Hard alias labels, diagnostics exit, 10s frozen pause, Easy results, replay and return; original entry absent");c->deinit(c);return 0;}
