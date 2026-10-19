# Persistent move library and save format

SELECT advances four-move pages; R goes back. The PP area displays the page.
The catalog capacity now covers every ordinary move ID supported by the pinned
engine, rather than truncating at 256 attacks. Deduplication uses a bitset.

Each Pokémon's library includes current battle attacks, four saved attacks,
current and pre-evolution level/evolution moves, the complete compatible
machine/tutor learnsets, egg moves, retained exceptional attacks and Pikachu's
signature/Bond attacks. Compatibility automatically unlocks ordinary teachable
moves; this is deliberately broader than a record of purchased TMs.

Exceptional event, Sketch and off-species attacks are keyed by the full original
trainer ID and personality. They survive party reordering, PC storage and
normal evolution. Owned Pokémon's move writes archive an exceptional attack
before replacing it. Battle-only Transform and Mimic moves are not written into
permanent Pokémon slots. Sketch persists only its legitimately replaced saved
Sketch slot. A virtual Sketch without a saved Sketch remains battle-only.

Pikachu's friendship thresholds are 120 (Zippy Zap), 180 (Splishy Splash) and 230
(Floaty Fall). Using the library or interacting with the follower retains newly
unlocked Bond moves, so a subsequent friendship decrease does not erase them.

## Hardware limit and protection

A 1,536-byte journal occupies unused space in the existing SaveBlock3 sector
chunks. It holds **152 exceptional attacks across the save**, not 152 per
Pokémon. Reconstructed compatible attacks require no journal entries. No entry
is evicted to make room for another Pokémon. If the journal is full or invalid,
replacement of an exceptional move's only saved copy is refused. The follower
reports the problem. At this limit a learning dialogue may describe a replacement
which was refused; inspect the saved move list before proceeding.

Old saves have a zero-filled unused tail. On first use it becomes a version-1
journal with a magic identifier, count and whole-payload integrity hash.
Unknown/future versions and damaged payloads are not reset or overwritten.
Moves forgotten before this journal existed cannot be retroactively recovered
unless they are reconstructible from the Pokémon's learnsets.

## Persistent layout comparison

ARM ABI probes against the previous committed header and the new header:

| Record | Before | After |
| --- | ---: | ---: |
| SaveBlock1 | 15,568 | 15,568 |
| SaveBlock2 | 3,884 | 3,884 |
| Pokémon storage | 34,144 | 34,144 |
| Party Pokémon | 100 | 100 |
| Box Pokémon | 80 | 80 |
| SaveBlock3 | 4 | 1,540 |

The party, Bag and flags offsets in SaveBlock1 remain 568, 1,376 and 4,720.
SaveBlock3's existing `dexNavChain` stays at offset zero. The extension fits the
existing 1,624-byte chunk capacity; sector IDs, main payload sizes/checksums,
Pokémon encryption formats and species indices remain unchanged. All original
map/layout/region-section IDs retain their previous indices, including NONE.

This is an append-only save-tail migration, not a claim that every historical
Delta save has been tested. Always retain an exported pre-update battery save.
