#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Include the upstream runner implementations and our targeted test cases.
# Selecting test sources keeps unrelated vanilla PP expectations out of this suite.
exec make -C engine -j2 -Otarget check TEST=1 TESTS=Shattered \
  TEST_SRCS_IN='test/test_runner.c test/test_runner_args.c test/test_runner_battle.c test/test_test_runner.c test/shattered_realms.c test/battle/shattered_realms.c' \
  TITLE=SHATTERED GAME_CODE=BSRE FILE_NAME=shattered-realms "$@"
