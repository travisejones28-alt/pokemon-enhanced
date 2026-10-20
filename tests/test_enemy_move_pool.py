"""Test the enemy move pool's actual generated C, not a Python reimplementation."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from scripts.apply_overrides import modify_enemy_move_pool

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"

MINIMAL_SOURCE = """void SetAiLogicDataForTurn(struct AiLogicData *aiData)
{
    // get/assume all battler data and simulate AI damage
    u32 battlersCount = gBattlersCount;
}
"""


class TestEnemyMovePool(unittest.TestCase):
    def test_override_is_deterministic_and_idempotent(self):
        patched = modify_enemy_move_pool(MINIMAL_SOURCE)
        self.assertEqual(patched, modify_enemy_move_pool(patched))
        self.assertEqual(patched.count("ShatteredRotateEnemyMoves(battler);"), 1)
        self.assertEqual(patched.count("struct ShatteredEnemyMovePool"), 3)
        script = (ROOT / "scripts/apply_overrides.py").read_text()
        self.assertIn("modify_enemy_move_pool(modify_hard_trainer_ai(c))", script)
        self.assertIn('"src/battle_ai_main.c"', script)

    def test_pool_rotation_and_special_battle_guards_execute_as_c(self):
        compiler = shutil.which("cc")
        if not compiler:
            self.skipTest("Host C compiler is unavailable")
        patched = modify_enemy_move_pool(MINIMAL_SOURCE)
        code = re.search(
            r"(#define SHATTERED_ENEMY_POOL_CAPACITY 64.*?)(?=\nvoid SetAiLogicDataForTurn)",
            patched, re.S).group(1)
        prefix = r"""
#include <assert.h>
#include <string.h>
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int bool8;
typedef int bool32;
#define TRUE 1
#define FALSE 0
#define EWRAM_DATA
#define MAX_BATTLERS_COUNT 4
#define MAX_MON_MOVES 4
#define LEVEL_UP_MOVE_END 65535
enum Species { SPECIES_NONE, SPECIES_PIKACHU };
enum Move {
    MOVE_NONE, MOVE_TACKLE, MOVE_GROWL, MOVE_BITE, MOVE_QUICK_ATTACK,
    MOVE_THUNDERBOLT, MOVE_ICE_BEAM, MOVE_SKETCH, MOVE_TRANSFORM,
    MOVE_MIMIC, MOVE_STRUGGLE, MOVES_COUNT
};
enum BattlerId { B_PLAYER, B_OPPONENT, B_PLAYER_PARTNER, B_OPPONENT_PARTNER };
#define BATTLE_TYPE_TRAINER (1u << 0)
#define BATTLE_TYPE_LINK (1u << 1)
#define BATTLE_TYPE_RECORDED (1u << 2)
#define BATTLE_TYPE_RECORDED_LINK (1u << 3)
#define BATTLE_TYPE_FRONTIER (1u << 4)
#define BATTLE_TYPE_FIRST_BATTLE (1u << 5)
#define BATTLE_TYPE_SAFARI (1u << 6)
#define BATTLE_TYPE_PALACE (1u << 7)
#define BATTLE_TYPE_INGAME_PARTNER (1u << 8)
#define BATTLE_TYPE_MULTI (1u << 9)
struct Volatiles {
    u32 multipleTurns, rechargeTimer, transformed, mimickedMoves;
    enum Move encoredMove, disabledMove;
};
struct BattlePokemon {
    enum Species species;
    u8 level;
    enum Move moves[4];
    u8 pp[4];
    struct Volatiles volatiles;
};
struct LevelUpMove { u16 level; enum Move move; };
struct BattleStruct { enum Move choicedMove[4]; };
static struct BattleStruct battleStruct;
static struct BattleStruct *gBattleStruct = &battleStruct;
static struct BattlePokemon gBattleMons[4];
static u8 gBattlerPartyIndexes[4];
static u32 gBattleTurnCounter;
static u32 gBattleTypeFlags;
static int doubleBattle, aiEnabled = 1;
#define SHATTERED_ENHANCED_AI (aiEnabled)
static int IsDoubleBattle(void) { return doubleBattle; }
static int IsOnPlayerSide(enum BattlerId battler) { return battler == 0 || battler == 2; }
static int IsBattlerAlive(enum BattlerId battler) { (void)battler; return 1; }
static const struct LevelUpMove learnset[] = {
    {2, MOVE_TACKLE}, {4, MOVE_GROWL}, {9, MOVE_THUNDERBOLT},
    {12, MOVE_ICE_BEAM}, {16, MOVE_SKETCH}, {65535, MOVE_NONE}
};
static const struct LevelUpMove *GetSpeciesLevelUpLearnset(enum Species species)
{
    assert(species == SPECIES_PIKACHU);
    return learnset;
}
static u8 GetMovePP(enum Move move) { return move == MOVE_NONE ? 0 : 10; }
"""
        suffix = r"""
int main(void)
{
    struct BattlePokemon *enemy = &gBattleMons[B_OPPONENT];
    enemy->species = SPECIES_PIKACHU;
    enemy->level = 20;
    enemy->moves[0] = MOVE_TACKLE;
    enemy->moves[1] = MOVE_GROWL;
    enemy->moves[2] = MOVE_BITE;
    enemy->moves[3] = MOVE_QUICK_ATTACK;
    for (int i = 0; i < 4; ++i) enemy->pp[i] = 10;
    gBattleTypeFlags = BATTLE_TYPE_TRAINER;
    // Four native slots + Thunderbolt and Ice Beam, excluding Sketch.
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(sShatteredEnemyPools[B_OPPONENT].count == 3);
    assert(enemy->moves[3] == MOVE_QUICK_ATTACK);
    enemy->pp[3] = 8;
    gBattleTurnCounter = 1;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_THUNDERBOLT);
    // No multiple rotations or PP resets within a single turn.
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_THUNDERBOLT);
    enemy->pp[3] = 9;
    gBattleTurnCounter = 2;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_ICE_BEAM);
    enemy->pp[3] = 7;
    gBattleTurnCounter = 3;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_QUICK_ATTACK && enemy->pp[3] == 8);
    gBattleTurnCounter = 4;
    gBattleStruct->choicedMove[B_OPPONENT] = MOVE_QUICK_ATTACK;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_QUICK_ATTACK);
    gBattleStruct->choicedMove[B_OPPONENT] = MOVE_NONE;
    enemy->volatiles.encoredMove = MOVE_TACKLE;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_QUICK_ATTACK);
    enemy->volatiles.encoredMove = MOVE_NONE;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_THUNDERBOLT && enemy->pp[3] == 9);
    // Disabled, multi-turn, double, normal difficulty and links are untouched.
    gBattleTurnCounter = 5;
    enemy->volatiles.disabledMove = MOVE_BITE;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_THUNDERBOLT);
    enemy->volatiles.disabledMove = MOVE_NONE;
    doubleBattle = 1;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_THUNDERBOLT);
    doubleBattle = 0;
    aiEnabled = 0;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_THUNDERBOLT);
    aiEnabled = 1;
    gBattleTypeFlags = BATTLE_TYPE_LINK | BATTLE_TYPE_TRAINER;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(enemy->moves[3] == MOVE_THUNDERBOLT);
    gBattleTypeFlags = BATTLE_TYPE_TRAINER;
    // Switching must reconstruct state from the newly active battle mon.
    gBattlerPartyIndexes[B_OPPONENT] = 1;
    enemy->moves[3] = MOVE_BITE;
    enemy->pp[3] = 6;
    ShatteredRotateEnemyMoves(B_OPPONENT);
    assert(sShatteredEnemyPools[B_OPPONENT].partyIndex == 1);
    assert(sShatteredEnemyPools[B_OPPONENT].moves[0] == MOVE_BITE);
    assert(sShatteredEnemyPools[B_OPPONENT].pp[0] == 6);
    // Player battlers are never given virtual enemy moves.
    ShatteredRotateEnemyMoves(B_PLAYER);
    assert(sShatteredEnemyPools[B_PLAYER].count == 0);
    return 0;
}
"""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "pool.c"
            binary = Path(directory) / "pool"
            source.write_text(prefix + code + suffix)
            build = subprocess.run([compiler, "-std=c99", "-Wall", "-Wextra",
                                    "-Werror", str(source), "-o", str(binary)],
                                   text=True, capture_output=True, timeout=30)
            self.assertEqual(build.returncode, 0, build.stderr)
            subprocess.run([str(binary)], check=True, timeout=10)


if __name__ == "__main__":
    unittest.main()
