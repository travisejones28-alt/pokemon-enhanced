# Pokémon: Shattered Realms

A work-in-progress **GBA adventure** using [RHH's pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion) as the engine.

> **Status: Alpha 0.1 — engine and gameplay prototype, NOT a new region or completed story.**
> The current prototype still uses the Emerald overworld/story and original starter/rival sequence.

## Implemented in Alpha 0.1

- Reproducible build pinned to pokeemerald-expansion **1.17.1** (`bb1093a7c72d3961d9a37d8e02ad2abc2c866682`).
- Modern species data from **Generations 1–9** provided by the engine. This does **not** mean every species can already be caught.
- Cross-generation encounter tables for **Routes 101–103** (12 slots each; levels and encounter rates remain unchanged).
- Kadabra, Machoke, Haunter and Graveler evolve by level, without trading. Linking Cord alternatives remain available.
- Reusable TMs, modern Exp. Share key item, and evolution held items usable from the bag.
- Unique GBA header title/game code for identification in emulators.
- GitHub Actions builds a `.gba` artifact that can be imported into Delta on iOS.

## Build on GitHub (no PC necessary)

1. Go to **Actions** > **Build Shattered Realms**.
2. Select **Run workflow** (or wait for a source push).
3. After the build job succeeds, open its run page and download the **ShatteredRealms-Alpha0.1-GBA** artifact.
4. Extract the ZIP using Files on iPhone, then import `ShatteredRealms-Alpha0.1.gba` into Delta.

For local builds, install the toolchain in the [upstream instructions](https://github.com/rh-hideout/pokeemerald-expansion/blob/expansion/1.17.1/INSTALL.md), clone the pinned upstream engine into `engine/`, then run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/apply_overrides.py --engine engine
make -C engine -j2 TITLE=SHATTERED GAME_CODE=BSRE FILE_NAME=shattered-realms
python3 scripts/verify_rom.py engine/shattered-realms.gba
```

The script applies edits to the engine checkout, not to the six original GBC games. It is designed to be safe to run twice.

## Project layout

- `scripts/apply_overrides.py` — deterministic gameplay patches for the pinned engine
- `scripts/verify_rom.py` — built-ROM header and size validation
- `tests/` — regression tests for our customizations
- `.github/workflows/` — engine checkout, compilation, and downloadable build
- `docs/ROADMAP.md` — milestones and future features

The large upstream engine is **downloaded automatically** when building; it is not duplicated into this repository. The six original Game Boy / Game Boy Color ROMs, if added separately, are not used as the GBA engine.

## Important

GitHub repository visibility is currently **public**. Change it to Private in repository Settings if that is your intent. Keep original ROMs/saves backed up; this project uses a different GBA engine and **Crystal `.sav` saves are not directly compatible**.

Credit: [RHH and contributors](https://github.com/rh-hideout/pokeemerald-expansion/blob/expansion/1.17.1/CREDITS.md). Pokémon and related assets belong to their respective rights holders. This is an unofficial fan-development project.
