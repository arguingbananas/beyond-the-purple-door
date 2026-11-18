# Roadmap

A draft. Nothing here is promised; order is rough priority. Edit freely.

## Game mod
- [ ] Hide the purple door graphic (poke the type byte at `$40A0`, then trace the drawing code;
      see `docs/Hide-Purple-Door-Notes.md`).
- [ ] Player-only passage: guards currently walk through the door too, which needs a separate
      player-collision lookup.
- [ ] Work out whether anything else reads the `$40A0` record (guard logic, "door reappears").
- [ ] Boot-test an image built purely from the IPS files.
- [ ] Patches for `.woz` and `.nib` copies (today only DOS-order `.dsk`).

## Tooling
- [ ] Script making a new emulator saved state through the menus (steps are documented in
      `tools/README-a2ts.md` but done by hand).
- [ ] A fetch-and-extract script for the Apple2TS web build into `a2ts-web/`.
- [ ] A bridge API reference listing every action and payload.
