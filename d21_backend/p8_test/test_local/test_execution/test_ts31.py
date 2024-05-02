import unittest


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

    def test_ts31_basr_1(self):
        test_data = self.tpf_server.run("TS31", self.test_data)
        self.assertEqual(1, int(test_data.get_field("EBT002"), 16))


    def test_ts31_basr_2(self):
        test_data = self.tpf_server.run("TS31", self.test_data)
        self.assertEqual(1, int(test_data.get_field("EBT001"), 16))
        self.assertEqual(1, int(test_data.get_field("EBT002"), 16))


if __name__ == "__main__":
    unittest.main()
