#!/usr/bin/env python3
"""Deterministic authored GBA tile layouts for the first Shattered Realms chapter."""
import copy
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1] / 'engine'
NAMES = ('LumenCrossing', 'RiftwayTrail', 'StormscarSanctum')
IDS = ('LUMEN_CROSSING', 'RIFTWAY_TRAIL', 'STORMSCAR_SANCTUM')

def npc(gfx, x, y, script, flag='0'):
    return dict(graphics_id=gfx, x=x, y=y, elevation=3,
                movement_type='MOVEMENT_TYPE_FACE_DOWN', movement_range_x=0,
                movement_range_y=0, trainer_type='TRAINER_TYPE_NONE',
                trainer_sight_or_berry_tree_id='0', script=script, flag=flag)

def trigger(x, y, script):
    return dict(type='trigger', x=x, y=y, elevation=3, var='VAR_TEMP_0',
                var_value='0', script=script)

def build():
    for name, identifier in zip(NAMES, IDS):
        cave = name == 'StormscarSanctum'
        # All walkable cells are elevation 3; borders and pillars are solid.
        floor, wall = (0x3211, 0x0611) if cave else (0x3001, 0x05D4)
        tiles = [[floor if 1 <= x <= 22 and 1 <= y <= 22 else wall
                  for x in range(24)] for y in range(24)]
        if cave:
            for x in (5, 6, 17, 18):
                for y in range(8, 16):
                    tiles[y][x] = wall
        else:
            for y in range(1, 23):
                tiles[y][11] = tiles[y][12] = 0x3004
            for x in range(1, 23):
                tiles[11][x] = tiles[12][x] = 0x3004
            if name == 'RiftwayTrail':
                for y in range(5, 20):
                    for x in list(range(3, 9)) + list(range(16, 22)):
                        tiles[y][x] = 0x300D
            else:
                for x, y in [(4,4),(5,4),(18,4),(19,4),(4,18),(5,18),(18,18),(19,18)]:
                    tiles[y][x] = 0x300D
        if name == 'LumenCrossing':
            # Reuse the engine's actual house/lab metatiles, while authoring a
            # new town arrangement. Door positions are linked to real interiors.
            old = struct.unpack('<400H', (ROOT/'data/layouts/LittlerootTown/map.bin').read_bytes())
            def copy_building(sx, sy, width, height, dx, dy):
                for yy in range(height):
                    for xx in range(width):
                        tiles[dy+yy][dx+xx] = old[(sy+yy)*20+sx+xx]
            copy_building(11, 2, 8, 7, 3, 3)
            copy_building(11, 2, 8, 7, 15, 3)
            copy_building(3, 11, 10, 6, 7, 13)
            for x, y in ((6,10),(18,10),(11,19),(11,20)):
                tiles[y][x] = 0x3004
        directory = ROOT / 'data/layouts' / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'map.bin').write_bytes(struct.pack('<576H', *(v for row in tiles for v in row)))
        (directory / 'border.bin').write_bytes(struct.pack('<4H', *([wall] * 4)))
        doc = dict(id='MAP_' + identifier, name=name, layout='LAYOUT_' + identifier,
                   music='MUS_RG_SEVII_CAVE' if cave else 'MUS_ROUTE101', region='REGION_HOENN',
                   region_map_section='MAPSEC_' + identifier, requires_flash=False,
                   weather='WEATHER_NONE' if cave else 'WEATHER_SUNNY',
                   map_type='MAP_TYPE_UNDERGROUND' if cave else 'MAP_TYPE_TOWN' if name=='LumenCrossing' else 'MAP_TYPE_ROUTE',
                   allow_cycling=not cave, allow_escaping=cave, allow_running=True,
                   show_map_name=True, battle_scene='MAP_BATTLE_SCENE_NORMAL', connections=None,
                   object_events=[], warp_events=[], coord_events=[], bg_events=[])
        if name == 'LumenCrossing':
            doc['object_events'] = [
                npc('OBJ_EVENT_GFX_SCIENTIST_1',8,11,'LumenCrossing_EventScript_Guide'),
                npc('OBJ_EVENT_GFX_GIRL_1',5,14,'LumenCrossing_EventScript_Collector')]
            doc['warp_events'] = [
                dict(x=6,y=9,elevation=0,dest_map='MAP_LUMEN_CROSSING_LODGE',dest_warp_id='0'),
                dict(x=18,y=9,elevation=0,dest_map='MAP_LUMEN_CROSSING_WORKSHOP',dest_warp_id='0'),
                dict(x=11,y=18,elevation=0,dest_map='MAP_LUMEN_CROSSING_GYM',dest_warp_id='0')]
            doc['coord_events'] = [trigger(12,22,'LumenCrossing_EventScript_Return'),
                                   trigger(12,1,'LumenCrossing_EventScript_Trail')]
        elif name == 'RiftwayTrail':
            doc['object_events'] = [
                npc('OBJ_EVENT_GFX_COOLTRAINER_F',12,9,'RiftwayTrail_EventScript_Nova'),
                npc('OBJ_EVENT_GFX_MAGMA_MEMBER_M',17,16,'RiftwayTrail_EventScript_Scout'),
                npc('OBJ_EVENT_GFX_SCIENTIST_1',8,12,'RiftwayTrail_EventScript_Researcher')]
            doc['coord_events'] = [trigger(12,22,'RiftwayTrail_EventScript_Return'),
                                   trigger(22,12,'RiftwayTrail_EventScript_Hollow'),
                                   trigger(12,1,'RiftwayTrail_EventScript_Stormscar')]
        else:
            doc['object_events'] = [npc('OBJ_EVENT_GFX_ZAPDOS',12,5,'StormscarSanctum_EventScript_Zapdos','FLAG_UNUSED_0x912'),
                                    npc('OBJ_EVENT_GFX_SCIENTIST_1',9,18,'StormscarSanctum_EventScript_Lore')]
            doc['coord_events'] = [trigger(12,22,'StormscarSanctum_EventScript_Return')]
        directory = ROOT / 'data/maps' / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'map.json').write_text(json.dumps(doc, indent=2)+'\n')

    for name, template, door_index in (
        ('LumenCrossing_Lodge','OldaleTown_House1',0),
        ('LumenCrossing_Workshop','OldaleTown_House1',1),
        ('LumenCrossing_Gym','RustboroCity_Gym',2),
    ):
        doc = copy.deepcopy(json.loads((ROOT/f'data/maps/{template}/map.json').read_text()))
        doc.update(id='MAP_'+{'LumenCrossing_Lodge':'LUMEN_CROSSING_LODGE',
                             'LumenCrossing_Workshop':'LUMEN_CROSSING_WORKSHOP',
                             'LumenCrossing_Gym':'LUMEN_CROSSING_GYM'}[name],
                   name=name,region_map_section='MAPSEC_LUMEN_CROSSING',allow_running=True)
        for warp in doc['warp_events']:
            warp.update(dest_map='MAP_LUMEN_CROSSING',dest_warp_id=str(door_index))
        if door_index == 0:
            doc['object_events'] = [npc('OBJ_EVENT_GFX_NURSE',6,4,'LumenCrossing_EventScript_Healer')]
        elif door_index == 1:
            doc['object_events'] = [npc('OBJ_EVENT_GFX_MART_EMPLOYEE',6,4,'LumenCrossing_EventScript_EvolutionShop')]
        else:
            for obj in doc['object_events']:
                if obj['script'] == 'RustboroCity_Gym_EventScript_Roxanne':
                    obj.update(script='LumenCrossing_EventScript_Astra',graphics_id='OBJ_EVENT_GFX_HEX_MANIAC')
        directory=ROOT/'data/maps'/name
        directory.mkdir(parents=True,exist_ok=True)
        (directory/'map.json').write_text(json.dumps(doc,indent=2)+'\n')

if __name__ == '__main__':
    build()
