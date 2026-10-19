# Emerald Expansion source provenance

Source: https://github.com/rh-hideout/pokeemerald-expansion
Pinned release: `expansion/1.17.1`
Pinned commit: `bb1093a7c72d3961d9a37d8e02ad2abc2c866682`
Destination: `engine/` in `travisejones28-alt/pokemon-enhanced`.

All tracked engine contents were copied from that pinned upstream Git checkout via GitHub Actions, excluding the nested Git metadata only. The source includes build tools, graphics, battle mechanics, maps, data, and documentation.

Shattered Realms overrides live in `scripts/apply_overrides.py` and apply before building. A later milestone may move stabilized changes directly to the engine source after tests are in place. Engine upgrades must be deliberate and re-tested.

The project is an unofficial fan work. Preserve upstream author credit and review any rights/redistribution considerations.
