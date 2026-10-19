# Pokémon: Shattered Realms

A work-in-progress **GBA adventure** using [RHH's pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion) as the engine.

> **Status: Alpha 0.2 development — persistent move library and first Rift chapter; full campaign unfinished.**
> The original opening remains a prologue. Lumen Crossing, Riftway Trail, Stormscar and their quests extend it while preserving Hoenn progression.

Read the [chapter walkthrough](docs/CHAPTER_ONE.md), [persistent move-library details](docs/MOVE_HISTORY.md), and [implementation audit](docs/IMPLEMENTATION_AUDIT.md). Targeted mGBA regressions pass; a full chapter playthrough and real Delta save acceptance remain. See the [published build validation](docs/BUILD_VALIDATION.md).

## Implemented in Alpha 0.1

- Complete Emerald Expansion source included in **engine/**, pinned to upstream **1.17.1** (`bb1093a7c72d3961d9a37d8e02ad2abc2c866682`).
- Modern species data from **Generations 1–9** provided by the engine. This does **not** mean every species can already be caught.
- Cross-generation encounter tables for **14 early/midgame areas** (12 slots each; levels and encounter rates remain unchanged).
- Kadabra, Machoke, Haunter and Graveler evolve by level, without trading. Linking Cord alternatives remain available.
- Reusable TMs, modern Exp. Share key item, and evolution held items usable from the bag.
- Unique GBA header title/game code for identification in emulators.
- GitHub Actions has **successfully compiled and validated** the 32 MiB ROM in [build #59](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39326577859), including host tests, patch idempotency, targeted mGBA regressions, header checks and a SHA-256 manifest. Actual Delta save testing remains.

## Current main-branch gameplay changes

**Published in build #59. Full campaign, visual and real-save acceptance checks remain listed in the implementation audit.**

- Pikachu starter with strong signature attacks, plus a friendship-based bond move progression.
- Multi-page battle move libraries for every player Pokémon: current/saved attacks, level-appropriate current/pre-evolution attacks, compatible machine, tutor and egg moves. Ordinary compatible attacks are reconstructed; exceptional event/Sketch attacks have a persistent save-tail journal. SELECT advances and R goes back. See the documented 152-entry exceptional-attack limit.
- Unlimited PP for the player, no visible numeric PP display, unlimited wallet, reusable Rare Candies and field supply of Master Balls, Max Repels, Max Revives, Full Restores and Escape Ropes.
- 4× battle EXP without changing experience tables or existing stored levels.
- Hard-mode trainers: higher levels, adaptive scaling to your strongest Pokémon, stronger IVs, smarter AI, hidden ability possibilities, no Bag items, no escaping.
- Pokémon following with Pikachu Bond interaction messages, persistent Bond unlocks, better item descriptions and wild-battle controls.
- Explicit competitive sets for all eight first Gym fights, Elite Four, Champion and Vesper: abilities, natures, EVs, coverage and held items.
- All trade-evolution targets have a local item/level alternative in the current species sources; Karrablast and Shelmet now accept a Linking Cord.
- Opening story teaser featuring strange Rifts and Team Eclipse. A three-anomaly quest, Lumen hub with lodge/workshop/Gym, Riftway rival and scout, Rift Hollow boss, Astra badge and Stormscar legendary quest are implemented. Chapter playthrough testing and the full later campaign remain unfinished.

**Save protection:** See the [Delta save recovery and safe update checklist](docs/SAVE_COMPATIBILITY.md). Never delete the original game tile until you've imported and verified your previous save in the new version.

## Latest iPhone / Delta game download

**Direct game link (always latest successful build):**
https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest/download/ShatteredRealms.gba

Gameplay source changes on `main` run automated tests and build the `.gba` game. Passing builds are published to [GitHub Releases](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest) with the same filename each time. See [iPhone update instructions](docs/IPHONE_UPDATES.md) and the [save-preserving update guide](docs/SAVE_COMPATIBILITY.md) before importing a newer game in Delta.

**Save warning:** Modified ROM hashes can make Delta display a separate game, and some engine changes may make saves incompatible. Always export your old game's in-game save before importing an update.

## Build on GitHub (no PC necessary)

1. Go to **Actions** > **Build Shattered Realms**.
2. Select **Run workflow** (or open the [successful build #59](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39326577859)).
3. After the build succeeds, open the [latest release](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest) and download **ShatteredRealms.gba** (no ZIP extraction needed).
4. Import `ShatteredRealms.gba` with **Delta → + → Files** on iPhone.

For local builds, clone **this** repository, install the toolchain in the [upstream instructions](https://github.com/rh-hideout/pokeemerald-expansion/blob/expansion/1.17.1/INSTALL.md), then run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/apply_overrides.py --engine engine
make -C engine -j2 TITLE=SHATTERED GAME_CODE=BSRE FILE_NAME=shattered-realms
bash scripts/run_gba_tests.sh
python3 scripts/verify_rom.py engine/shattered-realms.gba
```

The script applies edits to the engine checkout, not to the six original GBC games. It is designed to be safe to run twice.

## Project layout

- `engine/` — entire Emerald Expansion 1.17.1 engine, assets, maps and tools
- `scripts/apply_overrides.py` — deterministic gameplay patches for the pinned engine
- `scripts/verify_rom.py` — built-ROM header and size validation
- `tests/` — regression tests for our customizations
- `.github/workflows/` — local engine compilation, tests, downloadable artifact and automatic Latest Release
- `docs/ROADMAP.md` — development milestones and acceptance criteria

The complete Emerald Expansion engine is now **committed in `engine/`**. GitHub Actions builds the local engine source and applies our Shattered Realms customizations. The six original Game Boy / Game Boy Color ROMs, if added separately, are not used as the GBA engine.

## Important

GitHub repository visibility is currently **public**. Change it to Private in repository Settings if that is your intent. Keep original ROMs/saves backed up; this project uses a different GBA engine and **Crystal `.sav` saves are not directly compatible**.

Credit: [RHH and contributors](https://github.com/rh-hideout/pokeemerald-expansion/blob/expansion/1.17.1/CREDITS.md). Pokémon and related assets belong to their respective rights holders. This is an unofficial fan-development project.

