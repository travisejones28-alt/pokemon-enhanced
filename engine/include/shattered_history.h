#ifndef GUARD_SHATTERED_HISTORY_H
#define GUARD_SHATTERED_HISTORY_H

// Appended only to the existing SaveBlock3 tail; never to a Pokémon record.
#define SHATTERED_HISTORY_BYTES 1536
#define SHATTERED_HISTORY_HEADER_BYTES 16
#define SHATTERED_HISTORY_RECORD_BYTES 10
#define SHATTERED_HISTORY_CAPACITY ((SHATTERED_HISTORY_BYTES - SHATTERED_HISTORY_HEADER_BYTES) / SHATTERED_HISTORY_RECORD_BYTES)
#define SHATTERED_HISTORY_VERSION 1

struct BoxPokemon;
struct Pokemon;
bool32 ShatteredHistoryOpen(u8 *store);
bool32 ShatteredHistoryRemember(u8 *store, u32 personality, u32 otId, u16 move);
u32 ShatteredHistoryRead(u8 *store, u32 personality, u32 otId, u16 *moves, u32 capacity);
bool32 ShatteredBeforeSetBoxMove(struct BoxPokemon *mon, s32 field, u16 move);
u32 ShatteredReadBoxHistory(struct BoxPokemon *mon, u16 *moves, u32 capacity);
void ShatteredRememberBondMove(struct BoxPokemon *mon, u16 move);

const u8 *ShatteredGetBondMessage(struct Pokemon *mon);

#endif
