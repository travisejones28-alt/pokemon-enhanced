"""Compile and execute the production save-archive codec; no model reimplementation."""
import ctypes
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BYTES = 1536
CAPACITY = 152
Buffer = ctypes.c_uint8 * BYTES


class TestMoveHistoryCodec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cc')
        if compiler is None:
            raise unittest.SkipTest('Host C compiler unavailable')
        cls.directory = tempfile.TemporaryDirectory()
        directory = Path(cls.directory.name)
        (directory / 'global.h').write_text('''#include <stdint.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32;
typedef int32_t s32; typedef uint32_t bool32;
#define TRUE 1
#define FALSE 0
''')
        binary = directory / 'history.so'
        subprocess.run([compiler, '-std=c99', '-Wall', '-Wextra', '-Werror', '-shared',
                        '-fPIC', '-I', str(directory), '-I', str(ROOT / 'engine/include'),
                        str(ROOT / 'engine/src/shattered_history_store.c'),
                        '-o', str(binary)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(binary))
        ptr = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.ShatteredHistoryOpen.argtypes = [ptr]
        cls.lib.ShatteredHistoryOpen.restype = ctypes.c_uint32
        cls.lib.ShatteredHistoryRemember.argtypes = [ptr, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16]
        cls.lib.ShatteredHistoryRemember.restype = ctypes.c_uint32
        cls.lib.ShatteredHistoryRead.argtypes = [ptr, ctypes.c_uint32, ctypes.c_uint32,
                                               ctypes.POINTER(ctypes.c_uint16), ctypes.c_uint32]
        cls.lib.ShatteredHistoryRead.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def read(self, store, pid=123, ot=456, capacity=1024):
        output = (ctypes.c_uint16 * capacity)()
        count = self.lib.ShatteredHistoryRead(store, pid, ot, output, capacity)
        return list(output[:count])

    def test_old_zero_tail_migrates_idempotently(self):
        store = Buffer()
        self.assertTrue(self.lib.ShatteredHistoryOpen(store))
        first = bytes(store)
        self.assertEqual(first[:8], b'SMH1\x01\x00\x00\x00')
        self.assertTrue(self.lib.ShatteredHistoryOpen(store))
        self.assertEqual(bytes(store), first)

    def test_erased_tail_migrates(self):
        store = Buffer(*([255] * BYTES))
        self.assertTrue(self.lib.ShatteredHistoryOpen(store))
        self.assertEqual(self.read(store), [])

    def test_persistent_round_trip_and_deduplication(self):
        store = Buffer()
        for move in (344, 237, 344, 901):
            self.assertTrue(self.lib.ShatteredHistoryRemember(store, 123, 456, move))
        reloaded = Buffer.from_buffer_copy(bytes(store))
        self.assertEqual(self.read(reloaded), [344, 237, 901])
        self.assertEqual(self.read(reloaded, capacity=1), [344])

    def test_full_identity_is_required(self):
        store = Buffer()
        self.lib.ShatteredHistoryRemember(store, 123, 456, 344)
        self.lib.ShatteredHistoryRemember(store, 123, 457, 237)
        self.assertEqual(self.read(store), [344])
        self.assertEqual(self.read(store, ot=457), [237])
        self.assertEqual(self.read(store, pid=124), [])

    def test_full_archive_never_evicts_existing_entries(self):
        store = Buffer()
        for move in range(1, CAPACITY + 1):
            self.assertTrue(self.lib.ShatteredHistoryRemember(store, 123, 456, move))
        snapshot = bytes(store)
        self.assertFalse(self.lib.ShatteredHistoryRemember(store, 123, 456, 700))
        self.assertEqual(bytes(store), snapshot)
        self.assertTrue(self.lib.ShatteredHistoryRemember(store, 123, 456, 1))
        self.assertEqual(self.read(store), list(range(1, CAPACITY + 1)))

    def test_damage_and_future_versions_are_not_reset(self):
        for index in (4, 6, 8, 16, BYTES - 1):
            store = Buffer()
            self.lib.ShatteredHistoryRemember(store, 123, 456, 344)
            store[index] ^= 1
            snapshot = bytes(store)
            self.assertFalse(self.lib.ShatteredHistoryOpen(store))
            self.assertFalse(self.lib.ShatteredHistoryRemember(store, 123, 456, 237))
            self.assertEqual(bytes(store), snapshot)

    def test_unknown_old_tail_is_not_overwritten(self):
        store = Buffer()
        store[25] = 99
        snapshot = bytes(store)
        self.assertFalse(self.lib.ShatteredHistoryOpen(store))
        self.assertEqual(bytes(store), snapshot)

    def test_invalid_move_ids_do_not_write(self):
        store = Buffer()
        for move in (0, 2048, 65535):
            self.assertFalse(self.lib.ShatteredHistoryRemember(store, 123, 456, move))
        self.assertEqual(bytes(store), bytes(BYTES))
