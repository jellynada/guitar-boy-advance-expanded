// Optional headless smoke test. Requires mGBA development headers/library.
// Legacy smoke: game.gba cursor_address notes frames output.ppm
// Judgment run: same arguments, then mode(miss/perfect/mixed), frame_address,
// stats_address, chart_address, ticks_per_frame. Addresses come from matching ELF.
#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void log_message(struct mLogger* logger, int category, enum mLogLevel level,
                        const char* format, va_list args) {
    (void)logger; (void)category;
    if (level & (mLOG_FATAL | mLOG_ERROR | mLOG_WARN)) {
        vfprintf(stderr, format, args);
        fputc('\n', stderr);
    }
}
static int crashed;
static void on_crash(void* context) { (void)context; crashed = 1; }
int main(int argc, char** argv) {
    if (argc != 6 && argc != 11 && argc != 12) return 2;
    struct mLogger logger = {.log = log_message};
    mLogSetDefaultLogger(&logger);
    struct mCore* core = mCoreFind(argv[1]);
    assert(core && core->init(core));
    mCoreInitConfig(core, NULL);
    color_t pixels[240 * 160] = {0};
    core->setVideoBuffer(core, pixels, 240);
    core->setAudioBufferSize(core, 4096);
    blip_set_rates(core->getAudioChannel(core, 0), core->frequency(core), 32768);
    blip_set_rates(core->getAudioChannel(core, 1), core->frequency(core), 32768);
    struct mCoreCallbacks callbacks = {.coreCrashed = on_crash};
    core->addCoreCallbacks(core, &callbacks);
    assert(mCoreLoadFile(core, argv[1]));
    core->reset(core);
    unsigned cursor_address = strtoul(argv[2], NULL, 16);
    unsigned notes = strtoul(argv[3], NULL, 10);
    unsigned frames = strtoul(argv[4], NULL, 10);
    const char* mode = argc >= 11 ? argv[6] : "smoke";
    unsigned clock_address = argc >= 11 ? strtoul(argv[7], NULL, 16) : 0;
    unsigned stats_address = argc >= 11 ? strtoul(argv[8], NULL, 16) : 0;
    unsigned chart_address = argc >= 11 ? strtoul(argv[9], NULL, 16) : 0;
    unsigned bpm = argc >= 11 ? strtoul(argv[10], NULL, 10) : 0;
    assert(!strcmp(mode, "smoke") || !strcmp(mode, "miss") || !strcmp(mode, "perfect") || !strcmp(mode, "mixed"));
    const unsigned buttons[] = {32, 16, 1, 2}; // Left, Right, A, B.
    if (argc == 12) {
        unsigned mode_address = strtoul(argv[11], NULL, 16);
        for (unsigned i=0; i<90; ++i) core->runFrame(core);
        assert(core->busRead32(core, mode_address) == 0);
        core->setKeys(core, 8); // Start: Original Demo, default selection.
        for (unsigned i=0; i<2; ++i) core->runFrame(core);
        core->setKeys(core, 0);
        core->runFrame(core);
        assert(core->busRead32(core, mode_address) == 1);
    }
    unsigned next_note = 0;
    unsigned long nonzero_samples = 0, changed_frames = 0, hit_tile_frames = 0;
    unsigned previous_hash = 0;
    for (unsigned frame = 0; frame < frames; ++frame) {
        unsigned held = 0;
        if (!strcmp(mode, "smoke") || !strcmp(mode, "mixed")) {
            // Include wrong presses before/after the song. The opposing D-pad
            // directions can be injected by the core even though real hardware
            // normally cannot press both; the demo chart contains no chords.
            if (frame % 30 == 0) held = 32u | 16u | 1u | 2u;
        } else if (!strcmp(mode, "perfect")) {
            uint64_t tick = (uint64_t)core->busRead32(core, clock_address) * bpm;
            while (next_note < notes) {
                unsigned address = chart_address + next_note * 16;
                uint64_t target = core->busRead32(core, address) |
                    ((uint64_t)core->busRead32(core, address + 4) << 32);
                if (target > tick + bpm) break;
                unsigned lane = core->busRead32(core, address + 8);
                assert(lane < 4);
                held |= buttons[lane];
                ++next_note;
            }
        }
        core->setKeys(core, held);
        core->runFrame(core);
        assert(!crashed);
        unsigned cursor = core->busRead32(core, cursor_address);
        assert(cursor <= notes);
        if (argc >= 11) {
            unsigned perfect = core->busRead32(core, stats_address);
            unsigned good = core->busRead32(core, stats_address + 4);
            unsigned missed = core->busRead32(core, stats_address + 8);
            assert(perfect + good + missed <= notes);
        }
        // Verify actual GBA OAM receives the existing hit tile (65), not only
        // the counter/HUD. Only the first 32 OAM entries belong to note sprites.
        for (unsigned sprite = 0; sprite < 32; ++sprite) {
            if ((core->busRead16(core, 0x07000000 + sprite * 8 + 4) & 0x03ff) == 65 &&
                (core->busRead16(core, 0x07000000 + sprite * 8) & 0x0300) != 0x0200) {
                ++hit_tile_frames;
                break;
            }
        }
        unsigned hash = 2166136261u;
        for (unsigned i = 0; i < 240 * 160; ++i) hash = (hash ^ pixels[i]) * 16777619u;
        if (hash != previous_hash) ++changed_frames;
        previous_hash = hash;
        for (int channel = 0; channel < 2; ++channel) {
            short samples[4096];
            int count = blip_read_samples(core->getAudioChannel(core, channel), samples, 4096, 0);
            for (int i = 0; i < count; ++i) nonzero_samples += samples[i] != 0;
        }
        if (frame == 1000) {
            FILE* image = fopen(argv[5], "wb");
            assert(image);
            fprintf(image, "P6\n240 160\n255\n");
            for (unsigned i = 0; i < 240 * 160; ++i) {
                unsigned char rgb[] = {pixels[i] & 255, (pixels[i] >> 8) & 255, (pixels[i] >> 16) & 255};
                fwrite(rgb, 1, 3, image);
            }
            fclose(image);
        }
    }
    assert(core->busRead32(core, cursor_address) == notes);
    assert(changed_frames > 100 && nonzero_samples > 1000);
    printf("PASS: %u frames, final cursor %u, %lu changing frames, %lu nonzero audio samples, no core crash\n",
           frames, notes, changed_frames, nonzero_samples);
    if (argc >= 11) {
        unsigned perfect = core->busRead32(core, stats_address);
        unsigned good = core->busRead32(core, stats_address + 4);
        unsigned missed = core->busRead32(core, stats_address + 8);
        unsigned wrong = core->busRead32(core, stats_address + 12);
        assert(perfect + good + missed == notes);
        if (!strcmp(mode, "miss")) assert(missed == notes && wrong == 0);
        if (!strcmp(mode, "perfect")) {
            assert(perfect == notes && good == 0 && missed == 0 && wrong == 0);
            assert(hit_tile_frames > 100);
        }
        if (!strcmp(mode, "miss")) assert(hit_tile_frames == 0);
        if (!strcmp(mode, "mixed")) assert(wrong > 0);
        printf("PASS: mode %s, Perfect %u, Good %u, Miss %u, WrongInput %u; every note counted once\n",
               mode, perfect, good, missed, wrong);
        printf("PASS: visible hit-tile feedback present for %lu frames\n", hit_tile_frames);
    }
    fflush(stdout);
    core->deinit(core);
    mLogSetDefaultLogger(NULL);

    return 0;
}
