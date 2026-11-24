"""Check that patched disk images are as sound as the original, using CiderPress II (cp2).

usage: cp2_check.py REFERENCE.dsk IMAGE.dsk [IMAGE.dsk ...]
       (cp2 is taken from $CP2, else apps/cp2/cp2 at the repo root)

Why not just trust `cp2 test`? For a DOS 3.3 disk it reports "no failures" and exits 0 even when
the filesystem has real problems (bad track/sector entries, overlapping files); those only show
up as notes (--show-notes) and in the log's "Usage counts" line. So each image is compared with
the reference (the original game image): the same notes, the same usage counts, the same set of
files, and cp2 must have actually tested files. Nothing about the game (file count, names) is
hard-coded, so this keeps working if the project changes.
"""

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Minimum Python, kept in step with pyproject.toml target-version. Ruff assumes that version and
# calls this check dead code (UP036); it is for people running an older python3.
if sys.version_info < (3, 11):  # noqa: UP036
    sys.exit(f"cp2_check.py: needs Python 3.11 or newer (this is {sys.version.split()[0]})")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CP2 = ROOT / "apps" / "cp2" / "cp2"

TESTED_RE = re.compile(r"^Tested (\d+) files?; (no failures|\d+ failures?)", re.MULTILINE)
NOTES_HEADER_RE = re.compile(r"^Filesystem .* notes \((\d+) warning/(\d+) error\):", re.MULTILINE)
NOTE_LINE_RE = re.compile(r"^ {3}[WEI]\) (.*)$", re.MULTILINE)
USAGE_RE = re.compile(r"Usage counts: (.*)$", re.MULTILINE)


@dataclass
class Fingerprint:
    returncode: int = 0
    tested: int | None = None
    failures: str | None = None
    warnings: int = 0
    errors: int = 0
    notes: list[str] = field(default_factory=list)
    usage: str | None = None
    names: list[str] = field(default_factory=list)


def parse_test_output(text: str, fp: Fingerprint) -> None:
    """Fill in what `cp2 test --show-notes --show-log` printed."""
    if m := TESTED_RE.search(text):
        fp.tested = int(m.group(1))
        fp.failures = m.group(2)
    if m := NOTES_HEADER_RE.search(text):
        fp.warnings, fp.errors = int(m.group(1)), int(m.group(2))
    fp.notes = sorted(NOTE_LINE_RE.findall(text))
    if m := USAGE_RE.search(text):
        fp.usage = m.group(1).strip()


def parse_list(text: str) -> list[str]:
    return sorted(line.strip() for line in text.splitlines() if line.strip())


def run(cp2: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(cp2), *args], capture_output=True, text=True)  # noqa: S603


def fingerprint(cp2: Path, image: Path) -> Fingerprint:
    test = run(cp2, "test", "--show-notes", "--show-log", str(image))
    fp = Fingerprint(returncode=test.returncode)
    parse_test_output(test.stdout, fp)
    fp.names = parse_list(run(cp2, "list", str(image)).stdout)
    return fp


def problems_with_reference(ref: Fingerprint) -> list[str]:
    """The reference must itself be a usable baseline, or comparing against it proves nothing."""
    out = []
    if ref.returncode != 0:
        out.append(f"cp2 test failed on the reference image (exit {ref.returncode})")
    if not ref.tested:
        out.append("cp2 tested no files in the reference image")
    if ref.usage is None:
        out.append("no 'Usage counts' line for the reference image (cp2 output changed?)")
    return out


def compare(ref: Fingerprint, img: Fingerprint) -> list[str]:
    """Return what is wrong with img relative to ref (an empty list means it is as sound)."""
    out = []
    if img.returncode != 0:
        out.append(f"cp2 test exited {img.returncode}")
    if img.tested is None:
        out.append("cp2 test printed no 'Tested N files' line")
    elif img.tested != ref.tested:
        out.append(f"cp2 tested {img.tested} files, the reference tested {ref.tested}")
    if img.failures not in (None, "no failures"):
        out.append(f"cp2 test reports {img.failures}")
    if (img.warnings, img.errors) != (ref.warnings, ref.errors) or img.notes != ref.notes:
        extra = sorted(set(img.notes) - set(ref.notes))
        out.append(
            f"filesystem notes differ ({img.warnings} warning/{img.errors} error vs "
            f"{ref.warnings}/{ref.errors} in the reference): {extra or img.notes}"
        )
    if img.usage != ref.usage:
        out.append(f"usage counts differ: {img.usage!r} vs reference {ref.usage!r}")
    if img.names != ref.names:
        gone = sorted(set(ref.names) - set(img.names))
        new = sorted(set(img.names) - set(ref.names))
        out.append(f"file list differs: missing {gone}, added {new}")
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    cp2 = Path(os.environ.get("CP2") or DEFAULT_CP2)
    if not cp2.exists():
        print(f"cp2_check: cp2 not found at {cp2}", file=sys.stderr)
        return 2
    ref_path, images = Path(argv[0]), [Path(a) for a in argv[1:]]
    ref = fingerprint(cp2, ref_path)
    if bad := problems_with_reference(ref):
        for line in bad:
            print(f"FAIL reference {ref_path.name}: {line}")
        return 1
    status = 0
    for image in images:
        if issues := compare(ref, fingerprint(cp2, image)):
            status = 1
            for line in issues:
                print(f"FAIL {image.name}: {line}")
        else:
            print(f"ok   cp2 filesystem check vs original: {image.name}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
