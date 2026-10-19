#ifndef GUARD_SHATTERED_BATTLE_H
#define GUARD_SHATTERED_BATTLE_H
struct BoxPokemon;
bool32 ShatteredBoxKnowsMove(struct BoxPokemon *mon, u16 move);
#if TESTING
#include "test_runner.h"
extern bool32 gShatteredTestLocalMechanics;
#endif
#endif
