import unittest
from base64 import b64encode, b64decode
from typing import List, Dict

from execution.ex5_execute import Execute
from firestore import test_data
from firestore.test_data import FieldByte, Pnr


class NameGeneral(unittest.TestCase):

    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = test_data.TestData()
        aaa = test_data.Core()
        self.test_data.cores.append(aaa)
        aaa.macro_name = 'WA0AA'
        self.i_aaa = dict()
        for field in ['WA0PTY', 'WA0ETG', 'WA0US4', 'WA0UB1', 'WA0PTI', 'WA0ET3', 'WA0ET4', 'WA0ET6', 'WA0ASC',
                      'WA0USE', 'WA0ET2', 'WA0XX3', 'WA0US3']:
            field_byte = test_data.FieldByte()
            field_byte.field = field
            field_byte.data = b64encode(bytearray([00])).decode()
            aaa.field_bytes.append(field_byte)
            self.i_aaa[field] = field_byte
        # === OUTPUT ====
        self.test_data.outputs.append(test_data.Output())
        self.output = self.test_data.outputs[0]
        # AAA
        aaa = test_data.Core()
        self.test_data.outputs[0].cores.append(aaa)
        aaa.macro_name = 'WA0AA'
        self.o_aaa = dict()
        for field in ['WA0EXT', 'WA0PTY', 'WA0ETG', 'WA0PTI', 'WA0ET4', 'WA0ET5']:
            field_byte = test_data.FieldByte()
            field_byte.field = field
            aaa.field_bytes.append(field_byte)
            self.o_aaa[field] = field_byte
        # ECB
        ecb = test_data.Core()
        self.test_data.outputs[0].cores.append(ecb)
        ecb.macro_name = 'EB0EB'
        self.o_ecb = dict()
        for field in ['EBW015', 'EBW014', 'EBW038', 'EBSW01', 'EBW010', 'EBW016', 'EBRS01', 'EBX000', 'EBX004',
                      'EBX008', 'EBX012']:
            field_byte = test_data.FieldByte()
            field_byte.field = field
            field_byte.length = 4 if field[:3] == 'EBX' else 1
            ecb.field_bytes.append(field_byte)
            self.o_ecb[field] = field_byte
        # UI2PF
        ui2pf = test_data.Core()
        self.test_data.outputs[0].cores.append(ui2pf)
        ui2pf.macro_name = 'UI2PF'
        ui2pf.base_reg = 'R7'
        self.ui2cnn = test_data.FieldByte()
        ui2pf.field_bytes.append(self.ui2cnn)
        self.ui2cnn.field = 'UI2CNN'
        self.ui2cnn.length = 1
        self.ui2inc = test_data.FieldByte()
        ui2pf.field_bytes.append(self.ui2inc)
        self.ui2inc.field = 'UI2INC'
        self.ui2inc.length = 3
        # Registers
        self.test_data.outputs[0].regs['R6'] = 0
        self.test_data.outputs[0].regs['R1'] = 0
        self.test_data.outputs[0].regs['R15'] = 0

    def _setup_names(self, names: List[str]) -> None:
        for name in names:
            pnr = test_data.Pnr()
            self.test_data.pnr.append(pnr)
            pnr.key = 'name'
            pnr.data = name

    def _o_aaa(self, field) -> str:
        return b64decode(self.o_aaa[field].data).hex().upper()

    def _o_ecb(self, field) -> str:
        return b64decode(self.o_ecb[field].data).hex().upper()

    def _setup_fqtv(self, locator: str, fqtv_list: List[Dict[str, bytearray]]):
        for fqtv in fqtv_list:
            pnr = Pnr()
            pnr.key = 'fqtv'
            pnr.locator = locator
            pnr.field_bytes = self._convert_to_field_bytes(fqtv)
            self.test_data.pnr.append(pnr)
        return

    @staticmethod
    def _convert_to_field_bytes(field_byte_array: Dict[str, bytearray]) -> List[FieldByte]:
        field_bytes = list()
        for field, byte_array in field_byte_array.items():
            field_byte = FieldByte()
            field_byte.field = field
            field_byte.data = b64encode(byte_array).decode()
            field_bytes.append(field_byte)
        return field_bytes
