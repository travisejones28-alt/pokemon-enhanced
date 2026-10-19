# Pokémon: Shattered Realms — Development Roadmap

## Current reality (19 October 2026)

The full **pokeemerald-expansion 1.17.1** source is committed under `engine/`, and its Git tree exactly matches pinned upstream commit `bb1093a7c72d3961d9a37d8e02ad2abc2c866682`.

**Alpha 0.1 is a gameplay prototype, not a finished original adventure.** It still uses Emerald's story and world. Modern Pokémon species data is present, but we must deliberately make each species obtainable.

### Alpha 0.1 — Build and test baseline
- [x] Copy every upstream tracked engine file into `engine/`.
- [x] Retain six original GB/GBC game ROMs without altering them.
- [x] Pin the engine revision and create a GitHub build workflow.
- [x] Add all-generation wild Pokémon encounters on Routes 101–103.
- [x] Add reusable TMs, evolution items usable from the Bag, and level-up alternatives for four trade evolutions.
- [x] Configure a dedicated flag for the modern Exp. Share.
- [x] Add regression tests and GBA header checks.
- [x] **Successful end-to-end GitHub build and downloadable `.gba`**, verified in GitHub Actions run [39269721177](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39269721177).
- [ ] **Smoke test on Delta**: new game, starter, encounter, capture, battle, save/reload, basic menus.
- [ ] Record built **ROM** SHA-256 (separate from downloadable artifact ZIP digest) and tested Delta version.
- [ ] Investigate non-blocking upstream PNG `bKGD: invalid index` warnings as graphics are replaced (build currently passes).

### Alpha 0.2 — The first *new* game experience
- [ ] Original title/intro and Team Eclipse teaser.
- [ ] Design starter choices across generations; balance three rival paths.
- [ ] One new hometown, starter event and nearby original route.
- [ ] New encounters, trainers, signposts, NPC dialogue and item placement.
- [ ] First mysterious rift encounter / encounter cinematic.
- [ ] Verify start-to-first-town experience and save continuity.

### Alpha 0.3 — Chapter One (1–3 hour vertical slice)
- [ ] Original first gym, leader battle and badge reward.
- [ ] Three complete new maps with shortcuts, hidden secrets and optional paths.
- [ ] Three quests plus visible quest progress.
- [ ] First boss or rare Pokémon hunt with a unique reward.
- [ ] Balance wild encounters, XP, evolution and difficulty settings.
- [ ] Complete playthrough and emulator compatibility testing.

### Alpha 0.4 — Expanded Pokémon systems
- [ ] Full evolution-method audit: no mandatory trades.
- [ ] Phased generation-by-generation wild, gift, egg and quest distribution plan.
- [ ] Better Dex search, encounter hints, storage and collection goals.
- [ ] Mega Evolution unlock quest and progression gating.
- [ ] Legendary quests, shiny-hunt incentives, and difficulty modes.

### Beta — Shattered Realms world
- [ ] Distinct interconnected Rift Realm with towns, caves and dungeons.
- [ ] Curated return trips to classic regions, initially Johto and Kanto.
- [ ] Team Eclipse storyline, branching encounters and rival arcs.
- [ ] Champions Tournament, Battle Tower, and substantial endgame content.
- [ ] Completionist routes to every supported Pokémon.
- [ ] Full playthrough, balance, save migration and performance pass.

## Technical standards

1. Make small, testable commits; do not silently replace the pinned engine.
2. Source is now **vendored into `engine/`**; build from that source instead of automatically downloading another copy.
3. Keep original GB/GBC ROMs untouched. Shattered Realms is a **new GBA game**, not a patched Crystal save.
4. Pokémon being defined in species data does not make them catchable; test every encounter, evolution and gift.
5. Avoid save-data layout and species-index changes after saves are distributed unless a migration is supplied.
6. Keep the game playable on Delta and within actual GBA ROM/hardware limitations.
7. Maintain RHH contributor credits and respect the project's licenses.
8. If this is for personal use, **change repository visibility to Private**: the repository was public during inspection.
