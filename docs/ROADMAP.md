# Shattered Realms Roadmap

## Alpha 0.1 — Gameplay prototype
- [x] Stable pinned upstream engine and automated GBA build setup
- [x] All Gen 1–9 species data included through engine defaults
- [x] Rift-mixed wild Pokémon encounters across Routes 101, 102 and 103
- [x] Reusable TMs and modern Exp. Share
- [x] No-trade level-up evolution for Kadabra, Machoke, Haunter, Graveler
- [ ] Confirm complete GBA build and emulator smoke test

## Alpha 0.2 — Actual new game opening
- [ ] New title screen graphics and intro dialogue
- [ ] Rebuilt starter/rival teams across multiple generations
- [ ] World map plan and playable first original map
- [ ] Original Team Eclipse introduction; maintain save compatibility where feasible
- [ ] Event flags and save-data layout design

## Alpha 0.3 — First story chapter
- [ ] First custom town and routes with maps, NPCs, shops, encounters
- [ ] First rival battle and a chapter finale
- [ ] Quest log baseline and three side missions
- [ ] Wild encounter balance, level curve, encounter tracking

## Alpha 0.4+ — Progression and content
- [ ] Expand regions rather than simply porting nine full maps
- [ ] All species obtainable through a planned distribution and quest system
- [ ] Legendary questlines and rift dungeon architecture
- [ ] Advanced battle AI and scalable difficulty
- [ ] Optional debug/cheat menu separate from normal gameplay
- [ ] iPhone/Delta save migration testing each release

## Technical constraints
- GBA engine capacity is limited (32 MB ROM without special expansion).
- Generations 1–9 being defined in the engine does not mean they are distributed in the map.
- Keep story/maps separate from engine and pin upstream revision. Update engine only with deliberate tests.
- Keep downloaded engine sources out of this repo; workflow obtains them at build time.
- A completed fresh game with original regions is a large multi-release project, not the current alpha.
