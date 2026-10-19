#!/usr/bin/env python3
"""Deterministic Shattered Realms changes for RHH pokeemerald-expansion 1.17.1.

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
        "I_EXP_SHARE_FLAG": "FLAG_UNUSED_0x264",
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



def replace_once(contents: str, before: str, after: str) -> str:
    """Fail closed on unexpected engine edits and allow repeated application."""
    if after in contents:
        return contents
    if contents.count(before) != 1:
        raise ValueError(f"Expected one patch anchor, found {contents.count(before)}: {before[:80]!r}")
    return contents.replace(before, after, 1)


def modify_starter_choices(contents: str) -> str:
    """The default middle starter is Pikachu; the other two remain available."""
    return replace_once(
        contents,
        "    GRASS_STARTER,\n    FIRE_STARTER,\n    WATER_STARTER,",
        "    GRASS_STARTER,\n    SPECIES_PIKACHU,\n    WATER_STARTER,",
    )


def modify_starter_gift(contents: str) -> str:
    """Give the starting Pikachu four strong attacks without changing save layout."""
    contents = replace_once(
        contents,
        '#include "palette.h"\n',
        '#include "palette.h"\n#include "pokemon.h"\n',
    )
    return replace_once(
        contents,
        "    ScriptGiveMon(starterMon, 5, ITEM_NONE);\n    ResetTasks();",
        """    ScriptGiveMon(starterMon, 5, ITEM_NONE);
    // Shattered Realms starter: special moves apply only to the Pikachu gift.
    if (starterMon == SPECIES_PIKACHU)
    {
        struct Pokemon *starter = &gParties[B_TRAINER_PLAYER][0];
        SetMonMoveSlot(starter, MOVE_THUNDERBOLT, 0);
        SetMonMoveSlot(starter, MOVE_VOLT_TACKLE, 1);
        SetMonMoveSlot(starter, MOVE_SURF, 2);
        SetMonMoveSlot(starter, MOVE_EXTREME_SPEED, 3);
    }
    ResetTasks();""",
    )


def modify_player_battle_pp(contents: str) -> str:
    """Restore player-controlled moves at every turn, leaving enemy PP untouched."""
    before = "            RecordedBattle_CopyBattlerMoves(battler);\n            gBattleCommunication[battler] = STATE_BEFORE_ACTION_CHOSEN;"
    after = """            RecordedBattle_CopyBattlerMoves(battler);
            // Shattered Realms: player-controlled Pokémon never run out of PP.
            // Do not alter the PP rules for opponents, link or recorded battles.
            if (IsOnPlayerSide(battler) && !BattlerHasAi(battler)
                && !(gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED_LINK)))
            {
                struct Pokemon *partyMon = GetBattlerMon(battler);
                for (i = 0; i < MAX_MON_MOVES; i++)
                {
                    if (gBattleMons[battler].moves[i] != MOVE_NONE)
                    {
                        u32 maxPP = CalculatePPWithBonus(gBattleMons[battler].moves[i],
                                                         gBattleMons[battler].ppBonuses, i);
                        gBattleMons[battler].pp[i] = maxPP;
                        SetMonData(partyMon, MON_DATA_PP1 + i, &maxPP);
                    }
                }
            }
            gBattleCommunication[battler] = STATE_BEFORE_ACTION_CHOSEN;"""
    return replace_once(contents, before, after)


def modify_player_pp_checks(contents: str) -> str:
    """Prevent an occasional mid-turn drain from forcing the player's Struggle."""
    contents = replace_once(
        contents,
        "    if (gBattleMons[battler].pp[moveId] == 0)\n    {",
        "    if (gBattleMons[battler].pp[moveId] == 0 && !IsOnPlayerSide(battler))\n    {",
    )
    return replace_once(
        contents,
        "else if (check & MOVE_LIMITATION_PP && gBattleMons[battler].pp[i] == 0)",
        "else if (check & MOVE_LIMITATION_PP && gBattleMons[battler].pp[i] == 0 && !IsOnPlayerSide(battler))",
    )


def modify_move_pp_display(contents: str) -> str:
    """Remove the PP counter from the battle move selection interface."""
    contents = replace_once(
        contents,
        """static void MoveSelectionDisplayPPString(enum BattlerId battler)
{
    StringCopy(gDisplayedStringBattle, gText_MoveInterfacePP);
    BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_PP);
}""",
        """static void MoveSelectionDisplayPPString(enum BattlerId battler)
{
    BattlePutTextOnWindow(gText_EmptyString3, B_WIN_PP);
}""",
    )
    return replace_once(
        contents,
        """static void MoveSelectionDisplayPPNumber(enum BattlerId battler)
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
}""",
        """static void MoveSelectionDisplayPPNumber(enum BattlerId battler)
{
    BattlePutTextOnWindow(gText_EmptyString3, B_WIN_PP_REMAINING);
}""",
    )



def modify_pikachu_move_pages(contents: str) -> str:
    """Eight accessible starter attacks in two battle-menu pages (SELECT toggles).
    
    Extra moves are virtual battle choices. The standard four saved moves remain
    untouched, so we do not change BoxPokemon, battle data sizes or save layout.
    """
    contents = replace_once(
        contents,
        "void HandleInputChooseMove(enum BattlerId battler)\n{",
        """// Shattered Realms starter: SELECT toggles between four normal saved moves
// and four signature attacks without altering the saved Pokémon move slots.
static u8 sShatteredPikachuPage[MAX_BATTLERS_COUNT];

static void ShatteredTogglePikachuPage(enum BattlerId battler)
{
    static const enum Move sExtraMoves[MAX_MON_MOVES] =
    {
        MOVE_IRON_TAIL,
        MOVE_GRASS_KNOT,
        MOVE_BRICK_BREAK,
        MOVE_THUNDER_WAVE,
    };
    struct ChooseMoveStruct *moveInfo = (struct ChooseMoveStruct *)(&gBattleResources->bufferA[battler][4]);

    MoveSelectionDestroyCursorAt(gMoveSelectionCursor[battler]);
    sShatteredPikachuPage[battler] ^= 1;
    for (u32 i = 0; i < MAX_MON_MOVES; i++)
    {
        enum Move move = sShatteredPikachuPage[battler]
                       ? sExtraMoves[i]
                       : GetMonData(GetBattlerMon(battler), MON_DATA_MOVE1 + i);
        u32 pp = GetMovePP(move);
        moveInfo->moves[i] = move;
        moveInfo->currentPP[i] = pp;
        moveInfo->maxPP[i] = pp;
        gBattleMons[battler].moves[i] = move;
        gBattleMons[battler].pp[i] = pp;
    }
    gMoveSelectionCursor[battler] = 0;
    MoveSelectionDisplayMoveNames(battler);
    MoveSelectionCreateCursorAt(gMoveSelectionCursor[battler], 0);
    MoveSelectionDisplayPPNumber(battler);
    MoveSelectionDisplayMoveType(battler);
    if (B_SHOW_EFFECTIVENESS)
        MoveSelectionDisplayMoveEffectiveness(CheckTargetTypeEffectiveness(battler), battler);
    TryMoveSelectionDisplayMoveDescription(battler);
}

void HandleInputChooseMove(enum BattlerId battler)
{""",
    )
    contents = replace_once(
        contents,
        """    if (JOY_NEW(A_BUTTON) && !gBattleStruct->descriptionSubmenu)
    {""",
        """    if (JOY_NEW(SELECT_BUTTON) && !gBattleStruct->descriptionSubmenu
        && !gBattleStruct->zmove.viewing && gBattleMons[battler].species == SPECIES_PIKACHU
        && IsOnPlayerSide(battler) && !(gBattleTypeFlags & BATTLE_TYPE_LINK))
    {
        PlaySE(SE_SELECT);
        ShatteredTogglePikachuPage(battler);
    }
    else if (JOY_NEW(A_BUTTON) && !gBattleStruct->descriptionSubmenu)
    {""",
    )
    contents = replace_once(
        contents,
        """        InitMoveSelectionsVarsAndStrings(battler);
        gBattleStruct->gimmick.playerSelect = FALSE;""",
        """        sShatteredPikachuPage[battler] = 0;
        InitMoveSelectionsVarsAndStrings(battler);
        gBattleStruct->gimmick.playerSelect = FALSE;""",
    )
    contents = replace_once(
        contents,
        """static void MoveSelectionDisplayPPNumber(enum BattlerId battler)
{
    BattlePutTextOnWindow(gText_EmptyString3, B_WIN_PP_REMAINING);
}""",
        """static void MoveSelectionDisplayPPNumber(enum BattlerId battler)
{
    if (gBattleMons[battler].species == SPECIES_PIKACHU && IsOnPlayerSide(battler))
    {
        if (sShatteredPikachuPage[battler] == 0)
            BattlePutTextOnWindow(COMPOUND_STRING("1/2"), B_WIN_PP_REMAINING);
        else
            BattlePutTextOnWindow(COMPOUND_STRING("2/2"), B_WIN_PP_REMAINING);
    }
    else
    {
        BattlePutTextOnWindow(gText_EmptyString3, B_WIN_PP_REMAINING);
    }
}""",
    )
    return contents


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

    gameplay_sources = {
        "src/starter_choose.c": modify_starter_choices,
        "src/battle_setup.c": modify_starter_gift,
        "src/battle_main.c": modify_player_battle_pp,
        "src/battle_util.c": modify_player_pp_checks,
        "src/battle_controller_player.c": lambda c: modify_pikachu_move_pages(modify_move_pp_display(c)),
    }
    for relative_path, patcher in gameplay_sources.items():
        path = engine / relative_path
        updates[path] = patcher(path.read_text(encoding="utf-8"))

    # Don't partially write if validation fails.
    for path, content in updates.items():
        if path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
            print("Updated", path)
    print("Shattered Realms gameplay overrides applied")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path, required=True, help="Path to expansion checkout")
    args = parser.parse_args()
    apply(args.engine.resolve())


if __name__ == "__main__":
    main()
