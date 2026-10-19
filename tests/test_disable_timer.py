"""Execute the actual generated end-turn callback with controlled battle state."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from scripts.chapter import disable_timer

ROOT = Path(__file__).resolve().parents[1]


class TestDisableTimer(unittest.TestCase):
    def test_browsing_preserves_disable_but_transform_and_unknown_moves_do_not(self):
        compiler = shutil.which('cc')
        if not compiler:
            self.skipTest('Host C compiler unavailable')
        source = disable_timer((ROOT/'engine/src/battle_end_turn.c').read_text())
        callback = re.search(r'static bool32 HandleEndTurnDisable\(.*?\n}', source, re.S).group()
        code = '''#include <assert.h>
#include <string.h>
typedef unsigned u32; typedef unsigned bool32; typedef unsigned char u8;
enum BattlerId { PLAYER };
#define MAX_MON_MOVES 4
#define FALSE 0
#define TRUE 1
struct BoxPokemon { int unused; }; struct Pokemon { struct BoxPokemon box; };
static struct Pokemon mon;
static int unlimited, known, scripts;
static struct { unsigned moves[4]; struct { unsigned disableTimer, disabledMove, transformed, mimickedMoves; } volatiles; } gBattleMons[1];
static struct { struct { unsigned endTurnBattler; } eventState; } battleStruct;
static struct { unsigned battler; } gBattleScripting;
#define gBattleStruct (&battleStruct)
static const u8 BattleScript_DisabledNoMore[] = {0};
static int ShatteredHasUnlimitedPP(enum BattlerId battler) { (void)battler; return unlimited; }
static struct Pokemon *GetBattlerMon(enum BattlerId battler) { (void)battler; return &mon; }
static int ShatteredBoxKnowsMove(struct BoxPokemon *box, unsigned move) { (void)box; (void)move; return known; }
static void BattleScriptCall(const u8 *script) { (void)script; scripts++; }
''' + callback + '''
static void reset(void) {
    memset(gBattleMons,0,sizeof(gBattleMons)); scripts=0;
    gBattleMons[0].volatiles.disableTimer=4;
    gBattleMons[0].volatiles.disabledMove=42;
    unlimited=1; known=1;
}
int main(void) {
    reset(); assert(!HandleEndTurnDisable(PLAYER));
    assert(gBattleMons[0].volatiles.disableTimer==3);
    assert(gBattleMons[0].volatiles.disabledMove==42);
    reset(); known=0; HandleEndTurnDisable(PLAYER);
    assert(gBattleMons[0].volatiles.disableTimer==0);
    reset(); unlimited=0; HandleEndTurnDisable(PLAYER);
    assert(gBattleMons[0].volatiles.disabledMove==0);
    reset(); gBattleMons[0].volatiles.transformed=1; HandleEndTurnDisable(PLAYER);
    assert(gBattleMons[0].volatiles.disableTimer==0);
    reset(); gBattleMons[0].volatiles.mimickedMoves=1; HandleEndTurnDisable(PLAYER);
    assert(gBattleMons[0].volatiles.disableTimer==0);
    reset(); gBattleMons[0].moves[2]=42; unlimited=0; known=0; HandleEndTurnDisable(PLAYER);
    assert(gBattleMons[0].volatiles.disableTimer==3);
    reset(); gBattleMons[0].volatiles.disableTimer=1;
    assert(HandleEndTurnDisable(PLAYER)); assert(scripts==1);
    assert(gBattleMons[0].volatiles.disabledMove==0);
    return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'test.c'; binary=Path(directory)/'test'
            source.write_text(code)
            result = subprocess.run([compiler,'-std=c99','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            subprocess.run([str(binary)],check=True,timeout=10)
