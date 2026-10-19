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
    modify_all_move_pages,
    modify_unlimited_money,
    modify_infinite_candy,
    modify_bag_candy_supply,
    modify_fast_experience,
    modify_hard_trainer_levels,
    modify_hard_trainer_ivs,
    modify_hard_trainer_ai,
    modify_hard_trainer_bag,
    modify_rift_intro,
    modify_route_rift_teaser,
    modify_rift_map_groups,
    modify_quest_npc_map,
    modify_quest_map_script,
    RIFT_NPCS,
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
        self.assertEqual(CONFIG["include/config/overworld.h"]["OW_FOLLOWERS_ENABLED"], "TRUE")
        battle_settings = CONFIG["include/config/battle.h"]
        self.assertEqual(battle_settings["B_TRAINER_MON_RANDOM_ABILITY"], "2")
        self.assertEqual(battle_settings["B_RUN_TRAINER_BATTLE"], "FALSE")
        self.assertEqual(CONFIG["include/config/overworld.h"]["OW_SHOW_ITEM_DESCRIPTIONS"], "OW_ITEM_DESCRIPTIONS_ALWAYS")

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



    def test_all_pokemon_move_library_pages(self):
        original = '''#include "data.h"
void HandleInputChooseMove(enum BattlerId battler)
{
    if (JOY_NEW(A_BUTTON) && !gBattleStruct->descriptionSubmenu)
    {
}
static void MoveSelectionDisplayPPNumber(enum BattlerId battler)
{
    BattlePutTextOnWindow(gText_EmptyString3, B_WIN_PP_REMAINING);
}
        InitMoveSelectionsVarsAndStrings(battler);
        gBattleStruct->gimmick.playerSelect = FALSE;'''
        result = modify_all_move_pages(original)
        for name in ("MOVE_IRON_TAIL", "MOVE_GRASS_KNOT", "MOVE_BRICK_BREAK", "MOVE_THUNDER_WAVE"):
            self.assertIn(name, result)
        self.assertIn("GetSpeciesLevelUpLearnset(cursorSpecies)", result)
        self.assertIn("CanLearnTeachableMove(species, machineMove)", result)
        self.assertIn("CanLearnTeachableMove(species, tutorMove)", result)
        self.assertIn("GetSpeciesEggMoves(eggSpecies)", result)
        self.assertIn("SHATTERED_MAX_LIBRARY_MOVES 256", result)
        self.assertIn('#include "data/tutor_moves.h"', result)
        self.assertIn("GetMonData(mon, MON_DATA_FRIENDSHIP)", result)
        self.assertIn("MOVE_ZIPPY_ZAP", result)
        self.assertIn("MOVE_SPLISHY_SPLASH", result)
        self.assertIn("MOVE_FLOATY_FALL", result)
        self.assertIn("JOY_NEW(SELECT_BUTTON)", result)
        self.assertIn("sShatteredMoves[battler]", result)
        self.assertIn("sShatteredMoveCounts[battler]", result)
        self.assertIn("level <= level", result)
        self.assertIn("B_WIN_PP_REMAINING", result)
        self.assertEqual(modify_all_move_pages(result), result)


    def test_unlimited_money_only_player_wallet(self):
        sample = """u32 GetMoney(u32 *moneyPtr)
{
    return *moneyPtr ^ gSaveBlock2Ptr->encryptionKey;
}
void RemoveMoney(u32 *moneyPtr, u32 toSub)
{
    u32 toSet = GetMoney(moneyPtr);"""
        after = modify_unlimited_money(sample)
        self.assertIn("return MAX_MONEY;", after)
        self.assertIn("if (moneyPtr == &gSaveBlock1Ptr->money)", after)
        self.assertEqual(after, modify_unlimited_money(after))

    def test_reusable_candies_regular_bag_only(self):
        sample = """bool32 RemoveBagItem(enum Item itemId, u16 count)
{
    itemId = SanitizeBagItemId(itemId);
    if (itemId == ITEM_NONE)
        return FALSE;"""
        after = modify_infinite_candy(sample)
        self.assertIn("return CheckBagHasItem(itemId, 1);", after)
        self.assertIn("ITEM_MASTER_BALL", after)
        self.assertIn("CurrentBattlePyramidLocation() == PYRAMID_LOCATION_NONE", after)
        self.assertEqual(after, modify_infinite_candy(after))

    def test_existing_save_receives_candies_on_bag_open(self):
        sample = """void GoToBagMenu(u8 location, u8 pocket, MainCallback exitCallback)
{
    gBagMenu = AllocZeroed(sizeof(*gBagMenu));"""
        after = modify_bag_candy_supply(sample)
        self.assertIn("AddBagItem(ITEM_RARE_CANDY, 99);", after)
        self.assertIn("AddBagItem(ITEM_MASTER_BALL, 99);", after)
        self.assertIn("AddBagItem(ITEM_FULL_RESTORE, 99);", after)
        self.assertEqual(after, modify_bag_candy_supply(after))

    def test_four_times_battle_exp_preserves_exp_tables(self):
        sample = """        *expAmount = value + 1;
    }
}

void BS_ItemRestoreHP(void)"""
        after = modify_fast_experience(sample)
        self.assertIn("*expAmount *= 4;", after)
        self.assertEqual(after, modify_fast_experience(after))

    def test_trainer_boost_not_frontier(self):
        sample = "    CreateMon(mon, trainerMon->species, trainerMon->lvl, personality, trainer->otID);"
        after = modify_hard_trainer_levels(sample)
        self.assertIn("if (!trainer->isFrontier)", after)
        self.assertIn("min(MAX_LEVEL", after)
        self.assertIn("highestPlayerLevel", after)
        self.assertEqual(after, modify_hard_trainer_levels(after))

    def test_smart_hard_trainer_ai(self):
        sample = """    if (IsDoubleBattle() && flags != 0)
    {
        flags |= AI_FLAG_DOUBLE_BATTLE;"""
        after = modify_hard_trainer_ai(sample)
        self.assertIn("AI_FLAG_HP_AWARE", after)
        self.assertEqual(after, modify_hard_trainer_ai(after))

    def test_no_bag_in_trainer_battles(self):
        sample = """bool32 IsAllowedToUseBag(void)
{
    switch (VarGet(B_VAR_NO_BAG_USE))"""
        after = modify_hard_trainer_bag(sample)
        self.assertIn("return FALSE;", after)
        self.assertEqual(after, modify_hard_trainer_bag(after))


    def test_hard_trainer_perfectish_ivs(self):
        sample = "    SetMonData(mon, MON_DATA_IVS, &trainerMon->iv);"
        after = modify_hard_trainer_ivs(sample)
        self.assertIn("data < 28", after)
        self.assertIn("SetMonData(mon, MON_DATA_IVS, &data)", after)
        self.assertEqual(after, modify_hard_trainer_ivs(after))



    def test_shattered_realms_intro_teaser(self):
        sample = "gText_Birch_MainSpeech::\n\t.string \"Old speech.$\"\n\ngText_Birch_AndYouAre::"
        after = modify_rift_intro(sample)
        self.assertIn("TEAM ECLIPSE", after)
        self.assertIn("RIFTS", after)
        self.assertIn("gText_Birch_AndYouAre::", after)
        self.assertEqual(after, modify_rift_intro(after))

    def test_route_101_teaser_without_changing_events(self):
        sample = "Route101_Text_YouSavedMe:\n\t.string \"Old speech.$\"\n\nRoute101_Text_TakeTiredPokemonToPokeCenter:"
        after = modify_route_rift_teaser(sample)
        self.assertIn("RIFT flashed", after)
        self.assertIn("TEAM ECLIPSE", after)
        self.assertIn("Route101_Text_TakeTiredPokemonToPokeCenter:", after)
        self.assertEqual(after, modify_route_rift_teaser(after))



    def test_rift_hollow_append_does_not_change_old_map_ids(self):
        original = json.dumps({"gMapGroup_Dungeons": ["AlteringCave", "MeteorFalls_StevensCave"]})
        changed = modify_rift_map_groups(original)
        result = json.loads(changed)["gMapGroup_Dungeons"]
        self.assertEqual(result[:2], ["AlteringCave", "MeteorFalls_StevensCave"])
        self.assertEqual(result[-1], "RiftHollow")
        self.assertEqual(changed, modify_rift_map_groups(changed))

    def test_all_four_quest_npcs_are_single_swap(self):
        for map_name, (old_script, new_script) in RIFT_NPCS.items():
            original = json.dumps({"object_events": [{"script": old_script}]})
            changed = modify_quest_npc_map(original, map_name)
            self.assertIn(new_script, changed)
            self.assertEqual(changed, modify_quest_npc_map(changed, map_name))

    def test_all_four_quest_scripts_idempotent(self):
        for map_name in RIFT_NPCS:
            source = "DummyMap_MapScripts::\n\t.byte 0\n"
            changed = modify_quest_map_script(source, map_name)
            self.assertIn(RIFT_NPCS[map_name][1] + "::", changed)
            self.assertEqual(changed, modify_quest_map_script(changed, map_name))
        self.assertIn("FLAG_UNUSED_0x90F", modify_quest_map_script("", "OldaleTown"))


if __name__ == "__main__":
    unittest.main()
