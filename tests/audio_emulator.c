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
static uint64_t read64(struct mCore* c,unsigned a){return c->busRead32(c,a)|((uint64_t)c->busRead32(c,a+4)<<32);}
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
    assert(argc==7);const char* syms=argv[2];unsigned count=strtoul(argv[3],0,10),frames=strtoul(argv[4],0,10);const char* mode=argv[5];int isFault=!strncmp(mode,"fault",5); int reactiveMixed=!strcmp(mode,"reactive"); int reactiveWrong=!strcmp(mode,"wrong");int scoringMixed=!strcmp(mode,"scoring");int inconsistent=!strcmp(mode,"inconsistent");int allGood=!strcmp(mode,"good");int silentPerfect=!strcmp(mode,"silent-perfect");
    unsigned modeaddr=address(syms,"gameMode"),clockaddr=address(syms,"importedNowCycles"),statsaddr=address(syms,"displayedStats"),chartaddr=address(syms,"imported_notes");
    unsigned stateaddr=address(syms,"audioState"),consaddr=address(syms,"audioSamplesConsumed"),maxaddr=address(syms,"importedFrameWorkMaxCycles"),totaladdr=address(syms,"importedFrameWorkTotalCycles"),workcount=address(syms,"importedFrameWorkCount");
    unsigned serialaddr=address(syms,"guitarEventSerial"),traceaddr=address(syms,"guitarEventTrace"),gateaddr=address(syms,"guitarAudible"),gainaddr=address(syms,"guitarGain"),refilladdr=address(syms,"audioRefillCount"),irqmaxaddr=address(syms,"audioRefillMaxCycles"),irqtotaladdr=address(syms,"audioRefillTotalCycles"),underrunaddr=address(syms,"audioUnderruns");
    unsigned scoreaddr=address(syms,"displayedScore"),sessionaddr=address(syms,"importedSessionState");
    unsigned fontaddr=address(syms,"sys8Glyphs"),visibleChecks=0,stableScore=~0u,stableCombo=~0u,stableFrames=0;
    struct mLogger logger={.log=log_message};mLogSetDefaultLogger(&logger);
    struct mCore* c=mCoreFind(argv[1]);assert(c&&c->init(c));mCoreInitConfig(c,NULL);
    color_t pixels[240*160]={0};c->setVideoBuffer(c,pixels,240);c->setAudioBufferSize(c,4096);
    for(int ch=0;ch<2;++ch)blip_set_rates(c->getAudioChannel(c,ch),c->frequency(c),32768);
    struct mCoreCallbacks cb={.coreCrashed=crash};c->addCoreCallbacks(c,&cb);assert(mCoreLoadFile(c,argv[1]));c->reset(c);
    for(unsigned i=0;i<90;++i){frame(c,0);drain(c);}assert(c->busRead32(c,modeaddr)==0);screenshot(argv[6],"menu",pixels);
    for(unsigned i=0;i<2;++i){frame(c,128);drain(c);}frame(c,0);drain(c);
    char filename[1024];snprintf(filename,sizeof(filename),"%s.raw",argv[6]);FILE* audio=fopen(filename,"wb");assert(audio);
    snprintf(filename,sizeof(filename),"%s.csv",argv[6]);FILE* csv=fopen(filename,"w");assert(csv);fprintf(csv,"frame,tick,consumed,hardware_consumed,capture_samples,perfect,good,miss,state,gate,gain,refills,underruns\n");
    snprintf(filename,sizeof(filename),"%s.events.csv",argv[6]);FILE* events=fopen(filename,"w");assert(events);fprintf(events,"serial,sample,kind,gain,gameplay_tick\n");unsigned lastEventFrame=0,lastKind=0;unsigned eventSerial=0;int mutedSaved=0,recoveredSaved=0,resultSaved=0;unsigned refScore=0,refCombo=0,refMax=0,refHighest=1;
    unsigned firstaddr=address(syms,"importedFirstVisible"),endaddr=address(syms,"importedEndVisible");
    int lineSeen[5]={0};unsigned refIds[5]={0,1,2,count/2,count-1};
    uint64_t written=0,previous=0;unsigned next=0,nonzero=0,lastJudged=0;uint64_t frozen=0;unsigned frozenJudged=0;unsigned buttons[]={32,1,2};
    for(unsigned f=0;f<frames;++f){
        unsigned keys=f<2?8:0;
        uint64_t now=read64(c,clockaddr);
        if((!strcmp(mode,"perfect")||reactiveMixed||reactiveWrong||scoringMixed||allGood||silentPerfect)&&f>2)while(next<count){uint64_t target=read64(c,chartaddr+next*16);if(allGood||(scoringMixed&&next%4==1))target+=671088;if(target>now+280896)break;unsigned lane=c->busRead32(c,chartaddr+next*16+8);assert(lane<3);if((!reactiveMixed||next%3!=1)&&(!scoringMixed||next%4!=2))keys|=buttons[lane];++next;}
        if(reactiveWrong&&f>10&&f%30==0)keys=32|1|2;
        if(inconsistent&&f==400)c->busWrite32(c,stateaddr,2);
        if(isFault&&f==400){
            // Inject outside an ISR: its saved IME/IE restoration can otherwise
            // undo a debugger write made at the core's frame boundary.
            unsigned cpsr=0,steps=0;
            do {assert(c->readRegister(c,"cpsr",&cpsr));if((cpsr&31)==31&&c->busRead16(c,0x04000208)==1)break;c->step(c);assert(++steps<100000);}while(1);
            if(!strcmp(mode,"fault_dma"))c->busWrite16(c,0x04000106,0);
            else if(!strcmp(mode,"fault_sound"))c->busWrite16(c,0x04000084,0);
            else if(!strcmp(mode,"fault_irq"))c->busWrite16(c,0x04000200,c->busRead16(c,0x04000200)&~16);
            else if(!strcmp(mode,"fault_underrun"))c->busWrite16(c,0x04000208,0);
            else c->busWrite16(c,0x04000102,0);
        }
        if(isFault&&f>405&&f%2)keys=32|1|2; // inputs cannot judge after an audio fault
        if(!strcmp(mode,"fault_underrun")&&f==401)c->busWrite16(c,0x04000208,1);
        if(c->busRead32(c,sessionaddr)!=0)keys=0;
        frame(c,keys);
        if(getenv("GBA_TEST_HIDE_HUD")&&f>30)c->busWrite16(c,0x04000000,c->busRead16(c,0x04000000)&~256);
        if(f>4)assert(c->busRead32(c,modeaddr)==2);
        short left[4096],right[4096];int n=blip_read_samples(c->getAudioChannel(c,0),left,4096,0),r=blip_read_samples(c->getAudioChannel(c,1),right,4096,0);assert(n==r);
        for(int i=0;i<n;++i){assert(left[i]==right[i]);nonzero+=left[i]!=0;}
        fwrite(left,2,n,audio);written+=n;
        uint64_t tick=read64(c,clockaddr);assert(tick>=previous);previous=tick;
        unsigned p=c->busRead32(c,statsaddr),g=c->busRead32(c,statsaddr+4),m=c->busRead32(c,statsaddr+8),state=c->busRead32(c,stateaddr);
        assert(p+g+m<=count);
        // Start the independent hardware epoch only once playback has begun.
        // Stopped Timer1 reads zero, not the 65520 reload; treating that as a
        // running counter fabricated a 64-second wrap in the capture harness.
        static unsigned epoch=0,oldraw=0;static int hardwareActive=0;
        unsigned hw=c->busRead32(c,consaddr);
        if(state==1){unsigned raw=((unsigned)c->busRead16(c,0x04000108)<<4)|(c->busRead16(c,0x04000104)-65520);
            if(hardwareActive&&raw<oldraw)epoch+=1u<<20;
            oldraw=raw;hardwareActive=1;hw=epoch+raw;}
        fprintf(csv,"%u,%llu,%u,%u,%llu,%u,%u,%u,%u,%u,%u,%u,%u\n",f,(unsigned long long)tick,c->busRead32(c,consaddr),hw,(unsigned long long)written,p,g,m,state,c->busRead32(c,gateaddr),c->busRead32(c,gainaddr),c->busRead32(c,refilladdr),c->busRead32(c,underrunaddr));
        if(!mutedSaved&&!c->busRead32(c,gateaddr)&&!c->busRead32(c,gainaddr)){screenshot(argv[6],"muted",pixels);mutedSaved=1;}
        if(mutedSaved&&!recoveredSaved&&c->busRead32(c,gateaddr)&&c->busRead32(c,gainaddr)==256){screenshot(argv[6],"recovered",pixels);recoveredSaved=1;}
        unsigned latest=c->busRead32(c,serialaddr);if(inconsistent&&latest<eventSerial)eventSerial=latest;assert(latest-eventSerial<=16);
        while(eventSerial<latest){unsigned a=traceaddr+(eventSerial%16)*24;assert(c->busRead32(c,a+12)==eventSerial);fprintf(events,"%u,%u,%u,%u,%llu\n",eventSerial,c->busRead32(c,a),c->busRead32(c,a+4),c->busRead32(c,a+8),(unsigned long long)read64(c,a+16));unsigned kind=c->busRead32(c,a+4);lastKind=kind;lastEventFrame=f;
            if(kind<2){++refCombo;unsigned mult=refCombo<10?1:refCombo<20?2:refCombo<30?3:4;refScore+=(kind==0?10:5)*mult;if(refCombo>refMax)refMax=refCombo;if(mult>refHighest)refHighest=mult;}else refCombo=0;
            ++eventSerial;}
        if(eventSerial){assert(c->busRead32(c,scoreaddr)==refScore);assert(c->busRead32(c,scoreaddr+4)==refCombo);assert(c->busRead32(c,scoreaddr+8)==refMax);assert(c->busRead32(c,scoreaddr+16)==refHighest);}
        unsigned session=c->busRead32(c,sessionaddr);if(state==1)assert(session!=1);
        unsigned liveScore=c->busRead32(c,scoreaddr),liveCombo=c->busRead32(c,scoreaddr+4);
        if(liveScore==stableScore&&liveCombo==stableCombo)++stableFrames;else stableFrames=0;
        stableScore=liveScore;stableCombo=liveCombo;
        if(!session&&(f==120||f==9000)){char label[32];snprintf(label,sizeof(label),"hud-%u",f);screenshot(argv[6],label,pixels);}
        if(!session&&f>20&&f%61==0&&stableFrames>3) {
            char value[32];visible(c,pixels,fontaddr,0,0,"SCORE:");
            snprintf(value,sizeof(value),"%u",liveScore);visible(c,pixels,fontaddr,6,0,value);
            visible(c,pixels,fontaddr,0,1,"COMBO:");snprintf(value,sizeof(value),"%u",liveCombo);visible(c,pixels,fontaddr,6,1,value);
            visible(c,pixels,fontaddr,16,1,"MULT:");snprintf(value,sizeof(value),"%u",c->busRead32(c,scoreaddr+12));visible(c,pixels,fontaddr,21,1,value);++visibleChecks;
            if(eventSerial&&f>lastEventFrame+3&&f<lastEventFrame+14)visible(c,pixels,fontaddr,0,2,lastKind==0?"PERFECT":lastKind==1?"GOOD":lastKind==2?"MISS":"WRONG");
            if(f==480||f==1500||f==9000){char label[32];snprintf(label,sizeof(label),"hud-%u",f);screenshot(argv[6],label,pixels);}
        }
        if(session&&!resultSaved){screenshot(argv[6],session==1?"results":"error",pixels);resultSaved=1;
            char name[1024];snprintf(name,sizeof(name),"%s.screen.txt",argv[6]);FILE* screen=fopen(name,"w");assert(screen);for(unsigned y=0;y<20;++y){for(unsigned x=0;x<30;++x){unsigned tile=c->busRead16(c,0x0600f800+(y*32+x)*2)&1023;char ch=tile>=129&&tile<=223?(char)(tile-128+31):' ';fputc(ch,screen);}fputc('\n',screen);}fclose(screen);
        }
        for(unsigned ref=0;ref<5;++ref) if(!lineSeen[ref]) {
            unsigned index=refIds[ref];if(index>=count){lineSeen[ref]=1;continue;}
            unsigned first=c->busRead32(c,firstaddr),end=c->busRead32(c,endaddr);
            uint64_t target=read64(c,chartaddr+index*16);
            if(index>=first&&index<end&&tick+5*280896>=target) {
                unsigned slot=index-first;
                for(unsigned obj=0;obj<32;++obj){
                    unsigned a0=c->busRead16(c,0x07000000+obj*8),a1=c->busRead16(c,0x07000002+obj*8);
                    if((a0&0x300)!=0x300||((a1>>9)&31)!=slot)continue;
                    int x=a1&511,y=a0&255;if(x>=256)x-=512;if(y>=160)y-=256;x+=64;y+=64;
                    if(y>=116){
                        uint64_t distance=tick>target?tick-target:target-tick;
                        unsigned lane=c->busRead32(c,chartaddr+index*16+8);
                        assert(distance<=280896);assert(abs(x-(48+72*(int)lane))<=9);assert(y<=124);
                        lineSeen[ref]=1;
                        if(ref==0){char imageName[1024];snprintf(imageName,sizeof(imageName),"%s.ppm",argv[6]);FILE* image=fopen(imageName,"wb");assert(image);fprintf(image,"P6\n240 160\n255\n");for(unsigned pixel=0;pixel<240*160;++pixel){unsigned char rgb[]={pixels[pixel]&255,(pixels[pixel]>>8)&255,(pixels[pixel]>>16)&255};fwrite(rgb,1,3,image);}fclose(image);}
                        printf("LINE index%u expected_tick%llu displayed_tick%llu error_ms%.6f center_x%d center_y%d\n",index,(unsigned long long)target,(unsigned long long)tick,(tick>target?tick-target:target-tick)*1000.0/16777216,x,y);}
                }
            }
        }
        if(p+g+m>lastJudged){unsigned index=p+g+m-1;if(index==0||index==count/2||index==count-1){uint64_t target=read64(c,chartaddr+index*16);printf("REFERENCE index%u expected_tick%llu actual_tick%llu abs_error_ms%.6f\n",index,(unsigned long long)target,(unsigned long long)tick,(tick>target?tick-target:target-tick)*1000.0/16777216);}lastJudged=p+g+m;}
        if((isFault||inconsistent)&&f==405){frozen=tick;frozenJudged=p+g+m;}
        if((isFault||inconsistent)&&f>405){assert(state==(inconsistent?0:3));assert(tick==frozen);assert(p+g+m==frozenJudged);assert(c->busRead32(c,statsaddr+12)==0);}
    }
    fclose(audio);fclose(csv);fclose(events);
    if(!strcmp(mode,"perfect")||silentPerfect||allGood||!strcmp(mode,"miss")||!strcmp(mode,"silent"))for(unsigned r=0;r<5;++r)assert(lineSeen[r]);
    unsigned p=c->busRead32(c,statsaddr),g=c->busRead32(c,statsaddr+4),m=c->busRead32(c,statsaddr+8),w=c->busRead32(c,statsaddr+12),state=c->busRead32(c,stateaddr);
    if(!strcmp(mode,"perfect")||silentPerfect)assert(p==count&&g==0&&m==0&&w==0);
    if(allGood)assert(p==0&&g==count&&m==0&&w==0);
    if(!strcmp(mode,"miss"))assert(m==count&&p==0&&g==0&&w==0);
    if(scoringMixed)assert(p>0&&g>0&&m>0);
    if(reactiveMixed)assert(p+g>0&&m>0&&w==0);
    if(reactiveWrong)assert(p+g>0&&w>0);
    if(!isFault)assert(c->busRead32(c,underrunaddr)==0);
    if(isFault||inconsistent)assert(state==(inconsistent?0:3)&&p+g+m<count);
    else if(!strcmp(mode,"silent")||silentPerfect)assert(state==0&&nonzero==0);
    else if(!strcmp(mode,"preview"))assert(state==1&&nonzero>1000&&c->busRead32(c,gateaddr)==1&&eventSerial==0);
    else assert(state==2&&nonzero>1000);
    printf("PASS: %s frames%u notes%u Perfect%u Good%u Miss%u Wrong%u nonzero_samples%u audio_state%u; foreground max%u avg%.1f CPUcycles/frame\n",mode,frames,count,p,g,m,w,nonzero,state,c->busRead32(c,maxaddr),read64(c,totaladdr)/(double)c->busRead32(c,workcount));
    unsigned session=c->busRead32(c,sessionaddr);unsigned score=c->busRead32(c,scoreaddr),combo=c->busRead32(c,scoreaddr+4),maximum=c->busRead32(c,scoreaddr+8),highest=c->busRead32(c,scoreaddr+16),accuracy=c->busRead32(c,scoreaddr+40),finalized=c->busRead32(c,scoreaddr+44),fc=c->busRead32(c,scoreaddr+48),ap=c->busRead32(c,scoreaddr+52);
    if(isFault||inconsistent){assert(session==(inconsistent?3:2)&&!finalized&&!fc&&!ap);}else if(strcmp(mode,"preview")){assert(session==1&&finalized);if(state==2)assert(read64(c,clockaddr)==((uint64_t)c->busRead32(c,consaddr)-1)*1024);assert(c->busRead32(c,scoreaddr+20)==p&&c->busRead32(c,scoreaddr+24)==g&&c->busRead32(c,scoreaddr+28)==m&&c->busRead32(c,scoreaddr+32)==w);assert(accuracy==((uint64_t)(p+g)*10000+count/2)/count);assert(fc==(m==0&&w==0)&&ap==(p==count&&w==0));}
    if(!strcmp(mode,"perfect")||silentPerfect||allGood){unsigned independent=0;for(unsigned n=1;n<=count;++n)independent+=n<10?10:n<20?20:n<30?30:40;if(allGood)independent/=2;assert(score==independent&&combo==count&&maximum==count);if(count==395)assert(score==(allGood?7615:15230));}
    assert(visibleChecks>3);printf("PASS: %u composite framebuffer HUD checks\n",visibleChecks);
    printf("SCORE: score%u combo%u maximum%u highest%u accuracy%u FC%u AP%u session%u\n",score,combo,maximum,highest,accuracy,fc,ap,session);
    printf("IRQ: refills%u max%u mean%.1f cycles, underruns%u gate%u gain%u\n",c->busRead32(c,refilladdr),c->busRead32(c,irqmaxaddr),c->busRead32(c,refilladdr)?read64(c,irqtotaladdr)/(double)c->busRead32(c,refilladdr):0,c->busRead32(c,underrunaddr),c->busRead32(c,gateaddr),c->busRead32(c,gainaddr));
    if(isFault||inconsistent){for(unsigned i=0;i<3;++i){frame(c,0);drain(c);}visible(c,pixels,fontaddr,1,0,isFault?"AUDIO ERROR":"DATA ERROR");visible(c,pixels,fontaddr,1,16,"A / START: REPLAY");visible(c,pixels,fontaddr,1,18,"B / SELECT: MODE SELECT");screenshot(argv[6],"error-visible",pixels);}
    // Results replay uses existing A, and must reset score/clock/guitar.
    if(!isFault&&!inconsistent&&strcmp(mode,"preview")){
        const unsigned savedScore=c->busRead32(c,scoreaddr);
        if(getenv("GBA_TEST_HIDE_RESULTS"))c->busWrite16(c,0x04000000,0);
        for(unsigned i=0;i<60;++i){frame(c,0);}assert(c->busRead32(c,scoreaddr)==savedScore);
        visible(c,pixels,fontaddr,1,0,"RESULTS");visible(c,pixels,fontaddr,1,4,"SCORE");
        char value[32];snprintf(value,sizeof(value),"%u",savedScore);visible(c,pixels,fontaddr,18,4,value);
        visible(c,pixels,fontaddr,1,5,"ACCURACY");visible(c,pixels,fontaddr,1,6,"PERFECT");visible(c,pixels,fontaddr,1,7,"GOOD");
        visible(c,pixels,fontaddr,1,8,"MISS");visible(c,pixels,fontaddr,1,9,"WRONG INPUT");visible(c,pixels,fontaddr,1,10,"MAX COMBO");
        visible(c,pixels,fontaddr,1,11,"HIGHEST X");visible(c,pixels,fontaddr,1,16,"A / START: REPLAY");visible(c,pixels,fontaddr,1,18,"B / SELECT: MODE SELECT");
        for(unsigned row=6;row<=11;++row) {
            unsigned v=row==6?p:row==7?g:row==8?m:row==9?w:row==10?maximum:highest;
            snprintf(value,sizeof(value),"%u",v);visible(c,pixels,fontaddr,18,row,value);
        }
        snprintf(value,sizeof(value),"%u.%02u%%",accuracy/100,accuracy%100);visible(c,pixels,fontaddr,18,5,value);
        visible(c,pixels,fontaddr,1,13,ap?"ALL PERFECT / FULL COMBO":fc?"FULL COMBO":"SONG COMPLETE");
        screenshot(argv[6],"results-visible",pixels);puts("PASS: composed results heading, score, statistics labels and navigation instructions");
        frame(c,0);
        if(!strcmp(mode,"returnmenu")||!strcmp(mode,"returnselect")){
            frame(c,!strcmp(mode,"returnmenu")?2:4);frame(c,0);assert(c->busRead32(c,modeaddr)==0);screenshot(argv[6],"return-menu",pixels);
            frame(c,8);frame(c,0);assert(c->busRead32(c,modeaddr)==2);
        }else {frame(c,!strcmp(mode,"replaystart")?8:1);frame(c,0);}assert(c->busRead32(c,sessionaddr)==0&&c->busRead32(c,scoreaddr)==0&&c->busRead32(c,scoreaddr+4)==0&&c->busRead32(c,scoreaddr+16)==1);assert(c->busRead32(c,gateaddr)==1&&c->busRead32(c,gainaddr)==256);for(unsigned i=0;i<120;++i){frame(c,0);drain(c);}if(state==2)assert(c->busRead32(c,consaddr)>16000&&c->busRead32(c,stateaddr)==1);else assert(c->busRead32(c,stateaddr)==0);visible(c,pixels,fontaddr,0,0,"SCORE:0");screenshot(argv[6],"replay",pixels);printf("PASS: results %s action resets score, combo, multiplier, audio and guitar\n",!strcmp(mode,"returnmenu")?"B menu + Start":!strcmp(mode,"returnselect")?"Select menu + Start":!strcmp(mode,"replaystart")?"Start replay":"A replay");}
    // Rapid return/replay: exact counts start at0, timer position starts near0.
    for(unsigned repeat=0;repeat<4;++repeat){
        for(unsigned i=0;i<2;++i){frame(c,12);}frame(c,0);assert(c->busRead32(c,modeaddr)==0);
        for(unsigned i=0;i<2;++i){frame(c,128);}frame(c,0); // Original
        for(unsigned i=0;i<2;++i){frame(c,8);}frame(c,0);assert(c->busRead32(c,modeaddr)==1);
        unsigned sounding=0;for(unsigned i=0;i<90;++i){frame(c,0);short samples[4096];int n=blip_read_samples(c->getAudioChannel(c,0),samples,4096,0);for(int j=0;j<n;++j)sounding+=samples[j]!=0;blip_clear(c->getAudioChannel(c,1));}assert(sounding>100);
        for(unsigned i=0;i<2;++i){frame(c,12);}frame(c,0);
        for(unsigned i=0;i<2;++i){frame(c,128);}frame(c,0);
        for(unsigned i=0;i<2;++i){frame(c,8);}frame(c,0);assert(c->busRead32(c,modeaddr)==2);
        assert(c->busRead32(c,statsaddr)==0&&c->busRead32(c,statsaddr+8)==0);
        assert(c->busRead32(c,scoreaddr)==0&&c->busRead32(c,sessionaddr)==0);assert(c->busRead32(c,consaddr)<1500);assert(c->busRead32(c,gateaddr)==1&&c->busRead32(c,gainaddr)==256);drain(c);
    }
    printf("PASS:4rapid original/imported replay cycles, original sound, reset counters/position, no crash\n");
    c->deinit(c);mLogSetDefaultLogger(NULL);return 0;
}
