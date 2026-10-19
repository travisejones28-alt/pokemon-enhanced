# Pokémon: Shattered Realms

A work-in-progress **GBA adventure** using [RHH's pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion) as the engine.

> **Status: Alpha 0.1 — engine and gameplay prototype, NOT a new region or completed story.**
> The prototype still uses Emerald's maps and major events. Our Pikachu starter and a Team Eclipse/rift story teaser are layered onto that opening; a new region and full quest campaign are not finished.

See the [current implementation audit and remaining work](docs/IMPLEMENTATION_AUDIT.md). Automated builds do not establish gameplay or old-save compatibility.

## Implemented in Alpha 0.1

- Complete Emerald Expansion source included in **engine/**, pinned to upstream **1.17.1** (`bb1093a7c72d3961d9a37d8e02ad2abc2c866682`).
- Modern species data from **Generations 1–9** provided by the engine. This does **not** mean every species can already be caught.
- Cross-generation encounter tables for **14 early/midgame areas** (12 slots each; levels and encounter rates remain unchanged).
- Kadabra, Machoke, Haunter and Graveler evolve by level, without trading. Linking Cord alternatives remain available.
- Reusable TMs, modern Exp. Share key item, and evolution held items usable from the bag.
- Unique GBA header title/game code for identification in emulators.
- GitHub Actions has **successfully compiled and validated** a 32 MiB `.gba` artifact for Delta on iOS ([verified build](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39269721177)). Emulator gameplay and save/load testing remain to be done.

## Current main-branch gameplay changes

**Source changes still require a successful ROM build and gameplay testing before they appear in Delta.**

- Pikachu starter with strong signature attacks, plus a friendship-based bond move progression.
- Multi-page battle move libraries for every player Pokémon: current/saved attacks, level-appropriate current/pre-evolution attacks, compatible machine and egg moves, and curated tutors. SELECT switches pages. This is a reconstructed catalog; persistent learned-move history is unfinished.
- Unlimited PP for the player, no visible numeric PP display, unlimited wallet, reusable Rare Candies and field supply of Master Balls, Max Repels, Max Revives, Full Restores and Escape Ropes.
- 4× battle EXP without changing experience tables or existing stored levels.
- Hard-mode trainers: higher levels, adaptive scaling to your strongest Pokémon, stronger IVs, smarter AI, hidden ability possibilities, no Bag items, no escaping.
- Built-in Pokémon following enabled, better item descriptions and wild-battle controls.
- Opening story teaser featuring strange Rifts and Team Eclipse. A three-anomaly quest, Rift Hollow and Eclipse boss, and first Gym replacement are present in source but need playtesting. A new hometown and full original campaign remain unfinished.

**Save protection:** See the [Delta save recovery and safe update checklist](docs/SAVE_COMPATIBILITY.md). Never delete the original game tile until you've imported and verified your previous save in the new version.

## Latest iPhone / Delta game download

**Direct game link (always latest successful build):**
https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest/download/ShatteredRealms.gba

Every source change on `main` runs automated tests and builds the `.gba` game. Passing builds are published to [GitHub Releases](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest) with the same filename each time. The link does not work until the first release has finished publishing. See [iPhone update instructions](docs/IPHONE_UPDATES.md) and the [save-preserving update guide](docs/SAVE_COMPATIBILITY.md) before importing a newer game in Delta.

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

