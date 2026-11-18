"""Tests for tools/ips_apply.py (synthetic data only; no game image needed)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import ips_apply  # noqa: E402

EOF_MARK = b"EOF"


def record(offset: int, data: bytes) -> bytes:
    return offset.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data


def rle(offset: int, count: int, value: int) -> bytes:
    return offset.to_bytes(3, "big") + b"\x00\x00" + count.to_bytes(2, "big") + bytes([value])


class ApplyIps(unittest.TestCase):
    def test_plain_record(self):
        out = ips_apply.apply_ips(bytearray(16), b"PATCH" + record(4, b"\xaa\xbb") + EOF_MARK)
        self.assertEqual(bytes(out), bytes(4) + b"\xaa\xbb" + bytes(10))

    def test_rle_record(self):
        out = ips_apply.apply_ips(bytearray(8), b"PATCH" + rle(2, 3, 0x7F) + EOF_MARK)
        self.assertEqual(bytes(out), b"\x00\x00\x7f\x7f\x7f\x00\x00\x00")

    def test_size_never_changes(self):
        out = ips_apply.apply_ips(bytearray(8), b"PATCH" + record(6, b"\x01\x02") + EOF_MARK)
        self.assertEqual(len(out), 8)

    def test_empty_patch_is_a_noop(self):
        self.assertEqual(bytes(ips_apply.apply_ips(bytearray(b"abc"), b"PATCH" + EOF_MARK)), b"abc")

    def test_rejects_wrong_header(self):
        with self.assertRaisesRegex(ValueError, "not an IPS"):
            ips_apply.apply_ips(bytearray(8), b"garbage")

    def test_rejects_missing_eof(self):
        with self.assertRaisesRegex(ValueError, "no EOF"):
            ips_apply.apply_ips(bytearray(8), b"PATCH" + record(0, b"x"))

    def test_rejects_truncated_record_data(self):
        with self.assertRaisesRegex(ValueError, "past end of file"):
            ips_apply.apply_ips(bytearray(8), b"PATCH" + b"\x00\x00\x00\x00\x05ab")

    def test_rejects_truncated_record_header(self):
        with self.assertRaisesRegex(ValueError, "incomplete record header"):
            ips_apply.apply_ips(bytearray(8), b"PATCH" + b"\x00\x00\x00\x00")

    def test_rejects_truncated_rle(self):
        with self.assertRaisesRegex(ValueError, "incomplete RLE"):
            ips_apply.apply_ips(bytearray(8), b"PATCH" + b"\x00\x00\x00\x00\x00\x00\x02")

    def test_rejects_write_past_end_of_image(self):
        with self.assertRaisesRegex(ValueError, "past the end of the image"):
            ips_apply.apply_ips(bytearray(8), b"PATCH" + record(7, b"\x01\x02") + EOF_MARK)

    def test_rejects_rle_past_end_of_image(self):
        with self.assertRaisesRegex(ValueError, "past the end of the image"):
            ips_apply.apply_ips(bytearray(8), b"PATCH" + rle(6, 5, 1) + EOF_MARK)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: [p.unlink() for p in self.tmp.iterdir()] and self.tmp.rmdir())
        self.src = self.tmp / "in.dsk"
        self.src.write_bytes(bytes(8))
        self.ips = self.tmp / "p.ips"
        self.ips.write_bytes(b"PATCH" + record(1, b"\x09") + EOF_MARK)

    def test_writes_output_and_leaves_input_alone(self):
        out = self.tmp / "out.dsk"
        self.assertEqual(ips_apply.main([str(self.src), str(self.ips), str(out)]), 0)
        self.assertEqual(out.read_bytes(), b"\x00\x09" + bytes(6))
        self.assertEqual(self.src.read_bytes(), bytes(8))

    def test_refuses_to_overwrite_existing_output(self):
        out = self.tmp / "out.dsk"
        out.write_bytes(b"keep")
        self.assertEqual(ips_apply.main([str(self.src), str(self.ips), str(out)]), 1)
        self.assertEqual(out.read_bytes(), b"keep")

    def test_bad_patch_writes_nothing(self):
        self.ips.write_bytes(b"nope")
        out = self.tmp / "out.dsk"
        self.assertEqual(ips_apply.main([str(self.src), str(self.ips), str(out)]), 1)
        self.assertFalse(out.exists())

    def test_wrong_argument_count(self):
        self.assertEqual(ips_apply.main(["only-one"]), 2)


if __name__ == "__main__":
    unittest.main()
