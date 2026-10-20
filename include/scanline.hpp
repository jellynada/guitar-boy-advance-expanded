#ifndef SCANLINE_HPP
#define SCANLINE_HPP
// Imported-only transport for the existing perspective/fog tables.
namespace Scanline {
void start();
void stop();
void prepare();
void prepareAffines();
void vblank();
}
#endif
