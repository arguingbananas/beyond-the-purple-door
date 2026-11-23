"""DOS 3.3 disk-image helpers used by the patchers: catalog lookup and file byte offsets."""

from __future__ import annotations

IMAGE_SIZE = 35 * 16 * 256
SECTOR_SIZE = 256
SECTORS_PER_TRACK = 16
VTOC = (17, 0)
CATALOG_FIRST = (17, 15)


class PatchError(Exception):
    pass


def sector_offset(track: int, sector: int) -> int:
    if not (0 <= track < 35 and 0 <= sector < SECTORS_PER_TRACK):
        raise PatchError(f"Invalid DOS 3.3 sector address T{track}/S{sector}")
    return (track * SECTORS_PER_TRACK + sector) * SECTOR_SIZE


def read_sector(image: bytearray, track: int, sector: int) -> bytes:
    offset = sector_offset(track, sector)
    return bytes(image[offset : offset + SECTOR_SIZE])


def file_entries(image: bytearray) -> dict[str, tuple[int, int, int, int]]:
    vtoc = read_sector(image, *VTOC)
    track, sector = vtoc[1], vtoc[2]
    if (track, sector) != CATALOG_FIRST:
        raise PatchError(
            "This patcher expects the standard DOS 3.3 VTOC/catalog location "
            f"T17/S0 -> T{track}/S{sector}"
        )

    entries: dict[str, tuple[int, int, int, int]] = {}
    seen_catalog: set[tuple[int, int]] = set()
    while track:
        address = (track, sector)
        if address in seen_catalog:
            raise PatchError("Loop detected in the DOS catalog chain")
        seen_catalog.add(address)
        catalog = read_sector(image, track, sector)
        next_track, next_sector = catalog[1], catalog[2]

        for index in range(7):
            start = 0x0B + index * 0x23
            entry = catalog[start : start + 0x23]
            raw_name = entry[3:33]
            name = (
                bytes(value & 0x7F for value in raw_name)
                .decode("ascii", errors="replace")
                .rstrip(" ")
            )
            if not name:
                continue
            entries[name] = (
                entry[0],
                entry[1],
                entry[2],
                int.from_bytes(entry[33:35], "little"),
            )
        track, sector = next_track, next_sector
    return entries


def file_data_sectors(
    image: bytearray, entry: tuple[int, int, int, int], name: str
) -> list[tuple[int, int]]:
    track, sector, file_type, total_sectors = entry
    if file_type & 0x7F != 0x04:
        raise PatchError(f"{name} is not a DOS binary file")
    if total_sectors < 2:
        raise PatchError(f"{name} has an invalid DOS sector count")

    data_sectors: list[tuple[int, int]] = []
    seen_lists: set[tuple[int, int]] = set()
    while track:
        address = (track, sector)
        if address in seen_lists:
            raise PatchError(f"Loop detected in {name}'s T/S list")
        seen_lists.add(address)
        ts_list = read_sector(image, track, sector)
        next_track, next_sector = ts_list[1], ts_list[2]
        for offset in range(0x0C, SECTOR_SIZE, 2):
            data_track, data_sector = ts_list[offset], ts_list[offset + 1]
            if data_track:
                data_sectors.append((data_track, data_sector))
                if len(data_sectors) > total_sectors:
                    raise PatchError(f"Too many data sectors listed for {name}")
        track, sector = next_track, next_sector

    expected_data_sectors = total_sectors - len(seen_lists)
    if len(data_sectors) != expected_data_sectors:
        raise PatchError(
            f"{name} sector count mismatch: catalog says {total_sectors}, "
            f"T/S lists contain {len(seen_lists)} list and "
            f"{len(data_sectors)} data sectors"
        )
    return data_sectors


def binary_byte_offset(
    image: bytearray,
    entry: tuple[int, int, int, int],
    name: str,
    logical_offset: int,
) -> int:
    data_sectors = file_data_sectors(image, entry, name)
    stream_offset = logical_offset + 4  # DOS binary load address/length header.
    sector_index, offset_in_sector = divmod(stream_offset, SECTOR_SIZE)
    if sector_index >= len(data_sectors):
        raise PatchError(f"Offset ${logical_offset:X} is outside {name}")
    track, sector = data_sectors[sector_index]
    return sector_offset(track, sector) + offset_in_sector
