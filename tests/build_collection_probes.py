"""Reuse inherited assertions, changing only explicit song menu travel.
Observer-only aliases preserve old probe symbol names; active chart pointers are
still read from the running candidate after selection.
"""
from pathlib import Path
from build_ui_probes import generate as generate_ui
WRAPPER=r'''
static unsigned collectionSymbol(const char*sy,const char*name){FILE*f=fopen(sy,"r");assert(f);char line[256],n[180],t;unsigned a;while(fgets(line,sizeof line,f))if(sscanf(line,"%x %c %179s",&a,&t,n)==3&&!strcmp(n,name)){fclose(f);return a;}abort();}
static void m021Songs(struct mCore*c,const char*sy){
 m021SongsBase(c,sy);
 unsigned wanted=getenv("GBA_SONG")?atoi(getenv("GBA_SONG")):0,cur=collectionSymbol(sy,"uiCursor");
 for(unsigned n=0;c->busRead32(c,cur)!=wanted;++n){assert(n<32);m021Press(c,128);}
}
'''
def generate(root,out):
 out=generate_ui(root,out)
 for p in out.glob('*.c'):
  s=p.read_text().replace('static void m021Songs(','static void m021SongsBase(',1)
  at=s.index('static void m021Difficulty(');s=s[:at]+WRAPPER+s[at:]
  wait='for(unsigned init=0;!c->busRead32(c,collectionSymbol(sy,"importedReady"));++init){assert(init<16);m021Frame(c,0);}'
  if p.name in ['pause.c','stress.c']:
   old='step(c,1);step(c,0);assert(c->busRead32(c,gameMode)==2);'
   assert old in s
   s=s.replace(old,'step(c,1);step(c,0);'+wait+'assert(c->busRead32(c,gameMode)==2);')
  if p.name=='timing.c':
   old='selectDefaultDifficulty(c,mode);chart='
   assert old in s
   s=s.replace(old,'selectDefaultDifficulty(c,mode);'+wait.replace('collectionSymbol(sy,','collectionSymbol(syms,')+'chart=')
  p.write_text(s)
 return out
