# Beyond Castle Wolfenstein: Terminal Barrier Patch

This patch modifies an **unprotected, 35-track DOS 3.3 `.dsk` image** of
*Beyond Castle Wolfenstein*. It changes the player collision checks so the
player can cross the purple barrier in the terminal room. The barrier graphic
is not removed; it remains visible, but the patched game permits passage.

## Files

- `apply_bcw_terminal_patch.py` — recommended patcher. It locates `@FHR`,
  `CASTLE`, and `BACKUP` through the DOS catalog and T/S lists, checks the
  expected original bytes, then writes a **new** disk image.
- `bcw-terminal-barrier.ips` — IPS patch for the standard raw DOS-order image
  layout used by the supplied 4am unprotected disk. Use the Python patcher for
  other DOS-order copies whose file sectors may have been allocated differently.
- `Terminal-Barrier-Patch.pdf` — this document in PDF format.

## Applying the recommended patch

**1.** Make a backup of your original disk image. The patcher leaves the input
file unchanged and refuses to overwrite an existing output.

**2.** Install Python 3 if it is not already available.

**3.** Put `apply_bcw_terminal_patch.py` next to the disk image, open a terminal
in that directory, and run:

```sh
python3 ./apply_bcw_terminal_patch.py "Beyond Castle Wolfenstein.dsk" "Beyond Castle Wolfenstein - Terminal Barrier Passable.dsk"
```

**4.** The patcher reports success only after finding all three expected DOS
files and matching the original code/data bytes. If it reports a mismatch, do
not force the patch; the disk may be a different revision, already patched, or
not a DOS-order `.dsk` image.

**5.** Optionally validate the new image with CiderPress II:

```sh
cp2 test "Beyond Castle Wolfenstein - Terminal Barrier Passable.dsk"
```

**6.** Boot the new image in an Apple II emulator. The patch does not create a
saved game or select a starting room; use the game’s resume option if that disk
already contains a valid in-progress save.

### Applying the IPS file

Use an IPS-compatible patching tool. Select the unmodified, standard DOS-order
`.dsk` as the source, apply `bcw-terminal-barrier.ips`, and save the result to a
new filename. Do not apply the IPS file to a `.nib`, `.woz`, protected image,
or a disk image with a different sector ordering. The IPS records use absolute
raw-image offsets; the Python patcher is safer when file allocation differs.

<h2 style="page-break-before: always;">What changes</h2>

The game executable `@FHR` is a DOS binary loaded at `$0810`. Its DOS file
starts with a four-byte binary load-address/length header, which is not part of
the executable address space. The patcher resolves the executable's actual
sectors from its DOS T/S list rather than assuming that the file occupies fixed
sectors.

| File/address | Original | Patched | Effect |
|---|---|---|---|
| `@FHR:$13C9-$13CB` | `4C 3B 15` | `EA EA EA` | NOPs the jump from the initial movement-map rejection into the collision response. |
| `@FHR:$1524` | `16` | `00` | Changes the nearby `BCS` target from `$153B` to its fall-through at `$1525`. |
| `@FHR:$1532` | `08` | `1E` | Changes the nearby `BNE` target from `$153B` to `$1551`, the accepted-movement path. |
| `CASTLE:file+$1026` | `15` | `35` | Opens the native door cell in the room-15 map copy. |
| `BACKUP:file+$1026` | `15` | `35` | Keeps the backup map's corresponding room-15 door open as well. |

The first three edits are the collision bypass tested in the emulator. The two
map edits preserve the separate room-15 door-open change present in the
play-test disk; they are not what removes the terminal barrier's collision.
The patch intentionally does not rewrite the terminal-room drawing data,
erase the barrier graphic, edit a saved-game state, or clear other room maps.

The collision changes apply to the movement checks used by the game, not only
to one barrier tile. Other map walls that rely on these checks may also be
passable. Guard detection and other gameplay behavior are not intentionally
disabled.

## Patch scope and verification

The patcher supports 143,360-byte DOS 3.3 sector-ordered disk images with the
standard VTOC/catalog location. It follows the directory entries and T/S lists,
so the target files need not occupy exactly the same sectors as the reference
image. It requires the executable to load at `$0810` and all listed original
bytes to match. It fails safely instead of guessing when these assumptions do
not hold.

The reference unmodified disk used to build and validate this patch is
`Beyond Castle Wolfenstein (4am crack)/Beyond Castle Wolfenstein (4am crack).dsk`
(SHA-256
`5898ae8fdd538aee3cc7d95158de403561e8f47eb5d9465989bcd47e0a75068d`).
validation checked the original executable signatures and load addresses,
applied the patch to a separate scratch image, confirmed the five logical
edits, and ran CiderPress II's DOS filesystem test (18 files, no failures).

The resumable room-$3C save in the play-test disk is a **separate, disk-specific
save state**. This generic patcher does not manufacture or alter saved-game
data; apply it to a copy of the disk that already has the save you want to use.
