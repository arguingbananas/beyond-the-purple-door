"""Minimal IPS applier: ips_apply.py SRC.dsk PATCH.ips OUT.dsk

Strict on purpose: the image size never changes, so a record that would write past the end,
a truncated patch, or a missing EOF marker is an error rather than a silently grown or
half-patched image.
"""

import os
import sys


def apply_ips(img: bytearray, p: bytes) -> bytearray:
    if p[:5] != b"PATCH":
        raise ValueError("not an IPS file (missing PATCH header)")
    i = 5
    while True:
        if i + 3 > len(p):
            raise ValueError("truncated patch: no EOF marker")
        if p[i : i + 3] == b"EOF":
            return img
        if i + 5 > len(p):
            raise ValueError("truncated patch: incomplete record header")
        off = int.from_bytes(p[i : i + 3], "big")
        n = int.from_bytes(p[i + 3 : i + 5], "big")
        i += 5
        if n == 0:  # RLE record: 2-byte run length, 1 value byte
            if i + 3 > len(p):
                raise ValueError("truncated patch: incomplete RLE record")
            n = int.from_bytes(p[i : i + 2], "big")
            data = p[i + 2 : i + 3] * n
            i += 3
        else:
            if i + n > len(p):
                raise ValueError("truncated patch: record data runs past end of file")
            data = p[i : i + n]
            i += n
        if off + n > len(img):
            raise ValueError(f"record at offset {off:#x} writes past the end of the image")
        img[off : off + n] = data


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, ips, out = argv
    if os.path.exists(out):
        print(f"ips_apply: refusing to overwrite existing {out}", file=sys.stderr)
        return 1
    try:
        with open(src, "rb") as f, open(ips, "rb") as g:
            img = apply_ips(bytearray(f.read()), g.read())
    except (OSError, ValueError) as e:
        print(f"ips_apply: {e}", file=sys.stderr)
        return 1
    with open(out, "wb") as f:
        f.write(img)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
