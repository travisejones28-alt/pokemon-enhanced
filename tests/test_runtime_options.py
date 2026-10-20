"""Runtime Options: execute the shipped settings codec in host C.

A real iPhone save acceptance round trip is tracked separately; these tests
exercise configuration defaults, stored vars, cycling and defensive fallback.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "engine/include/shattered_runtime.h"
ENGINE = ROOT / "engine"


class TestRuntimeOptions(unittest.TestCase):
    def test_c_runtime_codec_and_old_save_defaults(self):
        compiler = shutil.which("cc")
        if not compiler:
            self.skipTest("Host C compiler unavailable")
        header = HEADER.read_text()
        header = header.replace('#include "config/shattered.h"', "")
        header = header.replace('#include "event_data.h"', "")
        harness = r"""
#include <assert.h>
#include <stddef.h>
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int bool32;
#define ARRAY_COUNT(x) (sizeof(x) / sizeof((x)[0]))
#define SHATTERED_NORMAL 0
#define SHATTERED_HARD 1
#define SHATTERED_EXTREME 2
#define SHATTERED_DIFFICULTY SHATTERED_EXTREME
#define SHATTERED_LEVEL_SCALING 1
#define SHATTERED_ENHANCED_AI 1
#define SHATTERED_UNLIMITED_PP 1
#define SHATTERED_EXPANDED_MOVES 1
#define SHATTERED_EXP_MULTIPLIER 4
#define SHATTERED_UNLIMITED_MONEY 1
#define SHATTERED_FREE_SUPPLIES 1
#define VAR_UNUSED_0x404E 0x404e
static int saveBlock;
static void *gSaveBlock1Ptr = &saveBlock;
static u16 saveVar;
static u32 VarGet(u32 varId) { assert(varId == 0x404e); return saveVar; }
static void VarSet(u32 varId, u16 value) { assert(varId == 0x404e); saveVar = value; }
""" + header + r"""
int main(void)
{
    // Uninitialized/old saves use the exact original build defaults.
    assert(ShatteredRuntimeDifficulty() == SHATTERED_EXTREME);
    assert(ShatteredRuntimeScaling());
    assert(ShatteredRuntimeEnhancedAI());
    assert(ShatteredRuntimeUnlimitedPP());
    assert(ShatteredRuntimeExpandedMoves());
    assert(ShatteredRuntimeExpMultiplier() == 4);
    assert(ShatteredRuntimeUnlimitedMoney());
    assert(ShatteredRuntimeFreeSupplies());
    // Garbage or unknown reserved flags may not enable custom settings.
    saveVar = 0xA001;
    assert(ShatteredRuntimeDifficulty() == SHATTERED_EXTREME);
    saveVar = 0xB003;
    assert(ShatteredRuntimeDifficulty() == SHATTERED_EXTREME);
    saveVar = 0xBE00;
    assert(ShatteredRuntimeExpMultiplier() == 4);
    saveVar = 0;
    // Cycle difficulty: Extreme -> Normal. AI follows difficulty.
    ShatteredRulesCycle(0, 1);
    assert(ShatteredRuntimeDifficulty() == SHATTERED_NORMAL);
    assert(!ShatteredRuntimeEnhancedAI());
    ShatteredRulesCycle(0, 0);
    assert(ShatteredRuntimeDifficulty() == SHATTERED_EXTREME);
    ShatteredRulesCycle(1, 1);
    assert(!ShatteredRuntimeScaling());
    // PAGES -> CLASSIC -> NO PP -> PAGES, pages never coexist with finite PP.
    ShatteredRulesCycle(2, 1);
    assert(!ShatteredRuntimeUnlimitedPP() && !ShatteredRuntimeExpandedMoves());
    ShatteredRulesCycle(2, 1);
    assert(ShatteredRuntimeUnlimitedPP() && !ShatteredRuntimeExpandedMoves());
    ShatteredRulesCycle(2, 1);
    assert(ShatteredRuntimeUnlimitedPP() && ShatteredRuntimeExpandedMoves());
    ShatteredRulesCycle(3, 1);
    assert(ShatteredRuntimeExpMultiplier() == 1);
    ShatteredRulesCycle(3, 0);
    assert(ShatteredRuntimeExpMultiplier() == 4);
    ShatteredRulesCycle(4, 1);
    ShatteredRulesCycle(5, 1);
    assert(!ShatteredRuntimeUnlimitedMoney() && !ShatteredRuntimeFreeSupplies());
    assert((saveVar & 0xf000) == 0xb000);
    // No-save boot/title code must not access the persistent vars.
    gSaveBlock1Ptr = NULL;
    assert(ShatteredRuntimeDifficulty() == SHATTERED_EXTREME);
    return 0;
}
"""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "rules.c"
            binary = Path(directory) / "rules"
            source.write_text(harness)
            result = subprocess.run([compiler, "-std=c99", "-Wall", "-Wextra",
                                     "-Werror", str(source), "-o", str(binary)],
                                    text=True, capture_output=True, timeout=25)
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run([str(binary)], check=True, timeout=10)

    def test_option_screen_accessible_and_apply_hook_runtime(self):
        menu = (ENGINE / "src/option_menu.c").read_text()
        patcher = (ROOT / "scripts/apply_overrides.py").read_text()
        self.assertIn("JOY_NEW(SELECT_BUTTON)", menu)
        self.assertIn("ShatteredRulesCycle(", menu)
        self.assertIn("sShatteredRulesPage ? sShatteredRuleNames", menu)
        self.assertIn("ShatteredRuntimeExpMultiplier()", menu)
        self.assertIn("ShatteredRuntimeFreeSupplies()", menu)
        for file in ("src/trainer_util.c", "src/battle_ai_main.c", "src/battle_util.c",
                     "src/battle_controller_player.c", "src/battle_script_commands.c",
                     "src/money.c", "src/item.c", "src/item_menu.c"):
            self.assertIn(f'"{file}"', patcher)
        self.assertIn('runtime_include = \'#include "shattered_runtime.h"\\n\'', patcher)


if __name__ == "__main__":
    unittest.main()
