"""Mission021 host-input adapters. Engine assertions/thresholds stay unchanged.
Only menu travel and UI-owned paused A/B stimuli differ from the frozen probes.
"""
from pathlib import Path
HELPERS=r'''
static unsigned m021Ui(struct mCore*c,const char*sy){FILE*f=fopen(sy,"r");assert(f);char line[256],n[180],t;unsigned a;while(fgets(line,sizeof line,f))if(sscanf(line,"%x %c %179s",&a,&t,n)==3&&!strcmp(n,"uiScreen")){fclose(f);return c->busRead32(c,a);}abort();}
static void m021Frame(struct mCore*c,unsigned key){c->setKeys(c,key);c->runFrame(c);short b[4096];for(int i=0;i<2;i++)while(blip_read_samples(c->getAudioChannel(c,i),b,4096,0)>0){}}
static void m021Press(struct mCore*c,unsigned key){m021Frame(c,0);m021Frame(c,key);m021Frame(c,0);}
static void m021Songs(struct mCore*c,const char*sy){for(unsigned attempts=0;m021Ui(c,sy)!=2;attempts++){assert(attempts<8);switch(m021Ui(c,sy)){case 0:m021Press(c,8);break;case 1:m021Press(c,1);break;case 3:case 7:case 8:m021Press(c,2);break;default:abort();}}}
static void m021Difficulty(struct mCore*c,const char*sy){m021Songs(c,sy);m021Press(c,1);assert(m021Ui(c,sy)==3);}
static void m021Original(struct mCore*c,const char*sy){m021Songs(c,sy);m021Press(c,2);m021Press(c,128);m021Press(c,1);assert(m021Ui(c,sy)==7);m021Press(c,4);for(unsigned n=0;m021Ui(c,sy)!=10;++n){assert(n<60);m021Frame(c,0);}}
'''
def inject(source):
 i=source.index('int main(');return source[:i]+HELPERS+'\n'+source[i:]
def replace(s,old,new):
 if s.count(old)!=1:raise ValueError('Upstream observer changed; review adapter anchor: '+old[:70])
 return s.replace(old,new)
def generate(root,output):
 root,output=Path(root),Path(output);output.mkdir(parents=True,exist_ok=True)
 s=(root/'tests/pause_emulator.c').read_text();s=replace(s,'step(c,128);step(c,0);step(c,8);step(c,0);','m021Difficulty(c,sy);')
 # A/B now act on a pause menu. During freeze, carry entry keys instead of
 # issuing fresh confirmation/cancel presses. Post-resume physical variants and
 # every frozen counter/image/timer assertion are retained.
 s=replace(s,'unsigned held=test==5?2:test==6?1:test==7?3:test==8?0:test==9?32:keys;','unsigned held=keys; /* M021: no fresh menu confirmation during freeze */')
 (output/'pause.c').write_text(inject(s))
 stress=s.replace('cycles=test==19?0:test==12?8:1','cycles=(test==19||test==22||test==23||test==28)?0:test==12?8:1')
 stress=stress.replace('if(test!=4){keys|=buttons[l];','if(test!=4&&test!=23&&((test!=22&&test!=28)||next%3!=1)){keys|=buttons[l];')
 stress=replace(stress,'  int trigger=','  if(test==22&&frame>10&&frame%30==0){keys=0;for(unsigned lane=0;lane<lanes;++lane)keys|=buttons[lane];}\n  if(test==23&&frame==30)keys=1;\n  if(test==28&&frame>10&&frame%30==0){keys=lanes==3?35:lanes==4?(frame%60?35:19):(frame%60?35:82);}\n  if(test==28){assert((keys&48)!=48);if((keys&192)!=0)keys=(keys&~192)|(frame%2?64:128);}\n  int trigger=')
 stress=replace(stress,'if(test!=4){assert(c->busRead32(c,displayedStats)+','if(test==23){assert(c->busRead32(c,displayedStats+8)==count&&c->busRead32(c,displayedStats+12)==1);}\nif(test!=4&&test!=22&&test!=23&&test!=28){assert(c->busRead32(c,displayedStats)+')
 stress=stress.replace('unsigned alias[]={64,192,128};','unsigned alias[]={64,test==28?128u:192u,test==28?64u:128u};')
 (output/'stress.c').write_text(inject(stress))
 s=(root/'tests/readiness_emulator.c').read_text();s=replace(s,'assert(c->busRead32(c,ready)==0);press(c,128);','assert(c->busRead32(c,ready)==0);m021Songs(c,argv[2]);');(output/'readiness.c').write_text(inject(s))
 s=(root/'tests/demo_timing_emulator.c').read_text();s=replace(s,'if(!original){frame(c,0);}','if(!original){m021Songs(c,syms);}else{m021Original(c,syms);}')
 (output/'timing.c').write_text(inject(s))
 s=(root/'tests/physical_emulator.c').read_text();s=replace(s,'frame(c,128);frame(c,0);frame(c,8);','m021Difficulty(c,argv[2]);frame(c,8);');s=replace(s,'frame(c,64);frame(c,0);frame(c,8);','m021Original(c,argv[2]);');(output/'physical.c').write_text(inject(s))
 s=(root/'tests/pause_trace_emulator.c').read_text();s=replace(s,' step(c,8);step(c,0);',' m021Difficulty(c,sy);');(output/'pause-trace.c').write_text(inject(s))
 s=(root/'tests/audio_emulator.c').read_text();s=replace(s,'while(firstHold<count&&!read64(c,lengthsaddr+firstHold*8))++firstHold;','')
 s=replace(s,'if(f==2)selectDefaultDifficulty(c,modeaddr);','if(f==2){selectDefaultDifficulty(c,modeaddr);chartaddr=c->busRead32(c,address(syms,"activeImportedNotes"));lengthsaddr=c->busRead32(c,address(syms,"activeImportedSustains"));while(firstHold<count&&!read64(c,lengthsaddr+firstHold*8))++firstHold;}')
 s=replace(s,'for(unsigned i=0;i<2;++i){frame(c,128);drain(c);}frame(c,0);drain(c);','m021Songs(c,syms);')
 start=s.index('    if(isFault||inconsistent){for(unsigned i=0;i<3;')
 end=s.index('    // Results replay',start)
 s=s[:start]+"    if(isFault||inconsistent){for(unsigned i=0;i<3;++i){frame(c,0);drain(c);}visible(c,pixels,fontaddr,5,0,\"SESSION INTERRUPTED\");screenshot(argv[6],\"error-visible\",pixels); }\n"+s[end:]
 start=s.index('        visible(c,pixels,fontaddr,1,0,"RESULTS");')
 end=s.index('        screenshot(argv[6],"results-visible"',start)
 s=s[:start]+"        visible(c,pixels,fontaddr,8,0,\"SONG COMPLETE!\");visible(c,pixels,fontaddr,1,5,\"SCORE:\");char value[32];snprintf(value,sizeof value,\"%u\",savedScore);visible(c,pixels,fontaddr,19,5,value);visible(c,pixels,fontaddr,3,12,\"RETRY\");visible(c,pixels,fontaddr,3,14,\"CHANGE DIFFICULTY\");visible(c,pixels,fontaddr,3,16,\"SONG SELECT\");visible(c,pixels,fontaddr,3,18,\"MAIN MENU\");\n"+s[end:]
 start=s.index('            frame(c,!strcmp(mode,"returnmenu")?2:4);')
 end=s.index('        }else {frame(c,',start)
 s=s[:start]+"            m021Press(c,2);m021Difficulty(c,syms);m021Press(c,1);assert(c->busRead32(c,modeaddr)==2);\n"+s[end:]
 s=replace(s,'for(unsigned i=0;i<2;++i){frame(c,64);}frame(c,0); // Up: Original, without entering diagnostics\n        for(unsigned i=0;i<2;++i){frame(c,8);}frame(c,0);','m021Original(c,syms);')
 s=replace(s,'for(unsigned i=0;i<2;++i){frame(c,128);}frame(c,0);\n        for(unsigned i=0;i<2;++i){frame(c,8);}frame(c,0);selectDefaultDifficulty(c,modeaddr);','m021Difficulty(c,syms);m021Press(c,1);')
 s=replace(s,'for(unsigned i=0;i<2;++i){frame(c,12);}frame(c,0);assert(c->busRead32(c,modeaddr)==0);','if(m021Ui(c,syms)==6){m021Press(c,2);}else{for(unsigned i=0;i<2;++i){frame(c,12);}frame(c,0);}assert(c->busRead32(c,modeaddr)==0);')
 (output/'audio.c').write_text(inject(s))
 return output
if __name__=='__main__':
 import sys;generate(Path(__file__).resolve().parents[1],sys.argv[1])
