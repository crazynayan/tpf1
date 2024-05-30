import unittest

from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS
from d21_backend.p1_utils.data_type import DataType


class Ts32Test(unittest.TestCase):

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()
        ecb_fields = [("EBW000", 4), ("EBW004", 4),("EBW008", 2), ("EBW012", 2), "EBT000",
                      "EBT001", "EBT002", "EBT003", "EBT004", ("EBX000", 4), ("EBX004", 4), ("EBX008", 4),
                      ("EBX012", 2), ("EBX016", 2), ("EBX020", 4), ("EBX024", 4), ("EBX028", 3), ("EBX032", 4)]
        self.test_data.add_fields(ecb_fields, "EB0EB")

    def test_ts32_srp_1(self):
        self.test_data.set_field('EBW000', bytes([0x12, 0x34, 0x56, 0x7C]))
        test_data = self.tpf_server.run("TS32", self.test_data)
        self.assertEqual("5670000C", test_data.get_field("EBX004"))
        self.assertEqual(2, int(test_data.get_field("EBT001"), 16))

    def test_ts32_spr_2(self):
        self.test_data.set_field('EBW004', bytes([0x12, 0x35, 0x56, 0x7C]))
        test_data = self.tpf_server.run("TS32", self.test_data)
        self.assertEqual("0001235C", test_data.get_field("EBX008"))
        self.assertEqual(2, int(test_data.get_field("EBT002"), 16))

    # def test_ts31_spr_3(self):
    #     test_data = self.tpf_server.run("TS32", self.test_data)
    #     self.assertEqual("025C", test_data.get_field("EBX012"))
    #     self.assertEqual(2, int(test_data.get_field("EBT003"), 16))

    # def test_ts31_spr_4(self):
    #     test_data = self.tpf_server.run("TS32", self.test_data)
    #     self.assertEqual("003C", test_data.get_field("EBX016"))
    #     self.assertEqual(2, int(test_data.get_field("EBT004"), 16))


if __name__ == "__main__":
    unittest.main()
