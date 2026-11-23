#!/usr/bin/env python3
"""Make only the room-$3C purple door passable in a Beyond Castle Wolfenstein image.

^THINGS builds the door's collision entries ($4200+X and $4208+X) with
"DEX / LDA $6B / STA $4200,X / STA $4208,X". The patch replaces "DEX / LDA $6B"
with a call to a stub appended to @FHR at $1EB3. The stub returns A=0 (no
collision) only when the room ($4050) is $3C, the cell index is $3D and the
object record is $40A0; otherwise it behaves exactly like the original code.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dos33 import (
    IMAGE_SIZE,
    SECTOR_SIZE,
    PatchError,
    binary_byte_offset,
    file_data_sectors,
    file_entries,
    sector_offset,
)

STUB_ADDRESS = 0x1EB3
STUB = bytes.fromhex(
    "CA"  # DEX
    "AD5040"  # LDA $4050 (current room)
    "C93C"  # CMP #$3C
    "D00D"  # BNE norm
    "E03D"  # CPX #$3D (purple door cell)
    "D009"  # BNE norm
    "A56B"  # LDA $6B
    "C9A0"  # CMP #$A0 (purple door record $40A0)
    "D003"  # BNE norm
    "A900"  # LDA #$00
    "60"  # RTS
    "A56B"  # norm: LDA $6B
    "60"  # RTS
)
SITE_ADDRESS = 0x5D2D
SITE_OLD = bytes.fromhex("CAA56B")  # DEX / LDA $6B
SITE_NEW = bytes.fromhex("20B31E")  # JSR $1EB3


def patch_image(source: Path, destination: Path) -> None:
    if destination.exists():
        raise PatchError(f"Refusing to overwrite existing output: {destination}")
    image = bytearray(source.read_bytes())
    if len(image) != IMAGE_SIZE:
        raise PatchError(
            f"Expected a 143,360-byte, 35-track DOS-order .dsk image; found {len(image)} bytes"
        )
    entries = file_entries(image)

    fhr_name = "@FHR"
    fhr_load = 0x810
    fhr_sectors = file_data_sectors(image, entries[fhr_name], fhr_name)
    first_offset = sector_offset(*fhr_sectors[0])
    load = int.from_bytes(image[first_offset : first_offset + 2], "little")
    length = int.from_bytes(image[first_offset + 2 : first_offset + 4], "little")
    if load != fhr_load or load + length != STUB_ADDRESS:
        raise PatchError(f"Unexpected @FHR extent ${load:X}+{length}")
    stream_end = length + 4
    if stream_end % SECTOR_SIZE + len(STUB) > SECTOR_SIZE:
        raise PatchError("Stub does not fit in the last @FHR sector")

    stub_offset = binary_byte_offset(image, entries[fhr_name], fhr_name, STUB_ADDRESS - fhr_load)
    if set(image[stub_offset : stub_offset + len(STUB)]) - {0x00, 0xFF}:
        raise PatchError("Stub area in @FHR is not unused padding")
    image[stub_offset : stub_offset + len(STUB)] = STUB
    image[first_offset + 2 : first_offset + 4] = (length + len(STUB)).to_bytes(2, "little")

    things = "^THINGS"
    things_load = 0x4800
    site = binary_byte_offset(image, entries[things], things, SITE_ADDRESS - things_load)
    if bytes(image[site : site + 3]) != SITE_OLD:
        raise PatchError("Unexpected bytes at the ^THINGS patch site")
    image[site : site + 3] = SITE_NEW

    destination.write_bytes(image)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: apply_bcw_purple_door_patch.py SOURCE.dsk DEST.dsk")
        return 2
    try:
        patch_image(Path(sys.argv[1]), Path(sys.argv[2]))
    except (OSError, PatchError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Patched disk written to {sys.argv[2]}")
    print("The input image was not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
