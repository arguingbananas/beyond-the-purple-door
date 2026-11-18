# Notes: Hiding the Purple Door Graphic (not started)

These are untested guesses. No drawing code has been traced yet.

## Background

- The purple door in room `$3C` is the object record at `$40A0` (type byte `60`).
- Poking the type byte to `$20` turned it into a green closet, so the type byte
  controls the sprite.
- `^THINGS` (loaded at `$4800`) registers each object's collision entries at
  `$4200,X` and `$4208,X`. The current patch stubs that routine at `$5D2D`.

## Approaches

1. **Skip the record on room load.** Stop room `$3C` from loading or
   registering the `$40A0` record. This should remove both the drawing and the
   collision entries. Otherwise the door is invisible but still solid.
2. **Change the type byte.** Try a value that selects a blank or empty sprite.
   Test live first: pause the emulator, poke `$40A0` to a few values, resume.

## Risks

- The record may also feed guard logic or the "door reappears" behaviour.
- Other code may expect a door there.
- The pixels may also be in the room background, which would need a separate
  edit.

## First step

Live-poke the type byte at `$40A0` with the game paused, and see what is drawn.
