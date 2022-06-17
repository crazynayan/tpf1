from typing import List
from unittest import TestCase

from flask import Response
from munch import Munch

from p3_db.response import RequestType
from p3_db.test_result_model import TestResult
from p8_test.test_api import api_post, api_delete, api_get


class TestResults(TestCase):

    def setUp(self) -> None:
        self.nz04_name = "NZTestResult - NZ04 - ETA5 - Companion Validation, TPFDF Variation"
        self.nz04_deleted = False

    def tearDown(self) -> None:
        if not self.nz04_deleted:
            TestResult.objects.filter_by(name=self.nz04_name).delete()

    def test_happy_path(self):
        # Test Result Create
        body = RequestType.RESULT_CREATE
        body.name = self.nz04_name
        nz04_td_id = "YTxEmSmxTAFbpNVwr4zC"
        response: Response = api_post(f"/test_data/{nz04_td_id}/save_results", json=body.__dict__)
        self.assertEqual(200, response.status_code)
        rsp: Munch = Munch.fromDict(response.get_json())
        self.assertEqual(False, rsp.error, rsp.message or rsp.error_fields.name)
        self.assertEqual("Test Result saved successfully.", rsp.message)
        # Test Result Duplicate Add
        response: Response = api_post(f"/test_data/{nz04_td_id}/save_results", json=body.__dict__)
        self.assertEqual(200, response.status_code)
        rsp: Munch = Munch.fromDict(response.get_json())
        self.assertEqual(True, rsp.error, rsp.message or rsp.error_fields.name)
        self.assertEqual("Test Result with the same name is already saved. Use unique name.", rsp.error_fields.name)
        # Test Result Read
        response: Response = api_get(f"/test_results", query_string=body.__dict__)
        self.assertEqual(200, response.status_code)
        rsp: Munch = Munch.fromDict(response.get_json())
        self.assertEqual(0, rsp.counters.dumps)
        self.assertEqual(0, rsp.counters.messages)
        self.assertEqual(1, rsp.counters.core_variations)
        self.assertEqual(2, rsp.counters.pnr_variations)
        self.assertEqual(2, rsp.counters.tpfdf_variations)
        self.assertEqual(0, rsp.counters.file_variations)
        result: Munch = next(result for result in rsp.test_results if result.type == TestResult.RESULT)
        self.assertListEqual(["EBX000", "EBRS01", "WA0PTY"], result.core_fields)
        self.assertEqual("EBRS01", result.core_field_data[1].field)
        self.assertEqual(1, result.result_id)
        self.assertEqual("HFAX == ITIN", result.variation_name.pnr)
        self.assertEqual("HFAX == TR1G", result.variation_name.tpfdf)
        self.assertEqual("60", result.core_field_data[1].data)
        self.assertEqual(" 15765:$$CN_PGM_START.5:ENTNC:[('ETK7', None)]", result.last_node)
        core: Munch = next(result for result in rsp.test_results if result.type == TestResult.CORE)
        self.assertEqual("WA0ET6", core.field_data[0].field)
        self.assertEqual("10", core.field_data[0].data)
        pnr_list: List[Munch] = [result for result in rsp.test_results if result.type == TestResult.PNR]
        self.assertEqual("HFAX != ITIN", pnr_list[4].variation_name)
        self.assertEqual(1, pnr_list[4].variation)
        self.assertEqual("fqtv", pnr_list[2].key)
        self.assertEqual("DGHWCL", pnr_list[2].locator)
        self.assertEqual("PR00_60_FQT_FTN", pnr_list[2].field_data[1].field)
        self.assertEqual("D5D2C5F9F0F8F7", pnr_list[2].field_data[1].data)
        self.assertEqual(1, pnr_list[2].field_data[1].item_number)
        self.assertListEqual(["SSRFQTUAA2812Y20OCTDFW  ORD  0510GLD*DGHWCL RR"], pnr_list[0].text)
        # Test Result Delete
        response: Response = api_delete(f"/test_results/delete", query_string=body.__dict__)
        self.assertEqual(200, response.status_code)
        self.nz04_deleted = True
        rsp = Munch.fromDict(response.get_json())
        self.assertEqual(False, rsp.error, rsp.message or rsp.error_fields.name)
        self.assertEqual("Test Result deleted successfully.", rsp.message)
