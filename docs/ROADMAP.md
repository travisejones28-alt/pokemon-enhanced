# Shattered Realms — Game Plan

**Goal:** a genuinely new single-player GBA Pokémon adventure that runs in Delta on iPhone, built on Emerald Expansion 1.17.1.

## Stage 1 — Engine and first playable build (Alpha 0.1)
- [x] Copy all Emerald Expansion source files into `engine/`.
- [x] Keep the original six GBC files untouched.
- [x] Configure starter prototype: mixed-generation wild encounters on Emerald Routes 101–103; no-trade level evolutions for Kadabra, Haunter, Machoke and Graveler; reusable TMs; modern experience share.
- [x] Set up build automation and regression tests.
- [ ] **Gate:** build must complete, ROM header must pass, and game must boot/save/load on Delta.
- [ ] Smoke-test wild encounter slot distribution, trade-free evolutions and player options.

The Alpha 0.1 prototype is NOT yet the full new game. It retains Emerald's existing map and story.

## Stage 2 — New game opening (Alpha 0.2)
- [ ] Replace the opening with an original **Team Eclipse / dimensional rift** setup.
- [ ] Design a new hometown and first original route (new mapping and scripted NPCs).
- [ ] Choose three new cross-generation starter Pokémon.
- [ ] Add an original rival, first battle, and scripted rift encounter.
- [ ] New title-screen art and game intro.
- [ ] **Gate:** 30 minutes of original, completable gameplay on Delta.

## Stage 3 — Complete first chapter (Alpha 0.3)
- [ ] Original regional map structure: at least 3 towns, 4 routes and 2 dungeons.
- [ ] New gym or major boss, custom trainer teams, and first legendary clue.
- [ ] Quest journal prototype, side missions, and story flags.
- [ ] Difficulty settings and tuned level curve.
- [ ] HM-free exploration design with story-appropriate abilities or key items.
- [ ] **Gate:** 2–3 hours of original progression with no progression softlocks.

## Stage 4 — Collection and advanced combat (Alpha 0.4)
- [ ] Catalog obtainability for each implemented Pokémon, Generation 1–9.
- [ ] Remove *all* mandatory trading requirements, not only the first four.
- [ ] Integrate regional forms, new evolutions and available mega evolutions.
- [ ] Add trainer rematches, scalable AI and optional harder difficulty.
- [ ] Upgrade Pokémon storage, move relearner and accessible evolution items.
- [ ] Balance shiny odds, rare encounters and XP progression.

## Stage 5 — Shattered Realms world expansion
- [ ] New region and interconnected rift dungeons; selectively revisit changed Johto/Kanto/Hoenn.
- [ ] Legendary questlines for Celebi, Mewtwo, Rayquaza, Giratina and more.
- [ ] Rare world events, environmental puzzles, hidden laboratories and boss phases.
- [ ] Battle Tower, Champion challenges, postgame and New Game+ (only after save compatibility review).
- [ ] National Dex distribution and late-game completion rewards.

## Development rules
1. **Source of truth:** all upstream game code/assets in `engine/`; Shattered Realms scripts/tests/docs alongside them.
2. **Never overwrite the six original GB/GBC ROMs.** They aren't the GBA source engine.
3. **Quality over size:** a polished small original region is more valuable than nine copied regions.
4. **Every milestone gets:** GitHub commit(s), repeatable build, unit tests, GBA boot/save check, and release notes.
5. **Mobile first:** validate with Delta touch controls, save/load, stable gameplay and playable performance.
6. **ROM constraints:** monitor 32 MiB GBA size, event flag allocations, memory, sprite limits and save format.
7. **Save compatibility:** never silently change data layouts; document when a fresh save is required.
8. **Credits:** preserve the upstream engine's credits and document any third-party content.

**Next build target:** Alpha 0.1 must compile successfully. After that the focus shifts to Stage 2 rather than stacking extra cheat features on Emerald.
