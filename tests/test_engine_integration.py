"""Exercise composed patches against the actual vendored engine, plus host C checks.

These checks do not emulate GBA battles or prove Delta save compatibility.
"""
import contextlib
import io
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from scripts.apply_overrides import (
    CONFIG, RIFT_NPCS, apply, modify_all_move_pages, modify_move_pp_display,
    modify_hard_trainer_ivs, replace_once, modify_player_pp_checks,
    modify_pp_drain_and_sketch, modify_rift_reward_retry,
)

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'engine'
INPUTS = set(CONFIG) | {
    'Makefile', 'src/data/pokemon/species_info/gen_1_families.h',
    'src/data/wild_encounters.json', 'src/starter_choose.c', 'src/battle_setup.c',
    'src/battle_main.c', 'src/battle_util.c', 'src/battle_controller_player.c',
    'src/money.c', 'src/item.c', 'src/item_menu.c', 'src/battle_script_commands.c',
    'src/trainer_util.c', 'src/battle_ai_main.c', 'data/text/birch_speech.inc',
    'src/battle_move_resolution.c', 'include/battle_util.h',
    'data/maps/RiftHollow/scripts.inc',
    'data/maps/Route101/scripts.inc', 'data/event_scripts.s',
    'src/data/trainers.party', 'data/maps/RustboroCity_Gym/scripts.inc',
    'data/maps/RustboroCity_Gym/map.json', 'data/maps/map_groups.json',
} | {f'data/maps/{name}/{file}' for name in RIFT_NPCS
     for file in ('map.json', 'scripts.inc')}


class TestEngineIntegration(unittest.TestCase):
    def test_full_application_is_byte_idempotent_and_composes_route101(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in INPUTS:
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ENGINE / name, path)
            with contextlib.redirect_stdout(io.StringIO()):
                apply(target)
                first = {name: (target / name).read_bytes() for name in INPUTS}
                apply(target)
            self.assertEqual(first, {name: (target / name).read_bytes() for name in INPUTS})
            route = (target / 'data/maps/Route101/scripts.inc').read_text()
            self.assertIn('RIFT flashed', route)
            self.assertIn('ShatteredRoute101_EventScript_Anomaly::', route)

    def test_invalid_input_does_not_partially_patch_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / 'Makefile').touch()
            first = next(iter(CONFIG))
            path = target / first
            path.parent.mkdir(parents=True)
            source = (ENGINE / first).read_text()
            path.write_text(source)
            with self.assertRaises(FileNotFoundError):
                apply(target)
            self.assertEqual(path.read_text(), source)

    def test_duplicate_or_mixed_patch_fails_closed(self):
        for source in ('old\nnew', 'new\nnew'):
            with self.assertRaises(ValueError):
                replace_once(source, 'old', 'new')

    def compile_and_run(self, code):
        compiler = shutil.which('cc')
        if not compiler:
            self.skipTest('Host C compiler unavailable')
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'test.c'
            binary = Path(directory) / 'test'
            source.write_text(code)
            result = subprocess.run([compiler, '-std=c99', '-Wall', '-Wextra',
                                     '-Werror', str(source), '-o', str(binary)],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run([str(binary)], check=True, timeout=10)

    def test_generated_iv_code_preserves_all_six_packed_fields(self):
        code = modify_hard_trainer_ivs('    SetMonData(mon, MON_DATA_IVS, &trainerMon->iv);')
        self.compile_and_run('''#include <assert.h>
#include <stdint.h>
typedef uint32_t u32;
#define NUM_STATS 6
#define max(a,b) ((a) > (b) ? (a) : (b))
#define MON_DATA_IVS 0
struct TrainerMon { u32 iv; };
struct Trainer { int isFrontier; };
static void SetMonData(u32 *mon, int field, const u32 *data)
{ (void)field; *mon = *data; }
static u32 run(u32 original, int frontier) {
    struct TrainerMon value = {original};
    struct Trainer config = {frontier};
    struct TrainerMon *trainerMon = &value;
    struct Trainer *trainer = &config;
    u32 result, data; u32 *mon = &result;
''' + code + '''
    return result;
}
int main(void) {
    for (u32 value = 0; value < 32; value++) {
        u32 packed = 0;
        for (u32 stat = 0; stat < 6; stat++)
            packed |= ((value + stat) % 32) << (stat * 5);
        u32 boosted = run(packed, 0);
        assert(run(packed, 1) == packed);
        for (u32 stat = 0; stat < 6; stat++) {
            u32 old = (packed >> (stat * 5)) & 31;
            assert(((boosted >> (stat * 5)) & 31) == max(old, 28));
        }
    }
    return 0;
}''')

    def test_generated_library_guard_handles_transform_encore_and_ai(self):
        source = (ENGINE / 'src/battle_controller_player.c').read_text()
        patched = modify_all_move_pages(modify_move_pp_display(source))
        guard = re.search(r'static bool32 ShatteredCanUseLibrary.*?\n}', patched, re.S).group()
        self.compile_and_run('''#include <assert.h>
typedef int bool32;
enum BattlerId { PLAYER, ENEMY };
#define BATTLE_TYPE_LINK 1
#define BATTLE_TYPE_RECORDED 2
#define BATTLE_TYPE_RECORDED_LINK 4
#define MOVE_NONE 0
static unsigned gBattleTypeFlags;
static int ai;
static struct { struct { int transformed, mimickedMoves, encoredMove; } volatiles; } gBattleMons[2];
static int IsOnPlayerSide(enum BattlerId battler) { return battler == PLAYER; }
static int BattlerHasAi(enum BattlerId battler) { (void)battler; return ai; }
''' + guard + '''
int main(void) {
    assert(ShatteredCanUseLibrary(PLAYER));
    assert(!ShatteredCanUseLibrary(ENEMY));
    for (unsigned flag = 1; flag <= 4; flag <<= 1) {
        gBattleTypeFlags = flag; assert(!ShatteredCanUseLibrary(PLAYER));
    }
    gBattleTypeFlags = 0; ai = 1; assert(!ShatteredCanUseLibrary(PLAYER)); ai = 0;
    gBattleMons[PLAYER].volatiles.transformed = 1;
    assert(!ShatteredCanUseLibrary(PLAYER));
    gBattleMons[PLAYER].volatiles.transformed = 0;
    gBattleMons[PLAYER].volatiles.mimickedMoves = 1;
    assert(!ShatteredCanUseLibrary(PLAYER));
    gBattleMons[PLAYER].volatiles.mimickedMoves = 0;
    gBattleMons[PLAYER].volatiles.encoredMove = 85;
    assert(!ShatteredCanUseLibrary(PLAYER));
    gBattleMons[PLAYER].volatiles.encoredMove = 0;
    assert(ShatteredCanUseLibrary(PLAYER));
    return 0;
}''')

    def test_pp_eligibility_preserves_enemy_ai_and_recording_rules(self):
        source = (ENGINE / 'src/battle_util.c').read_text()
        patched = modify_player_pp_checks(source)
        guard = re.search(r'bool32 ShatteredHasUnlimitedPP.*?\n}', patched, re.S).group()
        self.compile_and_run("""#include <assert.h>
typedef int bool32;
enum BattlerId { PLAYER, ENEMY };
#define BATTLE_TYPE_LINK 1
#define BATTLE_TYPE_RECORDED 2
#define BATTLE_TYPE_RECORDED_LINK 4
static unsigned gBattleTypeFlags;
static int ai;
static int IsOnPlayerSide(enum BattlerId battler) { return battler == PLAYER; }
static int BattlerHasAi(enum BattlerId battler) { (void)battler; return ai; }
""" + guard + """
int main(void) {
    assert(ShatteredHasUnlimitedPP(PLAYER));
    assert(!ShatteredHasUnlimitedPP(ENEMY));
    for (unsigned flag = 1; flag <= 4; flag <<= 1) {
        gBattleTypeFlags = flag; assert(!ShatteredHasUnlimitedPP(PLAYER));
    }
    gBattleTypeFlags = 0; ai = 1; assert(!ShatteredHasUnlimitedPP(PLAYER));
    return 0;
}""")

    def test_sketch_writes_saved_moves_instead_of_virtual_page(self):
        patched = modify_pp_drain_and_sketch((ENGINE / 'src/battle_script_commands.c').read_text())
        start = patched.index('            if (ShatteredHasUnlimitedPP(gBattlerAttacker))')
        end = patched.index('\n\n            BtlController_EmitSetMonData', start)
        snippet = patched[start:end]
        self.compile_and_run("""#include <assert.h>
#include <stdint.h>
typedef int32_t s32;
#define MAX_MON_MOVES 4
#define MOVE_SKETCH 166
#define MON_DATA_MOVE1 0
#define MON_DATA_PP1 4
#define MON_DATA_PP_BONUSES 8
struct Pokemon { unsigned data[9]; };
static struct Pokemon saved;
static int gBattlerAttacker;
static int gBattlerTarget;
static unsigned gLastPrintedMoves[2];
static int ShatteredHasUnlimitedPP(int battler) { (void)battler; return 1; }
static struct Pokemon *GetBattlerMon(int battler) { (void)battler; return &saved; }
static unsigned GetMonData(struct Pokemon *mon, int field) { return mon->data[field]; }
static unsigned GetMovePP(unsigned move) { (void)move; return 15; }
static void run(int slot) {
    struct { unsigned moves[4], pp[4], ppBonuses; } movePPData = {{99,98,97,96},{1,1,1,1},0};
    s32 i;
    for (i=0;i<4;i++) { saved.data[i] = 10+i; saved.data[4+i] = 20+i; }
    saved.data[8] = 255;
    if (slot >= 0) saved.data[slot] = MOVE_SKETCH;
    gLastPrintedMoves[gBattlerTarget] = 42;
""" + snippet + """
    for (i=0;i<4;i++) {
        assert(movePPData.moves[i] == (i == slot ? 42 : saved.data[i]));
        assert(movePPData.pp[i] == (i == slot ? 15 : saved.data[4+i]));
    }
    assert(movePPData.ppBonuses == (slot < 0 ? 255u : (255u & ~(3u << (slot*2)))));
}
int main(void) { for(int slot=-1;slot<4;slot++) run(slot); return 0; }
""")

    def test_rift_reward_has_retry_without_resetting_boss_flag(self):
        source = (ENGINE / 'data/maps/RiftHollow/scripts.inc').read_text()
        patched = modify_rift_reward_retry(source)
        self.assertEqual(patched, modify_rift_reward_retry(patched))
        repeat = patched.split('RiftHollow_EventScript_WardenAfterVictory::', 1)[1]
        self.assertIn('checkitem ITEM_SHINY_CHARM', repeat)
        self.assertIn('FALSE, RiftHollow_EventScript_ClaimReward', repeat)
        self.assertEqual(patched.count('setflag FLAG_UNUSED_0x90F'), 1)

    def test_unusable_page_search_and_failed_search_restore_battle_slots(self):
        patched = modify_all_move_pages(modify_move_pp_display(
            (ENGINE / 'src/battle_controller_player.c').read_text()))
        self.assertEqual(patched.count('bool32 ShatteredTryUsableLibraryPage('), 1)
        helper = re.search(r'bool32 ShatteredTryUsableLibraryPage.*?\n}', patched, re.S).group()
        self.compile_and_run('''#include <assert.h>
#include <stdint.h>
typedef uint32_t u32;
typedef uint8_t u8;
typedef int bool32;
#define TRUE 1
#define FALSE 0
#define MAX_MON_MOVES 4
#define MOVE_LIMITATIONS_ALL 255
enum Move { MOVE_NONE = 0, TEST_ATTACK = 2 };
enum BattlerId { PLAYER };
static struct { enum Move moves[4]; u8 pp[4]; } gBattleMons[1];
static unsigned sShatteredMoveCounts[1];
static enum Move sShatteredMoves[1][256];
static int eligible = 1, blocked, builds;
static bool32 ShatteredCanUseLibrary(enum BattlerId battler)
{ (void)battler; return eligible; }
static void ShatteredBuildMoveLibrary(enum BattlerId battler)
{
    builds++;
    enum Move moves[6] = {1,4,5,6,TEST_ATTACK,3};
    sShatteredMoveCounts[battler] = 6;
    for(int i=0;i<6;i++) sShatteredMoves[battler][i] = moves[i];
}
static unsigned GetMovePP(enum Move move) { return move ? 10 : 0; }
static unsigned CheckMoveLimitations(enum BattlerId battler, unsigned unused, unsigned check)
{
    (void)unused; (void)check;
    unsigned result = 0;
    for(int i=0;i<4;i++)
        if(blocked || gBattleMons[battler].moves[i] != TEST_ATTACK) result |= 1u << i;
    return result;
}
''' + helper + '''
static void original(void) {
    for(int i=0;i<4;i++) { gBattleMons[0].moves[i] = 10+i; gBattleMons[0].pp[i] = 20+i; }
}
static void checkOriginal(void) {
    for(int i=0;i<4;i++) { assert(gBattleMons[0].moves[i] == (enum Move)(10+i)); assert(gBattleMons[0].pp[i] == 20+i); }
}
int main(void) {
    original(); eligible = 0;
    assert(!ShatteredTryUsableLibraryPage(PLAYER)); assert(builds == 0); checkOriginal();
    eligible = 1; blocked = 1;
    assert(!ShatteredTryUsableLibraryPage(PLAYER)); checkOriginal();
    blocked = 0; assert(ShatteredTryUsableLibraryPage(PLAYER));
    assert(gBattleMons[0].moves[0] == TEST_ATTACK);
    assert(gBattleMons[0].moves[2] == MOVE_NONE);
    assert(gBattleMons[0].pp[0] == 10);
    return 0;
}''')
