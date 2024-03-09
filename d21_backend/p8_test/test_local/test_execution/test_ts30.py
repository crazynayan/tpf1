import unittest

from d21_backend.p1_utils.data_type import DataType
from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class Ts30Test(unittest.TestCase):

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()
        ecb_fields = [("EBW004", 4), ("EBW024", 4), ("EBW012", 2), "EBW000", "EBW016", "EBW017", "EBW018", "EBT000",
                      "EBT001", "EBT002", "EBT003", "EBT004", ("EBX000", 4), ("EBX004", 4), ("EBX008", 4),
                      ("EBX012", 4), ("EBX016", 4), ("EBX020", 4), ("EBX024", 4), ("EBX028", 3), ("EBX032", 4)]
        self.test_data.add_fields(ecb_fields, "EB0EB")

    def test_ts30_clr_1(self):
        self.test_data.regs["R0"] = 10
        self.test_data.regs["R1"] = 10
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBT000"), 16))

    def test_ts30_clr_2(self):
        self.test_data.regs["R0"] = 0x89ABCDEF
        self.test_data.regs["R1"] = 0x01234567
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(2, int(test_data.get_field("EBT000"), 16))

    def test_ts30_clr_3(self):
        self.test_data.regs["R0"] = 2309737967
        self.test_data.regs["R1"] = 2400000000
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(1, int(test_data.get_field("EBT000"), 16))

    def test_ts30_clm_1(self):
        self.test_data.regs["R1"] = 0x01234567
        self.test_data.set_field("EBX000", DataType("X", input="ABCDEF89").to_bytes())
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(1, int(test_data.get_field("EBT001"), 16))

    def test_ts30_clm_2(self):
        self.test_data.regs["R1"] = 0x20000020
        self.test_data.set_field("EBX000", DataType("X", input="20000020").to_bytes())
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(2, int(test_data.get_field("EBT001"), 16))

    def test_ts30_clm_3(self):
        self.test_data.regs["R1"] = 0x20202020
        self.test_data.set_field("EBX000", DataType("X", input="10101010").to_bytes())
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(2, int(test_data.get_field("EBT001"), 16))

    def test_ts30_mvo_1(self):
        self.test_data.set_field("EBW004", DataType("X", input="778899AC").to_bytes())
        self.test_data.set_field("EBX028", DataType("X", input="123456").to_bytes())
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual("0123456C", test_data.get_field("EBW004"))

    def test_ts30_mvo_2(self):
        self.test_data.set_field("EBW012", DataType("X", input="AABB").to_bytes())
        self.test_data.set_field("EBX028", DataType("X", input="123456").to_bytes())
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual("456B", test_data.get_field("EBW012"))

    def test_ts30_cp_1(self):
        self.test_data.set_field("EBW016", DataType("X", input="567C").to_bytes())
        self.test_data.set_field("EBX040", DataType("X", input="0000567C").to_bytes())
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBT002"), 16))

    def test_ts30_cp_2(self):
        self.test_data.set_field("EBW016", DataType("X", input="568D").to_bytes())
        self.test_data.set_field("EBX040", DataType("X", input="0000567D").to_bytes())
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(1, int(test_data.get_field("EBT002"), 16))

    def test_ts30_cp_3(self):
        self.test_data.set_field("EBW016", DataType("X", input="123C").to_bytes())
        self.test_data.set_field("EBX040", DataType("X", input="7654321D").to_bytes())
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(2, int(test_data.get_field("EBT002"), 16))

    def test_ts30_clcl_1(self):
        self.test_data.set_field("EBW000", DataType("C", input="SLU").to_bytes())
        self.test_data.set_field("EBW020", DataType("C", input="STAIN").to_bytes())
        self.test_data.regs["R3"] = 3
        self.test_data.regs["R5"] = 5
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(1, int(test_data.get_field("EBT003"), 16))  # condition code
        self.assertEqual(2, int(test_data.get_field("EBX012"), 16))  # target length
        self.assertEqual("40000004", test_data.get_field("EBX020"))  # source length

    def test_ts30_clcl_2(self):
        self.test_data.set_field("EBW000", DataType("C", input="SLUSH").to_bytes())
        self.test_data.set_field("EBW020", DataType("C", input="SLUS").to_bytes())
        self.test_data.regs["R3"] = 4
        self.test_data.regs["R5"] = 4
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBT003"), 16))  # condition code
        self.assertEqual(0, int(test_data.get_field("EBX012"), 16))  # target length
        self.assertEqual("40000000", test_data.get_field("EBX020"))  # source length

    def test_ts30_clcl_3(self):
        self.test_data.set_field("EBW000", DataType("C", input="SLUSH").to_bytes())
        self.test_data.set_field("EBW020", DataType("C", input="SLOSH").to_bytes())
        self.test_data.regs["R3"] = 6
        self.test_data.regs["R5"] = 5
        test_data = self.tpf_server.run("TS30", self.test_data)
        self.assertEqual(2, int(test_data.get_field("EBT003"), 16))
        self.assertEqual(4, int(test_data.get_field("EBX012"), 16))
        self.assertEqual("40000003", test_data.get_field("EBX020"))


if __name__ == "__main__":
    unittest.main()
