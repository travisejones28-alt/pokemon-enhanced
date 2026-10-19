#include "global.h"
#include "shattered_history.h"

#define HISTORY_MAGIC 0x31484D53u // SMH1 in little endian

static u32 Read32(const u8 *p)
{
    return p[0] | (u32)p[1] << 8 | (u32)p[2] << 16 | (u32)p[3] << 24;
}

static void Write32(u8 *p, u32 value)
{
    for (u32 i = 0; i < 4; i++)
        p[i] = value >> (i * 8);
}

static u16 Read16(const u8 *p)
{
    return p[0] | (u16)p[1] << 8;
}

static void Write16(u8 *p, u16 value)
{
    p[0] = value;
    p[1] = value >> 8;
}

static u32 HistoryChecksum(const u8 *store)
{
    u32 hash = 2166136261u;
    // Magic is checked separately. Include version/count and the entire payload.
    for (u32 i = 4; i < SHATTERED_HISTORY_BYTES; i++)
        if (i < 8 || i >= 12)
            hash = (hash ^ store[i]) * 16777619u;
    return hash;
}

bool32 ShatteredHistoryOpen(u8 *store)
{
    if (Read32(store) == HISTORY_MAGIC)
        return Read16(store + 4) == SHATTERED_HISTORY_VERSION
            && Read16(store + 6) <= SHATTERED_HISTORY_CAPACITY
            && Read32(store + 8) == HistoryChecksum(store);

    // Old saves wrote zero-filled unused sector tails. Never erase unknown or
    // damaged archive data, including an archive written by a future version.
    u8 fill = store[0];
    if (fill != 0 && fill != 0xFF)
        return FALSE;
    for (u32 i = 0; i < SHATTERED_HISTORY_BYTES; i++)
        if (store[i] != fill)
            return FALSE;
    for (u32 i = 0; i < SHATTERED_HISTORY_BYTES; i++)
        store[i] = 0;
    Write32(store, HISTORY_MAGIC);
    Write16(store + 4, SHATTERED_HISTORY_VERSION);
    Write32(store + 8, HistoryChecksum(store));
    return TRUE;
}

bool32 ShatteredHistoryRemember(u8 *store, u32 personality, u32 otId, u16 move)
{
    if (move == 0 || move >= 2048 || !ShatteredHistoryOpen(store))
        return FALSE;
    u32 count = Read16(store + 6);
    for (u32 i = 0; i < count; i++)
    {
        const u8 *record = store + SHATTERED_HISTORY_HEADER_BYTES + i * SHATTERED_HISTORY_RECORD_BYTES;
        if (Read32(record) == personality && Read32(record + 4) == otId && Read16(record + 8) == move)
            return TRUE;
    }
    if (count == SHATTERED_HISTORY_CAPACITY)
        return FALSE; // Never evict another Pokémon's learned attack.
    u8 *record = store + SHATTERED_HISTORY_HEADER_BYTES + count * SHATTERED_HISTORY_RECORD_BYTES;
    Write32(record, personality);
    Write32(record + 4, otId);
    Write16(record + 8, move);
    Write16(store + 6, count + 1);
    Write32(store + 8, HistoryChecksum(store));
    return TRUE;
}

u32 ShatteredHistoryRead(u8 *store, u32 personality, u32 otId, u16 *moves, u32 capacity)
{
    if (!ShatteredHistoryOpen(store))
        return 0;
    u32 copied = 0;
    u32 count = Read16(store + 6);
    for (u32 i = 0; i < count && copied < capacity; i++)
    {
        const u8 *record = store + SHATTERED_HISTORY_HEADER_BYTES + i * SHATTERED_HISTORY_RECORD_BYTES;
        if (Read32(record) == personality && Read32(record + 4) == otId)
            moves[copied++] = Read16(record + 8);
    }
    return copied;
}
