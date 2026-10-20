# Gameplay build profiles

Edit `engine/include/config/shattered.h` before building. These are **build-time
settings**, not an in-game menu. Defaults preserve the published Extreme-style
rules. Save and Pokemon structures remain unchanged.

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
never receive unlimited PP. Expanded pages do not implement per-move PP storage,
so they cannot safely coexist with finite PP. Enemy trainers still use four
active moves; expanded enemy selection is unfinished.

The 4x EXP default approximates one-quarter battle grinding while keeping
existing saved experience valid. It does not literally quarter all growth
tables. No runtime configuration or additional save fields are introduced.

Profile policy tests compile and execute the generated C level and PP/library
guards for Normal/Hard/Extreme, scaling on/off and supported PP/page combinations.
The full GBA build and emulator release gate exercise the default profile.
Full alternate-profile ROM/playthrough verification remains.
