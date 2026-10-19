RiftHollow_MapScripts::
	.byte 0

RiftHollow_EventScript_Scientist::
	lock
	faceplayer
	goto_if_set FLAG_UNUSED_0x90F, RiftHollow_EventScript_ScientistAfterVictory
	msgbox RiftHollow_Text_Scientist, MSGBOX_DEFAULT
	release
	end

RiftHollow_EventScript_ScientistAfterVictory::
	msgbox RiftHollow_Text_ScientistVictory, MSGBOX_DEFAULT
	release
	end

RiftHollow_EventScript_EclipseWarden::
	goto_if_set FLAG_UNUSED_0x90F, RiftHollow_EventScript_WardenAfterVictory
	trainerbattle_single TRAINER_ECLIPSE_WARDEN, RiftHollow_Text_WardenIntro, RiftHollow_Text_WardenDefeat, RiftHollow_EventScript_WardenVictory
	msgbox RiftHollow_Text_WardenAfterVictory, MSGBOX_AUTOCLOSE
	end

RiftHollow_EventScript_WardenVictory::
	setflag FLAG_UNUSED_0x90F
	msgbox RiftHollow_Text_WardenReward, MSGBOX_DEFAULT
	giveitem ITEM_SHINY_CHARM
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	release
	end

RiftHollow_EventScript_WardenAfterVictory::
	msgbox RiftHollow_Text_WardenAfterVictory, MSGBOX_NPC
	end

RiftHollow_Text_Scientist:
	.string "The Rift Hollow is unstable.\p"
	.string "TEAM ECLIPSE is stealing energy\n"
	.string "from the dimensional breach.\p"
	.string "Their commander is just ahead!\p"
	.string "Even unlimited power cannot\n"
	.string "replace good battle tactics.$"

RiftHollow_Text_ScientistVictory:
	.string "The Rift is calming down...\p"
	.string "But TEAM ECLIPSE is still\n"
	.string "operating in other regions.$"

RiftHollow_Text_WardenIntro:
	.string "VESPER: So you found the breach.\p"
	.string "You and your POKeMON have\n"
	.string "no idea what is coming!$"

RiftHollow_Text_WardenDefeat:
	.string "The Rift's power... fading!$"

RiftHollow_Text_WardenReward:
	.string "You drove ECLIPSE from the Rift!\p"
	.string "Take this SHINY CHARM as proof\n"
	.string "of your victory!$"

RiftHollow_Text_WardenAfterVictory:
	.string "VESPER: This was only the first\n"
	.string "rift. We will meet again.$"
