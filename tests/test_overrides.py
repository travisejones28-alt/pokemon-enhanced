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
    modify_starter_choices,
    modify_starter_gift,
    modify_player_battle_pp,
    modify_player_pp_checks,
    modify_move_pp_display,
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

    def test_exp_share_has_required_persistent_flag(self):
        item_settings = CONFIG["include/config/item.h"]
        self.assertEqual(item_settings["I_EXP_SHARE_ITEM"], "GEN_6")
        self.assertEqual(item_settings["I_EXP_SHARE_FLAG"], "FLAG_UNUSED_0x264")

    def test_no_unexpected_route_indices(self):
        for slots in ROUTE_SPECIES.values():
            self.assertTrue(all(isinstance(index, int) and 0 <= index < 12 for index in slots))

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



    def test_pikachu_starter_selector(self):
        original = "    GRASS_STARTER,\n    FIRE_STARTER,\n    WATER_STARTER,"
        result = modify_starter_choices(original)
        self.assertIn("SPECIES_PIKACHU", result)
        self.assertNotIn("    FIRE_STARTER,", result)
        self.assertEqual(result, modify_starter_choices(result))

    def test_pikachu_signature_moves_only_on_gift(self):
        original = (
            '#include "palette.h"\n'
            "    ScriptGiveMon(starterMon, 5, ITEM_NONE);\n"
            "    ResetTasks();"
        )
        result = modify_starter_gift(original)
        for move in ("THUNDERBOLT", "VOLT_TACKLE", "SURF", "EXTREME_SPEED"):
            self.assertIn("MOVE_" + move, result)
        self.assertIn("starterMon == SPECIES_PIKACHU", result)
        self.assertEqual(result, modify_starter_gift(result))

    def test_unlimited_pp_only_for_player(self):
        original = (
            "            RecordedBattle_CopyBattlerMoves(battler);\n"
            "            gBattleCommunication[battler] = STATE_BEFORE_ACTION_CHOSEN;"
        )
        result = modify_player_battle_pp(original)
        self.assertIn("IsOnPlayerSide(battler)", result)
        self.assertIn("!BattlerHasAi(battler)", result)
        self.assertIn("SetMonData(partyMon, MON_DATA_PP1 + i, &maxPP)", result)
        self.assertEqual(result, modify_player_battle_pp(result))

    def test_player_pp_exempt_but_enemy_still_checked(self):
        original = (
            "    if (gBattleMons[battler].pp[moveId] == 0)\n"
            "    {\n"
            "else if (check & MOVE_LIMITATION_PP && gBattleMons[battler].pp[i] == 0)"
        )
        result = modify_player_pp_checks(original)
        self.assertIn("&& !IsOnPlayerSide(battler)", result)
        self.assertEqual(result, modify_player_pp_checks(result))

    def test_no_pp_counter_in_battle_menu(self):
        original = '''static void MoveSelectionDisplayPPString(enum BattlerId battler)
{
    StringCopy(gDisplayedStringBattle, gText_MoveInterfacePP);
    BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_PP);
}
static void MoveSelectionDisplayPPNumber(enum BattlerId battler)
{
    u8 *txtPtr;
    struct ChooseMoveStruct *moveInfo;

    if (gBattleResources->bufferA[battler][2] == TRUE) // check if we didn't want to display PP number
        return;

    SetPPNumbersPaletteInMoveSelection(battler);
    moveInfo = (struct ChooseMoveStruct *)(&gBattleResources->bufferA[battler][4]);
    txtPtr = ConvertIntToDecimalStringN(gDisplayedStringBattle, moveInfo->currentPP[gMoveSelectionCursor[battler]], STR_CONV_MODE_RIGHT_ALIGN, 2);
    *(txtPtr)++ = CHAR_SLASH;
    ConvertIntToDecimalStringN(txtPtr, moveInfo->maxPP[gMoveSelectionCursor[battler]], STR_CONV_MODE_RIGHT_ALIGN, 2);

    BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_PP_REMAINING);
}'''
        result = modify_move_pp_display(original)
        self.assertIn("gText_EmptyString3, B_WIN_PP_REMAINING", result)
        self.assertNotIn("ConvertIntToDecimalStringN", result)
        self.assertEqual(result, modify_move_pp_display(result))


if __name__ == "__main__":
    unittest.main()
