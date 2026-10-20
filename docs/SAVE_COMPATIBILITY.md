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

## Current save structures and migration

SaveBlock1, SaveBlock2, party Pokémon, Box Pokémon and PC storage retain their
previous sizes and offsets. Species indices and original map/layout/region IDs
are preserved. The journal extends only the existing reserved SaveBlock3 tail:
4 bytes becomes 1,540 bytes within its 1,624-byte sector-chunk capacity. See
[MOVE_HISTORY.md](MOVE_HISTORY.md) for integrity checks, blank-tail migration and
the 152-entry exceptional-attack limit.

The library reconstructs current/pre-evolution level, evolution, machine/tutor
and egg moves. Exceptional event/Sketch attacks have a persistent journal keyed
by full trainer ID and personality. It cannot recover unknown moves forgotten
before this journal existed. Transform and Mimic remain battle-only, and Encore
holds the current slots. Numeric PP is replaced by page information.

Battle EXP is multiplied instead of changing saved experience tables. Existing
levels remain as saved. Field supplies add absent entries only; free space and
reopen the Bag if a pocket was full.

New maps and three new region sections append after existing IDs; NONE stays
209. New trainers fit the existing 864-trainer flag capacity. Old saves reach
Lumen through Elara in Littleroot after obtaining a Pokémon partner. No new game
is intentionally required.

## Verification and limits

ARM ABI probes confirm unchanged persistent Pokémon, PC and main-save sizes and
offsets. The automated suite includes the production journal codec and a
generated older-format save/load/migrate/save/load test in mGBA. A generated
fixture does not prove compatibility with every real Delta save. See the exact
recorded results in [BUILD_VALIDATION.md](BUILD_VALIDATION.md).

Before accepting an update, check Continue, party, PC, Bag, badges, map changes,
saving and a fresh reload. Also verify an archived attack after evolution and
PC deposit/withdrawal. Follower and full chapter playthrough checks remain.

## Downgrade and recovery

Every release remains separately tagged. Keep the old ROM and untouched exported
pre-update save. Older ROMs do not know the new map IDs or journal. Do not load a
save situated in a new map with an old ROM. Recover using the pre-update backup.
Saving in an older ROM can clear the journal. Do not overwrite your only backup.

An unchanged filename, title or game code cannot guarantee one Delta tile:
changed ROM contents can change Delta's game identity. Transfer the exported
in-game battery save manually. Save states contain ROM-dependent RAM and should
not be used for cross-build transfers.

## Build 65 update

No save-layout change was introduced in this update. Generated old-save migration
and save-footprint regression gates passed in Actions. Actual exported player
saves still need acceptance testing. Delta's import code computes the ROM SHA-1
as its identifier; see [DatabaseManager.swift](https://github.com/rileytestut/Delta/blob/main/Delta/Database/DatabaseManager.swift).
Stable ROM names do not preserve that hash when the game changes.
