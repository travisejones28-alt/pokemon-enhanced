"""Static campaign pacing checks for all rival paths and difficulty profiles.

These complement the compiled trainer-policy tests. They do not replace a
real playthrough or establish that any particular boss fight is fair.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEAMS = json.loads((ROOT / "scripts/boss_teams.json").read_text())
OWNERS = ("BRENDAN", "MAY")
STARTERS = ("MUDKIP", "TREECKO", "TORCHIC")
STAGES = ("ROUTE_110", "ROUTE_119", "LILYCOVE")
LEVELS = {
    "ROUTE_110": (18, 19, 19, 20),
    "ROUTE_119": (34, 34, 34, 34, 35),
    "LILYCOVE": (38, 39, 39, 39, 39, 40),
}
STARTER_COUNTER = {
    "MUDKIP": ("Grovyle", "Grovyle", "Sceptile"),
    "TREECKO": ("Combusken", "Combusken", "Blaziken"),
    "TORCHIC": ("Marshtomp", "Marshtomp", "Swampert"),
}


def difficulty_level(authored, profile):
    """Mirror fixed profile boosts (adaptive player floor is tested in C)."""
    if profile == "normal":
        return authored
    if profile == "hard":
        return min(100, authored * 11 // 10 + 1)
    if profile == "extreme":
        return min(100, authored * 5 // 4 + 2)
    raise ValueError(profile)


class TestCampaignBalance(unittest.TestCase):
    def test_all_six_rival_paths_have_rising_encounter_levels(self):
        for owner in OWNERS:
            for starter in STARTERS:
                path = []
                for stage_idx, stage in enumerate(STAGES):
                    key = f"TRAINER_{owner}_{stage}_{starter}"
                    with self.subTest(key=key):
                        self.assertIn(key, TEAMS)
                        party = TEAMS[key]
                        levels = tuple(mon["level"] for mon in party)
                        self.assertEqual(levels, LEVELS[stage])
                        self.assertEqual(party[-1]["species"], STARTER_COUNTER[starter][stage_idx])
                        path.append((min(levels), max(levels), len(levels)))
                self.assertTrue(path[0][1] < path[1][0] < path[1][1] < path[2][0])
                self.assertEqual(tuple(size for _, _, size in path), (4, 5, 6))

    def test_midgame_rivals_match_neighboring_gym_pacing(self):
        norman_ace = max(mon["level"] for mon in TEAMS["TRAINER_NORMAN_1"])
        winona_ace = max(mon["level"] for mon in TEAMS["TRAINER_WINONA_1"])
        juan_ace = max(mon["level"] for mon in TEAMS["TRAINER_JUAN_1"])
        for profile in ("normal", "hard", "extreme"):
            for owner in OWNERS:
                for starter in STARTERS:
                    route = TEAMS[f"TRAINER_{owner}_ROUTE_119_{starter}"]
                    lily = TEAMS[f"TRAINER_{owner}_LILYCOVE_{starter}"]
                    route_ace = difficulty_level(route[-1]["level"], profile)
                    lily_ace = difficulty_level(lily[-1]["level"], profile)
                    self.assertLessEqual(difficulty_level(norman_ace, profile) - route_ace, 2)
                    self.assertGreaterEqual(lily_ace, difficulty_level(winona_ace, profile))
                    self.assertLess(lily_ace, difficulty_level(juan_ace, profile))

    def test_rival_evolved_species_not_early_at_default_levels(self):
        for owner in OWNERS:
            for starter in STARTERS:
                route = TEAMS[f"TRAINER_{owner}_ROUTE_119_{starter}"]
                lily = TEAMS[f"TRAINER_{owner}_LILYCOVE_{starter}"]
                route_by_species = {mon["species"]: mon["level"] for mon in route}
                self.assertGreaterEqual(route_by_species["Staraptor"], 34)
                self.assertGreaterEqual(route_by_species["Gardevoir"], 30)
                self.assertGreaterEqual(route_by_species["Magneton"], 30)
                self.assertGreaterEqual(lily[-1]["level"], 36)

    def test_profile_progression_stays_below_level_cap(self):
        gyms = ("ROXANNE_1", "BRAWLY_1", "WATTSON_1", "FLANNERY_1",
                "NORMAN_1", "WINONA_1", "TATE_AND_LIZA_1", "JUAN_1")
        for profile in ("normal", "hard", "extreme"):
            peaks = []
            for gym in gyms:
                party = TEAMS[f"TRAINER_{gym}"]
                self.assertTrue(all(1 <= difficulty_level(mon["level"], profile) <= 100
                                    for mon in party))
                peaks.append(max(difficulty_level(mon["level"], profile) for mon in party))
            self.assertEqual(peaks, sorted(peaks))
            elite = ("SIDNEY", "PHOEBE", "GLACIA", "DRAKE", "WALLACE")
            finale = [max(difficulty_level(mon["level"], profile)
                          for mon in TEAMS[f"TRAINER_{boss}"]) for boss in elite]
            self.assertEqual(finale, sorted(finale))
            self.assertLess(peaks[-1], finale[0])


if __name__ == "__main__":
    unittest.main()
