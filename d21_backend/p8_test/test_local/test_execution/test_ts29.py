import unittest

from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class Ts29Test(unittest.TestCase):

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()
        ecb_fields = [("EBW001", 6), ("EBW008", 6), "EBW000", "EBW016", "EBW017", "EBW018",
                      ("EBX000", 4), ("EBX004", 4), ("EBX008", 4), ("EBX012", 4), ("EBX016", 4)]
        self.test_data.add_fields(ecb_fields, "EB0EB")

    def test_ts29_slda_1(self):
        test_data = self.tpf_server.run("TS29", self.test_data)
        self.assertEqual(6144, int(test_data.get_field("EBX008"), 16))
        self.assertEqual(00, int(test_data.get_field("EBX012"), 16))


if __name__ == "__main__":
    unittest.main()
