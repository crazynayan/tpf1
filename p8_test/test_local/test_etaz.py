import unittest

from p1_utils.data_type import DataType
from p3_db.pnr import RCVD_FROM
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class EtazTest(unittest.TestCase):
    DEBUG_DATA = list()
    SEGMENT = "ETKF"

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.output.debug = [self.SEGMENT]
        self.output = None

    def tearDown(self) -> None:
        if not self.output or not self.output.debug:
            return
        for debug_line in self.output.debug:
            if debug_line in self.DEBUG_DATA:
                continue
            self.DEBUG_DATA.append(debug_line)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"{cls.SEGMENT} LOC = {len(cls.DEBUG_DATA)}")

    def test_etaz_vanilla(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAZ1950.1", test_data.output.last_line, test_data.output.last_node)
        self.assertIn("NEED RECEIVED FROM FIELD - USE 6", test_data.output.messages)
        self.assertEqual(list(), test_data.output.dumps)
        self.output = test_data.output

    def test_etaz_rcvd_from(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("FMSG0100", test_data.output.last_line, test_data.output.last_node)
        self.assertIn("NEED PHONE FIELD - USE 9", test_data.output.messages)
        self.output = test_data.output
