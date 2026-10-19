import collections
import json
from pathlib import Path
import re
import struct
import tempfile
import unittest

from scripts import chapter
from scripts import generate_chapter_maps as generator

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'engine'


class TestChapter(unittest.TestCase):
    def test_authored_map_assets_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            original = generator.ROOT
            generator.ROOT = Path(directory)
            import shutil
            for relative in ['data/layouts/LittlerootTown/map.bin',
                             'data/maps/OldaleTown_House1/map.json',
                             'data/maps/RustboroCity_Gym/map.json']:
                target = generator.ROOT / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ENGINE/relative, target)
            try:
                generator.build()
                for name in generator.NAMES:
                    for folder, filenames in [('data/maps', ['map.json']),
                                              ('data/layouts', ['map.bin','border.bin'])]:
                        for filename in filenames:
                            path = Path(folder)/name/filename
                            self.assertEqual((generator.ROOT/path).read_bytes(), (ENGINE/path).read_bytes())
            finally:
                generator.ROOT = original

    def test_every_portal_and_npc_is_reachable(self):
        for name in generator.NAMES:
            with self.subTest(map=name):
                doc = json.loads((ENGINE/f'data/maps/{name}/map.json').read_text())
                values = struct.unpack('<576H', (ENGINE/f'data/layouts/{name}/map.bin').read_bytes())
                occupants = {(npc['x'],npc['y']) for npc in doc['object_events']}
                walkable = {(i % 24,i // 24) for i,value in enumerate(values)
                            if value & 0xC00 == 0 and (i%24,i//24) not in occupants}
                reached = {(12,21)}
                queue = collections.deque(reached)
                while queue:
                    x,y = queue.popleft()
                    for point in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                        if point in walkable and point not in reached:
                            reached.add(point); queue.append(point)
                for event in doc['coord_events']:
                    self.assertIn((event['x'],event['y']), reached)
                    self.assertEqual(values[event['y']*24+event['x']] >> 12, event['elevation'])
                for npc in doc['object_events']:
                    x,y = npc['x'],npc['y']
                    self.assertTrue(any(point in reached for point in ((x+1,y),(x-1,y),(x,y+1),(x,y-1))))

    def test_old_map_sections_and_none_keep_their_indices(self):
        raw = (ENGINE/'src/data/region_map/region_map_sections.json').read_text()
        source = json.loads(raw)['map_sections'][:209]
        changed = chapter.sections(raw)
        entries = json.loads(changed)['map_sections']
        self.assertEqual(entries[:209], source)
        self.assertEqual(entries[209]['id'], 'MAPSEC_NONE')
        self.assertEqual([e['id'] for e in entries[210:]], ['MAPSEC_'+s for s in generator.IDS])
        self.assertEqual(chapter.sections(changed), changed)

    def test_new_map_ids_append_without_reordering_old_ids(self):
        original = json.dumps({'gMapGroup_Dungeons':['AlteringCave','RiftHollow']})
        changed = chapter.groups(original)
        self.assertEqual(json.loads(changed)['gMapGroup_Dungeons'][:2], ['AlteringCave','RiftHollow'])
        self.assertEqual(chapter.groups(changed), changed)

    def test_boss_sets_have_legal_stats_and_complete_roles(self):
        teams = json.loads((ROOT/'scripts/boss_teams.json').read_text())
        self.assertEqual(len(teams), 14)
        for trainer, team in teams.items():
            with self.subTest(trainer=trainer):
                self.assertTrue(3 <= len(team) <= 6)
                self.assertEqual(len({mon['species'] for mon in team}), len(team))
                for mon in team:
                    self.assertTrue(1 <= mon['level'] <= 100)
                    self.assertEqual(len(mon['moves']),4)
                    self.assertEqual(len(set(mon['moves'])),4)
                    self.assertLessEqual(sum(mon['evs'].values()),510)
                    self.assertTrue(all(0 <= value <= 252 for value in mon['evs'].values()))
                    for field in ('ability','nature','item'):
                        self.assertTrue(mon[field])

    def test_all_trade_targets_have_a_local_evolution_alternative(self):
        count = 0
        for path in (ENGINE/'src/data/pokemon/species_info').glob('*.h'):
            text = path.read_text()
            if path.name == 'gen_5_families.h':
                text = chapter.trade_partners(text)
            for block in re.split(r'\n\s*\[SPECIES_',text):
                for target in re.findall(r'\{EVO_TRADE,\s*0,\s*(SPECIES_\w+)',block):
                    self.assertRegex(block, r'\{EVO_(?:ITEM|LEVEL),\s*[^,}]+,\s*'+target+r'\b')
                    count += 1
        self.assertGreater(count,20)

    def test_legendary_is_marked_complete_only_on_capture(self):
        text = (ENGINE/'data/maps/StormscarSanctum/scripts.inc').read_text()
        gate = text.index('goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT')
        self.assertGreater(text.index('setflag FLAG_UNUSED_0x912'),gate)
        self.assertEqual(text.count('setflag FLAG_UNUSED_0x912'),1)
        self.assertIn('FLAG_UNUSED_0x912', (ENGINE/'data/maps/StormscarSanctum/map.json').read_text())

    def test_reward_flag_follows_successful_delivery(self):
        text = (ENGINE/'data/maps/LumenCrossing/scripts.inc').read_text()
        self.assertLess(text.index('goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull'),
                        text.index('setflag FLAG_UNUSED_0x911'))

    def test_trainers_fit_existing_save_flag_capacity(self):
        text = chapter.opponents((ENGINE/'include/constants/opponents.h').read_text())
        count = int(re.search(r'TRAINERS_COUNT_EMERALD\s+(\d+)',text).group(1))
        capacity = int(re.search(r'MAX_TRAINERS_COUNT_EMERALD\s+(\d+)',text).group(1))
        self.assertEqual(count,858)
        self.assertEqual(capacity,864)
        self.assertLessEqual(count,capacity)
