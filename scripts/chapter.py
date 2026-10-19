"""Save-index-preserving registrations for the original Rift chapter."""
import copy
import json

MAPS = ('LumenCrossing', 'RiftwayTrail', 'StormscarSanctum', 'LumenCrossing_Lodge', 'LumenCrossing_Workshop', 'LumenCrossing_Gym')
MAP_IDS = ('LUMEN_CROSSING', 'RIFTWAY_TRAIL', 'STORMSCAR_SANCTUM')

def patch(text, before, after):
    if after and after in text:
        if text.count(after) != 1:
            raise ValueError('Duplicate chapter patch')
        return text
    if text.count(before) != 1:
        raise ValueError(f'Chapter anchor missing or duplicated: {before[:80]!r}')
    return text.replace(before, after, 1)

def dump(doc):
    return json.dumps(doc, indent=2, ensure_ascii=False)+'\n'

def groups(text):
    doc = json.loads(text)
    for name in MAPS:
        if name not in doc['gMapGroup_Dungeons']:
            doc['gMapGroup_Dungeons'].append(name)
    return dump(doc)

def layouts(text):
    doc = json.loads(text)
    for name, identifier in zip(MAPS, MAP_IDS):
        value = dict(id='LAYOUT_'+identifier, name=name+'_Layout', width=24, height=24,
                     primary_tileset='gTileset_General',
                     secondary_tileset='gTileset_Cave' if name=='StormscarSanctum' else 'gTileset_Petalburg',
                     border_filepath=f'data/layouts/{name}/border.bin',
                     blockdata_filepath=f'data/layouts/{name}/map.bin', layout_version='emerald')
        matches = [entry for entry in doc['layouts'] if entry['id'] == value['id']]
        if matches and matches != [value]:
            raise ValueError(f'Conflicting chapter layout {name}')
        if not matches:
            doc['layouts'].append(value)
    return dump(doc)

def events(text):
    includes = [f'\t.include "data/maps/{name}/scripts.inc"' for name in MAPS]
    # Normalize our own registrations so an earlier three-map chapter can be
    # upgraded without including its script labels twice.
    text = ''.join(line for line in text.splitlines(keepends=True)
                   if line.rstrip('\r\n') not in includes)
    anchor = '\t.include "data/maps/RiftHollow/scripts.inc"'
    return patch(text, anchor, anchor+'\n'+'\n'.join(includes))


def sections(text):
    doc = json.loads(text)
    entries = doc['map_sections']
    # NONE keeps index 209. New sections go AFTER it, preserving every old ID.
    if not any(entry['id']=='MAPSEC_NONE' for entry in entries):
        if len(entries) != 209:
            raise ValueError('Pinned map-section count changed; migration audit required')
        entries.append(dict(id='MAPSEC_NONE', name=''))
    for i, (identifier, name) in enumerate(zip(MAP_IDS, ('LUMEN CROSSING','RIFTWAY TRAIL','STORMSCAR RIFT'))):
        if not any(entry['id']=='MAPSEC_'+identifier for entry in entries):
            entries.append(dict(id='MAPSEC_'+identifier, name=name, x=18+i, y=13, width=1, height=1))
    if entries[209]['id'] != 'MAPSEC_NONE' or len(entries) >= 253:
        raise ValueError('Chapter section IDs would overlap saved/special locations')
    return dump(doc)

def section_template(text):
    if '#define IS_VALID_MAPSEC' in text:
        return text
    text = patch(text, '    MAPSEC_NONE,\n', '')
    return patch(text, '// Special location IDs',
                 '#define IS_VALID_MAPSEC(id) ((id) < MAPSEC_COUNT && (id) != MAPSEC_NONE)\n\n// Special location IDs')

def map_names(text):
    return patch(text, 'else if (regionMapId < MAPSEC_NONE)', 'else if (IS_VALID_MAPSEC(regionMapId))')

def summary(text):
    text = text.replace('sum->metLocation < MAPSEC_NONE', 'IS_VALID_MAPSEC(sum->metLocation)')
    return text.replace('sum->metLocation >= MAPSEC_NONE', '!IS_VALID_MAPSEC(sum->metLocation)')

def dex_area(text):
    return patch(text, 'if (regionMapSectionId < MAPSEC_NONE)', 'if (IS_VALID_MAPSEC(regionMapSectionId))')

def popup(text):
    return patch(text, 'sMapSectionToThemeId[MAPSEC_COUNT - KANTO_MAPSEC_COUNT - 1]',
                 'sMapSectionToThemeId[MAPSEC_COUNT - KANTO_MAPSEC_COUNT]')

def opponents(text):
    text = patch(text, '#define TRAINERS_COUNT_EMERALD     856', '#define TRAINERS_COUNT_EMERALD     858')
    anchor = '#define TRAINER_ECLIPSE_WARDEN              855'
    return patch(text, anchor, anchor+'\n#define TRAINER_NOVA_RIFT                   856\n#define TRAINER_ECLIPSE_SCOUT               857')

def trainers(text):
    if '=== TRAINER_NOVA_RIFT ===' in text:
        return text
    return text.rstrip()+'''

=== TRAINER_NOVA_RIFT ===
Name: NOVA
Class: Cooltrainer
Pic: Cooltrainer F
Gender: Female
Music: Female
AI: Check Bad Move / Check Viability / Try To Faint / Smart Switching

Riolu @ Eviolite
Level: 12
Ability: Prankster
Nature: Jolly
EVs: 4 HP / 128 Atk / 128 Spe
- Force Palm
- Bullet Punch
- Rock Tomb
- Copycat

Shinx @ Sitrus Berry
Level: 13
Ability: Intimidate
Nature: Adamant
EVs: 4 HP / 128 Atk / 128 Spe
- Spark
- Bite
- Ice Fang
- Thunder Wave

Wingull @ Sitrus Berry
Level: 14
Ability: Hydration
Nature: Timid
EVs: 4 HP / 128 SpA / 128 Spe
- Water Pulse
- Air Cutter
- Icy Wind
- Roost

=== TRAINER_ECLIPSE_SCOUT ===
Name: ORIN
Class: Team Magma
Pic: Magma Grunt M
Gender: Male
Music: Magma
AI: Check Bad Move / Check Viability / Try To Faint / Smart Switching

Impidimp @ Eviolite
Level: 12
Ability: Prankster
Nature: Careful
EVs: 128 HP / 128 SpD
- Fake Out
- Bite
- Thunder Wave
- Reflect

Nymble @ Sitrus Berry
Level: 13
Ability: Swarm
Nature: Adamant
EVs: 128 Atk / 128 Spe
- Bug Bite
- Double Kick
- Assurance
- Quick Attack

'''

def hometown_npc(text):
    doc = json.loads(text)
    matches = [obj for obj in doc['object_events'] if obj['script'] in
               ('LittlerootTown_EventScript_FatMan','ShatteredLittleroot_EventScript_Beacon')]
    if len(matches) != 1:
        raise ValueError('Littleroot beacon guide changed')
    matches[0]['script'] = 'ShatteredLittleroot_EventScript_Beacon'
    matches[0]['graphics_id'] = 'OBJ_EVENT_GFX_SCIENTIST_1'
    return dump(doc)

def hometown_script(text):
    if 'ShatteredLittleroot_EventScript_Beacon::' in text:
        return text
    return text.rstrip()+r'''

ShatteredLittleroot_EventScript_Beacon::
	lock
	faceplayer
	goto_if_unset FLAG_SYS_POKEMON_GET, ShatteredLittleroot_EventScript_BeforePartner
	msgbox ShatteredLittleroot_Text_Beacon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ShatteredLittleroot_EventScript_Exit
	closemessage
	warp MAP_LUMEN_CROSSING, 12, 21
	waitstate
ShatteredLittleroot_EventScript_Exit::
	release
	end
ShatteredLittleroot_EventScript_BeforePartner::
	msgbox ShatteredLittleroot_Text_BeforePartner, MSGBOX_DEFAULT
	release
	end
ShatteredLittleroot_Text_Beacon:
	.string "I am ELARA, keeper of the beacon.\p"
	.string "The violet light leads home to\n"
	.string "LUMEN CROSSING, between realms.\p"
	.string "Will you cross with your partner?$"
ShatteredLittleroot_Text_BeforePartner:
	.string "PROF. BIRCH needs help up north!\p"
	.string "Find a POKeMON partner first.\n"
	.string "Then I can open the beacon.$"
'''

def encounters(text):
    doc = json.loads(text)
    group = next(group for group in doc['wild_encounter_groups'] if group['label']=='gWildMonHeaders')
    if any(entry['map']=='MAP_RIFTWAY_TRAIL' for entry in group['encounters']):
        return dump(doc)
    route = copy.deepcopy(next(entry for entry in group['encounters'] if entry['map']=='MAP_ROUTE101'))
    route['map'] = 'MAP_RIFTWAY_TRAIL'
    route['base_label'] = 'gRiftwayTrail'
    route['land_mons']['encounter_rate'] = 12
    species = ['SHINX','PAWMI','ROWLET','TADBULB','RIOLU','GOOMY','ROOKIDEE','FROAKIE','SPRIGATITO','FRIGIBAX','DREEPY','EEVEE']
    for i, (entry, name) in enumerate(zip(route['land_mons']['mons'], species)):
        entry.update(species='SPECIES_'+name, min_level=6+i//3, max_level=9+i//3)
    group['encounters'].append(route)
    return dump(doc)

def trade_partners(text):
    for target, partner in (('ESCAVALIER','SHELMET'), ('ACCELGOR','KARRABLAST')):
        before = '{EVO_TRADE, 0, SPECIES_' + target + ', CONDITIONS({IF_TRADE_PARTNER_SPECIES, SPECIES_' + partner + '})}'
        text = patch(text, before, before + ',\n                                {EVO_ITEM, ITEM_LINKING_CORD, SPECIES_' + target + '}')
    return text


def disable_timer(text):
    text = patch(text, '#include "battle_util.h"\n', '#include "battle_util.h"\n#include "shattered_battle.h"\n')
    return patch(text,
        '        if (moveIndex == MAX_MON_MOVES)  // Pokémon does not have the disabled move anymore',
        """        if (moveIndex == MAX_MON_MOVES
            && ShatteredHasUnlimitedPP(battler)
            && !gBattleMons[battler].volatiles.transformed
            && !gBattleMons[battler].volatiles.mimickedMoves
            && ShatteredBoxKnowsMove(&GetBattlerMon(battler)->box, gBattleMons[battler].volatiles.disabledMove))
            moveIndex = 0; // Browsing a page does not erase Disable.
        if (moveIndex == MAX_MON_MOVES)  // Pokémon does not have the disabled move anymore""")


PATCHERS = {
    'src/battle_end_turn.c': disable_timer,
    'src/data/pokemon/species_info/gen_5_families.h': trade_partners,
    'data/maps/map_groups.json': groups,
    'data/layouts/layouts.json': layouts,
    'data/event_scripts.s': events,
    'src/data/region_map/region_map_sections.json': sections,
    'src/data/region_map/region_map_sections.constants.json.txt': section_template,
    'src/region_map.c': map_names,
    'src/pokemon_summary_screen.c': summary,
    'src/pokedex_area_screen.c': dex_area,
    'src/map_name_popup.c': popup,
    'include/constants/opponents.h': opponents,
    'src/data/trainers.party': trainers,
    'data/maps/LittlerootTown/map.json': hometown_npc,
    'data/maps/LittlerootTown/scripts.inc': hometown_script,
    'src/data/wild_encounters.json': encounters,
}
