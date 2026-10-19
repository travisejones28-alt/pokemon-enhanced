#include "global.h"
#include "pokemon.h"
#include "shattered_history.h"
#include "string_util.h"
#include "constants/moves.h"

static const u8 sBondNew[] = _("Bond: {STR_VAR_2}/255.\nNext: ZIPPY ZAP at 120.");
static const u8 sBondSpark[] = _("ZIPPY ZAP is unlocked!\nNext: SPLISHY SPLASH at 180.");
static const u8 sBondSplash[] = _("SPLISHY SPLASH is unlocked!\nNext: FLOATY FALL at 230.");
static const u8 sBondComplete[] = _("Our bond crosses every realm!\nAll three Bond attacks unlocked.");
static const u8 sArchiveFull[] = _("Your move journal is full!\nRare attacks cannot be forgotten.");
static const u8 sArchiveDamaged[] = _("Your move journal needs recovery.\nKeep a backup of this save.");

const u8 *ShatteredGetBondMessage(struct Pokemon *mon)
{
    u8 *store = gSaveBlock3Ptr->shatteredMoveHistory;
    if (!ShatteredHistoryOpen(store))
        return sArchiveDamaged;
    if ((store[6] | (u16)store[7] << 8) == SHATTERED_HISTORY_CAPACITY)
        return sArchiveFull;
    if (GetMonData(mon, MON_DATA_SPECIES) != SPECIES_PIKACHU)
        return NULL;
    u32 bond = GetMonData(mon, MON_DATA_FRIENDSHIP);
    ConvertIntToDecimalStringN(gStringVar2, bond, STR_CONV_MODE_LEFT_ALIGN, 3);
    if (bond >= 120)
        ShatteredRememberBondMove(&mon->box, MOVE_ZIPPY_ZAP);
    if (bond >= 180)
        ShatteredRememberBondMove(&mon->box, MOVE_SPLISHY_SPLASH);
    if (bond >= 230)
        ShatteredRememberBondMove(&mon->box, MOVE_FLOATY_FALL);
    return bond >= 230 ? sBondComplete : bond >= 180 ? sBondSplash
         : bond >= 120 ? sBondSpark : sBondNew;
}
