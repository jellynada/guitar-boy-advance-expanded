#ifndef PLAY_TRANSPORT_HPP
#define PLAY_TRANSPORT_HPP
#include <cstdint>

// Imported-only state/control policy. gameMode still identifies the scene.
namespace PlayTransport {
enum class Phase:uint32_t { Selector,Playing,Paused,Results,Exiting };
enum class Command:uint8_t { None,Pause,Resume,Exit };
constexpr uint16_t START=8,SELECT=4,SYSTEM=START|SELECT;
constexpr unsigned CHORD_POLLS=6; // about100ms, measured in UI polls, not song time
struct Controller {
    volatile Phase phase=Phase::Selector;
    uint16_t previous=0,windowKeys=0;
    unsigned remaining=0;
    void reset(){phase=Phase::Selector;previous=windowKeys=0;remaining=0;}
    void begin(uint16_t held){reset();phase=Phase::Playing;previous=held&SYSTEM;}
    void finish(){phase=Phase::Results;windowKeys=0;remaining=0;}
    bool apply(Command command){
        if(command==Command::Exit&&(phase==Phase::Playing||phase==Phase::Paused)){phase=Phase::Exiting;return true;}
        if(command==Command::Pause&&phase==Phase::Playing){phase=Phase::Paused;return true;}
        if(command==Command::Resume&&phase==Phase::Paused){phase=Phase::Playing;return true;}
        return false;
    }
    Command poll(uint16_t held){
        held&=SYSTEM;const uint16_t fresh=held&~previous;previous=held;
        if(phase!=Phase::Playing&&phase!=Phase::Paused)return Command::None;
        if(held==SYSTEM||(fresh&&remaining&&((windowKeys|fresh)==SYSTEM))||
           (phase==Phase::Paused&&(fresh&SELECT)))return Command::Exit;
        if(remaining){--remaining;if(!remaining)windowKeys=0;}
        if(fresh){windowKeys=fresh;remaining=CHORD_POLLS;}
        if(fresh&START)return phase==Phase::Playing?Command::Pause:Command::Resume;
        return Command::None;
    }
};
}
#endif
