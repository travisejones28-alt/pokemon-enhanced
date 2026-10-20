#include "global.h"
#include "battle.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "shattered_history.h"
#include "shattered_battle.h"
#include "load_save.h"
#include "item.h"
#include "test/test.h"

TEST("Shattered history retains exceptional moves through replacement and evolution")
{
    u16 history[16];
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    memset(gSaveBlock3Ptr->shatteredMoveHistory, 0, SHATTERED_HISTORY_BYTES);
    CreateMon(mon, SPECIES_MAGIKARP, 5, 123, OTID_STRUCT_PRESET(456));
    SetMonMoveSlot(mon, MOVE_ROAR_OF_TIME, 0);
    SetMonMoveSlot(mon, MOVE_SPLASH, 0);
    EXPECT_EQ(GetMonData(mon, MON_DATA_MOVE1), MOVE_SPLASH);
    EXPECT_EQ(ShatteredReadBoxHistory(&mon->box, history, ARRAY_COUNT(history)), 1);
    EXPECT_EQ(history[0], MOVE_ROAR_OF_TIME);
    u16 species = SPECIES_GYARADOS;
    SetMonData(mon, MON_DATA_SPECIES, &species);
    EXPECT_EQ(ShatteredReadBoxHistory(&mon->box, history, ARRAY_COUNT(history)), 1);
    EXPECT_EQ(history[0], MOVE_ROAR_OF_TIME);
}

TEST("Shattered history follows a Pokemon into PC storage")
{
    u16 history[16];
    struct Pokemon mon;
    memset(gSaveBlock3Ptr->shatteredMoveHistory, 0, SHATTERED_HISTORY_BYTES);
    CreateMon(&mon, SPECIES_MAGIKARP, 5, 124, OTID_STRUCT_PRESET(456));
    gPokemonStoragePtr->boxes[0][0] = mon.box;
    struct BoxPokemon *stored = &gPokemonStoragePtr->boxes[0][0];
    SetBoxMonMoveSlot(stored, MOVE_ROAR_OF_TIME, 0);
    SetBoxMonMoveSlot(stored, MOVE_SPLASH, 0);
    EXPECT_EQ(ShatteredReadBoxHistory(stored, history, ARRAY_COUNT(history)), 1);
    EXPECT_EQ(history[0], MOVE_ROAR_OF_TIME);
}

TEST("Shattered history separates identical personalities with different original trainers")
{
    u16 moves[2];
    u8 *store = gSaveBlock3Ptr->shatteredMoveHistory;
    memset(store, 0, SHATTERED_HISTORY_BYTES);
    EXPECT(ShatteredHistoryRemember(store, 100, 200, MOVE_SURF));
    EXPECT(ShatteredHistoryRemember(store, 100, 201, MOVE_FLY));
    EXPECT_EQ(ShatteredHistoryRead(store, 100, 200, moves, ARRAY_COUNT(moves)), 1);
    EXPECT_EQ(moves[0], MOVE_SURF);
}

TEST("Shattered history never overwrites an unarchived attack when storage is full")
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    u8 *store = gSaveBlock3Ptr->shatteredMoveHistory;
    memset(store, 0, SHATTERED_HISTORY_BYTES);
    CreateMon(mon, SPECIES_MAGIKARP, 5, 555, OTID_STRUCT_PRESET(777));
    SetMonMoveSlot(mon, MOVE_ROAR_OF_TIME, 0);
    for (u32 i = 1; i < SHATTERED_HISTORY_CAPACITY; i++)
        EXPECT(ShatteredHistoryRemember(store, i, 999, MOVE_TACKLE));
    // A new exceptional move can stay in the saved slot, even if not archived.
    SetMonMoveSlot(mon, MOVE_SPACIAL_REND, 0);
    EXPECT_EQ(GetMonData(mon, MON_DATA_MOVE1), MOVE_SPACIAL_REND);
    // Its only copy must survive a later replacement attempt.
    SetMonMoveSlot(mon, MOVE_SPLASH, 0);
    EXPECT_EQ(GetMonData(mon, MON_DATA_MOVE1), MOVE_SPACIAL_REND);
}

TEST("Shattered companion bond attacks remain learned after friendship decreases")
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    u16 history[4];
    memset(gSaveBlock3Ptr->shatteredMoveHistory, 0, SHATTERED_HISTORY_BYTES);
    CreateMon(mon, SPECIES_PIKACHU, 5, 888, OTID_STRUCT_PRESET(999));
    u32 bond = 240;
    SetMonData(mon, MON_DATA_FRIENDSHIP, &bond);
    EXPECT(ShatteredGetBondMessage(mon) != NULL);
    bond = 40;
    SetMonData(mon, MON_DATA_FRIENDSHIP, &bond);
    EXPECT_EQ(ShatteredReadBoxHistory(&mon->box, history, ARRAY_COUNT(history)), 3);
    EXPECT_EQ(history[0], MOVE_ZIPPY_ZAP);
    EXPECT_EQ(history[1], MOVE_SPLISHY_SPLASH);
    EXPECT_EQ(history[2], MOVE_FLOATY_FALL);
}

TEST("Shattered Karrablast and Shelmet can evolve without a trade partner")
{
    struct Pokemon mon;
    CreateMon(&mon, SPECIES_KARRABLAST, 5, 300, OTID_STRUCT_PRESET(400));
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_ITEM_CHECK, ITEM_LINKING_CORD, NULL, NULL, CHECK_EVO), SPECIES_ESCAVALIER);
    CreateMon(&mon, SPECIES_SHELMET, 5, 301, OTID_STRUCT_PRESET(400));
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_ITEM_CHECK, ITEM_LINKING_CORD, NULL, NULL, CHECK_EVO), SPECIES_ACCELGOR);
}

TEST("Shattered generated old-format save loads, migrates, saves and reloads")
{
    SetSaveBlocksPointers(0);
    ClearSav1();
    ClearSav2();
    ClearSav3();
    gPartiesCount[B_TRAINER_PLAYER] = 1;
    CreateMon(&gParties[B_TRAINER_PLAYER][0], SPECIES_PIKACHU, 5, 321, OTID_STRUCT_PRESET(654));
    EXPECT(AddBagItem(ITEM_RARE_CANDY, 99));
    gSaveBlock1Ptr->pos.x = 12;
    gSaveBlock1Ptr->pos.y = 14;
    gSaveBlock3Ptr->dexNavChain = 7;
    // A zero tail produces the same extension bytes as an older ROM: old
    // versions cleared the whole sector and wrote only their existing fields.
    memset(gSaveBlock3Ptr->shatteredMoveHistory, 0, SHATTERED_HISTORY_BYTES);
    Save_ResetSaveCounters();
    CheckForFlashMemory();
    EXPECT(gFlashMemoryPresent);
    EXPECT_EQ(TrySavingData(SAVE_NORMAL), SAVE_STATUS_OK);
    ZeroMonData(&gParties[B_TRAINER_PLAYER][0]);
    memset(gSaveBlock3Ptr->shatteredMoveHistory, 255, SHATTERED_HISTORY_BYTES);
    EXPECT_EQ(LoadGameSave(SAVE_NORMAL), SAVE_STATUS_OK);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_SPECIES), SPECIES_PIKACHU);
    EXPECT(CheckBagHasItem(ITEM_RARE_CANDY, 99));
    EXPECT_EQ(gSaveBlock1Ptr->pos.x, 12);
    EXPECT_EQ(gSaveBlock1Ptr->pos.y, 14);
    EXPECT_EQ(gSaveBlock3Ptr->dexNavChain, 7);
    EXPECT(ShatteredHistoryOpen(gSaveBlock3Ptr->shatteredMoveHistory));
    SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][0], MOVE_ROAR_OF_TIME, 0);
    SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][0], MOVE_THUNDERBOLT, 0);
    EXPECT_EQ(TrySavingData(SAVE_NORMAL), SAVE_STATUS_OK);
    ClearSav3();
    EXPECT_EQ(LoadGameSave(SAVE_NORMAL), SAVE_STATUS_OK);
    u16 moves[4];
    EXPECT_EQ(ShatteredReadBoxHistory(&gParties[B_TRAINER_PLAYER][0].box, moves, ARRAY_COUNT(moves)), 1);
    EXPECT_EQ(moves[0], MOVE_ROAR_OF_TIME);
    EXPECT_EQ(gSaveBlock3Ptr->dexNavChain, 7);
    EXPECT(CheckBagHasItem(ITEM_RARE_CANDY, 99));
}

TEST("Shattered library knowledge includes archived attacks outside the current page")
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    memset(gSaveBlock3Ptr->shatteredMoveHistory, 0, SHATTERED_HISTORY_BYTES);
    CreateMon(mon, SPECIES_MAGIKARP, 5, 1444, OTID_STRUCT_PRESET(1555));
    SetMonMoveSlot(mon, MOVE_ROAR_OF_TIME, 0);
    SetMonMoveSlot(mon, MOVE_SPLASH, 0);
    EXPECT(ShatteredBoxKnowsMove(&mon->box, MOVE_ROAR_OF_TIME));
    EXPECT(ShatteredBoxKnowsMove(&mon->box, MOVE_SPLASH));
    EXPECT(!ShatteredBoxKnowsMove(&mon->box, MOVE_MEMENTO));
}

TEST("Shattered save extension preserves every original persistent Pokemon and main save footprint")
{
    EXPECT_EQ(sizeof(struct SaveBlock1), 15568);
    EXPECT_EQ(sizeof(struct SaveBlock2), 3884);
    EXPECT_EQ(sizeof(struct PokemonStorage), 34144);
    EXPECT_EQ(sizeof(struct Pokemon), 100);
    EXPECT_EQ(sizeof(struct BoxPokemon), 80);
    EXPECT_EQ(__builtin_offsetof(struct SaveBlock1, flags), 4720);
    EXPECT_EQ(__builtin_offsetof(struct SaveBlock1, bag), 1376);
    EXPECT_EQ(__builtin_offsetof(struct SaveBlock1, playerParty), 568);
    EXPECT_EQ(__builtin_offsetof(struct SaveBlock3, dexNavChain), 0);
    EXPECT_EQ(sizeof(struct SaveBlock3), 1540);
}


TEST("Shattered automatic learning retains four saved attacks without forget prompts")
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    const enum Move saved[] = {MOVE_ROAR_OF_TIME, MOVE_SPACIAL_REND, MOVE_DARK_VOID, MOVE_AEROBLAST};
    memset(gSaveBlock3Ptr->shatteredMoveHistory, 0, SHATTERED_HISTORY_BYTES);
    CreateMon(mon, SPECIES_PIKACHU, 50, 2001, OTID_STRUCT_PRESET(2002));
    for (u32 i = 0; i < MAX_MON_MOVES; i++)
        SetMonMoveSlot(mon, saved[i], i);
    const struct LevelUpMove *learnset = GetSpeciesLevelUpLearnset(SPECIES_PIKACHU);
    u32 entry = 0;
    while (learnset[entry].move != LEVEL_UP_MOVE_END && learnset[entry].level <= 1)
        entry++;
    EXPECT(learnset[entry].move != LEVEL_UP_MOVE_END);
    u32 level = learnset[entry].level;
    EXPECT_EQ(MonTryLearningNewMoveAtLevel(mon, TRUE, level), MON_ALREADY_KNOWS_MOVE);
    EXPECT(ShatteredBoxKnowsMove(&mon->box, learnset[entry].move));
    for (u32 i = 0; i < MAX_MON_MOVES; i++)
        EXPECT_EQ(GetMonData(mon, MON_DATA_MOVE1 + i), saved[i]);
    // Multiple moves at one level must eventually finish, never repeat forever.
    u32 attempts = 0;
    while (MonTryLearningNewMoveAtLevel(mon, FALSE, level) != MOVE_NONE && attempts < 100)
        attempts++;
    EXPECT(attempts < 100);
}

TEST("Shattered move-based evolution recognizes an attack in the expanded library")
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    memset(gSaveBlock3Ptr->shatteredMoveHistory, 0, SHATTERED_HISTORY_BYTES);
    CreateMon(mon, SPECIES_TANGELA, 100, 2003, OTID_STRUCT_PRESET(2004));
    for (u32 i = 0; i < MAX_MON_MOVES; i++)
        SetMonMoveSlot(mon, MOVE_TACKLE, i);
    EXPECT(ShatteredBoxKnowsMove(&mon->box, MOVE_ANCIENT_POWER));
    EXPECT_EQ(GetEvolutionTargetSpecies(mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, NULL, CHECK_EVO),
              SPECIES_TANGROWTH);
}
