import unittest
from v2.assembler import Macro


class MacroTest(unittest.TestCase):
    NUMBER_OF_FILES = 4

    def setUp(self) -> None:
        self.macro = Macro()

    def test_files(self):
        self.assertTrue('WA0AA' in self.macro.files)
        self.assertTrue('EB0EB' in self.macro.files)
        self.assertFalse('eta5' in self.macro.files)
        self.assertEqual(self.NUMBER_OF_FILES, len(self.macro.files), 'Update number of files in MacroTest')

    def test_WA0AA(self):
        macro_name = 'WA0AA'
        self.macro.load(macro_name)
        self.assertTrue(self.macro.files[macro_name].data_mapped)
        self.assertEqual(100, self.macro.data_map['WA0OUT'].length)
        self.assertEqual(0x60, self.macro.data_map['WA0OUT'].dsp)
        self.assertEqual(0x2c, self.macro.data_map['WA0TTO'].dsp)
        self.assertEqual(0x180, self.macro.data_map['WA0ORG'].dsp)
        self.assertEqual(0x182, self.macro.data_map['WA0ITC'].dsp)
        self.assertEqual(148, self.macro.data_map['WA0ITS'].length)
        self.assertEqual(11, self.macro.data_map['WA2TSD'].length)
        self.assertEqual(0x218, self.macro.data_map['WA2TSD'].dsp)
        self.assertEqual(0x218, self.macro.data_map['WA2TAG'].dsp)
        self.assertEqual(0x10, self.macro.data_map['#WA0TTY'].dsp)
        self.assertEqual(0x3c6, self.macro.data_map['WA2LS3'].dsp)
        self.assertEqual(0x314, self.macro.data_map['WA2VFD'].dsp)
        self.assertEqual(178, self.macro.data_map['WA2VFD'].length)
        self.assertEqual(0x41e, self.macro.data_map['WA0AAZ'].dsp)
        self.assertEqual(48, self.macro.data_map['WA2AOF'].length)

    def test_SH0HS(self):
        macro_name = 'SH0HS'
        self.macro.load(macro_name)
        self.assertTrue(self.macro.files[macro_name].data_mapped)
        self.assertEqual(20, self.macro.data_map['SH0EQT'].length)
        self.assertEqual(14, self.macro.data_map['SH0CON'].dsp)

