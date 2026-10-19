#!/usr/bin/env python3
"""Validate a built Game Boy Advance ROM file before offering it for download."""
from __future__ import annotations

import argparse
from pathlib import Path


def check_rom(rom: bytes) -> None:
    if not (1024 * 1024 <= len(rom) <= 32 * 1024 * 1024):
        raise ValueError(f"Unexpected GBA file size: {len(rom):,} bytes")
    title = rom[0xA0:0xAC].rstrip(b"\x00")
    code = rom[0xAC:0xB0]
    if title != b"SHATTERED":
        raise ValueError(f"Wrong GBA header title: {title!r}")
    if code != b"BSRE":
        raise ValueError(f"Wrong GBA header game code: {code!r}")
    checksum = (-(sum(rom[0xA0:0xBD]) + 0x19)) & 0xFF
    if rom[0xBD] != checksum:
        raise ValueError(f"Invalid GBA header checksum: {rom[0xBD]:02x} vs {checksum:02x}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("rom", type=Path)
    args = p.parse_args()
    contents = args.rom.read_bytes()
    check_rom(contents)
    print(f"Validated {args.rom}: {len(contents):,} bytes, SHATTERED / BSRE")
