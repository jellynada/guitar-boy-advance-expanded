#include "tonc.h"
#include "maxmod.h"
#include "math.h"

#include "terminal.hpp"
#include "mode7.hpp"
#include "scanline.hpp"
#include "playTransport.hpp"
#include "build_identity.hpp"
#include "noteManager.hpp"
#include "sprite.hpp"
#include "gameControls.hpp"
#include "gameSession.hpp"
#include "importedRuntime.hpp"
#include "imported_chart.hpp"
#include "importedSelection.hpp"
#include "imported_audio.hpp"
#include "pcmPlayback.hpp"
#include "scoring.hpp"
#include "scoreDisplay.hpp"
#include "sustain.hpp"
#include "sustainDisplay.hpp"
#include "importedCompletion.hpp"
#include "textDisplay.hpp"
#include "inputDiagnostic.hpp"
#include "notes.h"

#include "image.h"
#include "palette.h"
#include "soundbank.h"
#include "soundbank_bin.h"

#include "text_sprites.h"
#include "careless.h"
#include "buttons.h"

#define CONTROLS_ENABLED false

static NoteManager<careless_expertsingle_count> originalNotes(careless_expertsingle_data, careless_BPM);
NoteManager<careless_expertsingle_count>* nm = &originalNotes;
static ImportedRuntime<imported_note_count,5> importedNotes(imported_notes);
volatile u32 gameMode = 0;
u32 importedLaneCount=imported_choices[0].lanes,importedChartCount=imported_choices[0].count;
const Note* activeImportedNotes=imported_choices[0].notes;
const uint64_t* activeImportedSustains=imported_choices[0].sustains;
static unsigned difficultySelection=0;
static bool difficultyReady=false;
static NoteScore<imported_note_count> importedScoring;
EWRAM_DATA static Sustain::Holds<imported_note_count,5> importedHolds(imported_notes,imported_sustain_us);
static u64 importedLastEnd=0;
ScoreSnapshot scoreSnapshot() {
    auto s=importedScoring.snapshot();const auto& h=importedHolds.stats();
    s.holdsCompleted=h.completed;s.holdsReleased=h.released;s.holdsMissed=h.missed;s.holdsTotal=h.total;return s;
}
Sustain::State sustainState(u32 i){return importedHolds.state(i);}
uint32_t sustainActiveNote(unsigned lane){return importedHolds.active(lane);}
ScoreSnapshot displayedScore;
volatile u32 importedSessionState=ImportedCompletion::Playing;
volatile u32 importedCompletionDiagnostic=0;
static u32 completionWaitFrames=0;
static u32 feedbackUntilFrame=0;
u32 importedFirstVisible = 0, importedEndVisible = 0;
u64 importedNowCycles = 0;
u64 importedMaxErrorCycles = 0;
u32 importedEventCount = 0;
u32 importedFrameWorkMaxCycles = 0;
u64 importedFrameWorkTotalCycles = 0;
u32 importedFrameWorkCount = 0;
u32 activeNoteCount() { return gameMode == 2 ? importedChartCount : careless_expertsingle_count; }
bool activeWasHit(u32 index) { return gameMode == 2 ? importedNotes.wasHit(index) : nm->wasHit(index); }
noteSprite importedSprite(u32 index) {
    noteSprite sprite{};
    if (index >= importedChartCount) return sprite;
    const Note& note = activeImportedNotes[index];
    sprite.pal = note.lane + 1;
    sprite.pos.x = ImportedTiming::laneX(note.lane,importedLaneCount);
    sprite.pos.z = m7_level.camera->pos.z + ImportedTiming::relativeZ(int64_t(note.tick) - int64_t(importedNowCycles));
    return sprite;
}

FIXED VEL_H = CONTROLS_ENABLED ? 0x200 : careless_BPM;

s64 curr_z = 0; // Avoid signed overflow when the music keeps looping.

void input_game()
{
	const FIXED OMEGA= 0x140;
	VECTOR dir= {0, 0, 0};
	M7_CAM *cam= m7_level.camera;

	if(CONTROLS_ENABLED){
		dir.z= -VEL_H*key_tri_fire();	// B/A : back/forward
		dir.x= VEL_H*key_tri_shoulder();	// strafe

		// Change camera orientation
		m7_rotate(cam,
			cam->phi + OMEGA*key_tri_horz(),	// look left/right
			cam->theta - OMEGA*key_tri_vert());	// look up.down

		m7_translate_level(cam, &dir);
	}else{
		curr_z += VEL_H;
		//crazy equation to balance tempo and highway speed
		cam->pos.z = ((cam->u.x * (-curr_z/871)) - 640000)>>4;
	}

}

//green button 	(3, 16)
//red button 	(9, 16)
//yellow button (15, 16)
//blue button 	(21, 16)
void drawButton(int b, bool active){
	int palette = b+1;
	int start_x = gameMode == 2 ? receptorX(b,importedLaneCount) : (b*6)+3;
	int start_ind = 32*13 + start_x;
	//y
	for(int i = 0; i < 3; i++){
		int row_start = start_ind + (i*32);
		//x
		for(int j = 0; j < int(gameMode==2?receptorWidth(importedLaneCount):6); j++){
			u16 map_start = active ? buttonsMap[(i*6)+(gameMode==2&&importedLaneCount==5?j*6/5:j)] + 18 : buttonsMap[(i*6)+(gameMode==2&&importedLaneCount==5?j*6/5:j)];
			se_mem[30][row_start+j] = map_start | SE_PALBANK(palette);
		}

	}
}

void configureFloor() {
    LZ77UnCompVram(imageTiles, tile_mem[2]);
    memcpy16(&se_mem[24], imageMap, imageMapLen/2);
    if (gameMode != 2) return;
    const u8* map = reinterpret_cast<const u8*>(imageMap);
    const u8* tiles = reinterpret_cast<const u8*>(tile_mem[2]);
    const u8 edge = tiles[map[64 + 28] * 64];
    const u8 fill = tiles[map[64 + 28] * 64 + 1];
    // Existing 64-pixel-wide highway, now divided into three logical stripes.
    for (int column=0; column<8; ++column) {
        u16* tile = reinterpret_cast<u16*>(tile_mem[2]) + (6+column)*32;
        for (int y=0; y<8; ++y) for (int pair=0; pair<4; ++pair) {
            int x=column*8+pair*2;
            auto color = [edge, fill](int p) { return p == 0 || p == 63 || (importedLaneCount==3?(p==21||p==42):((p*importedLaneCount)%64<importedLaneCount)) ? edge : fill; };
            tile[y*4+pair] = color(x) | (u16(color(x+1)) << 8);
        }
    }
    u16* floor = reinterpret_cast<u16*>(&se_mem[24]);
    // Affine maps use byte tile IDs; VRAM writes must be halfword-sized.
    for (int row=0; row<64; ++row) if (row % 32) for (int pair=0; pair<4; ++pair)
        floor[row*32+14+pair] = (6+pair*2) | ((7+pair*2) << 8);
}

void drawButtons(){
	//iterate through buttons
	for(int b = 0; b < (gameMode == 2 ? importedLaneCount : 4); b++){
		drawButton(b, false);
	}
}

void updateButtons(u16 hit, u16 released){
    if(gameMode==2){const u8 held=importedLaneMaskFromButtons(key_is_down(importedGameButtons(importedLaneCount)),importedLaneCount);
        for(unsigned lane=0;lane<importedLaneCount;++lane)drawButton(lane,held&(1u<<lane));return;}
	const u16* buttons = gameMode == 2 ? importedButtons(importedLaneCount) : LANE_BUTTONS;
	for(int i = 0; i < (gameMode == 2 ? importedLaneCount : 4); i ++){
		if( buttons[i] & hit ){
			drawButton(i, true);
		}

		if( buttons[i] & released ){
			drawButton(i, false);
		}
	}
}

// The interrupt owns only the frame clock and Maxmod DMA service. All note
// judgments and presentation happen together on the main thread.
volatile u32 gameplayFrames = 0;
volatile bool gameClockRunning = false;
u32 currentGameFrame = 0;
JudgmentStats displayedStats;
textDisplay judgmentText(4, 4, 32);
textDisplay hitText(96, 4, 48);
textDisplay missText(168, 4, 64);
textDisplay wrongText(4, 22, 80);
const char* lastJudgment = "READY";
bool feedbackDirty = true;
bool wrongVisible = false;
u32 wrongUntilFrame = 0;

void onGameplayEvent(void*, const GameplayEvent& event) {
    if (gameMode == 2) {
        ++importedEventCount;
        pcmGameplayEvent(event);
        importedScoring.consume(event);
        importedHolds.event(event,importedScoring.snapshot().multiplier);
        feedbackUntilFrame=currentGameFrame+18;
        if (event.kind == GameplayEventKind::PerfectHit || event.kind == GameplayEventKind::GoodHit) {
            const u64 error = event.gameplayTick >= event.chartTick ? event.gameplayTick - event.chartTick : event.chartTick - event.gameplayTick;
            if (error > importedMaxErrorCycles) importedMaxErrorCycles = error;
        }
    }
    switch (event.kind) {
        case GameplayEventKind::PerfectHit: lastJudgment = "PERFECT"; break;
        case GameplayEventKind::GoodHit: lastJudgment = "GOOD"; break;
        case GameplayEventKind::Miss: lastJudgment = "MISS"; break;
        case GameplayEventKind::WrongInput:
            if(gameMode==2)lastJudgment="WRONG";
            wrongVisible = true;
            wrongUntilFrame = currentGameFrame + 24;
            break;
    }
    feedbackDirty = true;
}

void refreshFeedback() {
    if(gameMode==2&&feedbackUntilFrame&&currentGameFrame>=feedbackUntilFrame) {feedbackUntilFrame=0;feedbackDirty=true;}
    if (wrongVisible && currentGameFrame >= wrongUntilFrame) {
        wrongVisible = false;
        feedbackDirty = true;
    }
    if (!feedbackDirty) return;
    displayedStats = gameMode == 2 ? importedNotes.stats() : nm->judgment().stats();
    if(gameMode==2) {
        displayedScore=scoreSnapshot();
        ScoreDisplay::hud(displayedScore,feedbackUntilFrame?lastJudgment:"",
            !imported_audio_enabled?"SILENT":!imported_audio_reactive?"FIXED MIX":guitarAudible?"GUITAR ON":"GUITAR MUTED");
        feedbackDirty=false;return;
    }
    judgmentText.updateText(lastJudgment);
    hitText.updateLabel("H:", displayedStats.hits());
    missText.updateLabel("M:", displayedStats.missed);
    wrongText.updateText(wrongVisible ? "WRONG" : "");
    feedbackDirty = false;
}

void update(){
    if (gameMode == 2) pcmService();
    else if (legacyAudioReady) mmVBlank();
    if (gameMode && gameClockRunning) ++gameplayFrames;
}

extern "C" {
PlayTransport::Controller importedTransport;
volatile u32 importedPauseCount=0,importedResumeCount=0;
}

int main(){

    const M7_CAM initialCamera = m7_cam_default;
    // Init mode 7
	m7_init(&m7_level, &m7_cam_default, m7_bgaffs, m7_sprites,
		BG_CBB(2) | BG_SBB(24) | BG_AFF_64x64 | BG_WRAP | BG_PRIO(2));

    //load palette
    memcpy16(pal_bg_mem, palettePal, palettePalLen/2);

    //load tiles
    LZ77UnCompVram(imageTiles, tile_mem[2]);
    
    //load image
    memcpy16(&se_mem[24], imageMap, imageMapLen/2);

	memcpy16(&tile_mem[1], buttonsTiles, buttonsTilesLen/2);
    ScoreDisplay::preparePauseFont();
	drawButtons();

	if(ENABLED){
		memset16(&se_mem[31], 0x0001, 32*32);
		memset16(&tile_mem[0][1], 0x6666, 16);
		memset16(&tile_mem[1][0x4F], 0x6666, 16);
		memset16(&se_mem[30], 0x004F, 32*3);
		REG_BLDCNT= BLD_BUILD(BLD_BG1, BLD_OBJ | BLD_BG2, 1);
	}
	

	REG_BG0CNT = BG_BUILD(1, 30, 0, 0, 0, 0, 0);
	
    //enable Text BG
    REG_BG1CNT = ENABLED ? BG_BUILD(0, 31, 0, 0, 0, 0, 0) : Terminal::setCNT(1, 0, 31);
    REG_DISPCNT = DCNT_BG0 | DCNT_BG1 | DCNT_BG2 | DCNT_OBJ | DCNT_OBJ_1D | DCNT_MODE1;

	memcpy16(pal_obj_mem, palettePal, palettePalLen/2);
    for(unsigned i=0;i<16;++i){
        const unsigned c=palettePal[4*16+i],r=c&31,g=(c>>5)&31,b=(c>>10)&31;
        const unsigned level=r>g?(r>b?r:b):(g>b?g:b);
        pal_bg_mem[5*16+i]=pal_obj_mem[5*16+i]=i?RGB15(level,level/2,0):c;
    }
	memcpy16(tile_mem_obj, notesTiles, notesTilesLen/2);
	memcpy16(&tile_mem_obj[1], text_spritesTiles, text_spritesTilesLen/2);

	oam_init(obj_mem, 128);
	init_sprites();
    // Initialize Interrupts
    irq_init(nullptr);
	nm->reset();
	nm->judgment().setEventSink(onGameplayEvent);
	refreshFeedback();

	// Initialise audio before any VBlank handler can call mmVBlank().
	legacyAudioInit();

	// Maxmod requires the vblank interrupt to reset sound DMA. 
	irq_set( II_VBLANK, update, 0);
    irq_add(II_HBLANK, (fnptr)m7_hbl_floor);
	irq_enable(II_VBLANK);

	// initialise maxmod with soundbank and 8 channels
    // Initialised above, before interrupts are enabled.
    
    //Setup is done. Lets put it into action!
    //Terminal::log("Hello World! %%", careless_expertsingle_data[0].tick);
    // Audio starts after a mode is chosen.
    textDisplay menuTitle(28, 28, 16, true, 24);
    textDisplay menuOriginal(16, 58, 48);
    textDisplay menuImported(16, 82, 64, true, 24);
    textDisplay menuDiagnostic(16, 106, 88, true, 24);
    textDisplay menuHelp(16, 128, 112, true, 16);
    textDisplay menuInfo(16, 146, 0);
    textDisplay modeLabel(4, 40, 96);
    int selection = 1;
    bool menuDirty = true;
    bool selectorControlsArmed = true;

    while(1){
        // Poll first: judge the newly observed input, not last frame's keys.
        key_poll();
        if(gameMode==4){
            if(!selectorControlsArmed){if(key_is_down(KEY_A|KEY_START|KEY_SELECT|KEY_B)){vid_vsync();continue;}selectorControlsArmed=true;}
            if(key_hit(KEY_B|KEY_SELECT)){gameMode=0;difficultyReady=false;menuDirty=true;selectorControlsArmed=false;vid_vsync();continue;}
            if(key_hit(KEY_DOWN)){difficultySelection=(difficultySelection+1)%imported_choice_count;menuDirty=true;}
            if(key_hit(KEY_UP)){difficultySelection=(difficultySelection+imported_choice_count-1)%imported_choice_count;menuDirty=true;}
            if(menuDirty){
                menuTitle.updateText("DIFFICULTY");menuInfo.updateText(imported_title);
                menuOriginal.updateText(imported_choice_count>0?(difficultySelection==0?">":" "):"");
                menuImported.updateText("");menuDiagnostic.updateText("");
                textDisplay* rows[]={&menuOriginal,&menuImported,&menuDiagnostic};
                for(unsigned i=0;i<imported_choice_count;++i){char label[16];unsigned j=0;label[j++]=i==difficultySelection?'>':' ';const char* name=imported_choices[i].difficulty;while(*name&&j<15)label[j++]=*name++;label[j]=0;rows[i]->updateText(label);}
                menuHelp.updateText("A:Choose B:Back");menuDirty=false;
            }
            if(!key_hit(KEY_A|KEY_START)){vid_vsync();continue;}
            const auto& chosen=imported_choices[difficultySelection];
            importedLaneCount=chosen.lanes;importedChartCount=chosen.count;activeImportedNotes=chosen.notes;activeImportedSustains=chosen.sustains;
            difficultyReady=true;gameMode=0;selection=2;
        }
        const auto systemCommand=gameMode==2&&importedSessionState==ImportedCompletion::Playing
            ?importedTransport.poll(key_is_down(KEY_START|KEY_SELECT)):PlayTransport::Command::None;
        const bool oldExitChord=gameMode&&(gameMode!=2||importedSessionState!=ImportedCompletion::Playing)&&
            key_is_down(KEY_START|KEY_SELECT)==(KEY_START|KEY_SELECT);
        if (oldExitChord||systemCommand==PlayTransport::Command::Exit) {
            importedTransport.apply(PlayTransport::Command::Exit);
            importedTransport.reset();
            selectorControlsArmed=false; // Require release after exit before another start.
            Scanline::stop();
            mmStop();
            pcmStop();
            importedSessionState=ImportedCompletion::Playing;
            irq_enable(II_HBLANK);
            ScoreDisplay::clear();
            gameClockRunning = false;
            gameMode = 0;difficultyReady=false;
            menuDirty = true;
            oam_init(oam_mem, 128);
            vid_vsync(); continue; // Return chord must not also confirm the selector.
        }
        if(gameMode==2&&importedTransport.phase==PlayTransport::Phase::Paused) {
            if(systemCommand!=PlayTransport::Command::Resume){vid_vsync();Scanline::vblank();continue;}
            // UI changes are made in VBlank while audio/time are still frozen.
            vid_vsync();Scanline::vblank();ScoreDisplay::pauseHide();
            const u8 held=importedLaneMaskFromButtons(key_is_down(importedGameButtons(importedLaneCount)),importedLaneCount);
            importedNotes.judgment().seedInput(held);
            importedHolds.resumeInput(importedNowCycles,held);
            for(unsigned lane=0;lane<importedLaneCount;++lane)drawButton(lane,held&(1u<<lane));
            const bool resumed=!imported_audio_enabled||pcmResume();
            importedTransport.apply(PlayTransport::Command::Resume);
            ++importedResumeCount;gameClockRunning=resumed;feedbackDirty=true;
        }
        if(gameMode==2&&importedSessionState!=ImportedCompletion::Playing) {
            if(key_hit(KEY_B|KEY_SELECT)) {
                Scanline::stop();pcmStop();importedTransport.reset();gameMode=0;difficultyReady=false;gameClockRunning=false;menuDirty=true;
                importedSessionState=ImportedCompletion::Playing;irq_enable(II_HBLANK);
                oam_init(oam_mem,128);ScoreDisplay::clear();
            } else if(key_hit(KEY_A|KEY_START)) {
                Scanline::stop();pcmStop();gameMode=0;selection=2; // reuse the existing fresh-mode initialization below
            } else {vid_vsync();continue;}
        }
        if(gameMode==3) {
            if(InputDiagnostic::finished()) {
                if(key_hit(KEY_B|KEY_SELECT)){gameMode=0;menuDirty=true;gameClockRunning=false;irq_enable(II_HBLANK);oam_init(oam_mem,128);ScoreDisplay::clear();}
                else if(key_hit(KEY_A|KEY_START)){gameplayFrames=0;InputDiagnostic::start(easyLaneMaskFromButtons(key_is_down(EASY_GAME_BUTTONS)));}
            }
            if(gameMode==3){vid_vsync();InputDiagnostic::update(gameplayFrames,easyLaneMaskFromButtons(key_is_down(EASY_GAME_BUTTONS)));continue;}
        }
        if (!gameMode) {
            if (key_hit(KEY_DOWN)) { selection=selection%3+1;menuDirty=true; }
            if (key_hit(KEY_UP)) { selection=(selection+1)%3+1;menuDirty=true; }
            if (menuDirty) {
                REG_DISPCNT = DCNT_OBJ | DCNT_OBJ_1D | DCNT_MODE1;
                menuTitle.updateText(GBA_BUILD_TITLE);
                menuOriginal.updateText(selection == 1 ? ">Original Demo" : " Original Demo");
                menuImported.updateText(selection == 2 ? ">Custom song" : " Custom song");
                menuDiagnostic.updateText(selection == 3 ? ">INPUT / CHORD TEST" : " INPUT / CHORD TEST");
                menuHelp.updateText("Up/Down A:Start");
                menuInfo.updateText(imported_audio_enabled ? imported_is_synthetic ? "SYNTH / AUDIO" : "LOCAL / AUDIO" : "SILENT FALLBACK");
                pal_bg_mem[0] = 0;
                menuDirty = false;
            }
            if(!selectorControlsArmed){
                if(key_is_down(KEY_START|KEY_SELECT|KEY_A)){vid_vsync();continue;}
                selectorControlsArmed=true;
            }
            if (!key_hit(KEY_A | KEY_START)) { vid_vsync(); continue; }
            if(selection==2&&!difficultyReady){gameMode=4;menuDirty=true;selectorControlsArmed=false;vid_vsync();continue;}
            Scanline::stop();
            // Fresh mode epoch: counters, camera, visuals and held-key history.
            const u16 interrupts = REG_IME;
            REG_IME = 0;
            gameClockRunning = false;
            gameplayFrames = 0;
            gameMode = selection;
            if(gameMode==2)importedTransport.begin(key_is_down(KEY_START|KEY_SELECT));else importedTransport.reset();
            importedPauseCount=importedResumeCount=0;
            REG_IME = interrupts;
            currentGameFrame = 0;
            curr_z = 0;
            m7_cam_default = initialCamera;
            m7_rotate(&m7_cam_default, initialCamera.phi, initialCamera.theta);
            importedNowCycles = importedMaxErrorCycles = 0;
            importedEventCount = 0;
            importedScoring.reset(importedChartCount);
            importedHolds.configure(activeImportedNotes,activeImportedSustains,importedChartCount);
            importedNotes.configure(activeImportedNotes,importedChartCount);
            importedLastEnd=0;for(u32 i=0;i<importedChartCount;++i)if(importedHolds.end(i)>importedLastEnd)importedLastEnd=importedHolds.end(i);
            displayedScore=scoreSnapshot();
            importedSessionState=ImportedCompletion::Playing;feedbackUntilFrame=0;
            importedCompletionDiagnostic=completionWaitFrames=0;
            importedFrameWorkMaxCycles = importedFrameWorkCount = 0;
            importedFrameWorkTotalCycles = 0;
            importedFirstVisible = importedEndVisible = 0;
            nm->reset(laneMaskFromButtons(key_is_down(GAME_BUTTONS)));
            importedNotes.reset(importedLaneMaskFromButtons(key_is_down(importedGameButtons(importedLaneCount)),importedLaneCount));
            importedNotes.judgment().setEventSink(onGameplayEvent);
            lastJudgment = "READY";
            displayedStats = {};
            wrongVisible = false;
            wrongUntilFrame = 0;
            feedbackDirty = true;
            recent_sprite = 0;
            first_sprite = SPR_COUNT;
            oam_init(oam_mem, 128);
            init_sprites();
            memset16(&se_mem[30][32*13], 0, 32*3);
            pal_bg_mem[0] = palettePal[0];
            configureFloor();
            drawButtons();
            REG_DISPCNT = DCNT_BG0 | DCNT_BG1 | DCNT_BG2 | DCNT_OBJ | DCNT_OBJ_1D | DCNT_MODE1;
            irq_enable(II_HBLANK);
            REG_BLDCNT=BLD_BUILD(BLD_BG1,BLD_OBJ|BLD_BG2,1);
            if(gameMode==2){ScoreDisplay::initialize();SustainDisplay::initialize();}else {ScoreDisplay::clear();REG_BG1CNT=BG_BUILD(0,31,0,0,0,0,0);}
            if(gameMode==2){
                m7_level.camera->pos.z=ImportedTiming::floorZ(0);
                m7_prep_horizon(&m7_level);m7_prep_affines(&m7_level);Scanline::start();
            }
            if (gameMode == 1) { legacyAudioInit(); mmStart(MOD_CARELESS_WHISPER, MM_PLAY_LOOP); }
            else if(gameMode==2) { mmStop(); pcmStart(); }
            else {mmStop();pcmStop();irq_disable(II_HBLANK);InputDiagnostic::start(easyLaneMaskFromButtons(key_is_down(EASY_GAME_BUTTONS)));}
            const u16 startIrq = REG_IME; REG_IME=0;
            gameplayFrames=0; gameClockRunning=true;
            REG_IME=startIrq;
            REG_TM3CNT=0; REG_TM3D=0; REG_TM3CNT=TM_ENABLE|1; // profile at64CPUcycles/tick
            modeLabel.updateText("");
            if(gameMode==3){vid_vsync();continue;}
        }
        bool pauseNow=false;
        if(gameMode==2&&systemCommand==PlayTransport::Command::Pause){
            const bool beforeSilentEnd=ImportedTiming::frameTick(gameplayFrames)<ImportedCompletion::silentEnd(importedLastEnd,importedChartCount!=0);
            if(imported_audio_enabled?pcmPause():beforeSilentEnd){gameClockRunning=false;pauseNow=true;}
        }
        currentGameFrame = gameplayFrames; // Aligned 32-bit read is atomic on GBA.
        const u16 workStart = REG_TM3D;
        const u16 mask = gameMode == 2 ? importedGameButtons(importedLaneCount) : GAME_BUTTONS;
        if (gameMode == 2) {
            if (imported_audio_enabled) {
                const u64 sampleTick=pcmSnapshotTick();
                if (audioState!=PcmClock::Fault) {
                    const u32 bonus=importedHolds.update(sampleTick,importedLaneMaskFromButtons(key_is_down(mask),importedLaneCount));
                    importedScoring.addSustainBonus(bonus);if(bonus)feedbackDirty=true;
                    importedNotes.updateTick(sampleTick, importedLaneMaskFromButtons(key_is_down(mask),importedLaneCount));
                }
            }
            else {
                importedScoring.addSustainBonus(importedHolds.update(ImportedTiming::frameTick(currentGameFrame),importedLaneMaskFromButtons(key_is_down(mask),importedLaneCount)));
                importedNotes.update(currentGameFrame,importedLaneMaskFromButtons(key_is_down(mask),importedLaneCount));feedbackDirty=true;
            }

            importedNowCycles = importedNotes.now();
            importedFirstVisible = importedNotes.firstVisible();
            importedEndVisible = importedNotes.endVisible();
            recent_sprite = importedEndVisible;
            if(!pauseNow){
            const u64 silentDeadline=ImportedCompletion::silentEnd(importedLastEnd,importedChartCount!=0);
            const u32 completionAudioState=audioState;
            const u64 finalAudioTick=PcmClock::tick(audioSamplesConsumed);
            importedSessionState=ImportedCompletion::boundedPoll(imported_audio_enabled,completionAudioState,importedNowCycles,silentDeadline,
                importedScoring.resolved()&&importedHolds.resolved()&&importedScoring.coherent(importedNotes.stats()),finalAudioTick,completionWaitFrames);
            if(imported_audio_enabled&&completionAudioState==PcmClock::Ended) {
                if(completionWaitFrames) {
                    importedCompletionDiagnostic=1; // stale final-clock snapshot
                } else if(importedSessionState==ImportedCompletion::Inconsistent) {
                    importedCompletionDiagnostic=importedScoring.resolved()&&importedHolds.resolved()?3:2;
                } else importedCompletionDiagnostic=0;
            }
            if(importedSessionState!=ImportedCompletion::Playing) {
                if(importedSessionState==ImportedCompletion::Complete)importedScoring.finalize();
                else if(importedSessionState==ImportedCompletion::Inconsistent)pcmStop();
                displayedStats=importedNotes.stats();displayedScore=scoreSnapshot();
                importedTransport.finish();
                gameClockRunning=false;Scanline::stop();irq_disable(II_HBLANK);oam_init(oam_mem,128);
                pal_bg_mem[0]=0;REG_BLDCNT=0;REG_DISPCNT=DCNT_BG1|DCNT_MODE0;
                ScoreDisplay::results(displayedScore,imported_title,importedSessionState,importedCompletionDiagnostic);
                vid_vsync();continue;
            }
            } // No end-of-song transition during a successful freeze.
        } else {
            recent_sprite = nm->update(currentGameFrame, laneMaskFromButtons(key_is_down(mask)));
        }
        updateButtons(key_hit(mask), key_released(mask));
        refreshFeedback();

        if (gameMode == 1) input_game();
        else {
            // Background wraps by one full texture; note coordinates stay local.
            m7_level.camera->pos.z = ImportedTiming::floorZ(importedNowCycles);
        }

        m7_prep_horizon(&m7_level);
		m7_update_sky(&m7_level);

		update_sprites();
        if(gameMode==2)SustainDisplay::draw(importedNowCycles);
		m7_prep_affines(&m7_level);
        if(gameMode==2)Scanline::prepare();

		//if(key_hit(KEY_START)) Terminal::log("Tick = %%", m7_level.camera->pos.z);

        //update song
        if (gameMode != 2) mmFrame();

        //update random nunmber
        qran();

        if (gameMode == 2) {
            const u32 cycles = u16(REG_TM3D-workStart)*64u;
            importedFrameWorkTotalCycles += cycles; ++importedFrameWorkCount;
            if (cycles > importedFrameWorkMaxCycles) importedFrameWorkMaxCycles=cycles;
        }
        // Poll the VBlank edge: do not rely on a callback that can lose an
        // interrupt simultaneous with the audio IRQ in Tonc's master handler.
        vid_vsync();
        Scanline::vblank();
        if(pauseNow){
            ScoreDisplay::pauseShow();
            importedTransport.apply(PlayTransport::Command::Pause);++importedPauseCount;
        }
    }
}