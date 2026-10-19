# Pokémon: Shattered Realms

A work-in-progress **GBA adventure** using [RHH's pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion) as the engine.

> **Status: Alpha 0.1 — engine and gameplay prototype, NOT a new region or completed story.**
> The current prototype still uses the Emerald overworld/story and original starter/rival sequence.

## Implemented in Alpha 0.1

- Complete Emerald Expansion source included in **engine/**, pinned to upstream **1.17.1** (`bb1093a7c72d3961d9a37d8e02ad2abc2c866682`).
- Modern species data from **Generations 1–9** provided by the engine. This does **not** mean every species can already be caught.
- Cross-generation encounter tables for **Routes 101–103** (12 slots each; levels and encounter rates remain unchanged).
- Kadabra, Machoke, Haunter and Graveler evolve by level, without trading. Linking Cord alternatives remain available.
- Reusable TMs, modern Exp. Share key item, and evolution held items usable from the bag.
- Unique GBA header title/game code for identification in emulators.
- GitHub Actions has **successfully compiled and validated** a 32 MiB `.gba` artifact for Delta on iOS ([verified build](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39269721177)). Emulator gameplay and save/load testing remain to be done.

## Latest iPhone / Delta game download

**Direct game link (always latest successful build):**
https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest/download/ShatteredRealms.gba

Every source change on `main` runs automated tests and builds the `.gba` game. Passing builds are published to [GitHub Releases](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest) with the same filename each time. The link does not work until the first release has finished publishing. See [iPhone update & save instructions](docs/IPHONE_UPDATES.md) before replacing a game in Delta.

**Save warning:** Modified ROM hashes can make Delta display a separate game, and some engine changes may make saves incompatible. Always export your old game's in-game save before importing an update.

## Build on GitHub (no PC necessary)

1. Go to **Actions** > **Build Shattered Realms**.
2. Select **Run workflow** (or open the [successful Alpha 0.1 run](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39269721177)).
3. After the build succeeds, open the [latest release](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest) and download **ShatteredRealms.gba** (no ZIP extraction needed).
4. Import `ShatteredRealms.gba` with **Delta → + → Files** on iPhone.

For local builds, clone **this** repository, install the toolchain in the [upstream instructions](https://github.com/rh-hideout/pokeemerald-expansion/blob/expansion/1.17.1/INSTALL.md), then run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/apply_overrides.py --engine engine
make -C engine -j2 TITLE=SHATTERED GAME_CODE=BSRE FILE_NAME=shattered-realms
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
