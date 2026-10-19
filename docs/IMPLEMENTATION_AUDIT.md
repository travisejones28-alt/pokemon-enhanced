# Implementation audit — 19 October 2026

## Baseline and verified scope

Audited main at `0c15a7e15d26a902862d1edc23e6076d9adcde19`.
Build #27 and build #52 succeeded. Build #46 failed during compilation;
intervening fixes registered Rift Hollow scripts and preserved engine trainer IDs.
There are no representative Delta `.sav` files in this checkout and no installed
GBA emulator or ARM toolchain in this session. GBA compilation runs in GitHub Actions.
A passing build is not proof that a playthrough, battle mechanic or save migration works.

## Repairs in this increment

- Full patch composition can run twice without changing bytes on its second pass.
  Previously the PP-display and move-page patches could not compose twice.
- Route 101 retains both the original-story teaser replacement and anomaly quest.
  Previously the later quest pass re-read the original file and lost the teaser.
- Patch anchors reject duplicate/mixed patched and unpatched copies.
- Enemy IV floors apply separately to each of six packed five-bit fields.
  Previously comparing the packed integer with 28 failed to raise most stats.
- Player PP refills no longer replace runtime attacks with the saved four attacks.
  Saved PP is calculated from the saved attack, independent of virtual pages.
- Transform, Mimic and Encore suspend library paging and preserve the active
  battle slots. Paging resumes when those effects end. This deliberately keeps
  upstream slot-based effects intact; transformed Pokémon use their copied moves.
- Link/replay and AI-controlled partners are excluded from library browsing.
- Changing pages recalculates Z-Move compatibility and refreshes move UI.
- Field Bag supplies include Linking Cords and common evolution stones, adding
  an item only when absent. If a pocket is full, free space and reopen the Bag.
- Advanced enemy AI also applies to ordinary zero-flag trainer definitions;
  smarter switching is enabled. Facilities and recorded/link battles are excluded.

## What the move library actually does

SELECT advances through four-move pages; the page counter replaces PP. The
current battle moves, saved moves, level-appropriate current/pre-evolution moves,
species-compatible machines, a curated tutor list and egg moves are reconstructed.
Pikachu gets four extra signature attacks and friendship unlocks at 120/180/230.
The catalog is capped at 256 distinct moves. Disabled attacks still use upstream
move-identity checks; targeting uses the upstream single/double battle controllers.

**This is not complete unlimited move history.** There is no persistent archive
of forgotten event-only attacks, acquired moves from another species, or which
machines/tutors were actually learned. Machine and egg compatibility currently
unlocks attacks without acquiring them. Some all-moves-unusable checks, Choice
locks, multi-turn effects, Sketch, Transform interactions and double battle
cancellations still need emulator regression tests. Do not call these verified.

## Story and collection reality

The source contains an Oldale three-anomaly quest, appended Rift Hollow dungeon,
Eclipse boss and reward, plus Astra replacing the first Gym encounter. These need
end-to-end playtesting. Most Hoenn progression remains intact. There is no complete
original hometown, original route network, rival campaign, multiple realms or
classic-region travel yet.

Fourteen wild encounter tables include cross-generation species. Engine species
support spans generations 1–9, but full availability and all trade evolutions have
not been audited. The expanded Pokédex and follower system are configured, not
verified across every species, interior, transition or movement mode.

## Automated verification

The regression suite includes actual vendored-source patch application, byte-for-
byte second-pass comparison, no partial writes on invalid input, and host-compiled
C tests of all packed IV fields and battle-library eligibility. These host tests
exercise generated C logic; they do not emulate battles.

Actions also compiles the GBA ROM, validates title/game code/header checksum and
size, and verifies a published SHA-256 manifest. Failed test/build steps cannot
publish the release. Old tagged releases are retained.

## Required release playtest

1. Export an old in-game save before importing a different ROM in Delta.
2. Continue, inspect party/PC/Bag/badges, change map, save, quit and reload.
3. Start separately: choose level-5 Pikachu and check four signature moves.
4. Test paged attacks in single and double battles, cancel/reopen, switching,
   fainting, Transform, Mimic, Disable, Encore, Choice items and multi-turn moves.
5. Verify opponent PP drains and player attacks remain usable after PP drain.
6. Verify fourfold battle EXP, adaptive trainer levels and blocked trainer Bag.
7. Play the full anomaly quest, Rift boss/reward, return portal and Astra fight.
8. Test following indoors/outdoors, stairs, doors, surfing, cycling and fainting.

No new game is intentionally required by this increment. Old-save compatibility
remains unverified until actual old saves pass the above checks.
