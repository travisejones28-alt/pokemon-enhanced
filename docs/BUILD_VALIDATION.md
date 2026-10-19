# Build #59 validation — 19 October 2026

Game source commit: `669bc9a6696dfb524fd0bb6874074651d66e8bff`.

- [GitHub Actions run](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39326577859)
- [Published release](https://github.com/travisejones28-alt/pokemon-enhanced/releases/tag/alpha0.1-build-59)
- [Permanent ROM download](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest/download/ShatteredRealms.gba)
- ROM size: 33554432 bytes (32 MiB).
- Published ROM SHA-256: `643e57af8c83f99b5c635d856e2bbdfd378aa7ee015c36949db5d2fdbe5a10c5`.
- Previous recovery ROM: [build #57](https://github.com/travisejones28-alt/pokemon-enhanced/releases/tag/alpha0.1-build-57).

## Results

| Check | Result |
| --- | --- |
| Python regression suite | 59 passed locally from the clean committed source; Actions gate passed |
| Full staged override application | Passed locally and in Actions |
| Second complete application makes no changes | Passed locally and in Actions |
| GBA compilation | Passed locally and in Actions |
| Targeted mGBA regressions | 17 passed locally; Actions gate passed |
| ROM title/game code | SHATTERED / BSRE |
| ROM size/header checksum/SHA-256 manifest | Passed |
| Release publication and expected ROM asset | Confirmed by release metadata |
| Full chapter/boss balance playthrough | Not performed |
| Follower map-transition visual checks | Not performed |
| Actual exported Delta save compatibility | Not performed; no player save supplied |

The GBA tests cover exceptional move retention through replacement, evolution
and PC storage; identity separation; journal capacity protection; friendship
unlock persistence; trade alternatives; single/double battle PP; Spite;
Transform; Encore; switching; blocked-page library recovery; and save footprint.
A generated old-format flash save is loaded, migrated, saved and reloaded while
checking party, Bag, position and the existing dexNavChain field. This is not a
real historical Delta save.

The upstream battle test harness uses replay controllers. Tests explicitly opt
into local-player policy through a TESTING-only adapter; a separate replay case
confirms ordinary PP depletion. The adapter is excluded from the production ROM.

ARM ABI probes comparing old/new persistent structures confirmed unchanged
SaveBlock1 (15568), SaveBlock2 (3884), PC storage (34144), Pokemon (100) and
BoxPokemon (80) byte sizes, plus sampled offsets. SaveBlock3 grows from 4 to
1540 bytes inside its existing 1624-byte reserved capacity. Existing species,
map/layout/region and trainer-flag indices are preserved.

This is a **compiled alpha with targeted emulator regressions**. It does not
establish every move/UI combination, real-save compatibility, or full campaign
balance. See [the implementation audit](IMPLEMENTATION_AUDIT.md),
[the chapter walkthrough](CHAPTER_ONE.md) and
[save backup/import instructions](SAVE_COMPATIBILITY.md).
Keep the old ROM tile and exported battery save until Continue, party, PC, Bag,
maps and saving/reloading have been verified on iPhone. New ROM contents can
produce another Delta tile; transfer the battery save manually, not a save state.
