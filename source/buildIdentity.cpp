#include "build_identity.hpp"

// Retained in the ROM and checked against its manifest by the release tools.
extern "C" const char gameBuildIdentity[] = GBA_BUILD_MARKER;
