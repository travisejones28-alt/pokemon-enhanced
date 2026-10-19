# Shattered Realms — Protect iPhone Saves

## Golden rule

**Do not delete the old game tile from Delta until the new ROM has loaded a real in-game save successfully.** Delta may display each GitHub build as a different game, because the ROM file changes between builds. The ROM cannot merge Delta saves for you.

## Safe iPhone update process

1. In the old Delta copy, save using the game's own **SAVE** menu (not just a Delta save state).
2. Long-press the old tile → **Manage Save File** → **Export Save File**.
3. Save the exported `.sav` in **Files**, with an identifiable name (e.g. `ShatteredRealms-before-build-25.sav`). Keep another backup in iCloud Drive when possible.
4. Download the new ROM at [latest Shattered Realms build](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest/download/ShatteredRealms.gba). Delta → **+** → Files → import.
5. New tile: long-press → **Manage Save File** → **Import Save File** → select the backed-up `.sav`.
6. Open the new game and select **Continue**. Check your party, money, badges, and position. Save **in game** again, quit Delta, reopen, and verify Continue still works.
7. Keep the old game and backup until fully verified.

If the new copy shows only **NEW GAME**, do not overwrite or delete the old copy. Check the exported `.sav`, import it into the right tile, and test again.

## Stable save structure and feature caveats

The current Shattered Realms gameplay patches do **not** change the persistent Pokémon move-slot count, `BoxPokemon`, `SaveBlock1`, `SaveBlock2`, or `SaveBlock3` layouts. The multi-page move library is reconstructed in battle from the four currently saved attacks and each species' previously unlocked level-up attacks. Previously forgotten TM/tutor moves are **not** permanently remembered yet.

The fourfold experience multiplier accelerates **battle EXP** instead of rewriting experience tables, preserving existing stored EXP. Hard-mode levels, money behavior, and infinite-item behavior are calculated or granted at runtime.

Companion following uses the existing Pokémon-follower configuration; its display and map transitions require in-game verification.

Every published GitHub release is kept as a separate tagged build so older ROM versions remain available through [Releases](https://github.com/travisejones28-alt/pokemon-enhanced/releases). GitHub can ensure a 32 MB ROM compiles, but **only gameplay testing in Delta** can validate saves across releases.

## Smoke test for each release

- Existing saved game: continue, party, bag, PC, map transition, save and load.
- New game: opening, choose Pikachu, Route 101 first battle and first trainer.
- All-Pokémon move pages: use SELECT, use an older unlocked attack, switch, cancel and reopen menu, then battle end and reload save.
- Hard trainer teams: adaptive levels, stronger AI, items disabled inside trainer battles.
- Field Bag: grant Rare Candies and item supply kit, reuse and re-open Bag.
- Overworld following: entering/exiting buildings, fishing, surfing, healing, fainting, Pokémon swapping.
