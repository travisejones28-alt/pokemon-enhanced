LumenCrossing_MapScripts::
	.byte 0

LumenCrossing_EventScript_Return::
	lockall
	warp MAP_LITTLEROOT_TOWN, 12, 14
	waitstate
	releaseall
	end

LumenCrossing_EventScript_Trail::
	lockall
	warp MAP_RIFTWAY_TRAIL, 12, 21
	waitstate
	releaseall
	end

LumenCrossing_EventScript_Guide::
	lock
	faceplayer
	goto_if_unset FLAG_UNUSED_0x90B, ShatteredOldale_EventScript_StartQuest
	goto_if_unset FLAG_UNUSED_0x90C, LumenCrossing_EventScript_FirstAnomaly
	goto_if_unset FLAG_UNUSED_0x90D, LumenCrossing_EventScript_SecondAnomaly
	goto_if_unset FLAG_UNUSED_0x90E, LumenCrossing_EventScript_ThirdAnomaly
	goto_if_unset FLAG_UNUSED_0x90F, LumenCrossing_EventScript_Warden
	goto_if_unset FLAG_BADGE01_GET, LumenCrossing_EventScript_FirstBadge
	msgbox LumenCrossing_Text_NextRealm, MSGBOX_DEFAULT
	release
	end

LumenCrossing_EventScript_FirstAnomaly::
	msgbox LumenCrossing_Text_FirstAnomaly, MSGBOX_DEFAULT
	release
	end

LumenCrossing_EventScript_SecondAnomaly::
	msgbox LumenCrossing_Text_SecondAnomaly, MSGBOX_DEFAULT
	release
	end

LumenCrossing_EventScript_ThirdAnomaly::
	msgbox LumenCrossing_Text_ThirdAnomaly, MSGBOX_DEFAULT
	release
	end

LumenCrossing_EventScript_Warden::
	msgbox LumenCrossing_Text_Warden, MSGBOX_DEFAULT
	release
	end

LumenCrossing_EventScript_FirstBadge::
	msgbox LumenCrossing_Text_FirstBadge, MSGBOX_DEFAULT
	release
	end

LumenCrossing_EventScript_Healer::
	lock
	faceplayer
	special HealPlayerParty
	msgbox LumenCrossing_Text_Healed, MSGBOX_DEFAULT
	goto_if_unset FLAG_UNUSED_0x910, LumenCrossing_EventScript_Exit
	goto_if_set FLAG_UNUSED_0x911, LumenCrossing_EventScript_Exit
	msgbox LumenCrossing_Text_Reward, MSGBOX_DEFAULT
	giveitem ITEM_LIGHT_BALL
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_UNUSED_0x911
LumenCrossing_EventScript_Exit::
	release
	end

LumenCrossing_EventScript_Astra::
	goto_if_unset FLAG_UNUSED_0x90F, LumenCrossing_EventScript_AstraSealed
	goto RustboroCity_Gym_EventScript_Roxanne
	end

LumenCrossing_EventScript_AstraSealed::
	msgbox LumenCrossing_Text_AstraSealed, MSGBOX_NPC
	end

LumenCrossing_EventScript_Collector::
	msgbox LumenCrossing_Text_Collector, MSGBOX_NPC
	end

LumenCrossing_Text_FirstAnomaly:
	.string "Welcome to LUMEN CROSSING!\p"
	.string "We anchor paths between worlds.\n"
	.string "ECLIPSE is tearing them apart.\p"
	.string "JOURNAL: Check the anomaly on\n"
	.string "ROUTE 101, then return.$"
LumenCrossing_Text_SecondAnomaly:
	.string "JOURNAL: First anomaly recorded.\n"
	.string "Investigate ROUTE 102 next.$"
LumenCrossing_Text_ThirdAnomaly:
	.string "JOURNAL: Two anomalies recorded.\n"
	.string "Investigate ROUTE 103 next.$"
LumenCrossing_Text_Warden:
	.string "JOURNAL: All anomalies recorded.\p"
	.string "Take RIFTWAY TRAIL north, then\n"
	.string "its eastern breach to RIFT HOLLOW.\p"
	.string "Stop VESPER from taking its core!$"
LumenCrossing_Text_FirstBadge:
	.string "JOURNAL: The first Rift is safe!\p"
	.string "ASTRA waits in our beacon GYM.\n"
	.string "The GYM is south of the plaza.$"
LumenCrossing_Text_NextRealm:
	.string "JOURNAL: LUMEN is stable again.\p"
	.string "With the DYNAMO BADGE, the north\n"
	.string "gate opens to STORMSCAR RIFT.\p"
	.string "NOVA may know its guardian.$"
LumenCrossing_Text_Healed:
	.string "Your team is fully restored.\p"
	.string "Our bond keeps this beacon lit.\n"
	.string "Talk to your following POKeMON!$"
LumenCrossing_Text_Reward:
	.string "NOVA told me about your battle.\p"
	.string "This LIGHT BALL belongs with\n"
	.string "a brave PIKACHU and its partner!$"
LumenCrossing_Text_AstraSealed:
	.string "ASTRA: I protect LUMEN'S beacon.\p"
	.string "First stop ECLIPSE in RIFT HOLLOW.\n"
	.string "Then we can test your bond.$"
LumenCrossing_Text_Collector:
	.string "RIFTWAY habitats: SHINX, RIOLU,\n"
	.string "PAWMI, ROWLET and TADBULB.\p"
	.string "Look deeper for DREEPY, GOOMY,\n"
	.string "SPRIGATITO and FRIGIBAX.\p"
	.string "STORMSCAR shelters a legendary\n"
	.string "guardian. NOVA knows its story.$"

LumenCrossing_EventScript_EvolutionShop::
	lock
	faceplayer
	msgbox LumenCrossing_Text_EvolutionShop, MSGBOX_DEFAULT
	pokemart LumenCrossing_EvolutionStock
	msgbox LumenCrossing_Text_EvolutionThanks, MSGBOX_DEFAULT
	release
	end

LumenCrossing_Text_EvolutionShop:
	.string "Every world has ways to grow.\p"
	.string "Use a LINKING CORD instead of\n"
	.string "trading KARRABLAST or SHELMET.\p"
	.string "Our stones and rare evolution\n"
	.string "items are available to everyone.$"
LumenCrossing_Text_EvolutionThanks:
	.string "No partner should be left behind.$"

	.align 2
LumenCrossing_EvolutionStock:
	.2byte ITEM_LINKING_CORD
	.2byte ITEM_FIRE_STONE
	.2byte ITEM_WATER_STONE
	.2byte ITEM_THUNDER_STONE
	.2byte ITEM_LEAF_STONE
	.2byte ITEM_ICE_STONE
	.2byte ITEM_MOON_STONE
	.2byte ITEM_SUN_STONE
	.2byte ITEM_SHINY_STONE
	.2byte ITEM_DUSK_STONE
	.2byte ITEM_DAWN_STONE
	.2byte ITEM_KINGS_ROCK
	.2byte ITEM_METAL_COAT
	.2byte ITEM_DRAGON_SCALE
	.2byte ITEM_UPGRADE
	.2byte ITEM_DUBIOUS_DISC
	.2byte ITEM_ELECTIRIZER
	.2byte ITEM_MAGMARIZER
	.2byte ITEM_REAPER_CLOTH
	.2byte ITEM_PRISM_SCALE
	.2byte ITEM_PROTECTOR
	.2byte ITEM_DEEP_SEA_TOOTH
	.2byte ITEM_DEEP_SEA_SCALE
	.2byte ITEM_RAZOR_CLAW
	.2byte ITEM_RAZOR_FANG
	.2byte ITEM_SACHET
	.2byte ITEM_WHIPPED_DREAM
	.2byte ITEM_SWEET_APPLE
	.2byte ITEM_TART_APPLE
	.2byte ITEM_CRACKED_POT
	.2byte ITEM_CHIPPED_POT
	.2byte ITEM_GALARICA_CUFF
	.2byte ITEM_GALARICA_WREATH
	.2byte ITEM_BLACK_AUGURITE
	.2byte ITEM_PEAT_BLOCK
	.2byte ITEM_AUSPICIOUS_ARMOR
	.2byte ITEM_MALICIOUS_ARMOR
	.2byte ITEM_LEADERS_CREST
	.2byte ITEM_SCROLL_OF_DARKNESS
	.2byte ITEM_SCROLL_OF_WATERS
	.2byte ITEM_SYRUPY_APPLE
	.2byte ITEM_UNREMARKABLE_TEACUP
	.2byte ITEM_MASTERPIECE_TEACUP
	.2byte ITEM_NONE
