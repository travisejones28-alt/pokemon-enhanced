"""Regression tests for Shattered Realms transformations."""
import json
import unittest

from scripts.apply_overrides import (
    CONFIG,
    ROUTE_SPECIES,
    TRADE_EVOLUTIONS,
    modify_defines,
    modify_encounters,
    modify_evolutions,
)


class TestOverrides(unittest.TestCase):
    def test_defines_exact_target_only(self):
        data = "#define I_REUSABLE_TMS FALSE // comment\n#define I_OTHER FALSE\n"
        changed = modify_defines(data, {"I_REUSABLE_TMS": "TRUE"})
        self.assertIn("#define I_REUSABLE_TMS TRUE // comment", changed)
        self.assertIn("#define I_OTHER FALSE", changed)
        self.assertEqual(modify_defines(changed, {"I_REUSABLE_TMS": "TRUE"}), changed)

    def test_fail_closed_missing_define(self):
        with self.assertRaises(ValueError):
            modify_defines("#define OTHER TRUE\n", {"I_REUSABLE_TMS": "TRUE"})

    def test_evolution_idempotence(self):
        original = "\n".join(
            "{EVO_TRADE, 0, " + s + "}" for s in TRADE_EVOLUTIONS
        )
        changed = modify_evolutions(original)
        self.assertNotIn("EVO_TRADE", changed)
        self.assertEqual(modify_evolutions(changed), changed)
        for species, level in TRADE_EVOLUTIONS.items():
            self.assertIn(f"{{EVO_LEVEL, {level}, {species}}}", changed)

    def test_encounters(self):
        entries = []
        for route in ROUTE_SPECIES:
            entries.append({
                "map": route,
                "land_mons": {
                    "mons": [
                        {"min_level": 2, "max_level": 3, "species": "SPECIES_WURMPLE"}
                        for _ in range(12)
                    ],
                },
            })
        data = json.dumps({"wild_encounter_groups": [
            {"label": "gWildMonHeaders", "encounters": entries},
        ]})
        after = modify_encounters(data)
        self.assertEqual(modify_encounters(after), after)
        modified = json.loads(after)["wild_encounter_groups"][0]["encounters"]
        for entry in modified:
            for slot, name in ROUTE_SPECIES[entry["map"]].items():
                self.assertEqual(entry["land_mons"]["mons"][slot]["species"], name)
            self.assertEqual(entry["land_mons"]["mons"][0]["min_level"], 2)
            self.assertEqual(entry["land_mons"]["mons"][0]["max_level"], 3)


if __name__ == "__main__":
    unittest.main()
