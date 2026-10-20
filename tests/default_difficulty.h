// Called only at a known fresh custom-song menu entry, never on a song clock.
static void selectDefaultDifficulty(struct mCore* c,unsigned mode){
    if(c->busRead32(c,mode)!=4)return;
    c->setKeys(c,0);c->runFrame(c);c->setKeys(c,1);c->runFrame(c);c->setKeys(c,0);c->runFrame(c);
}
