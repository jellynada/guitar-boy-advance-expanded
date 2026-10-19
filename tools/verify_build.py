#!/usr/bin/env python3
"""Reject stale/mismatched ROM, ELF and chart inputs before reporting a build."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def verify(rom, elf, count):
    prefix = Path(os.environ['DEVKITARM']) / 'bin' / 'arm-none-eabi-'
    symbols = subprocess.check_output([str(prefix) + 'nm', '-S', str(elf)], text=True)
    record = re.search(r'^\w+\s+(\w+)\s+\w\s+imported_notes$', symbols, re.M)
    if not record or int(record[1], 16) != count * 16:
        raise ValueError('ELF note count does not match the requested chart; rebuild first.')
    with tempfile.TemporaryDirectory() as directory:
        binary = Path(directory) / 'linked.bin'
        subprocess.run([str(prefix) + 'objcopy', '-O', 'binary', str(elf), str(binary)], check=True)
        linked = binary.read_bytes()
    cartridge = rom.read_bytes()
    # gbafix fills the cartridge header at4..191 after linking. The entry
    # instruction and every program/data byte must still match the ELF.
    if len(cartridge) != len(linked) or cartridge[:4] != linked[:4] or cartridge[192:] != linked[192:]:
        raise ValueError('ROM does not match the ELF; do not test or publish this pair.')
    return dict(notes=count, rom_bytes=len(cartridge), rom_sha256=hashlib.sha256(cartridge).hexdigest(),
                elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('elf', type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--note-count', type=int)
    group.add_argument('--header', type=Path)
    args = parser.parse_args()
    try:
        count = args.note_count
        if args.header:
            match = re.search(r'imported_note_count = (\d+)', args.header.read_text())
            if not match:
                raise ValueError('Chart header has no note count.')
            count = int(match[1])
        if count is None or count <= 0 or count > 8192:
            raise ValueError('Invalid chart count.')
        print(json.dumps(verify(args.rom, args.elf, count), sort_keys=True))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit('Build verification failed: ' + str(error))
