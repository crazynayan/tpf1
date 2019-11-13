import unittest
from base64 import b64decode, b64encode
from typing import List

from db.pnr import Pnr
from firestore import test_data
from test.input_td import TD


class NameSuccessETAW(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        TD.state.init_run()
        self.test_data = test_data.TestData()
        aaa = test_data.Core()
        self.test_data.cores.append(aaa)
        aaa.macro_name = 'WA0AA'
        self.i_aaa = dict()
        for field in ['WA0PTY', 'WA0ETG', 'WA0US4', 'WA0UB1', 'WA0PTI']:
            field_byte = test_data.FieldByte()
            field_byte.field = field
            field_byte.data = b64encode(bytearray([00])).decode()
            aaa.field_bytes.append(field_byte)
            self.i_aaa[field] = field_byte
        # Output section
        self.test_data.outputs.append(test_data.Output())
        aaa = test_data.Core()
        self.test_data.outputs[0].cores.append(aaa)
        aaa.macro_name = 'WA0AA'
        self.o_aaa = dict()
        for field in ['WA0EXT', 'WA0PTY', 'WA0ETG', 'WA0PTI']:
            field_byte = test_data.FieldByte()
            field_byte.field = field
            aaa.field_bytes.append(field_byte)
            self.o_aaa[field] = field_byte
        ecb = test_data.Core()
        self.test_data.outputs[0].cores.append(ecb)
        ecb.macro_name = 'EB0EB'
        self.o_ecb = dict()
        for field in ['EBW015', 'EBW014', 'EBW038', 'EBSW01', 'EBW010', 'EBW016']:
            field_byte = test_data.FieldByte()
            field_byte.field = field
            ecb.field_bytes.append(field_byte)
            self.o_ecb[field] = field_byte
        ui2pf = test_data.Core()
        self.test_data.outputs[0].cores.append(ui2pf)
        ui2pf.macro_name = 'UI2PF'
        ui2pf.base_reg = 'R7'
        ui2cnn = test_data.FieldByte()
        ui2pf.field_bytes.append(ui2cnn)
        ui2cnn.field = 'UI2CNN'
        ui2cnn.length = 1
        self.test_data.outputs[0].regs['R6'] = 0

    def _setup_names(self, names: List[str]) -> None:
        for name in names:
            pnr = test_data.Pnr()
            self.test_data.pnr.append(pnr)
            pnr.key = 'name'
            pnr.data = name

    def test_single_name_wa0pty_no_match_ETAW(self) -> None:
        self._setup_names(['1ZAVERI'])
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual(bytes([0xF0, 0xF0]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([0x01]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([0x01]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([TD.ui2214]), b64decode(output.cores[2].field_bytes[0].data))  # UI2CNN

    def test_multiple_names_wa0pty_match_ETAW(self) -> None:
        self._setup_names(['45ZAVERI', '54SHAH'])
        self.i_aaa['WA0PTY'].data = b64encode(bytearray([99])).decode()
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual(bytes([0xF0, 0xF0]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([TD.ui2214]), b64decode(output.cores[2].field_bytes[0].data))  # UI2CNN

    def test_WA0NAD_ETAW(self) -> None:
        self._setup_names(['1ZAVERI', '3SHAH'])
        self.i_aaa['WA0ETG'].data = b64encode(bytearray([TD.wa0nad])).decode()
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual(bytes([0xF0, 0xF0]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([4]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([4]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([TD.ui2214]), b64decode(output.cores[2].field_bytes[0].data))  # UI2CNN
        self.assertEqual(bytes([0x00]), b64decode(output.cores[0].field_bytes[2].data))  # WA0ETG, #WA0NAD
        self.assertEqual(7, output.regs['R6'])  # Call to ETK2 with R6=7 will ensure Name association is deleted

    def test_WA0CDI_ETAW(self) -> None:
        self._setup_names(['33ZAVERI'])
        self.i_aaa['WA0US4'].data = b64encode(bytearray([TD.wa0cdi])).decode()
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual(bytes([0xF0, 0xF0]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([33]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([33]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(60, output.regs['R6'])

    def test_group_C_ETAW(self) -> None:
        self._setup_names(['C/21TOURS', '2ZAVERI'])
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual(bytes([0xF1, 0xF9]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([21]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([21]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([0xC3]), b64decode(self.o_ecb['EBW014'].data))
        self.assertEqual(bytes([0x80]), b64decode(self.o_ecb['EBW038'].data))
        self.assertEqual(bytes([0x10]), b64decode(self.o_ecb['EBSW01'].data))

    def test_group_Z_ETAW_wa0pyt_no_match(self) -> None:
        self._setup_names(['Z/25SABRE', '3SHAH'])
        self.i_aaa['WA0PTY'].data = b64encode(bytearray([3])).decode()
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual(bytes([0xF2, 0xF2]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([25]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([25]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([0xE9]), b64decode(self.o_ecb['EBW014'].data))
        self.assertEqual(bytes([0x80]), b64decode(self.o_ecb['EBW038'].data))
        self.assertEqual(bytes([0x10]), b64decode(self.o_ecb['EBSW01'].data))

    def test_group_C_not_at_start_wa0pty_history_no_match_ETAW(self):
        self._setup_names(['10ZAVERI', 'C/21TOURS', '1SHAH'])
        self.i_aaa['WA0PTY'].data = b64encode(bytearray([0xE3])).decode()  # 99 = 0x63 with bit0 on is 0xE3
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual(bytes([0xF1, 0xF0]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([0xC3]), b64decode(self.o_ecb['EBW014'].data))
        self.assertEqual(bytes([0x95]), b64decode(self.o_aaa['WA0PTY'].data))  # 0x15 with bit0 on
        self.assertEqual(bytes([0x15]), b64decode(self.o_ecb['EBW015'].data))  # 21 = 0x15

    def test_pn2_on_group_9_C_ETAW(self):
        self._setup_names(['C/99W/TOURS', '3SHAH'])
        self.i_aaa['WA0UB1'].data = b64encode(bytearray([TD.wa0pn2])).decode()
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertEqual(bytes([0xF0, 0xF6]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([9]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([9]), b64decode(self.o_ecb['EBW015'].data))

    def test_pn2_on_group_99_C_ETAW(self):
        self._setup_names(['C/999W/TOURS', '3SHAH'])
        self.i_aaa['WA0UB1'].data = b64encode(bytearray([TD.wa0pn2])).decode()
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertEqual(bytes([0xF9, 0xF6]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_ecb['EBW015'].data))

    def test_pn2_on_group_Z_wa0pty_history_match_ETAW(self):
        # T.wa0PN2 OFF behaves the same way
        self._setup_names(['Z/99W/SABRE', '3SHAH'])
        self.i_aaa['WA0UB1'].data = b64encode(bytearray([TD.wa0pn2])).decode()
        self.i_aaa['WA0PTY'].data = b64encode(bytearray([0xE3])).decode()  # 99 = 0x63 with bit0 on is 0xE3
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertEqual(bytes([0xF9, 0xF6]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([0xE3]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_ecb['EBW015'].data))

    def test_pn2_off_group_wa0pti_ETAW(self):
        self._setup_names(['C/99W/TOURS', '3SHAH'])
        self.i_aaa['WA0UB1'].data = b64encode(bytearray([0x00])).decode()
        self.i_aaa['WA0PTI'].data = b64encode(bytearray([0x03])).decode()
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual(bytes([0xF9, 0xF6]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([0x00]), b64decode(self.o_aaa['WA0PTI'].data))

    def test_infant_with_adults_ETAW(self):
        self._setup_names(['2ZAVERI', 'I/1ZAVERI'])
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual(bytes([0xF0, 0xF0]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([3]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([3]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([1]), b64decode(self.o_ecb['EBW010'].data))
        self.assertEqual(bytes([1]), b64decode(self.o_aaa['WA0PTI'].data))

    def test_infant_only_ETAW(self):
        self._setup_names(['I/3ZAVERI'])
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual(bytes([0xF0, 0xF3]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([3]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([3]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([3]), b64decode(self.o_ecb['EBW010'].data))
        self.assertEqual(bytes([3]), b64decode(self.o_aaa['WA0PTI'].data))

    def test_infant_at_start_with_less_adults_ETAW(self):
        self._setup_names(['I/33ZAVERI', '44ZAVERI', 'I/22SHAH'])
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual(bytes([0xF0, 0xF0]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([99]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([55]), b64decode(self.o_ecb['EBW010'].data))
        self.assertEqual(bytes([55]), b64decode(self.o_aaa['WA0PTI'].data))

    def test_infant_with_group_wa0pti_ETAW(self):
        self._setup_names(['Z/21SABRE', '3ZAVERI', 'I/1ZAVERI', '4SHAH', 'I/2SHAH'])
        self.i_aaa['WA0PTI'].data = b64encode(bytearray([0x03])).decode()
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual(bytes([0xF1, 0xF4]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([24]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([24]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([3]), b64decode(self.o_ecb['EBW010'].data))
        self.assertEqual(bytes([3]), b64decode(self.o_aaa['WA0PTI'].data))

    def test_infant_at_start_with_group_ETAW(self):
        self._setup_names(['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'])
        TD.state.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual(bytes([0xF1, 0xF6]), b64decode(self.o_aaa['WA0EXT'].data))
        self.assertEqual(bytes([32]), b64decode(self.o_ecb['EBW015'].data))
        self.assertEqual(bytes([32]), b64decode(self.o_aaa['WA0PTY'].data))
        self.assertEqual(bytes([7]), b64decode(self.o_ecb['EBW010'].data))
        self.assertEqual(bytes([7]), b64decode(self.o_aaa['WA0PTI'].data))
        self.assertEqual(bytes([0]), b64decode(self.o_ecb['EBW016'].data))


if __name__ == '__main__':
    unittest.main()
