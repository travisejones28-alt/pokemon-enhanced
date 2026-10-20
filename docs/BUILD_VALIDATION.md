# Build #65 validation — 19 October 2026 (America/Chicago)

Game source commit: `1ffb11c7bef4776b5e55f40b9ea0689b74379f1b`.

- [Successful GitHub Actions run](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39355319252)
- [Published release](https://github.com/travisejones28-alt/pokemon-enhanced/releases/tag/alpha0.1-build-65)
- [Permanent ROM download](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest/download/ShatteredRealms.gba)
- ROM: 33,554,432 bytes (32 MiB), title `SHATTERED`, game code `BSRE`.
- Published SHA-256: `f9a1bfacc5b8eca29bde2b0426e39223f717aa0588d3e16c052d9cfc88b33dcc`.

## Changes in this development pass

- Functional build-time Normal/Hard/Extreme profiles and switches for adaptive
  levels, global AI enhancements, unlimited PP, player move pages, battle EXP,
  unlimited wallet and free supplies. Preferred defaults retained.
- Finite-PP and replay/link battle menus display current/max PP again.
- Automatic level/evolution move learning retains full saved slots without
  repeatedly opening forget dialogs. Reconstructed moves remain available in
  the expanded library. Manual TM/relearning editors still edit four saved slots.
- Move-based evolution checks recognize attacks available in the move library.
- Competitive teams expanded from 14 to 36 encounters, including all mid/late
  Brendan/May starter branches, two Maxie fights, Archie and Victory Road Wally.
- Include transformations repaired to remain byte-idempotent when composed.

## Verification performed for this build

All following checks ran in GitHub Actions, not locally in this Windows session:

| Check | Result |
| --- | --- |
| Python regression suite and host C policy execution | Passed |
| Full staged override application and identical second application | Passed |
| Clean GBA ROM compilation | Passed |
| Targeted mGBA emulator regression suite | Passed |
| GBA title/game code, size, header checksum and SHA-256 packaging | Passed |
| Release publication and expected ROM asset | Confirmed |

New host C cases exercise Normal/Hard/Extreme with scaling on/off, supported
finite/unlimited PP and page combinations, invalid profile rejection and level
caps/egg exclusion. New mGBA tests exercise automatic learning without saved-slot
replacement and Tangela evolution using Ancient Power from the library.
Existing targeted tests include battle PP rules, move history, generated
old-save migration, party switching, blocked pages and persistent structure sizes.

## Save and identity findings

This update does not change persistent structures, species/map identifiers or
growth tables. Existing generated old-save migration and footprint tests pass.
A real exported Delta save was not supplied, so actual player-save compatibility
remains unverified.

Delta's [import implementation](https://github.com/rileytestut/Delta/blob/main/Delta/Database/DatabaseManager.swift)
uses a SHA-1 hash of the imported file as the game identifier. Stable naming and
GBA identifiers cannot prevent separate tiles after ROM contents change.
Export the in-game battery save from the old tile, import it into the updated
tile, verify Continue/party/PC/Bag/location/save/reload, and retain the old copy.
Do not rely on emulator save states for cross-build transfer.

## Remaining work and limits

- No full campaign/boss-balance or visual playthrough was performed.
- No physical GBA or actual iPhone/Delta test was performed.
- Enemies still have four active moves. Expanded enemy move selection is unfinished.
- Configuration is build-time, not an in-game settings menu.
- The default is 4x battle EXP, not literal quarter-size growth tables or 4x Day Care.
- Expanded pages require unlimited PP. The exceptional-move journal remains
  limited to 152 records; compatible attacks do not use those records.
- Full alternate-profile ROM/playthrough verification remains.
- Priority next: real Delta save acceptance, campaign balance, in-game settings,
  then safe enemy expanded-move mechanics.

See [gameplay settings](GAMEPLAY_SETTINGS.md), [save transfer](SAVE_COMPATIBILITY.md)
and [move history](MOVE_HISTORY.md).
