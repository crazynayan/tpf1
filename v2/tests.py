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

    def _common_checks(self, macro_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.macro.load(macro_name)
        self.assertListEqual(accepted_errors_list, self.macro.errors, '\n\n\n' + '\n'.join(self.macro.errors))
        self.assertTrue(self.macro.files[macro_name].data_mapped)

    def test_WA0AA(self):
        macro_name = 'WA0AA'
        self._common_checks(macro_name)
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

    def test_EB0EB(self):
        macro_name = 'EB0EB'
        self._common_checks(macro_name)
        self.assertEqual(8, self.macro.data_map['EBW000'].dsp)
        self.assertEqual(0x70, self.macro.data_map['EBT000'].dsp)
        self.assertEqual(0xD4, self.macro.data_map['EBSW01'].dsp)
        self.assertEqual(8, self.macro.data_map['CE1ERS15'].length)

    def test_SH0HS(self):
        macro_name = 'SH0HS'
        self._common_checks(macro_name)
        self.assertEqual(20, self.macro.data_map['SH0EQT'].length)
        self.assertEqual(14, self.macro.data_map['SH0CON'].dsp)

    def test_PR001W(self):
        macro_name = 'PR001W'
        accepted_errors_list = [
            "DS - Invalid data type. #PR00_X1_TYP1:DS:X'0001' PR001W",
            "Expression - Field not present in data map for no data type. #PR001WS:EQU:&SW00WRS PR001W",
            "Expression - Field not present in data map for hex data type. #PR001WI:EQU:X'&SW00WID' PR001W",
        ]
        self._common_checks(macro_name, accepted_errors_list)
        self.assertEqual(0, self.macro.data_map['PR00HDR'].dsp)
        self.assertEqual(0, self.macro.data_map['PR00REC'].dsp)
        self.assertEqual(3, self.macro.data_map['PR00ORG'].dsp)
        self.assertEqual(40, self.macro.data_map['#PR00_00_TYP_040'].dsp)
        self.assertEqual(20, self.macro.data_map['PR00E54'].dsp)
        self.assertEqual(20, self.macro.data_map['#PR00L54'].dsp)
        # self.assertEqual(219, self.macro.data_map['PR00_D4_HPFPT_GRP'].length)
