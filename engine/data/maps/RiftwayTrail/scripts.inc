RiftwayTrail_MapScripts::
	.byte 0

RiftwayTrail_EventScript_Return::
	lockall
	warp MAP_LUMEN_CROSSING, 12, 2
	waitstate
	releaseall
	end

RiftwayTrail_EventScript_Hollow::
	lockall
	goto_if_unset FLAG_UNUSED_0x90E, RiftwayTrail_EventScript_NeedAnomalies
	warp MAP_RIFT_HOLLOW, 18, 21
	waitstate
	releaseall
	end
RiftwayTrail_EventScript_NeedAnomalies::
	msgbox RiftwayTrail_Text_NeedAnomalies, MSGBOX_DEFAULT
	releaseall
	end

RiftwayTrail_EventScript_Stormscar::
	lockall
	goto_if_unset FLAG_BADGE03_GET, RiftwayTrail_EventScript_NeedBadge
	warp MAP_STORMSCAR_SANCTUM, 12, 21
	waitstate
	releaseall
	end
RiftwayTrail_EventScript_NeedBadge::
	msgbox RiftwayTrail_Text_NeedBadge, MSGBOX_DEFAULT
	releaseall
	end

RiftwayTrail_EventScript_Nova::
	goto_if_set FLAG_UNUSED_0x910, RiftwayTrail_EventScript_NovaAfter
	trainerbattle_single TRAINER_NOVA_RIFT, RiftwayTrail_Text_NovaIntro, RiftwayTrail_Text_NovaDefeat, RiftwayTrail_EventScript_NovaWon
	end
RiftwayTrail_EventScript_NovaWon::
	setflag FLAG_UNUSED_0x910
	msgbox RiftwayTrail_Text_NovaAfter, MSGBOX_DEFAULT
	release
	end
RiftwayTrail_EventScript_NovaAfter::
	msgbox RiftwayTrail_Text_NovaAfter, MSGBOX_NPC
	end

RiftwayTrail_EventScript_Scout::
	trainerbattle_single TRAINER_ECLIPSE_SCOUT, RiftwayTrail_Text_ScoutIntro, RiftwayTrail_Text_ScoutDefeat
	msgbox RiftwayTrail_Text_ScoutAfter, MSGBOX_AUTOCLOSE
	end

RiftwayTrail_EventScript_Researcher::
	msgbox RiftwayTrail_Text_Researcher, MSGBOX_NPC
	end

RiftwayTrail_Text_NeedAnomalies:
	.string "The violet breach flickers.\p"
	.string "Record all three anomalies on\n"
	.string "ROUTES 101, 102 and 103 first.$"
RiftwayTrail_Text_NeedBadge:
	.string "Lightning seals the northern path.\p"
	.string "The DYNAMO BADGE can anchor\n"
	.string "a bridge to STORMSCAR RIFT.$"
RiftwayTrail_Text_NovaIntro:
	.string "NOVA: You are BIRCH'S new partner?\p"
	.string "I grew up between these Rifts.\n"
	.string "Let's see how your team adapts!$"
RiftwayTrail_Text_NovaDefeat:
	.string "That bond is stronger than a Rift!$"
RiftwayTrail_Text_NovaAfter:
	.string "NOVA: A thunderbird is trapped\n"
	.string "beyond our northern gate.\p"
	.string "Earn the DYNAMO BADGE, then\n"
	.string "free it from STORMSCAR RIFT.\p"
	.string "The healer has a gift for you.$"
RiftwayTrail_Text_ScoutIntro:
	.string "ECLIPSE SCOUT: The core belongs\n"
	.string "to COMMANDER VESPER! Step aside!$"
RiftwayTrail_Text_ScoutDefeat:
	.string "The readings never predicted this!$"
RiftwayTrail_Text_ScoutAfter:
	.string "VESPER is waiting in RIFT HOLLOW.\n"
	.string "Don't say I didn't warn you!$"
RiftwayTrail_Text_Researcher:
	.string "West grass and east grass share\n"
	.string "POKeMON from distant regions.\p"
	.string "Use SELECT for the next move page\n"
	.string "or R for the previous page.\p"
	.string "The eastern breach leads to the\n"
	.string "first ECLIPSE stronghold.$"
