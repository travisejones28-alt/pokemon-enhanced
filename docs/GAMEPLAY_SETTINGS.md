# Shattered Realms gameplay settings

**In-game (new runtime-options builds):** Open START -> OPTION, then press **SELECT**
to switch to the **SHATTERED RULES** page. Use Up/Down to choose an item
and Left/Right to change it; press SELECT again to return to standard options.
B or CANCEL exits. Changes affect subsequent battles and field actions.
**Use the game's SAVE command to preserve them after restarting Delta.**
The game's own ordinary Options page remains unchanged.

| In-game setting | Values | Default |
| --- | --- | --- |
| Difficulty | Normal / Hard / Extreme | Extreme |
| Level scaling | On / Off | On |
| Move mode | Classic (four moves, finite PP) / No PP (four moves) / Pages (unlimited PP and move library) | Pages |
| EXP rate | x1 / x2 / x3 / x4 battle EXP | x4 |
| Max money | On / Off | On |
| Free supplies | On / Off | On |

Enhanced ordinary-trainer AI follows the difficulty setting (off on Normal,
on for Hard/Extreme). Explicit authored boss teams retain their intended AI.
An existing save with no Shattered setting automatically uses the original
build defaults. The menu uses the formerly unused **VAR_UNUSED_0x404E**
(0x404E) in the existing saved event variables with a validated version marker;
no save/Pokemon structure sizes or offsets are changed. The setting value must
be saved in-game and does not travel with save states reliably across ROM builds.

The build-time defaults remain in `engine/include/config/shattered.h` for
older saves, builds and policy tests. At runtime, the Options page overrides
those values in ordinary gameplay; unsupported link/recorded-battle mechanics
continue using native rules.

| Setting | Behavior |
| --- | --- |
| Difficulty: Normal | Original trainer levels/IVs; no global extra AI or Bag restriction. Authored boss teams and chapter content remain enhanced. |
| Difficulty: Hard | Base levels +10% +1; IV floor 20; enhanced AI; optional scaling to your highest party level; Bag allowed. |
| Difficulty: Extreme (default) | Base levels +25% +2; IV floor 28; enhanced AI; optional scaling to highest party level +1; trainer Bag restricted. |
| Level scaling | Enable/disable the adaptive floor. Fixed profile level boosts remain. |
| Enhanced AI | Enable/disable globally added decision and switching flags. Explicit boss AI remains. |
| Unlimited PP | Local player only. Link/replay and AI-controlled battlers retain normal PP. |
| Expanded moves | Enable/disable player battle move pages. Requires unlimited PP; invalid combinations fail compilation. |
| EXP multiplier | Integer 1–4; default 4. Affects battle EXP, not stored growth tables, Day Care or Rare Candies. |
| Unlimited money | Enable/disable the infinite player wallet. Other money fields retain normal behavior. |
| Free supplies | Enable/disable field Bag grants and reusable selected consumables. Existing items are not removed when disabled. |

Normal is a reduced-challenge Shattered Realms profile, not a restoration of
unmodified Emerald. Explicit competitive teams retain their designed IVs.
Frontier-generated trainer levels/IVs are excluded from profile boosts.
Eggs do not raise the adaptive level floor; generated levels cap at 100.

Finite PP displays current/max PP again, including replay/link contexts that
never receive unlimited PP. Player expanded pages do not implement per-move
PP storage, so they cannot safely coexist with finite PP. The in-game Move Mode
only changes locally controlled player battlers.

## Enemy expanded move pool (Hard/Extreme)

Ordinary **single trainer battles** now use a separate, battle-only enemy move
pool. The trainer's first three authored move slots remain fixed. Before AI
scoring each turn, the fourth slot cycles through its original move and
eligible, already-learned species level-up attacks (up to 64 candidates),
excluding duplicates, Sketch, Transform, Mimic and Struggle. Native AI still
scores and executes its four currently presented moves, so opponents can use
more than four *different* attacks over a multi-turn battle, not four or more
simultaneously. Each candidate keeps a separate PP count across turn rotations.

The mechanic follows enhanced AI: **Hard and Extreme enabled, Normal disabled**.
It does not operate in double battles, link/replay, Battle Frontier/Palace,
partner/multi battles or scripted first battles. It also pauses replacement
under Choice locks, Disable, Encore, Mimic/Transform, multi-turn and recharge
states. The team and save layouts remain untouched; no save migration is
required. This is an initial bounded implementation: high-level enemy moves
which are not in their own level-up learnset remain in their authored slots;
all double-battle and special-mode expansion is future work. Full visual
playtesting and broader battle-effect compatibility are still required.

The 4x EXP default approximates one-quarter battle grinding while keeping
existing saved experience valid. It does not literally quarter all growth
tables. Runtime configuration now uses an existing unused saved event variable; no new save fields or layouts are introduced.

Profile policy tests compile and execute the generated C level and PP/library
guards for Normal/Hard/Extreme, scaling on/off and supported PP/page combinations.
The full GBA build and emulator release gate exercise the default profile.
Full alternate-profile ROM/playthrough verification remains. On-device runtime
Options menu acceptance and actual Delta save round-trip verification remain.

## Additional story battles

Competitive authored sets now cover 36 encounters, including all Brendan/May
starter branches on Routes 110/119 and in Lilycove, Maxie at Mt. Chimney and the
Magma Hideout, Archie and Victory Road Wally. Teams use pivots, setup, priority,
weather, status and complementary coverage. Early Route 103 and Mauville Wally
parties remain unchanged; shared Mossdeep multi-battle party sizes remain intact.
Full encounter balance and campaign playthrough have not been performed.
