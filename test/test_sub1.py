import unittest
from base64 import b64encode

from assembly.seg6_segment import segments
from execution.ex5_execute import Execute
from test import TestDataUTS
from utils.data_type import DataType


class Sub1Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.output = self.test_data.output
        self.i_ecb = self.test_data.add_core(['EBX000', 'EBX003', 'EBX008'], 'EB0EB')
        self.o_ecb = self.test_data.add_core_with_len([('EBX000', 3), ('EBX003', 5), ('EBX008', 3)], 'EB0EB')
        self.output.regs['R0'] = 0

    def test_b4t0(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='B4T0').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('B4T0 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('C2F4E3', self.o_ecb['EBX000'].hex)
        self.assertEqual('00017F', self.o_ecb['EBX008'].hex)
        # TODO remove once the scenario for it is present
        tnaa_bytes = DataType('X', input='00003EF8000002A40000001A00040000').to_bytes()
        self.assertEqual(tnaa_bytes, segments['SUB1'].get_constant_bytes('SUB2TNAA', 16))

    def test_00017F(self):
        self.i_ecb['EBX008'].data = b64encode(DataType('X', input='00017F').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('B4T0 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('C2F4E3', self.o_ecb['EBX000'].hex)
        self.assertEqual('00017F', self.o_ecb['EBX008'].hex)

    def test_b4t1(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='B4T1').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('B4T1 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('006F2F', self.o_ecb['EBX000'].hex)
        self.assertEqual('006F2F', self.o_ecb['EBX008'].hex)

    def test_006F2F_encode(self):
        self.i_ecb['EBX000'].data = b64encode(DataType('X', input='006F2F').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('B4T1 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('006F2F', self.o_ecb['EBX000'].hex)
        self.assertEqual('006F2F', self.o_ecb['EBX008'].hex)

    def test_A0B_encode(self):
        self.i_ecb['EBX000'].data = b64encode(DataType('C', input='A0B').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('A0B0 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('C1F0C2', self.o_ecb['EBX000'].hex)
        self.assertEqual('000001', self.o_ecb['EBX008'].hex)

    def test_000001(self):
        self.i_ecb['EBX008'].data = b64encode(DataType('X', input='000001').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('A0B0 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('C1F0C2', self.o_ecb['EBX000'].hex)
        self.assertEqual('000001', self.o_ecb['EBX008'].hex)

    def test_A1B1(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='A1B1').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('A1B1 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('006DCB', self.o_ecb['EBX000'].hex)
        self.assertEqual('006DCB', self.o_ecb['EBX008'].hex)

    def test_006DCB(self):
        self.i_ecb['EBX008'].data = b64encode(DataType('X', input='006DCB').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('A1B1 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('006DCB', self.o_ecb['EBX000'].hex)
        self.assertEqual('006DCB', self.o_ecb['EBX008'].hex)

    def test_DP83(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='DP83').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('DP83 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('01714A', self.o_ecb['EBX000'].hex)
        self.assertEqual('01714A', self.o_ecb['EBX008'].hex)

    def test_01714A(self):
        self.i_ecb['EBX008'].data = b64encode(DataType('X', input='01714A').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('DP83 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('01714A', self.o_ecb['EBX000'].hex)
        self.assertEqual('01714A', self.o_ecb['EBX008'].hex)

    def test_2Z3T(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='2Z3T').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(3, self.output.regs['R0'])

    def test_23Y7(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='23Y7').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('23Y7 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('0365C6', self.o_ecb['EBX000'].hex)
        self.assertEqual('0365C6', self.o_ecb['EBX008'].hex)

    def test_0365C6(self):
        self.i_ecb['EBX008'].data = b64encode(DataType('X', input='0365C6').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('23Y7 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('0365C6', self.o_ecb['EBX000'].hex)
        self.assertEqual('0365C6', self.o_ecb['EBX008'].hex)

    def test_4K37(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='4K37').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('4K37 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('035DA7', self.o_ecb['EBX000'].hex)
        self.assertEqual('035DA7', self.o_ecb['EBX008'].hex)

    def test_035DA7(self):
        self.i_ecb['EBX008'].data = b64encode(DataType('X', input='035DA7').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])
        self.assertEqual('4K37 ', DataType('X', input=self.o_ecb['EBX003'].hex).decode)
        self.assertEqual('035DA7', self.o_ecb['EBX000'].hex)
        self.assertEqual('035DA7', self.o_ecb['EBX008'].hex)

    def test_C4C6E6_encode(self):
        self.i_ecb['EBX000'].data = b64encode(DataType('X', input='C4C6E6').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])

    def test_F1F2F3_encode(self):
        self.i_ecb['EBX000'].data = b64encode(DataType('X', input='F1F2F3').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])

    def test_DFW(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='DFW').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])

    def test_123(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='123').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(0, self.output.regs['R0'])

    def test_error_code_1(self):
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(1, self.output.regs['R0'])

    def test_error_code_3(self):
        self.i_ecb['EBX003'].data = b64encode(DataType('C', input='-*A').to_bytes()).decode()
        self.tpf_server.run('TS22', self.test_data)
        self.assertEqual('TS22EXIT.1', self.output.last_line)
        self.assertEqual(3, self.output.regs['R0'])

    def tearDown(self) -> None:
        if 'SUB1' in self.tpf_server.DEBUG.seg_list:
            with open('trace_log.txt', 'w') as trace_log:
                trace_log.write('\n'.join([str(trace) for trace in self.tpf_server.DEBUG.get_no_hit()]))


if __name__ == '__main__':
    unittest.main()
