# Roadmap

The project's goal is met (v1.0.0) and it is in maintenance mode. These are optional follow-ups,
not plans. Nothing here is promised; order is rough priority. Edit freely.

## Open questions
- [ ] Which ending telegram is shown, and why ("HITLER AND MOST OF CABINET DEAD" versus "FUEHRER
      ESCAPED UNHARMED"): trace the code that picks it (see "What is not known" in
      `docs/Project-Notes.md`).
- [ ] Where the player's own position is kept (it is not in the room's object list).

## Game mod
- [ ] Hide the purple door graphic (poke the type byte at `$40A0`, then trace the drawing code;
      see `docs/Hide-Purple-Door-Notes.md`).
- [ ] Player-only passage: guards currently walk through the door too, which needs a separate
      player-collision lookup.
- [ ] Work out whether anything else reads the `$40A0` record (guard logic, "door reappears").
- [ ] Patches for `.woz` and `.nib` copies (today only DOS-order `.dsk`).

## Tooling
- [ ] Script making a new emulator saved state through the menus (steps are documented in
      `tools/README-a2ts.md` but done by hand).
- [ ] A fetch-and-extract script for the Apple2TS web build into `a2ts-web/`.
