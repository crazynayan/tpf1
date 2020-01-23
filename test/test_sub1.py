import unittest

from assembly.seg6_segment import segments
from execution.ex5_execute import Execute
from test import TestDataUTS
from utils.data_type import DataType


class Sub1Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.output = self.test_data.output
        self.test_data.add_fields([('EBX000', 3), ('EBX003', 5), ('EBX008', 3)], 'EB0EB')
        self.output.regs['R0'] = 0

    def test_b4t0(self):
        self.test_data.set_field('EBX003', DataType('C', input='B4T0').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('B4T0 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('C2F4E3', test_data.get_field('EBX000'))
        self.assertEqual('00017F', test_data.get_field('EBX008'))
        # TODO remove once the scenario for it is present
        tnaa_bytes = DataType('X', input='00003EF8000002A40000001A00040000').to_bytes()
        self.assertEqual(tnaa_bytes, segments['SUB1'].get_constant_bytes('SUB2TNAA', 16))

    def test_00017F(self):
        self.test_data.set_field('EBX008', DataType('X', input='00017F').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('B4T0 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('C2F4E3', test_data.get_field('EBX000'))
        self.assertEqual('00017F', test_data.get_field('EBX008'))

    def test_b4t1(self):
        self.test_data.set_field('EBX003', DataType('C', input='B4T1').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('B4T1 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('006F2F', test_data.get_field('EBX000'))
        self.assertEqual('006F2F', test_data.get_field('EBX008'))

    def test_006F2F_encode(self):
        self.test_data.set_field('EBX000', DataType('X', input='006F2F').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('B4T1 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('006F2F', test_data.get_field('EBX000'))
        self.assertEqual('006F2F', test_data.get_field('EBX008'))

    def test_A0B_encode(self):
        self.test_data.set_field('EBX000', DataType('C', input='A0B').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('A0B0 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('C1F0C2', test_data.get_field('EBX000'))
        self.assertEqual('000001', test_data.get_field('EBX008'))

    def test_000001(self):
        self.test_data.set_field('EBX008', DataType('X', input='000001').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('A0B0 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('C1F0C2', test_data.get_field('EBX000'))
        self.assertEqual('000001', test_data.get_field('EBX008'))

    def test_A1B1(self):
        self.test_data.set_field('EBX003', DataType('C', input='A1B1').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('A1B1 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('006DCB', test_data.get_field('EBX000'))
        self.assertEqual('006DCB', test_data.get_field('EBX008'))

    def test_006DCB(self):
        self.test_data.set_field('EBX008', DataType('X', input='006DCB').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('A1B1 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('006DCB', test_data.get_field('EBX000'))
        self.assertEqual('006DCB', test_data.get_field('EBX008'))

    def test_DP83(self):
        self.test_data.set_field('EBX003', DataType('C', input='DP83').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('DP83 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('01714A', test_data.get_field('EBX000'))
        self.assertEqual('01714A', test_data.get_field('EBX008'))

    def test_01714A(self):
        self.test_data.set_field('EBX008', DataType('X', input='01714A').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('DP83 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('01714A', test_data.get_field('EBX000'))
        self.assertEqual('01714A', test_data.get_field('EBX008'))

    def test_2Z3T(self):
        self.test_data.set_field('EBX003', DataType('C', input='2Z3T').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(3, test_data.output.regs['R0'])

    def test_23Y7(self):
        self.test_data.set_field('EBX003', DataType('C', input='23Y7').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('23Y7 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('0365C6', test_data.get_field('EBX000'))
        self.assertEqual('0365C6', test_data.get_field('EBX008'))

    def test_0365C6(self):
        self.test_data.set_field('EBX008', DataType('X', input='0365C6').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('23Y7 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('0365C6', test_data.get_field('EBX000'))
        self.assertEqual('0365C6', test_data.get_field('EBX008'))

    def test_4K37(self):
        self.test_data.set_field('EBX003', DataType('C', input='4K37').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('4K37 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('035DA7', test_data.get_field('EBX000'))
        self.assertEqual('035DA7', test_data.get_field('EBX008'))

    def test_035DA7(self):
        self.test_data.set_field('EBX008', DataType('X', input='035DA7').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])
        self.assertEqual('4K37 ', DataType('X', input=test_data.get_field('EBX003')).decode)
        self.assertEqual('035DA7', test_data.get_field('EBX000'))
        self.assertEqual('035DA7', test_data.get_field('EBX008'))

    def test_C4C6E6_encode(self):
        self.test_data.set_field('EBX000', DataType('X', input='C4C6E6').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])

    def test_F1F2F3_encode(self):
        self.test_data.set_field('EBX000', DataType('X', input='F1F2F3').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])

    def test_DFW(self):
        self.test_data.set_field('EBX003', DataType('C', input='DFW').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])

    def test_123(self):
        self.test_data.set_field('EBX003', DataType('C', input='123').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(0, test_data.output.regs['R0'])

    def test_error_code_1(self):
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(1, test_data.output.regs['R0'])

    def test_error_code_3(self):
        self.test_data.set_field('EBX003', DataType('C', input='-*A').to_bytes())
        test_data = self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', test_data.output.last_line)
        self.assertEqual(3, test_data.output.regs['R0'])

    def tearDown(self) -> None:
        pass
        # if 'SUB1' in self.tpf_server.DEBUG.seg_list:
        #     with open('trace_log.txt', 'w') as trace_log:
        #         trace_log.write('\n'.join([str(trace) for trace in self.tpf_server.DEBUG.get_no_hit()]))


if __name__ == '__main__':
    unittest.main()
