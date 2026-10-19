#include "global.h"
#include "test/battle.h"
#include "shattered_battle.h"
#include "battle_util.h"

SINGLE_BATTLE_TEST("Shattered PP stays unlimited for player and normal for opponent")
{
    GIVEN {
        gShatteredTestLocalMechanics = TRUE;
        PLAYER(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
        OPPONENT(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
    } WHEN {
        TURN { MOVE(player, MOVE_CELEBRATE); MOVE(opponent, MOVE_CELEBRATE); }
        TURN { MOVE(player, MOVE_CELEBRATE); MOVE(opponent, MOVE_CELEBRATE); }
    } THEN {
        EXPECT_EQ(player->pp[0], GetMovePP(MOVE_CELEBRATE));
        EXPECT_EQ(opponent->pp[0], GetMovePP(MOVE_CELEBRATE) - 2);
    }
}

SINGLE_BATTLE_TEST("Shattered PP resists opponent Spite")
{
    GIVEN {
        gShatteredTestLocalMechanics = TRUE;
        PLAYER(SPECIES_WOBBUFFET) { Speed(100); Moves(MOVE_CELEBRATE); }
        OPPONENT(SPECIES_WOBBUFFET) { Speed(50); Moves(MOVE_SPITE); }
    } WHEN {
        TURN { MOVE(player, MOVE_CELEBRATE); MOVE(opponent, MOVE_SPITE); }
    } THEN {
        EXPECT_EQ(player->pp[0], GetMovePP(MOVE_CELEBRATE));
        EXPECT_EQ(opponent->pp[0], GetMovePP(MOVE_SPITE) - 1);
    }
}

DOUBLE_BATTLE_TEST("Shattered PP supports both player battlers independently")
{
    GIVEN {
        gShatteredTestLocalMechanics = TRUE;
        PLAYER(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
        PLAYER(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
        OPPONENT(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
        OPPONENT(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
    } WHEN {
        TURN { MOVE(playerLeft, MOVE_CELEBRATE); MOVE(playerRight, MOVE_CELEBRATE);
               MOVE(opponentLeft, MOVE_CELEBRATE); MOVE(opponentRight, MOVE_CELEBRATE); }
    } THEN {
        EXPECT_EQ(playerLeft->pp[0], GetMovePP(MOVE_CELEBRATE));
        EXPECT_EQ(playerRight->pp[0], GetMovePP(MOVE_CELEBRATE));
        EXPECT_EQ(opponentLeft->pp[0], GetMovePP(MOVE_CELEBRATE) - 1);
        EXPECT_EQ(opponentRight->pp[0], GetMovePP(MOVE_CELEBRATE) - 1);
    }
}

SINGLE_BATTLE_TEST("Shattered Transform keeps copied moves on the next turn")
{
    GIVEN {
        gShatteredTestLocalMechanics = TRUE;
        PLAYER(SPECIES_DITTO) { Moves(MOVE_SPLASH, MOVE_TRANSFORM); }
        OPPONENT(SPECIES_WOBBUFFET) { Moves(MOVE_SPLASH, MOVE_CELEBRATE); }
    } WHEN {
        TURN { MOVE(player, MOVE_TRANSFORM); MOVE(opponent, MOVE_CELEBRATE); }
        TURN { MOVE(player, MOVE_SPLASH); MOVE(opponent, MOVE_CELEBRATE); }
    } THEN {
        EXPECT(player->volatiles.transformed);
        EXPECT_EQ(player->moves[0], MOVE_SPLASH);
        EXPECT_EQ(player->moves[1], MOVE_CELEBRATE);
    }
}

SINGLE_BATTLE_TEST("Shattered Encore keeps the original forced move slot")
{
    GIVEN {
        gShatteredTestLocalMechanics = TRUE;
        PLAYER(SPECIES_WOBBUFFET) { Speed(100); Moves(MOVE_CELEBRATE, MOVE_SPLASH); }
        OPPONENT(SPECIES_WOBBUFFET) { Speed(50); Moves(MOVE_ENCORE, MOVE_CELEBRATE); }
    } WHEN {
        TURN { MOVE(player, MOVE_CELEBRATE); MOVE(opponent, MOVE_ENCORE); }
        TURN { MOVE(player, MOVE_CELEBRATE); MOVE(opponent, MOVE_CELEBRATE); }
    } THEN {
        EXPECT_EQ((u32)player->volatiles.encoredMove, MOVE_CELEBRATE);
        EXPECT_EQ(player->moves[player->volatiles.encoredMovePos], MOVE_CELEBRATE);
    }
}

SINGLE_BATTLE_TEST("Shattered replay mode retains ordinary player PP limitations")
{
    GIVEN {
        gShatteredTestLocalMechanics = FALSE;
        PLAYER(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
        OPPONENT(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
    } WHEN {
        TURN { MOVE(player, MOVE_CELEBRATE); MOVE(opponent, MOVE_CELEBRATE); }
    } THEN {
        EXPECT_EQ(player->pp[0], GetMovePP(MOVE_CELEBRATE) - 1);
        EXPECT_EQ(opponent->pp[0], GetMovePP(MOVE_CELEBRATE) - 1);
    }
}

SINGLE_BATTLE_TEST("Shattered switching keeps each Pokemon's saved attacks and PP separate")
{
    GIVEN {
        gShatteredTestLocalMechanics = TRUE;
        PLAYER(SPECIES_PIKACHU) { Moves(MOVE_CELEBRATE, MOVE_THUNDER_WAVE); }
        PLAYER(SPECIES_MAGIKARP) { Moves(MOVE_SPLASH, MOVE_CELEBRATE); }
        OPPONENT(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
    } WHEN {
        TURN { MOVE(player, MOVE_CELEBRATE); MOVE(opponent, MOVE_CELEBRATE); }
        TURN { SWITCH(player, 1); MOVE(opponent, MOVE_CELEBRATE); }
        TURN { MOVE(player, MOVE_SPLASH); MOVE(opponent, MOVE_CELEBRATE); }
    } THEN {
        EXPECT_EQ(player->species, SPECIES_MAGIKARP);
        EXPECT_EQ(player->moves[0], MOVE_SPLASH);
        EXPECT_EQ(player->pp[0], GetMovePP(MOVE_SPLASH));
        EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_MOVE1), MOVE_CELEBRATE);
        EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][1], MON_DATA_MOVE1), MOVE_SPLASH);
    }
}

SINGLE_BATTLE_TEST("Shattered blocked visible page finds an unlocked attack without changing the save")
{
    GIVEN {
        gShatteredTestLocalMechanics = TRUE;
        PLAYER(SPECIES_PIKACHU) { Moves(MOVE_GROWL, MOVE_TAIL_WHIP, MOVE_THUNDER_WAVE, MOVE_CELEBRATE); }
        OPPONENT(SPECIES_WOBBUFFET) { Moves(MOVE_CELEBRATE); }
    } WHEN {
        TURN { MOVE(player, MOVE_CELEBRATE); MOVE(opponent, MOVE_CELEBRATE); }
    } THEN {
        player->volatiles.tauntTimer = 2;
        EXPECT(ShatteredTryUsableLibraryPage(B_BATTLER_0));
        EXPECT(CheckMoveLimitations(B_BATTLER_0, 0, MOVE_LIMITATIONS_ALL) != 15);
        EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_MOVE1), MOVE_GROWL);
        EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_MOVE4), MOVE_CELEBRATE);
    }
}
