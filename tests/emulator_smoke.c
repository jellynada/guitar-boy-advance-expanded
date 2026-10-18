// Optional headless smoke test. Requires mGBA development headers/library.
// Usage: emulator_smoke game.gba recent_sprite_address expected_notes frames output.ppm
#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

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
    if (argc != 6) return 2;
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
    unsigned long nonzero_samples = 0, changed_frames = 0;
    unsigned previous_hash = 0;
    for (unsigned frame = 0; frame < frames; ++frame) {
        // Exercise all four buttons, including after the final note.
        core->setKeys(core, frame % 30 == 0 ? (1u | 2u | 256u | 512u) : 0);
        core->runFrame(core);
        assert(!crashed);
        unsigned cursor = core->busRead32(core, cursor_address);
        assert(cursor <= notes);
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
    fflush(stdout);
    core->deinit(core);
    mLogSetDefaultLogger(NULL);

    return 0;
}
