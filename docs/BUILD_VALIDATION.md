# Build #57 validation — 19 October 2026

Game source commit: `3edce876a204ec067cbe2f5e99ae2c8acbca5f93`.

- [Successful GitHub Actions run](https://github.com/travisejones28-alt/pokemon-enhanced/actions/runs/39316354404)
- [Published release](https://github.com/travisejones28-alt/pokemon-enhanced/releases/tag/alpha0.1-build-57)
- [Permanent ROM download](https://github.com/travisejones28-alt/pokemon-enhanced/releases/latest/download/ShatteredRealms.gba)
- ROM size: 33554432 bytes (32 MiB).
- ROM SHA-256: `cb37df1271863a005f9d9da8ac1efa70b12a8b2aaf162483fd936b0b9add6bc3`.
- Previous recovery ROM: [build #55](https://github.com/travisejones28-alt/pokemon-enhanced/releases/tag/alpha0.1-build-55).

## Results

| Check | Result |
| --- | --- |
| Python regression suite, including generated-C host tests | 41 tests passed locally; Actions test step passed |
| Full override application to vendored sources | Passed |
| Second complete application makes no changes | Passed locally and in Actions |
| GBA compilation using the existing workflow | Passed |
| ROM title/game code: SHATTERED / BSRE | Verification step passed |
| ROM size and header checksum | Verification step passed |
| SHA-256 manifest verification | Passed |
| Release publication and expected ROM asset | Confirmed by release metadata |
| New-game playthrough in Delta | Not performed |
| Single/double battle emulator regression | Not performed |
| Representative previous/new save load/save round trips | Not performed; save files unavailable |
| Entire anomaly quest, boss reward and first Gym playthrough | Not performed |
| Follower transitions and friendship unlock gameplay | Not performed |

The local host has a C compiler but no GBA toolchain or GBA emulator. Compilation
and ROM verification ran in GitHub Actions. Host C tests exercise generated
logic; they do not emulate the GBA battle engine.

This is a **compiled alpha for testing**, not a claim of fully verified gameplay.
See [the implementation audit](IMPLEMENTATION_AUDIT.md) for unfinished systems,
and [save backup/import instructions](SAVE_COMPATIBILITY.md) before updating.

No save or Pokémon layouts were intentionally changed by the two repair commits.
No new game is intentionally required. This does not establish compatibility with
every previous build. Keep the old ROM tile and exported battery save until
Continue, party, PC, Bag, maps and save/reload have been verified on iPhone.
