# Shattered Realms implementation audit

## Current source

The pinned Emerald Expansion engine remains in place. This update extends it
with persistent move retention, complete teachable lists, a playable original
Rift chapter, competitive boss teams and targeted GBA emulator regressions.
It does not replace the whole Emerald campaign.

| System | Implemented behavior | Verification scope |
| --- | --- | --- |
| Patch pipeline | Staged writes, deterministic repeated application, pinned map-section count checks | Full application tested against a fresh source snapshot |
| Move library | Current/saved moves, current/pre-evolution level/evolution/teachable/egg lists, persistent exceptional attacks | Host integration tests; targeted GBA cases |
| Journal migration | Versioned, integrity-checked reserved save-tail extension; old blank tails initialize safely | Production codec executed by host tests; generated old-format save round trip in GBA suite |
| Save layouts | Existing Pokémon/PC/main save sizes and offsets preserved | ARM ABI probes compared old and new headers |
| Player PP | Selection/execution/Pressure/Spite/Grudge paths bypass local player depletion; enemy PP stays normal | Targeted single/double battle tests |
| Battle effects | Transform/Mimic/Encore suspend paging; Sketch protects saved slots; Disable survives browsing | Host callback tests and targeted GBA regressions; full UI combinations still need Delta |
| Supplies/EXP | Infinite wallet and selected consumables, reusable TMs, field supply grants, 4x battle EXP | Patch regressions; campaign balance testing remains |
| Difficulty | Adaptive levels, IV floors, smart AI/switching and explicit sets for 36 key fights | Generated trainer data compiles; EV/team validation; full fight balance remains |
| Companion | Native following plus Pikachu Bond interaction messages and persistent threshold unlocks | Source/logic tests; indoor/outdoor/surf/cycle visual checks still needed |
| Original chapter | Lumen with lodge/workshop/Gym, Riftway, Nova, scout, Rift Hollow/Vesper, Stormscar/Zapdos, journal dialogue and rewards | Registrations, reachability and reward/flag checks; full playthrough remains |
| Collection | Fifteen expanded wild tables including Riftway; habitat NPC; evolution shop; local alternatives for every trade target in species sources | Static source audit; full obtainable-species audit unfinished |

## Important limits

- The exceptional move journal has 152 entries across the save. Compatible moves
  are reconstructed without entries. No entry is silently evicted. At capacity,
  overwriting the only copy of an exceptional move is refused; see
  [MOVE_HISTORY.md](MOVE_HISTORY.md), including the learning-dialogue caveat.
- A virtual Sketch without an existing saved Sketch slot is battle-only.
- The original prologue and title-screen artwork remain. Lumen is the first new
  chapter hub, reached through Elara after obtaining a Pokémon partner.
- This is not the full original campaign. Further realms, classic-region travel,
  additional legendary/mythical quests and complete distribution remain open.
- A source-level alternative to trading does not prove every species is obtainable.
- No real previously exported Delta save was supplied. Generated save tests do
  not establish compatibility with every historical ROM/save combination.

## Required acceptance playthrough

1. Back up a real in-game save, import the new ROM separately and Continue.
2. Inspect party, PC, Bag, badges and location; change maps; save, quit and reload.
3. Choose Pikachu in a separate new game. Verify its four saved signatures and
   extra pages. Test SELECT/R, cancellation, switching, doubles, targets, fainting,
   Transform, Mimic, Disable, Encore, Choice items, multi-turn moves and Sketch.
4. Learn/replace an exceptional attack, evolve and deposit/withdraw the Pokémon,
   save/reload and confirm the attack remains in the battle library.
5. Walk the entire chapter in [CHAPTER_ONE.md](CHAPTER_ONE.md), test every door,
   complete both full-Bag reward retries, earn the first badge and revisit Hoenn.
6. Test following indoors/outdoors, stairs, doors, surfing, cycling and fainting.
7. Test midgame and late bosses against varied teams and Rare Candy use.

The release workflow now runs the targeted mGBA suite before publication, in
addition to host tests, repeated patch application, compilation and ROM/hash
verification. A failed gate leaves the previous release available. See
[BUILD_VALIDATION.md](BUILD_VALIDATION.md) for the recorded published build.

## Build 65 additions

Automatic learning no longer requires forgetting when the four saved slots are
full; library attacks satisfy move-based evolution checks. Build-time gameplay
profiles are implemented and tested, and finite-PP displays are restored. See
[settings and limits](GAMEPLAY_SETTINGS.md) and [current validation](BUILD_VALIDATION.md).
Enemy move expansion and an in-game configuration menu remain unfinished.
