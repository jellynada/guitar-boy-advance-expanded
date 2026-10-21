# Mission 019 resource and hardware risk register

All new numeric timing/stack observations below are from emulation or ELF
analysis. They are not physical GBA safety-margin measurements.

| Area | Evidence / current bound | Remaining risk and acceptance |
|---|---|---|
| Public cartridge |2,643,632 bytes; valid header; limit33,554,432|Real flash-cartridge loading/compatibility on RC2 pending |
| Static IWRAM |8308 bytes:1888 code,6196 BSS,200 data,16 init,8 fini|Compiler/linker layout bound; other runtime stack paths not exhaustively proven |
| Static EWRAM |7016 bytes; linker heap begins0x02001B68|Game has fixed arrays and no explicit per-frame/transition heap calls; no newly introduced allocation |
| Main stack |Three complete public eight-pause runs:23,288 untouched sentinel bytes;916 touched from user top;24,204 monitored region|Intrusive writes only to unused emulated RAM,64-byte initial guard; not whole-device high-water or all possible control flow |
| IRQ stack |40 touched of160 monitored bytes,120 untouched|BIOS/private-lib/interrupt nesting worst case and physical high-water remain unmeasured |
| Private profile memory |ROM9,191,156 bytes; static IWRAM27,276, EWRAM9600; fresh eight-pause sentinel:4256 untouched,980 touched of5236 monitored user bytes; IRQ40/160|Much tighter than public; includes inherited legacy storage. No assumption that public graphics additions will fit private memory |
| Notes/holds |ROM notes are16-byte records, lane offset8, duration12; public charts86/171/335; fixed judgment/hold arrays and5 lane slots|Importer verifies lengths/lanes/order, sanitizers exercise bounds; no arbitrary future-chart safety implied |
| Objects/tails |32 head slots,96 tail-object slots; public soak head peak8, tail peak12; private tails11; overflow0|128 OAM total; future graphics would consume the same budget and require a fresh audit |
| Scanline data |Two static161-entry affine/blend tables; final entry handles visible-line160 trigger; inactive buffer built before ready handoff|Physical DMA/IRQ contention and complete transition latency unmeasured |
| DMA ownership |Imported DMA0 affine /DMA3 blend; DMA1/2 disabled for software FIFO refill; legacy Maxmod isolated|Mode-change stop/reset code reviewed; original699 profile exercised independently |
| Interrupt/clock ownership |Timer0 requests PCM; Timer1 counts16 samples/refill IRQ; Timer2 blocks; Timer3 measurements; VBlank affine commit polled|Shared PCM gate/count snapshots use IME critical sections; no new race fix inferred from source alone |
| Baseline foreground |119616/147008/155392 of280896 cycles|Measured maximum, not exhaustive worst-case execution time |
| Soak foreground/refill |Public155776 (125120 remaining); private137088; refill1472 max|64-cycle timer quantization; refill counter excludes full IRQ dispatch/return and total pause/resume path |
| HBlank observer |15 transports:11,190,415 affine, final-word and blend writes each;0 late writes; minimum39 remaining emulated cycles;0 paused FIFO requests|Emulator scheduling value, not physical bus/scanline margin |
| Composed frames |Baseline27,420 checked; extra public3016/version, private3276;0 displaced pixels|Floor oracle checks geometry, not every UI/art defect; readiness-invalid frames explicitly counted |
| Negative oracle |Shifted DMA table in host-only diagnostic:1769/1769 defect frames,500758 displaced pixels, expected exit134|Demonstrates detector sensitivity; modified observation run is never delivered |
| Long sessions |Public0.10.1/0.10.5, real private Easy and original699 each exceed3600 seconds|Bounded deterministic inputs; host RSS recorded, no physical memory-growth proof or exhaustive input proof |
| Output audio |Digital15/15, ordinary9/15|**Open certification blocker**; see audio gate |
| Owner hardware |Owner's historical RC1 positive report|RC2 all-difficulty checklist, device/cartridge record, listening and prolonged-session feedback pending |

Audit reviewed `source/main.cpp`, `source/pcmPlayback.cpp`, `source/scanline.cpp`,
`source/sustainDisplay.cpp`, physical mapping, judgment, scoring, sustain and
imported-runtime headers plus the Makefile/generation boundary. DMA sources are
static and aligned; a ready buffer is not overwritten before consumption. PCM
interrupt work consumes ROM stems directly, without a growable ring/decoder.
Count extension has the existing rollover handling; snapshots and gate changes
exclude interrupts. Note indices are checked before access in the exercised
paths; generated record size/offset assertions remain intact. Host ASan/UBSan
passes do not instrument executing ARM instructions or prove all game paths.

No runtime safety defect was reproduced that justified changing the ROM. No
engine fix or physical margin certification is claimed. Graphics work must wait
for the audio/owner gates and must re-budget OAM, scanline work and IRQ/stack use.
