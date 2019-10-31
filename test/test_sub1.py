import unittest

from test.input_td import TD
from utils.data_type import DataType


class Sub1Test(unittest.TestCase):
    def setUp(self) -> None:
        TD.state.init_run()

    def test_b4t0(self):
        TD.state.setup.ecb['EBX003'] = DataType('C', input='B4T0').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('B4T0 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0xC2F4E3, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x017F, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_00017F(self):
        TD.state.setup.ecb['EBX008'] = DataType('X', input='00017F').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('B4T0 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0xC2F4E3, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x017F, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_b4t1(self):
        TD.state.setup.ecb['EBX003'] = DataType('C', input='B4T1').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('B4T1 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x006F2F, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x006F2F, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_006F2F_encode(self):
        TD.state.setup.ecb['EBX000'] = DataType('X', input='006F2F').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('B4T1 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x006F2F, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x006F2F, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_A0B_encode(self):
        TD.state.setup.ecb['EBX000'] = DataType('C', input='A0B').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('A0B0 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0xC1F0C2, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x000001, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_000001(self):
        TD.state.setup.ecb['EBX008'] = DataType('X', input='000001').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('A0B0 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0xC1F0C2, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x000001, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_A1B1(self):
        TD.state.setup.ecb['EBX003'] = DataType('C', input='A1B1').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('A1B1 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x006DCB, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x006DCB, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_006DCB(self):
        TD.state.setup.ecb['EBX008'] = DataType('X', input='006DCB').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('A1B1 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x006DCB, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x006DCB, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_DP83(self):
        TD.state.setup.ecb['EBX003'] = DataType('C', input='DP83').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('DP83 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x01714A, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x01714A, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_01714A(self):
        TD.state.setup.ecb['EBX008'] = DataType('X', input='01714A').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('DP83 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x01714A, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x01714A, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_2Z3T(self):
        TD.state.setup.ecb['EBX003'] = DataType('C', input='2Z3T').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(3, TD.state.regs.R0)

    def test_23Y7(self):
        TD.state.setup.ecb['EBX003'] = DataType('C', input='23Y7').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('23Y7 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x0365C6, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x0365C6, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_0365C6(self):
        TD.state.setup.ecb['EBX008'] = DataType('X', input='0365C6').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('23Y7 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x0365C6, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x0365C6, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_4K37(self):
        TD.state.setup.ecb['EBX003'] = DataType('C', input='4K37').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('4K37 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x035DA7, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x035DA7, TD.state.vm.get_value(TD.ebx000 + 8, 3))

    def test_035DA7(self):
        TD.state.setup.ecb['EBX008'] = DataType('X', input='035DA7').to_bytes()
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual('4K37 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebx000 + 3, 5)).decode)
        self.assertEqual(0x035DA7, TD.state.vm.get_unsigned_value(TD.ebx000, 3))
        self.assertEqual(0x035DA7, TD.state.vm.get_value(TD.ebx000 + 8, 3))


# noinspection PyPep8Naming
def tearDownModule():
    if 'SUB1' in TD.state.DEBUG.seg_list:
        with open('trace_log.txt', 'w') as trace_log:
            trace_log.write('\n'.join([str(trace) for trace in TD.state.DEBUG.get_no_hit()]))
    return


if __name__ == '__main__':
    unittest.main()
