"""Tests for tools/cp2_check.py.

Part 1 feeds canned cp2 output (captured from real runs) to the parser and comparison, so it
always runs, including in CI where cp2 is not installed. Part 2 runs the real cp2 against the
real game image and deliberately damaged copies; it skips unless both are available.
"""

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "patches"))
import apply_bcw_purple_door_patch as door  # noqa: E402
import apply_bcw_terminal_patch as terminal  # noqa: E402
import cp2_check  # noqa: E402

CRACK_DIR = "Beyond Castle Wolfenstein (4am crack)"
IMAGE = Path(os.environ.get("BCW_IMAGE") or ROOT / CRACK_DIR / f"{CRACK_DIR}.dsk")
CP2 = Path(os.environ.get("CP2") or cp2_check.DEFAULT_CP2)

GOOD = """Scanning DOS 3.x filesystem 'DOS-001'
Tested 7 files; no failures
Log:
02:08:01.546 I Usage counts: 533 in use, 0 unused but marked, 0 used but not marked, 0 conflicts
"""
BAD_POINTER = """Scanning DOS 3.x filesystem 'DOS-001'
Filesystem 'DOS-001' notes (2 warning/0 error):
   W) Found bad T/S entry in T7 S13: CASTLE
   W) I/A/B stored length (15868 + 4) exceeds actual file length (512): CASTLE
   I) Found 61 unused sectors that are marked used

Tested 7 files; no failures
Log:
02:08:01.719 I Usage counts: 533 in use, 61 unused but marked, 0 used but not marked, 0 conflicts
"""
NO_FILES = """Scanning DOS 3.x filesystem 'DOS-001'
Filesystem 'DOS-001' notes (0 warning/0 error):
   I) Found 477 unused sectors that are marked used

Tested 0 files; no failures
Log:
02:08:01.719 I Usage counts: 56 in use, 477 unused but marked, 0 used but not marked, 0 conflicts
"""
NAMES = "SEKTOR\nCASTLE\nBACKUP\n"


def fp(test_output: str, names: str = NAMES, returncode: int = 0) -> cp2_check.Fingerprint:
    out = cp2_check.Fingerprint(returncode=returncode)
    cp2_check.parse_test_output(test_output, out)
    out.names = cp2_check.parse_list(names)
    return out


class Parsing(unittest.TestCase):
    def test_good_output(self):
        out = fp(GOOD)
        self.assertEqual(
            (out.tested, out.failures, out.warnings, out.errors), (7, "no failures", 0, 0)
        )
        self.assertEqual(out.notes, [])
        self.assertEqual(
            out.usage, "533 in use, 0 unused but marked, 0 used but not marked, 0 conflicts"
        )
        self.assertEqual(out.names, ["BACKUP", "CASTLE", "SEKTOR"])

    def test_notes_are_collected(self):
        out = fp(BAD_POINTER)
        self.assertEqual((out.warnings, out.errors), (2, 0))
        self.assertEqual(len(out.notes), 3)
        self.assertIn("Found bad T/S entry in T7 S13: CASTLE", out.notes)

    def test_singular_file_wording(self):
        out = fp("Tested 1 file; no failures\n")
        self.assertEqual((out.tested, out.failures), (1, "no failures"))

    def test_unparseable_output_leaves_nothing_set(self):
        out = fp("garbage\n")
        self.assertIsNone(out.tested)
        self.assertIsNone(out.usage)


class Comparison(unittest.TestCase):
    def test_identical_is_clean(self):
        self.assertEqual(cp2_check.compare(fp(GOOD), fp(GOOD)), [])

    def test_does_not_depend_on_how_many_files_there_are(self):
        many = GOOD.replace("Tested 7 files", "Tested 99 files")
        self.assertEqual(cp2_check.compare(fp(many, "A\nB\n"), fp(many, "A\nB\n")), [])

    def test_the_old_text_check_would_have_passed_this_but_we_do_not(self):
        issues = cp2_check.compare(fp(GOOD), fp(BAD_POINTER))
        self.assertTrue(any("notes differ" in i for i in issues))
        self.assertTrue(any("usage counts differ" in i for i in issues))

    def test_zero_files_tested_is_flagged_even_with_no_failures(self):
        issues = cp2_check.compare(fp(GOOD), fp(NO_FILES))
        self.assertTrue(any("tested 0 files" in i for i in issues))

    def test_added_or_missing_files_are_flagged(self):
        issues = cp2_check.compare(fp(GOOD), fp(GOOD, "SEKTOR\nCASTLE\nEXTRA\n"))
        self.assertTrue(any("missing ['BACKUP']" in i and "added ['EXTRA']" in i for i in issues))

    def test_nonzero_exit_and_failures_are_flagged(self):
        self.assertTrue(cp2_check.compare(fp(GOOD), fp(GOOD, returncode=1)))
        failing = GOOD.replace("no failures", "2 failures")
        self.assertTrue(any("2 failures" in i for i in cp2_check.compare(fp(GOOD), fp(failing))))

    def test_missing_tested_line_is_flagged(self):
        self.assertTrue(any("no 'Tested" in i for i in cp2_check.compare(fp(GOOD), fp("x\n"))))

    def test_reference_must_be_a_usable_baseline(self):
        self.assertEqual(cp2_check.problems_with_reference(fp(GOOD)), [])
        self.assertTrue(cp2_check.problems_with_reference(fp(NO_FILES)))
        self.assertTrue(cp2_check.problems_with_reference(fp("x\n")))
        self.assertTrue(cp2_check.problems_with_reference(fp(GOOD, returncode=1)))


@unittest.skipUnless(
    IMAGE.exists() and CP2.exists(),
    "needs the game image and CiderPress II (apps/cp2/cp2 or $CP2)",
)
class RealCp2(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)
        self.ref = cp2_check.fingerprint(CP2, IMAGE)

    def issues(self, image: Path) -> list[str]:
        return cp2_check.compare(self.ref, cp2_check.fingerprint(CP2, image))

    def damaged(self, name: str, edit) -> Path:
        data = bytearray(IMAGE.read_bytes())
        edit(data)
        path = self.tmp / f"{name}.dsk"
        path.write_bytes(data)
        return path

    def ts_list_offset(self, data: bytearray) -> int:
        track, sector = terminal.file_entries(data)["CASTLE"][:2]
        return terminal.sector_offset(track, sector)

    def test_reference_is_a_usable_baseline(self):
        self.assertEqual(cp2_check.problems_with_reference(self.ref), [])

    def test_patched_images_are_as_sound_as_the_original(self):
        door_img, term_img = self.tmp / "door.dsk", self.tmp / "term.dsk"
        door.patch_image(IMAGE, door_img)
        terminal.patch_image(IMAGE, term_img)
        for image in (door_img, term_img):
            with self.subTest(image=image.name):
                self.assertEqual(self.issues(image), [])

    def test_bad_track_sector_pointer_is_detected(self):
        def edit(data):
            data[self.ts_list_offset(data) + 12 + 4] = 99  # third data entry -> track 99

        self.assertTrue(self.issues(self.damaged("badptr", edit)))

    def test_overlapping_files_are_detected(self):
        def edit(data):
            base = self.ts_list_offset(data) + 12
            data[base + 4 : base + 6] = data[base + 2 : base + 4]  # entry 3 repeats entry 2

        self.assertTrue(self.issues(self.damaged("dup", edit)))

    def test_damaged_catalog_is_detected(self):
        def edit(data):
            start = terminal.sector_offset(*terminal.CATALOG_FIRST)
            data[start + 11] = 99  # first catalog entry's track/sector list pointer

        self.assertTrue(self.issues(self.damaged("badcat", edit)))

    def test_cli_returns_nonzero_for_a_damaged_image(self):
        def edit(data):
            data[self.ts_list_offset(data) + 12 + 4] = 99

        bad = self.damaged("cli", edit)
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            self.assertEqual(cp2_check.main([str(IMAGE), str(bad)]), 1)
        self.assertIn("FAIL cli.dsk", printed.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cp2_check.main([str(IMAGE), str(IMAGE)]), 0)


if __name__ == "__main__":
    unittest.main()
