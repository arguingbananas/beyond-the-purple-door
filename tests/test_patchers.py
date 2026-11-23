"""Tests for the purple-door patcher and the DOS 3.3 helpers in patches/.

Error paths use synthetic images and always run. Checks against the real game image run only
when you supply it (the image is not in this repo): by default the 4am crack folder at the repo
root, or the path in the BCW_IMAGE environment variable.
"""

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "patches"))
import apply_bcw_purple_door_patch as door  # noqa: E402
import dos33  # noqa: E402

CRACK_DIR = "Beyond Castle Wolfenstein (4am crack)"
IMAGE = Path(os.environ.get("BCW_IMAGE") or ROOT / CRACK_DIR / f"{CRACK_DIR}.dsk")
CRACK_SHA = "5898ae8f"
DOOR_SHA = "3d843c2c"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


class TmpDirCase(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)

    def blank(self, size=dos33.IMAGE_SIZE) -> Path:
        p = self.tmp / "blank.dsk"
        p.write_bytes(bytes(size))
        return p


class SectorMath(unittest.TestCase):
    def test_known_offsets(self):
        self.assertEqual(dos33.sector_offset(0, 0), 0)
        self.assertEqual(dos33.sector_offset(17, 0), 17 * 16 * 256)
        self.assertEqual(dos33.sector_offset(34, 15), dos33.IMAGE_SIZE - 256)

    def test_out_of_range_is_rejected(self):
        for track, sector in ((35, 0), (0, 16), (-1, 0), (0, -1)):
            with self.subTest(track=track, sector=sector), self.assertRaises(dos33.PatchError):
                dos33.sector_offset(track, sector)


class DoorPatcherErrors(TmpDirCase):
    def test_blank_image_has_no_dos_catalog(self):
        with self.assertRaises(dos33.PatchError):
            door.patch_image(self.blank(), self.tmp / "out.dsk")
        self.assertFalse((self.tmp / "out.dsk").exists())

    def test_usage_message(self):
        sys.argv = ["x"]
        self.assertEqual(door.main(), 2)

    def test_cli_reports_errors_cleanly(self):
        sys.argv = ["x", str(self.blank(1000)), str(self.tmp / "out.dsk")]
        self.assertEqual(door.main(), 1)


@unittest.skipUnless(
    IMAGE.exists(),
    "game image not supplied (set BCW_IMAGE or place the 4am crack at the repo root)",
)
class RealImage(TmpDirCase):
    def test_image_is_the_expected_crack(self):
        self.assertEqual(sha(IMAGE), CRACK_SHA)

    def test_door_patch_hash(self):
        out = self.tmp / "door.dsk"
        door.patch_image(IMAGE, out)
        self.assertEqual(sha(out), DOOR_SHA)

    def test_input_is_never_modified(self):
        before = IMAGE.read_bytes()
        door.patch_image(IMAGE, self.tmp / "d.dsk")
        self.assertEqual(IMAGE.read_bytes(), before)

    def test_door_patch_changes_exactly_28_bytes(self):
        out = self.tmp / "door.dsk"
        door.patch_image(IMAGE, out)
        a, b = IMAGE.read_bytes(), out.read_bytes()
        self.assertEqual(sum(x != y for x, y in zip(a, b, strict=True)), 28)

    def test_door_patcher_refuses_to_overwrite_output(self):
        out = self.tmp / "out.dsk"
        out.write_bytes(b"keep")
        with self.assertRaises(dos33.PatchError):
            door.patch_image(IMAGE, out)
        self.assertEqual(out.read_bytes(), b"keep")

    def test_patching_twice_is_refused(self):
        once = self.tmp / "once.dsk"
        door.patch_image(IMAGE, once)
        with self.assertRaises(dos33.PatchError):
            door.patch_image(once, self.tmp / "twice.dsk")


if __name__ == "__main__":
    unittest.main()
