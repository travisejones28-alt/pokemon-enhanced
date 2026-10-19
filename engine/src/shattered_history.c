#include "global.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "shattered_history.h"
#include "shattered_battle.h"
#include "constants/battle.h"
#include "constants/moves.h"
#if TESTING
EWRAM_DATA bool32 gShatteredTestLocalMechanics = FALSE;
#endif

static bool32 IsOwnedBoxMon(struct BoxPokemon *mon)
{
    for (u32 i = 0; i < PARTY_SIZE; i++)
        if (mon == &gParties[B_TRAINER_PLAYER][i].box)
            return TRUE;
    for (u32 i = 0; i < DAYCARE_MON_COUNT; i++)
        if (mon == &gSaveBlock1Ptr->daycare.mons[i].mon)
            return TRUE;
    if (gPokemonStoragePtr != NULL)
        for (u32 box = 0; box < TOTAL_BOXES_COUNT; box++)
            for (u32 slot = 0; slot < IN_BOX_COUNT; slot++)
                if (mon == &gPokemonStoragePtr->boxes[box][slot])
                    return TRUE;
    return FALSE;
}

static bool32 IsReconstructedMove(struct BoxPokemon *mon, u16 move)
{
    enum Species species = GetBoxMonData(mon, MON_DATA_SPECIES);
    u32 level = GetLevelFromBoxMonExp(mon);
    for (u32 depth = 0; species != SPECIES_NONE && depth < 16; depth++)
    {
        const struct LevelUpMove *levelMoves = GetSpeciesLevelUpLearnset(species);
        for (u32 i = 0; levelMoves[i].move != LEVEL_UP_MOVE_END; i++)
            if (levelMoves[i].move == move && levelMoves[i].level <= level)
                return TRUE;
        const u16 *teachable = GetSpeciesTeachableLearnset(species);
        for (u32 i = 0; teachable[i] != MOVE_UNAVAILABLE; i++)
            if (teachable[i] == move)
                return TRUE;
        const u16 *egg = GetSpeciesEggMoves(species);
        for (u32 i = 0; egg[i] != MOVE_UNAVAILABLE; i++)
            if (egg[i] == move)
                return TRUE;
        // Starter signatures remain reconstructible after evolution, too.
        if (species == SPECIES_PIKACHU
            && (move == MOVE_THUNDERBOLT || move == MOVE_VOLT_TACKLE
                || move == MOVE_SURF || move == MOVE_EXTREME_SPEED
                || move == MOVE_IRON_TAIL || move == MOVE_GRASS_KNOT
                || move == MOVE_BRICK_BREAK || move == MOVE_THUNDER_WAVE))
            return TRUE;
        species = GetSpeciesPreEvolution(species);
    }
    return FALSE;
}

static bool32 Remember(struct BoxPokemon *mon, u16 move)
{
    if (move == MOVE_NONE || move >= MOVES_COUNT)
        return TRUE;
    return ShatteredHistoryRemember(gSaveBlock3Ptr->shatteredMoveHistory,
        mon->personality, mon->otId, move);
}

bool32 ShatteredBeforeSetBoxMove(struct BoxPokemon *mon, s32 field, u16 move)
{
    if (!IsOwnedBoxMon(mon) || !mon->hasSpecies || mon->isBadEgg || mon->isEgg)
        return TRUE;
    u16 oldMove = GetBoxMonData(mon, field);
    if (oldMove == move)
        return TRUE;
    // Compatible moves are reconstructed without using any archive slots.
    // Never overwrite the only copy of an exceptional move if storage is full
    // or the archive checksum/version is invalid.
    if (oldMove != MOVE_NONE && !IsReconstructedMove(mon, oldMove) && !Remember(mon, oldMove))
        return FALSE;
    // If this fails the new attack is still retained in the saved move slot;
    // the next replacement will preserve it or refuse the overwrite.
    if (!IsReconstructedMove(mon, move))
        Remember(mon, move);
    return TRUE;
}

u32 ShatteredReadBoxHistory(struct BoxPokemon *mon, u16 *moves, u32 capacity)
{
    return ShatteredHistoryRead(gSaveBlock3Ptr->shatteredMoveHistory,
        mon->personality, mon->otId, moves, capacity);
}

void ShatteredRememberBondMove(struct BoxPokemon *mon, u16 move)
{
    Remember(mon, move);
}

bool32 ShatteredBoxKnowsMove(struct BoxPokemon *mon, u16 move)
{
    if (move == MOVE_NONE || move >= MOVES_COUNT)
        return FALSE;
    for (u32 slot = 0; slot < MAX_MON_MOVES; slot++)
        if (GetBoxMonData(mon, MON_DATA_MOVE1 + slot) == move)
            return TRUE;
    if (IsReconstructedMove(mon, move))
        return TRUE;
    u16 moves[SHATTERED_HISTORY_CAPACITY];
    u32 count = ShatteredReadBoxHistory(mon, moves, ARRAY_COUNT(moves));
    for (u32 i = 0; i < count; i++)
        if (moves[i] == move)
            return TRUE;
    return FALSE;
}
