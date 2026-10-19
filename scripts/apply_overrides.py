#!/usr/bin/env python3
"""Deterministic Alpha 0.1 changes for RHH pokeemerald-expansion 1.17.1.

Only writes to a separately checked-out engine directory. Fails closed when
expected data/definitions are missing, to avoid silently applying to a new
incompatible engine version.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ENGINE_VERSION = "expansion/1.17.1"

# Slot indices preserve upstream encounter rates, distribution and levels.
# This is our first small Rift prototype, not a fully rebalanced world.
ROUTE_SPECIES = {
    "MAP_ROUTE101": {
        0: "SPECIES_SENTRET",       # Gen 2
        2: "SPECIES_SHINX",        # Gen 4
        3: "SPECIES_FLETCHLING",   # Gen 6
        4: "SPECIES_ROOKIDEE",     # Gen 8
        5: "SPECIES_LECHONK",      # Gen 9
        6: "SPECIES_ROWLET",       # Gen 7
        7: "SPECIES_LILLIPUP",     # Gen 5
        8: "SPECIES_FROAKIE",      # Gen 6
        9: "SPECIES_RIOLU",        # Gen 4
        10: "SPECIES_SPRIGATITO",  # Gen 9
        11: "SPECIES_EEVEE",       # Gen 1
    },
    "MAP_ROUTE102": {
        1: "SPECIES_PIDOVE",
        3: "SPECIES_BUNEARY",
        5: "SPECIES_SEWADDLE",
        7: "SPECIES_WOOLOO",
        8: "SPECIES_PAWMI",
        10: "SPECIES_FENNEKIN",
        11: "SPECIES_SANDILE",
    },
    "MAP_ROUTE103": {
        1: "SPECIES_ROCKRUFF",
        3: "SPECIES_AXEW",
        5: "SPECIES_PANCHAM",
        7: "SPECIES_IMPIDIMP",
        9: "SPECIES_MAREEP",
        10: "SPECIES_DREEPY",
        11: "SPECIES_TADBULB",
    },
}

CONFIG = {
    "include/config/item.h": {
        "I_REUSABLE_TMS": "TRUE",
        "I_USE_EVO_HELD_ITEMS_FROM_BAG": "TRUE",
        "I_EXP_SHARE_ITEM": "GEN_6",
    },
    "include/config/general.h": {
        "EXPANSION_INTRO": "FALSE",
    },
    "include/config/text.h": {
        "TEXT_SPEED_FAST_MODIFIER": "3",
    },
}

# Retain the Linking Cord method as a second, early-evolution option.
TRADE_EVOLUTIONS = {
    "SPECIES_ALAKAZAM": 37,
    "SPECIES_MACHAMP": 40,
    "SPECIES_GENGAR": 38,
    "SPECIES_GOLEM": 38,
}


def modify_defines(contents: str, changes: dict[str, str]) -> str:
    for key, value in changes.items():
        regex = re.compile(r"(?m)^(\s*#define\s+" + re.escape(key) + r"\s+)(\S+)")
        matches = list(regex.finditer(contents))
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one #define for {key}, found {len(matches)}")
        contents = regex.sub(lambda m: m.group(1) + value, contents, count=1)
    return contents


def modify_evolutions(contents: str) -> str:
    for species, level in TRADE_EVOLUTIONS.items():
        original = "{EVO_TRADE, 0, " + species + "}"
        replacement = "{EVO_LEVEL, " + str(level) + ", " + species + "}"
        old_count = contents.count(original)
        new_count = contents.count(replacement)
        if old_count == 1:
            contents = contents.replace(original, replacement, 1)
        elif new_count != 1:
            raise ValueError(f"Unexpected evolution format: {species}")
    return contents


def modify_encounters(contents: str) -> str:
    parsed = json.loads(contents)
    groups = [g for g in parsed["wild_encounter_groups"] if g.get("label") == "gWildMonHeaders"]
    if len(groups) != 1:
        raise ValueError("Expected gWildMonHeaders encounter group")
    entries = groups[0]["encounters"]
    for route, slots in ROUTE_SPECIES.items():
        matches = [e for e in entries if e.get("map") == route]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one encounter table for {route}")
        mons = matches[0]["land_mons"]["mons"]
        if len(mons) != 12:
            raise ValueError(f"Expected 12 land slots for {route}; got {len(mons)}")
        for slot, species in slots.items():
            mons[slot]["species"] = species
    return json.dumps(parsed, indent=2, ensure_ascii=False) + "\n"


def apply(engine: Path) -> None:
    if not (engine / "Makefile").is_file():
        raise FileNotFoundError(f"Missing pokeemerald-expansion Makefile: {engine}")
    updates: dict[Path, str] = {}
    for relative_path, changes in CONFIG.items():
        path = engine / relative_path
        updates[path] = modify_defines(path.read_text(encoding="utf-8"), changes)
    species_file = engine / "src/data/pokemon/species_info/gen_1_families.h"
    updates[species_file] = modify_evolutions(species_file.read_text(encoding="utf-8"))
    encounter_file = engine / "src/data/wild_encounters.json"
    updates[encounter_file] = modify_encounters(encounter_file.read_text(encoding="utf-8"))

    # Don't partially write if validation fails.
    for path, content in updates.items():
        if path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
            print("Updated", path)
    print("Shattered Realms Alpha 0.1 overrides applied")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path, required=True, help="Path to expansion checkout")
    args = parser.parse_args()
    apply(args.engine.resolve())


if __name__ == "__main__":
    main()
