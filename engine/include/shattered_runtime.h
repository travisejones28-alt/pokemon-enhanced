#ifndef GUARD_SHATTERED_RUNTIME_H
#define GUARD_SHATTERED_RUNTIME_H

// Runtime Shattered Rules. Uses one pre-existing, formerly unused event var.
// Does not alter any save block size, Pokemon format or save serialization.
// A marker distinguishes configured saves from old saves (which retain the
// build-time defaults). Changes persist after a normal in-game SAVE.
#include "config/shattered.h"
#include "event_data.h"

#define SHATTERED_RULES_VAR VAR_UNUSED_0x404E
#define SHATTERED_RULES_MARKER 0xB000
#define SHATTERED_RULES_MASK 0xF000

// Layout: difficulty 0-1; scaling 2; move mode 3-4; EXP-1 5-6;
// unlimited money 7; supplies 8. Bits 9-11 are reserved and zero.
// Move mode: 0 = normal four moves/finite PP, 1 = unlimited PP,
// 2 = unlimited PP + library pages. Link and recorded battles stay native.
static inline u16 ShatteredRulesDefaults(void)
{
    return SHATTERED_RULES_MARKER
        | (SHATTERED_DIFFICULTY & 3)
        | ((SHATTERED_LEVEL_SCALING ? 1 : 0) << 2)
        | ((SHATTERED_EXPANDED_MOVES ? 2 : (SHATTERED_UNLIMITED_PP ? 1 : 0)) << 3)
        | ((SHATTERED_EXP_MULTIPLIER - 1) << 5)
        | ((SHATTERED_UNLIMITED_MONEY ? 1 : 0) << 7)
        | ((SHATTERED_FREE_SUPPLIES ? 1 : 0) << 8);
}

static inline u16 ShatteredRulesRead(void)
{
    u16 value;
    // A few engine utility functions query money before any save is loaded.
    if (gSaveBlock1Ptr == NULL)
        return ShatteredRulesDefaults();
    value = VarGet(SHATTERED_RULES_VAR);
    if ((value & SHATTERED_RULES_MASK) != SHATTERED_RULES_MARKER
        || (value & 3) > 2 || ((value >> 3) & 3) > 2
        || (value & 0x0E00) != 0)
        return ShatteredRulesDefaults();
    return value;
}

static inline u32 ShatteredRuntimeDifficulty(void)
{
    return ShatteredRulesRead() & 3;
}

static inline bool32 ShatteredRuntimeScaling(void)
{
    return (ShatteredRulesRead() & (1 << 2)) != 0;
}

static inline bool32 ShatteredRuntimeEnhancedAI(void)
{
    return ShatteredRuntimeDifficulty() != SHATTERED_NORMAL;
}

static inline u32 ShatteredRuntimeMoveMode(void)
{
    return (ShatteredRulesRead() >> 3) & 3;
}

static inline bool32 ShatteredRuntimeUnlimitedPP(void)
{
    return ShatteredRuntimeMoveMode() != 0;
}

static inline bool32 ShatteredRuntimeExpandedMoves(void)
{
    return ShatteredRuntimeMoveMode() == 2;
}

static inline u32 ShatteredRuntimeExpMultiplier(void)
{
    return ((ShatteredRulesRead() >> 5) & 3) + 1;
}

static inline bool32 ShatteredRuntimeUnlimitedMoney(void)
{
    return (ShatteredRulesRead() & (1 << 7)) != 0;
}

static inline bool32 ShatteredRuntimeFreeSupplies(void)
{
    return (ShatteredRulesRead() & (1 << 8)) != 0;
}

// Only called from the out-of-battle Options screen.
static inline void ShatteredRulesCycle(u32 option, bool32 forward)
{
    static const u8 shifts[] = {0, 2, 3, 5, 7, 8};
    static const u8 choices[] = {3, 2, 3, 4, 2, 2};
    u16 value;
    u32 shift, mask, current;
    if (option >= ARRAY_COUNT(shifts) || gSaveBlock1Ptr == NULL)
        return;
    value = ShatteredRulesRead();
    shift = shifts[option];
    mask = (option == 0 || option == 2 || option == 3) ? 3 : 1;
    current = (value >> shift) & mask;
    current = forward ? (current + 1) % choices[option]
                      : (current + choices[option] - 1) % choices[option];
    value = (value & ~(mask << shift)) | (current << shift);
    VarSet(SHATTERED_RULES_VAR, value);
}

// Override build defaults only in source files that opt in to the runtime
// rules. The defaults above and config's compile-time guards remain intact.
#undef SHATTERED_DIFFICULTY
#define SHATTERED_DIFFICULTY ShatteredRuntimeDifficulty()
#undef SHATTERED_LEVEL_SCALING
#define SHATTERED_LEVEL_SCALING ShatteredRuntimeScaling()
#undef SHATTERED_ENHANCED_AI
#define SHATTERED_ENHANCED_AI ShatteredRuntimeEnhancedAI()
#undef SHATTERED_UNLIMITED_PP
#define SHATTERED_UNLIMITED_PP ShatteredRuntimeUnlimitedPP()
#undef SHATTERED_EXPANDED_MOVES
#define SHATTERED_EXPANDED_MOVES ShatteredRuntimeExpandedMoves()
#undef SHATTERED_EXP_MULTIPLIER
#define SHATTERED_EXP_MULTIPLIER ShatteredRuntimeExpMultiplier()
#undef SHATTERED_UNLIMITED_MONEY
#define SHATTERED_UNLIMITED_MONEY ShatteredRuntimeUnlimitedMoney()
#undef SHATTERED_FREE_SUPPLIES
#define SHATTERED_FREE_SUPPLIES ShatteredRuntimeFreeSupplies()

#endif // GUARD_SHATTERED_RUNTIME_H
