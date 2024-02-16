import unittest
from d21_backend.p1_utils.data_type import DataType
from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class Ts29Test(unittest.TestCase):

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()
        ecb_fields = [("EBW001", 6), ("EBW008", 6), "EBW000", "EBW016", "EBW017", "EBW018", "EBT000", "EBT001",
                      "EBT002", "EBT003", ("EBX000", 4), ("EBX004", 4), ("EBX008", 4), ("EBX012", 4), ("EBX016", 4),
                      ("EBX020", 4), ("EBX024", 4), ("EBX028", 4), ("EBX056", 4)]
        self.test_data.add_fields(ecb_fields, "EB0EB")

    def test_ts29_slda_1(self):
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(6144, int(test_data.get_field("EBX008"), 16))
        self.assertEqual(00, int(test_data.get_field("EBX012"), 16))

    def test_ts29_alr_1(self):
        # CC1 GETS SET
        self.test_data.regs["R5"] = 80
        self.test_data.regs["R6"] = 80
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(160, int(test_data.get_field("EBX020"), 16))
        self.assertEqual(1, int(test_data.get_field("EBT000"), 16))

    def test_ts29_alr_2(self):
        # CC0 GETS SET
        self.test_data.regs["R5"] = 0000
        self.test_data.regs["R6"] = 0000
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBX020"), 16))
        self.assertEqual(0, int(test_data.get_field("EBT000"), 16))

    def test_ts29_alr_3(self):
        # CC2 GETS SET
        self.test_data.regs["R5"] = 4294967295
        self.test_data.regs["R6"] = 1
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBX020"), 16))
        self.assertEqual(2, int(test_data.get_field("EBT000"), 16))

    def test_ts29_alr_4(self):
        # CC3 GETS SET
        self.test_data.regs["R5"] = 2147483648
        self.test_data.regs["R6"] = 2214592512
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(67108864, int(test_data.get_field("EBX020"), 16))
        self.assertEqual(3, int(test_data.get_field("EBT000"), 16))

    def test_ts29_alr_5(self):
        # CC3 GETS SET
        self.test_data.regs["R5"] = -10
        self.test_data.regs["R6"] = -3
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(4294967283, int(test_data.get_field("EBX020"), 16))
        self.assertEqual(3, int(test_data.get_field("EBT000"), 16))

    def test_ts29_al_1(self):
        # CC3 GETS SET
        self.test_data.regs["R6"] = 2147483648
        self.test_data.set_field("EBW000", DataType("F", input="2214592512").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(67108864, int(test_data.get_field("EBX024"), 16))
        self.assertEqual(3, int(test_data.get_field("EBT001"), 16))

    def test_ts29_al_2(self):
        # CC1 GETS SET
        self.test_data.regs["R6"] = 80
        self.test_data.set_field("EBW000", DataType("F", input="80").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(160, int(test_data.get_field("EBX024"), 16))
        self.assertEqual(1, int(test_data.get_field("EBT001"), 16))

    def test_ts29_al_3(self):
        # CC2 GETS SET
        self.test_data.regs["R6"] = 4294967295
        self.test_data.set_field("EBW000", DataType("F", input="1").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBX024"), 16))
        self.assertEqual(2, int(test_data.get_field("EBT001"), 16))

    def test_ts29_al_4(self):
        # CC0 GETS SET
        self.test_data.regs["R6"] = 00
        self.test_data.set_field("EBW000", DataType("F", input="00").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBX024"), 16))
        self.assertEqual(0, int(test_data.get_field("EBT001"), 16))

    def test_ts29_al_5(self):
        # CC0 GETS SET
        self.test_data.regs["R6"] = -10
        self.test_data.set_field("EBW000", DataType("F", input="-3").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(4294967283, int(test_data.get_field("EBX024"), 16))
        self.assertEqual(3, int(test_data.get_field("EBT001"), 16))
    def test_ts29_slr_1(self):
        # CC3 GETS SET
        self.test_data.regs["R7"] = 5
        self.test_data.regs["R1"] = 3
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(2, int(test_data.get_field("EBX028"), 16))
        self.assertEqual(3, int(test_data.get_field("EBT002"), 16))

    def test_ts29_slr_2(self):
        # CC2 GETS SET
        self.test_data.regs["R7"] = 6
        self.test_data.regs["R1"] = 6
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBX028"), 16))
        self.assertEqual(2, int(test_data.get_field("EBT002"), 16))

    def test_ts29_slr_3(self):
        # CC1 GETS SET
        self.test_data.regs["R7"] = 0
        self.test_data.regs["R1"] = 3
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(4294967293, int(test_data.get_field("EBX028"), 16))
        self.assertEqual(1, int(test_data.get_field("EBT002"), 16))

    def test_ts29_slr_4(self):
        # CC1 GETS SET
        self.test_data.regs["R7"] = -10
        self.test_data.regs["R1"] = -3
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(4294967289, int(test_data.get_field("EBX028"), 16))
        self.assertEqual(1, int(test_data.get_field("EBT002"), 16))

    def test_ts29_sl_1(self):
        # CC3 GETS SET
        self.test_data.regs["R1"] = 5
        self.test_data.set_field("EBW000", DataType("F", input="3").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(2, int(test_data.get_field("EBX004"), 16))
        self.assertEqual(3, int(test_data.get_field("EBT003"), 16))

    def test_ts29_sl_2(self):
        # CC2 GETS SET
        self.test_data.regs["R1"] = 0
        self.test_data.set_field("EBW000", DataType("F", input="0").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(0, int(test_data.get_field("EBX004"), 16))
        self.assertEqual(2, int(test_data.get_field("EBT003"), 16))

    def test_ts29_sl_3(self):
        # CC1 GETS SET#
        self.test_data.regs["R1"] = 2
        self.test_data.set_field("EBW000", DataType("F", input="3").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(4294967295, int(test_data.get_field("EBX004"), 16))
        self.assertEqual(1, int(test_data.get_field("EBT003"), 16))

    def test_ts29_sl_4(self):
        # CC1 GETS SET#
        self.test_data.regs["R1"] = -10
        self.test_data.set_field("EBW000", DataType("F", input="-3").to_bytes())
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(4294967289, int(test_data.get_field("EBX004"), 16))
        self.assertEqual(1, int(test_data.get_field("EBT003"), 16))


if __name__ == "__main__":
    unittest.main()
