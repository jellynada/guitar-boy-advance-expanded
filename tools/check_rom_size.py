#!/usr/bin/env python3
"""Reject oversized cartridges rather than relying on emulator extensions."""
import sys
from pathlib import Path
size=Path(sys.argv[1]).stat().st_size
if size>32*1024*1024:raise SystemExit(f'ROM{size}bytes exceeds conventional GBA32MiB address space.')
print(f'Cartridge size:{size}bytes /33554432bytes')
