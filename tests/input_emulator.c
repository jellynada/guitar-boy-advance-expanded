#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int crashed;
static void crash(void* context){(void)context;crashed=1;}
static void log_message(struct mLogger* logger,int category,enum mLogLevel level,const char* format,va_list args){
    (void)logger;(void)category;if(level&(mLOG_FATAL|mLOG_ERROR|mLOG_WARN)){vfprintf(stderr,format,args);fputc('\n',stderr);}
}
static unsigned address(const char* filename,const char* name){
    FILE* in=fopen(filename,"r");assert(in);char line[256],symbol[180],kind;unsigned value=0,result=0;
    while(fgets(line,sizeof(line),in))if(sscanf(line,"%x %c %179s",&value,&kind,symbol)==3&&!strcmp(symbol,name)){result=value;break;}
    fclose(in);assert(result);return result;
}
static void frame(struct mCore* c,unsigned keys){c->setKeys(c,keys);c->runFrame(c);assert(!crashed);}
static void drain(struct mCore* c){for(int ch=0;ch<2;++ch){short v[4096];while(blip_read_samples(c->getAudioChannel(c,ch),v,4096,0)>0){}}}
static void screenshot(const char* prefix,const char* suffix,const color_t* pixels){
    char name[1024];snprintf(name,sizeof(name),"%s.%s.ppm",prefix,suffix);FILE* out=fopen(name,"wb");assert(out);fprintf(out,"P6\n240 160\n255\n");
    for(unsigned i=0;i<240*160;++i){unsigned char rgb[]={pixels[i]&255,(pixels[i]>>8)&255,(pixels[i]>>16)&255};fwrite(rgb,1,3,out);}fclose(out);
}
// Verify the actual composed framebuffer, not the BG map or internal state.
static void visible(struct mCore* c,const color_t* pixels,unsigned font,unsigned x,unsigned y,const char* text) {
    for(;*text;++text,++x)for(unsigned row=0;row<8;++row) {
        unsigned bits=c->busRead8(c,font+((unsigned char)*text-32)*8+row);
        for(unsigned col=0;col<8;++col) {
            unsigned rgb=pixels[(y*8+row)*240+x*8+col];
            int white=(rgb&255)>200&&((rgb>>8)&255)>200&&((rgb>>16)&255)>200;
            if(white!=!!(bits&(1u<<col))){fprintf(stderr,"Invisible text '%c' at tile %u,%u pixel %u,%u\n",*text,x,y,col,row);abort();}
        }
    }
}

int main(int argc,char** argv){
    assert(argc==5);const char* mode=argv[3];int partial=!strcmp(mode,"partial"),wrong=!strcmp(mode,"wrong"),early=!strcmp(mode,"early"),stuck=!strcmp(mode,"stuck");
    unsigned game=address(argv[2],"gameMode"),clock=address(argv[2],"gameplayFrames"),snapshot=address(argv[2],"diagnosticSnapshot"),results=address(argv[2],"diagnosticResults"),font=address(argv[2],"sys8Glyphs");
    struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);struct mCore* c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
    color_t pixels[240*160]={0};c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);
    for(int ch=0;ch<2;++ch)blip_set_rates(c->getAudioChannel(c,ch),c->frequency(c),32768);
    struct mCoreCallbacks cb={.coreCrashed=crash};c->addCoreCallbacks(c,&cb);assert(mCoreLoadFile(c,argv[1]));c->reset(c);
    for(unsigned i=0;i<90;++i){frame(c,0);drain(c);}
    frame(c,128);frame(c,0);frame(c,128);frame(c,0);frame(c,8);frame(c,0);assert(c->busRead32(c,game)==3);
    unsigned rawChecks=0,chordChecks=0,holdChecks=0,pressedChecks=0,oldKeys=~0u,stableKeys=0;int captured[13]={0};
    // Independent hardware-key script. No writes to game input or judgment RAM.
    unsigned masks[]={32,1,2,33,34,3,35,32,32,3,3,1,32};
    while(c->busRead32(c,clock)<120+13*240){
        unsigned f=c->busRead32(c,clock)+1,keys=0;
        for(unsigned t=0;t<13;++t){unsigned start=120+t*240;if(f<start)continue;unsigned dt=f-start;
            if(dt<1)keys|=masks[t];
            if(t==7&&dt==30)keys|=1;
            if(t==8){if(dt<90)keys|=32;if(dt==45)keys|=1;}
            if(t==9&&dt<90)keys|=3;
            if(t==10){if(dt<30)keys|=1;if(dt<90)keys|=2;}
            if(t==11&&(dt==10||dt==20))keys|=1;
            if(t==12&&dt==20)keys|=1;
            if(t==12&&dt==40)keys|=2;
            if(partial&&t==3&&dt==0)keys=32;
            if(wrong&&t==4&&dt==0)keys=35;
            if(early&&t==9&&dt>=20&&dt<90)keys=0;
            if(stuck&&t==11&&dt<=20)keys=1;
        }
        frame(c,keys);drain(c);assert(c->busRead32(c,game)==3);
        unsigned observed=c->busRead32(c,snapshot),test=c->busRead32(c,snapshot+4),held=c->busRead32(c,snapshot+8),pressed=c->busRead32(c,snapshot+12),active=c->busRead32(c,snapshot+28);
        if(observed>5&&observed%37==0){visible(c,pixels,font,0,0,"INPUT / CHORD TEST");++rawChecks;}
        if(pressed)++pressedChecks;
        if(test>=3&&test<=6&&held&&(held&(held-1)))++chordChecks;
        if(keys==oldKeys)++stableKeys;else stableKeys=0;oldKeys=keys;
        if(stableKeys>5&&observed<3100){unsigned expectedHeld=((keys&32)?1:0)|((keys&1)?2:0)|((keys&2)?4:0);assert(held==expectedHeld);}
        if(test==9&&observed>120+9*240+20&&observed<120+9*240+70&&!early){
            visible(c,pixels,font,17,5,"A");visible(c,pixels,font,21,5,"B");visible(c,pixels,font,17,12,"A");visible(c,pixels,font,21,12,"B");}
        if(test==10&&observed>120+10*240+45&&observed<120+10*240+70){visible(c,pixels,font,17,5,"-");visible(c,pixels,font,21,5,"B");visible(c,pixels,font,17,12,"-");visible(c,pixels,font,21,12,"B");}
        if(active&&held){++holdChecks;if(test==10&&observed>120+10*240+40&&observed<120+10*240+80)assert(active==4);}
        if(test<13&&!captured[test]&&observed>=120+test*240+160){
            // Give composed pixels two frames to settle independently of state.
            if(getenv("GBA_TEST_HIDE_DIAGNOSTIC"))c->busWrite16(c,0x04000000,0);
            const char* label=(partial&&test==3)?"PARTIAL":(wrong&&test==4)?"WRONG":(early&&test==9)?"HOLD FAIL":(stuck&&test==11)?"PARTIAL":"PASS";
            if(test<12){visible(c,pixels,font,0,3,label);visible(c,pixels,font,0,5,"GBA HELD");visible(c,pixels,font,0,8,"EXPECTED");}
            char suffix[64];snprintf(suffix,sizeof(suffix),"case-%u",test);screenshot(argv[4],suffix,pixels);captured[test]=1;
        }
        if(observed==120+9*240+40)screenshot(argv[4],"ab-hold",pixels);
        if(observed==120+10*240+60)screenshot(argv[4],"release-a-keep-b",pixels);
    }
    assert(rawChecks>40&&chordChecks>0&&holdChecks>30&&pressedChecks>10);
    for(unsigned test=0;test<13;++test){unsigned expected=(partial&&test==3)?2:(wrong&&test==4)?4:(early&&test==9)?5:(stuck&&test==11)?2:1;assert(c->busRead32(c,results+test*4)==expected);
        const char* label=expected==2?"PARTIAL":expected==4?"WRONG":expected==5?"HOLD FAIL":"PASS";visible(c,pixels,font,21,test+2,label);}
    visible(c,pixels,font,0,16,"A/START RETRY B/SELECT EXIT");screenshot(argv[4],"results",pixels);
    frame(c,8);frame(c,0);assert(c->busRead32(c,clock)<10);for(unsigned i=0;i<4;++i){frame(c,0);drain(c);}visible(c,pixels,font,0,5,"GBA HELD");
    frame(c,12);frame(c,0);assert(c->busRead32(c,game)==0);screenshot(argv[4],"menu",pixels);
    // Move from diagnostic to imported, then original, checking both remain available.
    frame(c,64);frame(c,0);frame(c,8);frame(c,0);assert(c->busRead32(c,game)==2);
    for(unsigned i=0;i<180;++i){frame(c,0);drain(c);}visible(c,pixels,font,0,0,"SCORE:");
    frame(c,12);frame(c,0);frame(c,64);frame(c,0);frame(c,8);frame(c,0);assert(c->busRead32(c,game)==1);
    unsigned sound=0;for(unsigned i=0;i<120;++i){frame(c,0);short v[4096];int n=blip_read_samples(c->getAudioChannel(c,0),v,4096,0);for(int j=0;j<n;++j)sound+=v[j]!=0;blip_clear(c->getAudioChannel(c,1));}assert(sound>1000);
    printf("PASS: diagnostic %s; %u composed labels, %u chord observations, %u valid holds, %u new presses; retry/exit/imported/original audio checked\n",mode,rawChecks,chordChecks,holdChecks,pressedChecks);
    c->deinit(c);return 0;
}
