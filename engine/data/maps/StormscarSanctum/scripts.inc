StormscarSanctum_MapScripts::
	.byte 0

StormscarSanctum_EventScript_Return::
	lockall
	warp MAP_RIFTWAY_TRAIL, 12, 2
	waitstate
	releaseall
	end

StormscarSanctum_EventScript_Lore::
	msgbox StormscarSanctum_Text_Lore, MSGBOX_NPC
	end

StormscarSanctum_EventScript_Zapdos::
	lock
	faceplayer
	goto_if_unset FLAG_UNUSED_0x910, StormscarSanctum_EventScript_NeedNova
	goto_if_unset FLAG_UNUSED_0x90F, StormscarSanctum_EventScript_NeedWarden
	msgbox StormscarSanctum_Text_Guardian, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, StormscarSanctum_EventScript_Exit
	setwildbattle SPECIES_ZAPDOS, 35
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, StormscarSanctum_EventScript_Exit
	setflag FLAG_UNUSED_0x912
	removeobject VAR_LAST_TALKED
	msgbox StormscarSanctum_Text_Freed, MSGBOX_DEFAULT
StormscarSanctum_EventScript_Exit::
	release
	end
StormscarSanctum_EventScript_NeedNova::
	msgbox StormscarSanctum_Text_NeedNova, MSGBOX_DEFAULT
	release
	end
StormscarSanctum_EventScript_NeedWarden::
	msgbox StormscarSanctum_Text_NeedWarden, MSGBOX_DEFAULT
	release
	end

StormscarSanctum_Text_Lore:
	.string "ECLIPSE tried to drain this realm.\p"
	.string "Its guardian hid inside the storm.\n"
	.string "A kind Trainer might reach it.\p"
	.string "If it faints or you retreat,\n"
	.string "you can try again.$"
StormscarSanctum_Text_Guardian:
	.string "The thunderbird studies your bond.\n"
	.string "Will you face ZAPDOS?$"
StormscarSanctum_Text_Freed:
	.string "The storm breaks. A new partner\n"
	.string "will carry its strength with you.$"
StormscarSanctum_Text_NeedNova:
	.string "The guardian is wary of strangers.\n"
	.string "Meet NOVA on RIFTWAY TRAIL first.$"
StormscarSanctum_Text_NeedWarden:
	.string "An ECLIPSE device blocks its cry.\n"
	.string "Defeat VESPER in RIFT HOLLOW first.$"
