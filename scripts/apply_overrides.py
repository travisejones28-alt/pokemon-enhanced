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
    "MAP_ROUTE104": {
        0: "SPECIES_YAMPER",
        2: "SPECIES_SKIDDO",
        3: "SPECIES_BUDEW",
        4: "SPECIES_BOUNSWEET",
        5: "SPECIES_HOPPIP",
        6: "SPECIES_PIKIPEK",
        7: "SPECIES_STARLY",
        8: "SPECIES_WATTREL",
        9: "SPECIES_FLABEBE",
        10: "SPECIES_SNIVY",
        11: "SPECIES_TURTWIG",
    },
    "MAP_ROUTE110": {
        0: "SPECIES_BLITZLE",
        2: "SPECIES_TOXEL",
        3: "SPECIES_HELIOPTILE",
        4: "SPECIES_EMOLGA",
        5: "SPECIES_JOLTIK",
        6: "SPECIES_DEDENNE",
        7: "SPECIES_MORPEKO",
        8: "SPECIES_PAWMI",
        9: "SPECIES_SHINX",
        10: "SPECIES_TADBULB",
        11: "SPECIES_MAREEP",
    },
    "MAP_ROUTE111": {
        0: "SPECIES_SANDYGAST",
        2: "SPECIES_SILICOBRA",
        3: "SPECIES_DRILBUR",
        4: "SPECIES_ROGGENROLA",
        5: "SPECIES_ROLYCOLY",
        6: "SPECIES_GIBLE",
        7: "SPECIES_HELIOPTILE",
        8: "SPECIES_TRAPINCH",
        9: "SPECIES_SANDILE",
        10: "SPECIES_KROKOROK",
        11: "SPECIES_GREAT_TUSK",
    },
    "MAP_ROUTE113": {
        0: "SPECIES_NUMEL", 2: "SPECIES_CHARCADET",
        3: "SPECIES_ROLYCOLY", 4: "SPECIES_LARVESTA",
        5: "SPECIES_LITLEO", 6: "SPECIES_SALANDIT",
        7: "SPECIES_SIZZLIPEDE", 8: "SPECIES_CARKOL",
        9: "SPECIES_TORKOAL", 10: "SPECIES_MAGBY",
        11: "SPECIES_FLETCHINDER",
    },
    "MAP_ROUTE114": {
        0: "SPECIES_SWABLU", 2: "SPECIES_SKIDDO",
        3: "SPECIES_DEERLING", 4: "SPECIES_PANCHAM",
        5: "SPECIES_LOMBRE", 6: "SPECIES_GROOKEY",
        7: "SPECIES_TEDDIURSA", 8: "SPECIES_SEVIPER",
        9: "SPECIES_DREEPY", 10: "SPECIES_NOIBAT",
        11: "SPECIES_AXEW",
    },
    "MAP_ROUTE116": {
        0: "SPECIES_LILLIPUP", 2: "SPECIES_NINCADA",
        3: "SPECIES_ABRA", 4: "SPECIES_DRILBUR",
        5: "SPECIES_STARLY", 6: "SPECIES_ROCKRUFF",
        7: "SPECIES_RIOLU", 8: "SPECIES_SHINX",
        9: "SPECIES_WHISMUR", 10: "SPECIES_SKITTY",
        11: "SPECIES_FENNEKIN",
    },
    "MAP_ROUTE117": {
        0: "SPECIES_BUNEARY", 2: "SPECIES_SNIVY",
        3: "SPECIES_PAWMI", 4: "SPECIES_MARILL",
        5: "SPECIES_FLABEBE", 6: "SPECIES_COMBEE",
        7: "SPECIES_CUTIEFLY", 8: "SPECIES_ILLUMISE",
        9: "SPECIES_VOLBEAT", 10: "SPECIES_SEWADDLE",
        11: "SPECIES_SEEDOT",
    },
    "MAP_ROUTE119": {
        0: "SPECIES_FROAKIE", 2: "SPECIES_TROPIUS",
        3: "SPECIES_LOTAD", 4: "SPECIES_GROOKEY",
        5: "SPECIES_DREEPY", 6: "SPECIES_GOOMY",
        7: "SPECIES_TREECKO", 8: "SPECIES_ROWLET",
        9: "SPECIES_SOBBLE", 10: "SPECIES_KECLEON",
        11: "SPECIES_SPRIGATITO",
    },
    "MAP_PETALBURG_WOODS": {
        0: "SPECIES_SCATTERBUG", 2: "SPECIES_SEWADDLE",
        3: "SPECIES_GRUBBIN", 4: "SPECIES_CATERPIE",
        5: "SPECIES_METAPOD", 6: "SPECIES_VENIPEDE",
        7: "SPECIES_SHROOMISH", 8: "SPECIES_BOUNSWEET",
        9: "SPECIES_PHANTUMP", 10: "SPECIES_PUMPKABOO",
        11: "SPECIES_ROWLET",
    },
    "MAP_GRANITE_CAVE_1F": {
        0: "SPECIES_NOIBAT", 2: "SPECIES_ROGGENROLA",
        3: "SPECIES_ZUBAT", 4: "SPECIES_WOOBAT",
        5: "SPECIES_DRILBUR", 6: "SPECIES_MAKUHITA",
        7: "SPECIES_RIOLU", 8: "SPECIES_GEODUDE",
        9: "SPECIES_CARBINK", 10: "SPECIES_SABLEYE",
        11: "SPECIES_GIBLE",
    },
    "MAP_ROUTE112": {
        0: "SPECIES_FUECOCO",
        2: "SPECIES_LITLEO",
        3: "SPECIES_FLETCHINDER",
        4: "SPECIES_SALANDIT",
        5: "SPECIES_SIZZLIPEDE",
        6: "SPECIES_CHARCADET",
        7: "SPECIES_ROLYCOLY",
        8: "SPECIES_LARVESTA",
        9: "SPECIES_TORKOAL",
        10: "SPECIES_CARKOL",
        11: "SPECIES_MAGBY",
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
    "include/config/overworld.h": {
        "OW_FOLLOWERS_ENABLED": "TRUE",
        "OW_SHOW_ITEM_DESCRIPTIONS": "OW_ITEM_DESCRIPTIONS_ALWAYS",
    },
    "include/config/summary_screen.h": {
        "P_ENABLE_MOVE_RELEARNERS": "TRUE",
        "P_TM_MOVES_RELEARNER": "TRUE",
        "P_SUMMARY_SCREEN_MOVE_RELEARNER": "TRUE",
        "P_ENABLE_ALL_TM_MOVES": "TRUE",
        "P_PRE_EVO_MOVES": "TRUE",
    },
    "include/config/pokedex_plus_hgss.h": {
        "POKEDEX_PLUS_HGSS": "TRUE",
        "HGSS_DARK_MODE": "TRUE",
        "HGSS_SORT_TMS_BY_NUM": "TRUE",
        "HGSS_HIDE_UNSEEN_EVOLUTION_NAMES": "FALSE",
        "HGSS_HIDE_UNOWNED_EVOLUTION_METHODS": "FALSE",
        "HGSS_SHOW_EGG_MOVES_FOR_EVOS": "TRUE",
    },
    "include/config/battle.h": {
        "B_TRAINER_MON_RANDOM_ABILITY": "2",
        "B_QUICK_MOVE_CURSOR_TO_RUN": "TRUE",
        "B_RUN_TRAINER_BATTLE": "FALSE",
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
        if contents.count(after) != 1 or before in contents.replace(after, "", 1):
            raise ValueError(f"Duplicate or mixed patch state: {before[:80]!r}")
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
                && !(gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED | BATTLE_TYPE_RECORDED_LINK)))
            {
                struct Pokemon *partyMon = GetBattlerMon(battler);
                for (i = 0; i < MAX_MON_MOVES; i++)
                {
                    // Preserve battle-only moves, transformation and Encore slots.
                    // No virtual move is ever copied into the saved move slots.
                    if (gBattleMons[battler].moves[i] != MOVE_NONE)
                    {
                        u32 maxPP = CalculatePPWithBonus(gBattleMons[battler].moves[i],
                                                         gBattleMons[battler].ppBonuses, i);
                        gBattleMons[battler].pp[i] = maxPP;
                    }
                    // Party PP belongs to the SAVED move, not its virtual slot.
                    enum Move savedMove = GetMonData(partyMon, MON_DATA_MOVE1 + i);
                    if (savedMove != MOVE_NONE)
                    {
                        u32 savedPP = CalculatePPWithBonus(savedMove,
                            GetMonData(partyMon, MON_DATA_PP_BONUSES), i);
                        SetMonData(partyMon, MON_DATA_PP1 + i, &savedPP);
                    }
                }
            }
            gBattleCommunication[battler] = STATE_BEFORE_ACTION_CHOSEN;"""
    return replace_once(contents, before, after)


def modify_player_pp_checks(contents: str) -> str:
    """Apply unlimited PP only to locally controlled player battlers."""
    contents = replace_once(
        contents,
        "u32 CheckMoveLimitations(enum BattlerId battler, u8 unusableMoves, u32 check)\n{",
        """bool32 ShatteredHasUnlimitedPP(enum BattlerId battler)
{
    return IsOnPlayerSide(battler) && !BattlerHasAi(battler)
        && !(gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED
                                | BATTLE_TYPE_RECORDED_LINK));
}

u32 CheckMoveLimitations(enum BattlerId battler, u8 unusableMoves, u32 check)
{""",
    )
    contents = replace_once(
        contents,
        "    if (gBattleMons[battler].pp[moveId] == 0)\n    {",
        "    if (gBattleMons[battler].pp[moveId] == 0 && !ShatteredHasUnlimitedPP(battler))\n    {",
    )
    contents = replace_once(
        contents,
        "else if (check & MOVE_LIMITATION_PP && gBattleMons[battler].pp[i] == 0)",
        "else if (check & MOVE_LIMITATION_PP && gBattleMons[battler].pp[i] == 0 && !ShatteredHasUnlimitedPP(battler))",
    )

    return replace_once(
        contents,
        "    if (unusable == allMovesMask) // All moves are unusable.",
        """    if (unusable == allMovesMask && ShatteredTryUsableLibraryPage(battler))
        unusable = CheckMoveLimitations(battler, 0, MOVE_LIMITATIONS_ALL);

    if (unusable == allMovesMask) // All moves are unusable.""",
    )


def modify_unlimited_pp_header(contents: str) -> str:
    return replace_once(contents, "bool32 IsAllowedToUseBag(void);",
                        "bool32 IsAllowedToUseBag(void);\nbool32 ShatteredHasUnlimitedPP(enum BattlerId battler);\nbool32 ShatteredTryUsableLibraryPage(enum BattlerId battler);")


def modify_pp_resolution(contents: str) -> str:
    """No ordinary/Pressure/Grudge PP depletion; retain move bookkeeping."""
    contents = replace_once(
        contents,
        "    if (gBattleMons[cv->battlerAtk].pp[gCurrMovePos] == 0\n",
        "    if (!ShatteredHasUnlimitedPP(cv->battlerAtk)\n     && gBattleMons[cv->battlerAtk].pp[gCurrMovePos] == 0\n",
    )
    contents = replace_once(
        contents,
        """    if (gBattleMons[cv->battlerAtk].pp[movePosition] > ppToDeduct)
        gBattleMons[cv->battlerAtk].pp[movePosition] -= ppToDeduct;
    else
        gBattleMons[cv->battlerAtk].pp[movePosition] = 0;""",
        """    if (!ShatteredHasUnlimitedPP(cv->battlerAtk))
    {
        if (gBattleMons[cv->battlerAtk].pp[movePosition] > ppToDeduct)
            gBattleMons[cv->battlerAtk].pp[movePosition] -= ppToDeduct;
        else
            gBattleMons[cv->battlerAtk].pp[movePosition] = 0;
    }""",
    )
    contents = replace_once(
        contents,
        "    if (MOVE_IS_PERMANENT(cv->battlerAtk, movePosition))",
        "    if (!ShatteredHasUnlimitedPP(cv->battlerAtk) && MOVE_IS_PERMANENT(cv->battlerAtk, movePosition))",
    )
    return replace_once(
        contents,
        "            if (gBattleMons[cv->battlerDef].volatiles.grudge\n",
        "            if (!ShatteredHasUnlimitedPP(cv->battlerAtk)\n             && gBattleMons[cv->battlerDef].volatiles.grudge\n",
    )


def modify_pp_drain_and_sketch(contents: str) -> str:
    contents = replace_once(
        contents,
        "    if (gLastMoves[gBattlerTarget] != MOVE_NONE\n",
        "    if (!ShatteredHasUnlimitedPP(gBattlerTarget)\n     && gLastMoves[gBattlerTarget] != MOVE_NONE\n",
    )
    return replace_once(
        contents,
        """            movePPData.ppBonuses = gBattleMons[gBattlerAttacker].ppBonuses;

            BtlController_EmitSetMonData(gBattlerAttacker, B_COMM_TO_CONTROLLER, REQUEST_MOVES_PP_BATTLE,""",
        """            movePPData.ppBonuses = gBattleMons[gBattlerAttacker].ppBonuses;
            if (ShatteredHasUnlimitedPP(gBattlerAttacker))
            {
                // Sketch must not persist unrelated moves from a virtual page.
                struct Pokemon *mon = GetBattlerMon(gBattlerAttacker);
                s32 savedSketchSlot = -1;
                for (i = 0; i < MAX_MON_MOVES; i++)
                {
                    movePPData.moves[i] = GetMonData(mon, MON_DATA_MOVE1 + i);
                    movePPData.pp[i] = GetMonData(mon, MON_DATA_PP1 + i);
                    if (movePPData.moves[i] == MOVE_SKETCH)
                        savedSketchSlot = i;
                }
                movePPData.ppBonuses = GetMonData(mon, MON_DATA_PP_BONUSES);
                // A virtual Sketch is battle-only unless a saved Sketch exists.
                if (savedSketchSlot >= 0)
                {
                    movePPData.moves[savedSketchSlot] = gLastPrintedMoves[gBattlerTarget];
                    movePPData.pp[savedSketchSlot] = GetMovePP(gLastPrintedMoves[gBattlerTarget]);
                    movePPData.ppBonuses &= ~(3 << (savedSketchSlot * 2));
                }
            }

            BtlController_EmitSetMonData(gBattlerAttacker, B_COMM_TO_CONTROLLER, REQUEST_MOVES_PP_BATTLE,""",
    )


def modify_rift_reward_retry(contents: str) -> str:
    contents = replace_once(
        contents,
        "\tsetflag FLAG_UNUSED_0x90F\n\tmsgbox RiftHollow_Text_WardenReward, MSGBOX_DEFAULT",
        "\tsetflag FLAG_UNUSED_0x90F\n\nRiftHollow_EventScript_ClaimReward::\n\tmsgbox RiftHollow_Text_WardenReward, MSGBOX_DEFAULT",
    )
    return replace_once(
        contents,
        """RiftHollow_EventScript_WardenAfterVictory::
\tmsgbox RiftHollow_Text_WardenAfterVictory, MSGBOX_NPC
\tend""",
        """RiftHollow_EventScript_WardenAfterVictory::
\tlock
\tfaceplayer
\tcheckitem ITEM_SHINY_CHARM
\tgoto_if_eq VAR_RESULT, FALSE, RiftHollow_EventScript_ClaimReward
\tmsgbox RiftHollow_Text_WardenAfterVictory, MSGBOX_DEFAULT
\trelease
\tend""",
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
    if "#define SHATTERED_MAX_LIBRARY_MOVES" in contents:
        return contents
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



def modify_all_move_pages(contents: str) -> str:
    """All player Pokémon can use all unlocked level-up attacks via SELECT pages.

    This is deliberately save-layout-preserving: the catalog is rebuilt from the
    saved four move slots and the species' level-up learnset each battle turn.
    Compatible TM/egg moves are unlocked by species rather than history.
    Forgotten event-only moves are not archived; persistent history is pending.
    """
    contents = replace_once(contents, '#include "battle.h"\n',
                            '#include "battle.h"\n#include "battle_util.h"\n')
    contents = replace_once(
        contents,
        "void HandleInputChooseMove(enum BattlerId battler)\n{",
        """// Shattered Realms move library: multi-page selection without changing the
// persistent four slots in BoxPokemon or the battle controller wire format.
#define SHATTERED_MAX_LIBRARY_MOVES 256
static enum Move sShatteredMoves[MAX_BATTLERS_COUNT][SHATTERED_MAX_LIBRARY_MOVES];
static u16 sShatteredMoveCounts[MAX_BATTLERS_COUNT];
static u8 sShatteredMovePages[MAX_BATTLERS_COUNT];

static bool32 ShatteredCanUseLibrary(enum BattlerId battler)
{
    return IsOnPlayerSide(battler) && !BattlerHasAi(battler)
        && !(gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED
                                | BATTLE_TYPE_RECORDED_LINK))
        && !gBattleMons[battler].volatiles.transformed
        && !gBattleMons[battler].volatiles.mimickedMoves
        && gBattleMons[battler].volatiles.encoredMove == MOVE_NONE;
}

static void ShatteredRememberMove(enum BattlerId battler, enum Move move)
{
    if (move == MOVE_NONE || move == LEVEL_UP_MOVE_END)
        return;
    for (u32 i = 0; i < sShatteredMoveCounts[battler]; i++)
        if (sShatteredMoves[battler][i] == move)
            return;
    if (sShatteredMoveCounts[battler] < SHATTERED_MAX_LIBRARY_MOVES)
        sShatteredMoves[battler][sShatteredMoveCounts[battler]++] = move;
}

static void ShatteredBuildMoveLibrary(enum BattlerId battler)
{
    static const enum Move sStarterSignatureMoves[] =
    {
        MOVE_IRON_TAIL, MOVE_GRASS_KNOT, MOVE_BRICK_BREAK, MOVE_THUNDER_WAVE,
    };
    sShatteredMoveCounts[battler] = 0;
    sShatteredMovePages[battler] = 0;
    if (!ShatteredCanUseLibrary(battler))
        return;

    struct Pokemon *mon = GetBattlerMon(battler);
    enum Species species = GetMonData(mon, MON_DATA_SPECIES);
    u32 level = GetMonData(mon, MON_DATA_LEVEL);
    // Keep current runtime slots first: Encore and move effects refer to slots.
    // Saved attacks are then included even after browsing virtual pages.
    for (u32 i = 0; i < MAX_MON_MOVES; i++)
        ShatteredRememberMove(battler, gBattleMons[battler].moves[i]);
    for (u32 i = 0; i < MAX_MON_MOVES; i++)
        ShatteredRememberMove(battler, GetMonData(mon, MON_DATA_MOVE1 + i));

    // Every previously unlocked level-up attack, including pre-evolutions.
    for (enum Species cursorSpecies = species; cursorSpecies != SPECIES_NONE;
         cursorSpecies = GetSpeciesPreEvolution(cursorSpecies))
    {
        const struct LevelUpMove *learnset = GetSpeciesLevelUpLearnset(cursorSpecies);
        for (u32 i = 0; learnset[i].move != LEVEL_UP_MOVE_END; i++)
        {
            if (learnset[i].level > 0 && learnset[i].level <= level)
                ShatteredRememberMove(battler, learnset[i].move);
        }
    }

    // Species-compatible machines are available without owning each TM.
    // This is a compatibility catalog, not a persistent learned-move archive.
    for (u32 i = 0; i < NUM_ALL_MACHINES; i++)
    {
        enum Move machineMove = GetTMHMMoveId(i + 1);
        if (machineMove != MOVE_NONE && CanLearnTeachableMove(species, machineMove))
            ShatteredRememberMove(battler, machineMove);
    }
    // The pinned engine has no vendored data/tutor_moves.h. Use a curated
    // set of tutor-style attacks with the same compatibility validation.
    static const enum Move sTutorMoves[] =
    {
        MOVE_ICE_PUNCH, MOVE_FIRE_PUNCH, MOVE_THUNDER_PUNCH,
        MOVE_DRAIN_PUNCH, MOVE_BUG_BITE, MOVE_IRON_HEAD,
        MOVE_SEED_BOMB, MOVE_KNOCK_OFF, MOVE_SUPERPOWER,
        MOVE_STEALTH_ROCK, MOVE_TRICK, MOVE_COVET, MOVE_SNORE,
        MOVE_BOUNCE, MOVE_HEAT_WAVE, MOVE_ICY_WIND,
        MOVE_TAILWIND, MOVE_DARK_PULSE, MOVE_THROAT_CHOP,
    };
    for (u32 i = 0; i < ARRAY_COUNT(sTutorMoves); i++)
    {
        enum Move tutorMove = sTutorMoves[i];
        if (CanLearnTeachableMove(species, tutorMove))
            ShatteredRememberMove(battler, tutorMove);
    }

    // Egg moves also remain available once the species can legally learn them.
    enum Species eggSpecies = species;
    while (GetSpeciesPreEvolution(eggSpecies) != SPECIES_NONE)
        eggSpecies = GetSpeciesPreEvolution(eggSpecies);
    const u16 *eggMoves = GetSpeciesEggMoves(eggSpecies);
    if (eggMoves[0] != MOVE_UNAVAILABLE)
        for (u32 i = 0; eggMoves[i] != MOVE_UNAVAILABLE; i++)
            ShatteredRememberMove(battler, eggMoves[i]);

    // Your original Pikachu starter keeps four extra signature moves.
    // Built-in friendship is the save-compatible Bond System.
    if (species == SPECIES_PIKACHU)
    {
        for (u32 i = 0; i < ARRAY_COUNT(sStarterSignatureMoves); i++)
            ShatteredRememberMove(battler, sStarterSignatureMoves[i]);
        u32 bond = GetMonData(mon, MON_DATA_FRIENDSHIP);
        if (bond >= 120)
            ShatteredRememberMove(battler, MOVE_ZIPPY_ZAP);
        if (bond >= 180)
            ShatteredRememberMove(battler, MOVE_SPLISHY_SPLASH);
        if (bond >= 230)
            ShatteredRememberMove(battler, MOVE_FLOATY_FALL);
    }
}

// Called before the engine commits to Struggle for a blocked visible page.
bool32 ShatteredTryUsableLibraryPage(enum BattlerId battler)
{
    if (!ShatteredCanUseLibrary(battler))
        return FALSE;
    enum Move originalMoves[MAX_MON_MOVES];
    u8 originalPP[MAX_MON_MOVES];
    for (u32 slot = 0; slot < MAX_MON_MOVES; slot++)
    {
        originalMoves[slot] = gBattleMons[battler].moves[slot];
        originalPP[slot] = gBattleMons[battler].pp[slot];
    }
    ShatteredBuildMoveLibrary(battler);
    for (u32 page = 0; page * MAX_MON_MOVES < sShatteredMoveCounts[battler]; page++)
    {
        for (u32 slot = 0; slot < MAX_MON_MOVES; slot++)
        {
            u32 index = page * MAX_MON_MOVES + slot;
            enum Move move = index < sShatteredMoveCounts[battler]
                           ? sShatteredMoves[battler][index] : MOVE_NONE;
            gBattleMons[battler].moves[slot] = move;
            gBattleMons[battler].pp[slot] = GetMovePP(move);
        }
        if (CheckMoveLimitations(battler, 0, MOVE_LIMITATIONS_ALL) != ((1u << MAX_MON_MOVES) - 1))
            return TRUE;
    }
    // All library choices really are blocked. Keep the original battle state.
    for (u32 slot = 0; slot < MAX_MON_MOVES; slot++)
    {
        gBattleMons[battler].moves[slot] = originalMoves[slot];
        gBattleMons[battler].pp[slot] = originalPP[slot];
    }
    return FALSE;
}

static void ShatteredToggleMovePage(enum BattlerId battler)
{
    u32 pageCount = (sShatteredMoveCounts[battler] + MAX_MON_MOVES - 1) / MAX_MON_MOVES;
    if (pageCount <= 1)
        return;

    struct ChooseMoveStruct *moveInfo = (struct ChooseMoveStruct *)(&gBattleResources->bufferA[battler][4]);
    MoveSelectionDestroyCursorAt(gMoveSelectionCursor[battler]);
    sShatteredMovePages[battler] = (sShatteredMovePages[battler] + 1) % pageCount;
    for (u32 i = 0; i < MAX_MON_MOVES; i++)
    {
        u32 index = sShatteredMovePages[battler] * MAX_MON_MOVES + i;
        enum Move move = index < sShatteredMoveCounts[battler]
                       ? sShatteredMoves[battler][index] : MOVE_NONE;
        u32 pp = GetMovePP(move);
        moveInfo->moves[i] = move;
        moveInfo->currentPP[i] = pp;
        moveInfo->maxPP[i] = pp;
        gBattleMons[battler].moves[i] = move;
        gBattleMons[battler].pp[i] = pp;
    }
    gMoveSelectionCursor[battler] = 0;
    AssignUsableZMoves(battler, moveInfo->moves);
    TryChangeZTrigger(battler, 0);
    MoveSelectionDisplayMoveNames(battler);
    MoveSelectionCreateCursorAt(0, 0);
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
        && !gBattleStruct->zmove.viewing && ShatteredCanUseLibrary(battler)
        && sShatteredMoveCounts[battler] > MAX_MON_MOVES)
    {
        PlaySE(SE_SELECT);
        ShatteredToggleMovePage(battler);
    }
    else if (JOY_NEW(A_BUTTON) && !gBattleStruct->descriptionSubmenu)
    {""",
    )
    contents = replace_once(
        contents,
        "else if (B_MOVE_REARRANGEMENT_IN_BATTLE < GEN_4 && JOY_NEW(SELECT_BUTTON)",
        "else if (B_MOVE_REARRANGEMENT_IN_BATTLE < GEN_4 && sShatteredMoveCounts[battler] == 0 && JOY_NEW(SELECT_BUTTON)",
    )
    contents = replace_once(
        contents,
        """        InitMoveSelectionsVarsAndStrings(battler);
        gBattleStruct->gimmick.playerSelect = FALSE;""",
        """        ShatteredBuildMoveLibrary(battler);
        // Preserve battle-only slots when transformed, mimicking or Encored.
        if (ShatteredCanUseLibrary(battler))
        {
            for (u32 slot = 0; slot < MAX_MON_MOVES; slot++)
            {
                enum Move move = slot < sShatteredMoveCounts[battler]
                               ? sShatteredMoves[battler][slot] : MOVE_NONE;
                u32 pp = GetMovePP(move);
                moveInfo->moves[slot] = move;
                moveInfo->currentPP[slot] = pp;
                moveInfo->maxPP[slot] = pp;
                gBattleMons[battler].moves[slot] = move;
                gBattleMons[battler].pp[slot] = pp;
            }
        }
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
    u32 pageCount = (sShatteredMoveCounts[battler] + MAX_MON_MOVES - 1) / MAX_MON_MOVES;
    if (pageCount > 1 && IsOnPlayerSide(battler) && !(gBattleTypeFlags & BATTLE_TYPE_LINK))
    {
        u8 *cursor = ConvertIntToDecimalStringN(gDisplayedStringBattle,
                                                sShatteredMovePages[battler] + 1,
                                                STR_CONV_MODE_LEFT_ALIGN, 2);
        *(cursor)++ = CHAR_SLASH;
        ConvertIntToDecimalStringN(cursor, pageCount, STR_CONV_MODE_LEFT_ALIGN, 2);
        BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_PP_REMAINING);
    }
    else
    {
        BattlePutTextOnWindow(gText_EmptyString3, B_WIN_PP_REMAINING);
    }
}""",
    )
    return contents


def modify_unlimited_money(contents: str) -> str:
    """The player's wallet always acts like max cash; no save-layout changes."""
    contents = replace_once(
        contents,
        """u32 GetMoney(u32 *moneyPtr)
{
    return *moneyPtr ^ gSaveBlock2Ptr->encryptionKey;
}""",
        """u32 GetMoney(u32 *moneyPtr)
{
    if (moneyPtr == &gSaveBlock1Ptr->money)
        return MAX_MONEY;
    return *moneyPtr ^ gSaveBlock2Ptr->encryptionKey;
}""",
    )
    return replace_once(
        contents,
        """void RemoveMoney(u32 *moneyPtr, u32 toSub)
{
    u32 toSet = GetMoney(moneyPtr);""",
        """void RemoveMoney(u32 *moneyPtr, u32 toSub)
{
    // Purchases and losses cannot drain the player's infinite wallet.
    if (moneyPtr == &gSaveBlock1Ptr->money)
        return;
    u32 toSet = GetMoney(moneyPtr);""",
    )


def modify_infinite_candy(contents: str) -> str:
    """Rare Candies can be reused; preserve normal behavior for other items."""
    return replace_once(
        contents,
        """bool32 RemoveBagItem(enum Item itemId, u16 count)
{
    itemId = SanitizeBagItemId(itemId);
    if (itemId == ITEM_NONE)
        return FALSE;""",
        """bool32 RemoveBagItem(enum Item itemId, u16 count)
{
    itemId = SanitizeBagItemId(itemId);
    if (itemId == ITEM_NONE)
        return FALSE;
    // Shattered Realms: unlimited use once the candy is in the normal Bag.
    if ((itemId == ITEM_RARE_CANDY || itemId == ITEM_MASTER_BALL
          || itemId == ITEM_MAX_REPEL || itemId == ITEM_MAX_REVIVE
          || itemId == ITEM_FULL_RESTORE || itemId == ITEM_ESCAPE_ROPE)
        && CurrentBattlePyramidLocation() == PYRAMID_LOCATION_NONE
        && !FlagGet(FLAG_STORING_ITEMS_IN_PYRAMID_BAG))
        return CheckBagHasItem(itemId, 1);""",
    )


def modify_bag_candy_supply(contents: str) -> str:
    """Provide Rare Candies to existing saves whenever the ordinary Bag opens."""
    return replace_once(
        contents,
        """void GoToBagMenu(u8 location, u8 pocket, MainCallback exitCallback)
{
    gBagMenu = AllocZeroed(sizeof(*gBagMenu));""",
        """void GoToBagMenu(u8 location, u8 pocket, MainCallback exitCallback)
{
    // Existing Delta saves receive the same reusable Rare Candy as new games.
    // Avoid battle-frontier / special bags and do not duplicate the item.
    if (location == ITEMMENULOCATION_FIELD
        && CurrentBattlePyramidLocation() == PYRAMID_LOCATION_NONE
        && !CheckBagHasItem(ITEM_RARE_CANDY, 1))
        AddBagItem(ITEM_RARE_CANDY, 99);
    if (location == ITEMMENULOCATION_FIELD
        && CurrentBattlePyramidLocation() == PYRAMID_LOCATION_NONE)
    {
        if (!CheckBagHasItem(ITEM_MASTER_BALL, 1))
            AddBagItem(ITEM_MASTER_BALL, 99);
        if (!CheckBagHasItem(ITEM_MAX_REPEL, 1))
            AddBagItem(ITEM_MAX_REPEL, 99);
        if (!CheckBagHasItem(ITEM_MAX_REVIVE, 1))
            AddBagItem(ITEM_MAX_REVIVE, 99);
        if (!CheckBagHasItem(ITEM_FULL_RESTORE, 1))
            AddBagItem(ITEM_FULL_RESTORE, 99);
        if (!CheckBagHasItem(ITEM_ESCAPE_ROPE, 1))
            AddBagItem(ITEM_ESCAPE_ROPE, 99);
        static const enum Item evolutionItems[] =
        {
            ITEM_LINKING_CORD, ITEM_FIRE_STONE, ITEM_WATER_STONE,
            ITEM_THUNDER_STONE, ITEM_LEAF_STONE, ITEM_MOON_STONE,
            ITEM_SUN_STONE, ITEM_SHINY_STONE, ITEM_DUSK_STONE,
            ITEM_DAWN_STONE, ITEM_ICE_STONE,
        };
        for (u32 i = 0; i < ARRAY_COUNT(evolutionItems); i++)
            if (!CheckBagHasItem(evolutionItems[i], 1))
                AddBagItem(evolutionItems[i], 1);
    }
    gBagMenu = AllocZeroed(sizeof(*gBagMenu));""",
    )


def modify_fast_experience(contents: str) -> str:
    """Give x4 experience, equivalent to quartering level-up work in battles."""
    return replace_once(
        contents,
        """        *expAmount = value + 1;
    }
}

void BS_ItemRestoreHP(void)""",
        """        *expAmount = value + 1;
    }
    // Faster progression without changing EXP tables or existing saved levels.
    // Battle EXP only; Rare Candies still grant one level per use.
    *expAmount *= 4;
}

void BS_ItemRestoreHP(void)""",
    )


def modify_hard_trainer_levels(contents: str) -> str:
    """Increase ordinary trainer levels; preserve Frontier trainer definitions."""
    return replace_once(
        contents,
        """    CreateMon(mon, trainerMon->species, trainerMon->lvl, personality, trainer->otID);""",
        """    // Hard mode: +25% levels and +2 levels for every standard trainer.
    // Keep Frontier and battle facility enemy sets untouched.
    u32 shatteredLevel = trainerMon->lvl;
    if (!trainer->isFrontier)
    {
        shatteredLevel = min(MAX_LEVEL, ((shatteredLevel * 5) / 4) + 2);
        // Adaptive rivals: Rare Candies cannot trivialize the entire game.
        // Standard trainers are at least the player's best level + 1.
        u32 highestPlayerLevel = 1;
        for (u32 i = 0; i < gPartiesCount[B_TRAINER_PLAYER]; i++)
        {
            enum Species playerSpecies = GetMonData(&gParties[B_TRAINER_PLAYER][i], MON_DATA_SPECIES_OR_EGG);
            if (playerSpecies != SPECIES_NONE && playerSpecies != SPECIES_EGG)
                highestPlayerLevel = max(highestPlayerLevel, GetMonData(&gParties[B_TRAINER_PLAYER][i], MON_DATA_LEVEL));
        }
        shatteredLevel = max(shatteredLevel, min(MAX_LEVEL, highestPlayerLevel + 1));
    }
    CreateMon(mon, trainerMon->species, shatteredLevel, personality, trainer->otID);""",
    )


def modify_hard_trainer_ivs(contents: str) -> str:
    """Give normal opposing trainers respectable IVs in every stat."""
    return replace_once(
        contents,
        "    SetMonData(mon, MON_DATA_IVS, &trainerMon->iv);",
        """    // IVs are SIX packed 5-bit values, not a single uniform IV.
    data = trainerMon->iv;
    if (!trainer->isFrontier)
    {
        for (u32 stat = 0; stat < NUM_STATS; stat++)
        {
            u32 shift = stat * 5;
            u32 iv = (data >> shift) & 31;
            data = (data & ~(31u << shift)) | (max(iv, 28) << shift);
        }
    }
    SetMonData(mon, MON_DATA_IVS, &data);""",
    )


def modify_hard_trainer_ai(contents: str) -> str:
    """Allow ordinary enemy trainers to choose moves with advanced AI."""
    return replace_once(
        contents,
        """    if (IsDoubleBattle() && flags != 0)
    {
        flags |= AI_FLAG_DOUBLE_BATTLE;""",
        """    // Hard mode: even early enemy trainers make competent decisions.
    // Do not alter link battles, tutorials, or recorded battles.
    if (trainerId != 0xFFFF && (gBattleTypeFlags & BATTLE_TYPE_TRAINER)
        && !(gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED
                                 | BATTLE_TYPE_RECORDED_LINK | BATTLE_TYPE_FRONTIER
                                 | BATTLE_TYPE_FIRST_BATTLE | BATTLE_TYPE_SAFARI)))
    {
        flags |= AI_FLAG_CHECK_BAD_MOVE | AI_FLAG_CHECK_VIABILITY
               | AI_FLAG_TRY_TO_FAINT | AI_FLAG_TRY_TO_2HKO | AI_FLAG_HP_AWARE
               | AI_FLAG_SMART_SWITCHING;
    }
    if (IsDoubleBattle() && flags != 0)
    {
        flags |= AI_FLAG_DOUBLE_BATTLE;""",
    )


def modify_hard_trainer_bag(contents: str) -> str:
    """No using healing items in trainer battles, but allow catching in the wild."""
    return replace_once(
        contents,
        """bool32 IsAllowedToUseBag(void)
{
    switch (VarGet(B_VAR_NO_BAG_USE))""",
        """bool32 IsAllowedToUseBag(void)
{
    // Hard mode: trainer fights cannot be won by endlessly healing.
    if ((gBattleTypeFlags & BATTLE_TYPE_TRAINER)
        && !(gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_FIRST_BATTLE)))
        return FALSE;
    switch (VarGet(B_VAR_NO_BAG_USE))""",
    )




def modify_rift_intro(contents: str) -> str:
    """First original story teaser without altering map or event IDs."""
    if "TEAM ECLIPSE" in contents:
        return contents
    pattern = r"gText_Birch_MainSpeech::\n.*?\ngText_Birch_AndYouAre::"
    replacement = r'''gText_Birch_MainSpeech::
	.string "Something strange has happened\n"
	.string "to our world.\p"
	.string "Violet RIFTS are opening across\n"
	.string "the regions of POKéMON.\p"
	.string "Creatures from distant lands\n"
	.string "are appearing everywhere.\p"
	.string "A shadowy group named\n"
	.string "TEAM ECLIPSE is investigating\l"
	.string "these mysterious breaches.\p"
	.string "I'm studying the RIFTS, but\n"
	.string "I need a brave new Trainer!\p$"

gText_Birch_AndYouAre::'''
    matches = list(re.finditer(pattern, contents, flags=re.S))
    if len(matches) != 1:
        raise ValueError("Could not uniquely identify intro dialogue")
    return re.sub(pattern, lambda m: replacement, contents, count=1, flags=re.S)


def modify_route_rift_teaser(contents: str) -> str:
    """Keep all Route 101 scripts intact; change only Birch's rescue dialogue."""
    if "RIFT flashed" in contents:
        return contents
    pattern = r"Route101_Text_YouSavedMe:\n.*?\nRoute101_Text_TakeTiredPokemonToPokeCenter:"
    replacement = r'''Route101_Text_YouSavedMe:
	.string "PROF. BIRCH: Whew! Thank you!\p"
	.string "I was studying strange POKéMON\n"
	.string "when a violet RIFT flashed.\p"
	.string "Then I was attacked!\p"
	.string "TEAM ECLIPSE may know why\n"
	.string "these RIFTS keep opening.\p"
	.string "Come to my LAB. We have\n"
	.string "important work to do!$"

Route101_Text_TakeTiredPokemonToPokeCenter:'''
    matches = list(re.finditer(pattern, contents, flags=re.S))
    if len(matches) != 1:
        raise ValueError("Could not uniquely identify Route 101 dialogue")
    return re.sub(pattern, lambda m: replacement, contents, count=1, flags=re.S)




# Rift chapter flags use pre-existing unused system flag bits, not new save fields.
RIFT_NPCS = {
    "OldaleTown": ("OldaleTown_EventScript_Girl", "ShatteredOldale_EventScript_RiftGuide"),
    "Route101": ("Route101_EventScript_Boy", "ShatteredRoute101_EventScript_Anomaly"),
    "Route102": ("Route102_EventScript_Boy", "ShatteredRoute102_EventScript_Anomaly"),
    "Route103": ("Route103_EventScript_Boy", "ShatteredRoute103_EventScript_Anomaly"),
}

RIFT_QUEST_SCRIPTS = {
    "OldaleTown": r"""
ShatteredOldale_EventScript_RiftGuide::
	lock
	faceplayer
	goto_if_set FLAG_UNUSED_0x90F, ShatteredOldale_EventScript_RiftCleared
	goto_if_unset FLAG_UNUSED_0x90B, ShatteredOldale_EventScript_StartQuest
	goto_if_unset FLAG_UNUSED_0x90E, ShatteredOldale_EventScript_QuestProgress
	msgbox ShatteredOldale_Text_EnterRift, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ShatteredOldale_EventScript_QuestExit
	closemessage
	warp MAP_RIFT_HOLLOW, 18, 21
	waitstate
	release
	end

ShatteredOldale_EventScript_StartQuest::
	goto_if_unset FLAG_SYS_POKEMON_GET, ShatteredOldale_EventScript_NoStarter
	msgbox ShatteredOldale_Text_QuestStart, MSGBOX_DEFAULT
	setflag FLAG_UNUSED_0x90B
	release
	end

ShatteredOldale_EventScript_NoStarter::
	msgbox ShatteredOldale_Text_NoStarter, MSGBOX_DEFAULT
	release
	end

ShatteredOldale_EventScript_QuestProgress::
	msgbox ShatteredOldale_Text_QuestProgress, MSGBOX_DEFAULT
	release
	end

ShatteredOldale_EventScript_RiftCleared::
	msgbox ShatteredOldale_Text_QuestComplete, MSGBOX_DEFAULT
	msgbox ShatteredOldale_Text_EnterRift, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ShatteredOldale_EventScript_QuestExit
	closemessage
	warp MAP_RIFT_HOLLOW, 18, 21
	waitstate
	release
	end

ShatteredOldale_EventScript_QuestExit::
	closemessage
	release
	end

ShatteredOldale_Text_QuestStart:
	.string "I am studying the ECLIPSE RIFTS.\p"
	.string "Please find three anomalies:\n"
	.string "ROUTE 101, 102 and 103.\p"
	.string "Speak to the researchers on\n"
	.string "each route, then return here!$"

ShatteredOldale_Text_NoStarter:
	.string "First, rescue PROF. BIRCH and\n"
	.string "choose your first POKeMON.$"

ShatteredOldale_Text_QuestProgress:
	.string "Investigate ROUTES 101, 102,\n"
	.string "and 103, in that order.\p"
	.string "Then return to open RIFT HOLLOW.$"

ShatteredOldale_Text_EnterRift:
	.string "All three anomalies are confirmed!\p"
	.string "A doorway to RIFT HOLLOW is open.\n"
	.string "Enter the dimensional breach?$"

ShatteredOldale_Text_QuestComplete:
	.string "You defeated the ECLIPSE WARDEN!\p"
	.string "The region is safer, but\n"
	.string "more RIFTS remain.$"
""",
    "Route101": r"""
ShatteredRoute101_EventScript_Anomaly::
	lock
	faceplayer
	goto_if_unset FLAG_UNUSED_0x90B, ShatteredRoute101_EventScript_Inactive
	goto_if_set FLAG_UNUSED_0x90C, ShatteredRoute101_EventScript_Done
	msgbox ShatteredRoute101_Text_Scan, MSGBOX_DEFAULT
	setflag FLAG_UNUSED_0x90C
	release
	end

ShatteredRoute101_EventScript_Inactive::
	msgbox ShatteredRoute101_Text_Inactive, MSGBOX_DEFAULT
	release
	end

ShatteredRoute101_EventScript_Done::
	msgbox ShatteredRoute101_Text_Done, MSGBOX_DEFAULT
	release
	end

ShatteredRoute101_Text_Scan:
	.string "This RIFT is pulsing with\n"
	.string "strange violet energy!\p"
	.string "Anomaly one recorded!\n"
	.string "Look for a scout on ROUTE 102.$"

ShatteredRoute101_Text_Inactive:
	.string "The air here has turned violet.\p"
	.string "A researcher in OLDALE TOWN\n"
	.string "might know what that means.$"

ShatteredRoute101_Text_Done:
	.string "The first anomaly is stable.\n"
	.string "Head to ROUTE 102 next.$"
""",
    "Route102": r"""
ShatteredRoute102_EventScript_Anomaly::
	lock
	faceplayer
	goto_if_unset FLAG_UNUSED_0x90C, ShatteredRoute102_EventScript_Inactive
	goto_if_set FLAG_UNUSED_0x90D, ShatteredRoute102_EventScript_Done
	msgbox ShatteredRoute102_Text_Scan, MSGBOX_DEFAULT
	setflag FLAG_UNUSED_0x90D
	release
	end

ShatteredRoute102_EventScript_Inactive::
	msgbox ShatteredRoute102_Text_Inactive, MSGBOX_DEFAULT
	release
	end

ShatteredRoute102_EventScript_Done::
	msgbox ShatteredRoute102_Text_Done, MSGBOX_DEFAULT
	release
	end

ShatteredRoute102_Text_Scan:
	.string "The second RIFT is stronger...\p"
	.string "I saw TEAM ECLIPSE taking\n"
	.string "readings near ROUTE 103!\p"
	.string "Anomaly two recorded!$"

ShatteredRoute102_Text_Inactive:
	.string "An odd noise is coming from\n"
	.string "the grass near here.\p"
	.string "Investigate ROUTE 101 first.$"

ShatteredRoute102_Text_Done:
	.string "The second anomaly is stable.\n"
	.string "Go north to ROUTE 103.$"
""",
    "Route103": r"""
ShatteredRoute103_EventScript_Anomaly::
	lock
	faceplayer
	goto_if_unset FLAG_UNUSED_0x90D, ShatteredRoute103_EventScript_Inactive
	goto_if_set FLAG_UNUSED_0x90E, ShatteredRoute103_EventScript_Done
	msgbox ShatteredRoute103_Text_Scan, MSGBOX_DEFAULT
	setflag FLAG_UNUSED_0x90E
	release
	end

ShatteredRoute103_EventScript_Inactive::
	msgbox ShatteredRoute103_Text_Inactive, MSGBOX_DEFAULT
	release
	end

ShatteredRoute103_EventScript_Done::
	msgbox ShatteredRoute103_Text_Done, MSGBOX_DEFAULT
	release
	end

ShatteredRoute103_Text_Scan:
	.string "TEAM ECLIPSE left behind\n"
	.string "a strange dimensional device!\p"
	.string "Anomaly three recorded!\n"
	.string "Return to OLDALE TOWN.$"

ShatteredRoute103_Text_Inactive:
	.string "These footprints do not look\n"
	.string "human. Something passed by.\p"
	.string "First check the earlier RIFTS.$"

ShatteredRoute103_Text_Done:
	.string "You found the last anomaly.\n"
	.string "The OLDALE guide is waiting.$"
""",
}


def modify_rift_map_groups(contents: str) -> str:
    document = json.loads(contents)
    group = document["gMapGroup_Dungeons"]
    if "RiftHollow" not in group:
        # Appending leaves every pre-existing dungeon map index unchanged.
        group.append("RiftHollow")
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def modify_quest_npc_map(contents: str, map_name: str) -> str:
    old_script, new_script = RIFT_NPCS[map_name]
    document = json.loads(contents)
    matching = [obj for obj in document["object_events"] if obj.get("script") in (old_script, new_script)]
    if len(matching) != 1:
        raise ValueError(f"Could not uniquely identify quest NPC on {map_name}")
    matching[0]["script"] = new_script
    if map_name == "OldaleTown":
        matching[0]["graphics_id"] = "OBJ_EVENT_GFX_SCIENTIST_1"
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def modify_quest_map_script(contents: str, map_name: str) -> str:
    patch = RIFT_QUEST_SCRIPTS[map_name]
    first_label = RIFT_NPCS[map_name][1] + "::"
    if first_label in contents:
        return contents
    return contents.rstrip() + "\n\n" + patch.strip() + "\n"




def modify_first_gym_party(contents: str) -> str:
    """First badge is earned in Astra's harder multi-type Rift Gym."""
    if "Name: ASTRA" in contents.split("=== TRAINER_ROXANNE_1 ===", 1)[1].split("=== TRAINER_BRAWLY_1 ===", 1)[0]:
        return contents
    pattern = r"=== TRAINER_ROXANNE_1 ===\n.*?(?=\n=== TRAINER_BRAWLY_1 ===)"
    replacement = """=== TRAINER_ROXANNE_1 ===
Name: ASTRA
Class: Leader
Pic: Hex Maniac
Gender: Female
Music: Female
Items: Super Potion / Super Potion
Double Battle: No
AI: Check Bad Move / Try To Faint / Check Viability

Wooper @ Eviolite
Level: 16
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
- Mud Shot
- Water Gun
- Yawn
- Protect

Sandile @ Oran Berry
Level: 17
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
- Bite
- Sand Tomb
- Rock Tomb
- Assurance

Gible @ Sitrus Berry
Level: 19
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
- Dragon Breath
- Bulldoze
- Sandstorm
- Rock Tomb

Misdreavus @ Sitrus Berry
Level: 20
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
- Shadow Sneak
- Psybeam
- Confuse Ray
- Mystical Fire
"""
    if len(re.findall(pattern, contents, re.S)) != 1:
        raise ValueError("Could not find original first gym leader party")
    result = re.sub(pattern, lambda match: replacement.rstrip() + "\n", contents, count=1, flags=re.S)
    # Preserve rematch IDs, but align other Roxanne battle names with Astra.
    result = re.sub(r"(=== TRAINER_ROXANNE_\d+ ===\nName: )ROXANNE",
                    lambda match: match.group(1) + "ASTRA", result)
    return result


def modify_first_gym_dialogue(contents: str) -> str:
    """Original first gym storyline and badge flags remain, with new chapter script."""
    if "I guard the RIFT GYM" in contents:
        return contents
    start = contents.index("RustboroCity_Gym_Text_RoxanneIntro:\n")
    end = contents.index("\nRustboroCity_Gym_Text_RoxanneDefeat:", start)
    new_intro = r'''RustboroCity_Gym_Text_RoxanneIntro:
	.string "ASTRA: I guard the RIFT GYM.\p"
	.string "TEAM ECLIPSE has unsettled\n"
	.string "the balance of every type.\p"
	.string "Here you will face GROUND,\n"
	.string "DRAGON, and GHOST POKeMON!\p"
	.string "Your unlimited power will\n"
	.string "not replace good strategy!$"'''
    contents = contents[:start] + new_intro + contents[end:]
    # Keep engine symbols and save flags stable; rename dialogue only.
    contents = contents.replace('"ROXANNE', '"ASTRA').replace(' ROXANNE', ' ASTRA')
    contents = contents.replace(
        '"of ROCK-type POKéMON.\\p"',
        '"of many different POKéMON.\\p"',
    )
    contents = contents.replace(
        '"The ROCK type is very durable, but\\n"',
        '"Her GROUND-types resist ELECTRIC.\\n"',
    )
    return contents


def modify_first_gym_character(contents: str) -> str:
    document = json.loads(contents)
    targets = [obj for obj in document["object_events"]
               if obj.get("script") == "RustboroCity_Gym_EventScript_Roxanne"]
    if len(targets) != 1:
        raise ValueError("Expected one first gym leader overworld sprite")
    targets[0]["graphics_id"] = "OBJ_EVENT_GFX_HEX_MANIAC"
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"



def modify_rift_script_registration(contents: str) -> str:
    """Include new Rift Hollow scripts in the event-script assembler."""
    return replace_once(
        contents,
        '\t.include "data/maps/Route101/scripts.inc"',
        '\t.include "data/maps/Route101/scripts.inc"\n\t.include "data/maps/RiftHollow/scripts.inc"',
    )


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
        "src/battle_util.c": lambda c: modify_hard_trainer_bag(modify_player_pp_checks(c)),
        "src/battle_controller_player.c": lambda c: modify_all_move_pages(modify_move_pp_display(c)),
        "src/money.c": modify_unlimited_money,
        "src/item.c": modify_infinite_candy,
        "src/item_menu.c": modify_bag_candy_supply,
        "src/battle_script_commands.c": lambda c: modify_pp_drain_and_sketch(modify_fast_experience(c)),
        "src/battle_move_resolution.c": modify_pp_resolution,
        "include/battle_util.h": modify_unlimited_pp_header,
        "data/maps/RiftHollow/scripts.inc": modify_rift_reward_retry,
        "src/trainer_util.c": lambda c: modify_hard_trainer_ivs(modify_hard_trainer_levels(c)),
        "src/battle_ai_main.c": modify_hard_trainer_ai,
        "data/text/birch_speech.inc": modify_rift_intro,
        "data/maps/Route101/scripts.inc": modify_route_rift_teaser,
        "data/event_scripts.s": modify_rift_script_registration,
    }
    for relative_path, patcher in gameplay_sources.items():
        path = engine / relative_path
        updates[path] = patcher(path.read_text(encoding="utf-8"))

    gym_party_path = engine / "src/data/trainers.party"
    updates[gym_party_path] = modify_first_gym_party(gym_party_path.read_text(encoding="utf-8"))
    gym_script_path = engine / "data/maps/RustboroCity_Gym/scripts.inc"
    updates[gym_script_path] = modify_first_gym_dialogue(gym_script_path.read_text(encoding="utf-8"))
    gym_map_path = engine / "data/maps/RustboroCity_Gym/map.json"
    updates[gym_map_path] = modify_first_gym_character(gym_map_path.read_text(encoding="utf-8"))

    map_groups_path = engine / "data/maps/map_groups.json"
    updates[map_groups_path] = modify_rift_map_groups(map_groups_path.read_text(encoding="utf-8"))
    for map_name in RIFT_NPCS:
        map_path = engine / "data/maps" / map_name / "map.json"
        scripts_path = engine / "data/maps" / map_name / "scripts.inc"
        updates[map_path] = modify_quest_npc_map(map_path.read_text(encoding="utf-8"), map_name)
        updates[scripts_path] = modify_quest_map_script(
            updates.get(scripts_path, scripts_path.read_text(encoding="utf-8")), map_name)

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

