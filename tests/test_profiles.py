"""Run generated trainer and PP policies as C for every supported profile."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from scripts.apply_overrides import (
    modify_hard_trainer_levels, modify_player_pp_checks, modify_all_move_pages,
    modify_move_pp_display,
)

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"


class TestProfiles(unittest.TestCase):
    def compile(self, code, defines="", valid=True):
        compiler = shutil.which("cc")
        if not compiler:
            self.skipTest("Host C compiler unavailable")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "profile.c"
            binary = Path(directory) / "profile"
            source.write_text("#define TRUE 1\n#define FALSE 0\n" + defines + "\n"
                              + (ENGINE / "include/config/shattered.h").read_text()
                              + "\n" + code)
            result = subprocess.run(
                [compiler, "-std=c99", "-Wall", "-Wextra", "-Werror",
                 str(source), "-o", str(binary)],
                capture_output=True, text=True, timeout=30)
            if not valid:
                self.assertNotEqual(result.returncode, 0)
                return
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run([str(binary)], check=True, timeout=10)

    def test_all_difficulty_levels_and_scaling_bounds(self):
        patch = modify_hard_trainer_levels(
            "    CreateMon(mon, trainerMon->species, trainerMon->lvl, personality, trainer->otID);")
        code = r"""
#include <assert.h>
typedef unsigned u32;
enum Species { SPECIES_NONE, SPECIES_EGG, SPECIES_PIKACHU };
#define MAX_LEVEL 100
#define B_TRAINER_PLAYER 0
#define MON_DATA_SPECIES_OR_EGG 0
#define MON_DATA_LEVEL 1
#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))
static struct { unsigned species, level; } gParties[1][6];
static unsigned gPartiesCount[1] = {2};
static unsigned GetMonData(const void *mon, unsigned field) {
    const unsigned *data = mon; return data[field];
}
static void CreateMon(unsigned *mon, unsigned species, unsigned level,
                      unsigned personality, unsigned otId) {
    (void)species; (void)personality; (void)otId; *mon = level;
}
static unsigned run(unsigned level, unsigned frontier) {
    struct { unsigned species, lvl; } member = {SPECIES_PIKACHU, level};
    struct { unsigned isFrontier, otID; } config = {frontier, 0};
    unsigned result, personality = 0;
    unsigned *mon = &result;
    const typeof_not_used *unused;
"""
        code = code.replace("    const typeof_not_used *unused;\n",
                            "    __typeof__(member) *trainerMon = &member;\n"
                            "    __typeof__(config) *trainer = &config;\n")
        code += patch + r"""
    return result;
}
int main(void) {
    gParties[0][0].species = SPECIES_PIKACHU;
    gParties[0][0].level = 80;
    gParties[0][1].species = SPECIES_EGG;
    gParties[0][1].level = 100;
    assert(run(20, 1) == 20);
    unsigned base = SHATTERED_DIFFICULTY == SHATTERED_NORMAL ? 20
                  : SHATTERED_DIFFICULTY == SHATTERED_HARD ? 23 : 27;
    unsigned expected = SHATTERED_LEVEL_SCALING && SHATTERED_DIFFICULTY != SHATTERED_NORMAL
                      ? (SHATTERED_DIFFICULTY == SHATTERED_EXTREME ? 81 : 80) : base;
    assert(run(20, 0) == expected);
    assert(run(100, 0) == 100);
    gPartiesCount[0] = 0;
    assert(run(20, 0) == base);
    return 0;
}
"""
        for difficulty in range(3):
            for scaling in range(2):
                with self.subTest(difficulty=difficulty, scaling=scaling):
                    self.compile(code, f"#define SHATTERED_DIFFICULTY {difficulty}\n"
                                       f"#define SHATTERED_LEVEL_SCALING {scaling}\n")

    def test_finite_pp_disables_virtual_pages_and_preserves_policy(self):
        source = (ENGINE / "src/battle_util.c").read_text()
        policy = re.search(r"bool32 ShatteredHasUnlimitedPP.*?\n}",
                           modify_player_pp_checks(source), re.S).group()
        source = (ENGINE / "src/battle_controller_player.c").read_text()
        patched = modify_all_move_pages(modify_move_pp_display(source))
        guard = re.search(r"static bool32 ShatteredCanUseLibrary.*?\n}", patched, re.S).group()
        code = r"""
#include <assert.h>
typedef int bool32;
enum BattlerId { PLAYER, ENEMY };
#define BATTLE_TYPE_LINK 1
#define BATTLE_TYPE_RECORDED 2
#define BATTLE_TYPE_RECORDED_LINK 4
#define MOVE_NONE 0
static unsigned gBattleTypeFlags;
static int ai;
static struct { struct { int transformed, mimickedMoves, encoredMove; } volatiles; } gBattleMons[2];
static int IsOnPlayerSide(enum BattlerId b) { return b == PLAYER; }
static int BattlerHasAi(enum BattlerId b) { (void)b; return ai; }
""" + policy + "\n" + guard + r"""
int main(void) {
    assert(ShatteredHasUnlimitedPP(PLAYER) == !!SHATTERED_UNLIMITED_PP);
    assert(ShatteredCanUseLibrary(PLAYER) == !!SHATTERED_EXPANDED_MOVES);
    assert(!ShatteredHasUnlimitedPP(ENEMY));
    for (unsigned flag=1; flag<=4; flag<<=1) {
        gBattleTypeFlags=flag;
        assert(!ShatteredHasUnlimitedPP(PLAYER));
        assert(!ShatteredCanUseLibrary(PLAYER));
    }
    return 0;
}
"""
        for pp, pages in ((0, 0), (1, 0), (1, 1)):
            self.compile(code, f"#define SHATTERED_UNLIMITED_PP {pp}\n"
                               f"#define SHATTERED_EXPANDED_MOVES {pages}\n")

    def test_invalid_profiles_fail_at_compile_time(self):
        for defines in ("#define SHATTERED_DIFFICULTY 3",
                        "#define SHATTERED_EXP_MULTIPLIER 0",
                        "#define SHATTERED_EXP_MULTIPLIER 5",
                        "#define SHATTERED_UNLIMITED_PP 0\n#define SHATTERED_EXPANDED_MOVES 1"):
            self.compile("int main(void) { return 0; }", defines, valid=False)

    def test_finite_pp_ui_is_not_blank(self):
        source = (ENGINE / "src/battle_controller_player.c").read_text()
        patched = modify_all_move_pages(modify_move_pp_display(source))
        display = re.search(r"static void MoveSelectionDisplayPPNumber\(enum BattlerId battler\)\n\{.*?\n}",
                            patched, re.S).group()
        self.assertIn("if (!ShatteredHasUnlimitedPP(battler))", display)
        self.assertIn("moveInfo->currentPP[gMoveSelectionCursor[battler]]", display)
        self.assertIn("moveInfo->maxPP[gMoveSelectionCursor[battler]]", display)
