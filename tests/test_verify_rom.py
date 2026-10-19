"""ROM header validation regression tests; a synthetic dummy ROM is used, not copyrighted data."""

import unittest

from scripts.verify_rom import check_rom


def make_test_rom():
    rom = bytearray(1024 * 1024)
    rom[0xA0:0xAC] = b"SHATTERED" + b"\x00" * 3
    rom[0xAC:0xB0] = b"BSRE"
    rom[0xBD] = (-(sum(rom[0xA0:0xBD]) + 0x19)) & 0xFF
    return rom


class TestRomVerification(unittest.TestCase):
    def test_valid_header(self):
        check_rom(bytes(make_test_rom()))

    def test_bad_title(self):
        rom = make_test_rom()
        rom[0xA0] = ord("X")
        with self.assertRaisesRegex(ValueError, "title"):
            check_rom(bytes(rom))

    def test_bad_game_code(self):
        rom = make_test_rom()
        rom[0xAC] = ord("X")
        with self.assertRaisesRegex(ValueError, "game code"):
            check_rom(bytes(rom))

    def test_bad_checksum(self):
        rom = make_test_rom()
        rom[0xBD] ^= 0xFF
        with self.assertRaisesRegex(ValueError, "checksum"):
            check_rom(bytes(rom))

    def test_wrong_size(self):
        with self.assertRaisesRegex(ValueError, "size"):
            check_rom(bytes(make_test_rom()[:1024]))


if __name__ == "__main__":
    unittest.main()
