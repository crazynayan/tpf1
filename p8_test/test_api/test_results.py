from typing import List
from unittest import TestCase

from munch import Munch

from p3_db.test_data import TestData
from p3_db.test_result_model import TestResult
from p8_test.test_api import api_post, api_delete, api_get


class TestResults(TestCase):

    def setUp(self) -> None:
        self.nz04_name = "NZTestResult - NZ04 - ETA5 - Companion Validation, TPFDF Variation"
        self.td_deleted = True
        self.nz04_td_id = "YTxEmSmxTAFbpNVwr4zC"
        self.nz07_name = "NZTestResult - NZ07 - ETAJ - Validate PNR Owner PCC"
        self.nz07_td_id = "u6999F91vQtV0K56LsMF"

    def tearDown(self) -> None:
        if not self.td_deleted:
            TestResult.objects.filter("name", TestResult.objects.IN, [self.nz04_name, self.nz07_name]).delete()

    def test_happy_path(self):
        # Test Result Create
        body = Munch()
        body.name = self.nz04_name
        rsp: Munch = api_post(f"/test_data/{self.nz04_td_id}/save_results", json=body.__dict__)
        self.assertEqual(False, rsp.error, rsp.message or rsp.error_fields.name)
        self.assertEqual("Test Result saved successfully.", rsp.message)
        self.td_deleted = False
        # Test Result Duplicate Add
        rsp: Munch = api_post(f"/test_data/{self.nz04_td_id}/save_results", json=body.__dict__)
        self.assertEqual(True, rsp.error, rsp.message or rsp.error_fields.name)
        self.assertEqual("Test Result with the same name is already saved. Use unique name.", rsp.error_fields.name)
        # Test Result Read
        rsp: Munch = api_get(f"/test_results", query_string=body.__dict__)
        self.assertEqual(0, rsp.counters.dumps)
        self.assertEqual(0, rsp.counters.messages)
        self.assertEqual(1, rsp.counters.core_variations)
        self.assertEqual(2, rsp.counters.pnr_variations)
        self.assertEqual(2, rsp.counters.tpfdf_variations)
        self.assertEqual(0, rsp.counters.file_variations)
        result: Munch = rsp.results[0]
        self.assertListEqual(["EBX000", "EBRS01", "WA0PTY"], result.core_fields)
        self.assertListEqual(list(), result.pnr_field_data)
        self.assertEqual("EBRS01", result.core_field_data[1].field)
        self.assertEqual(1, result.result_id)
        self.assertEqual("HFAX == ITIN", result.variation_name.pnr)
        self.assertEqual("HFAX == TR1G", result.variation_name.tpfdf)
        self.assertEqual("60", result.core_field_data[1].data)
        self.assertEqual(" 15765:$$CN_PGM_START.5:ENTNC:[('ETK7', None)]", result.last_node)
        core: Munch = rsp.cores[0]
        self.assertEqual("WA0ET6", core.field_data[0].field)
        self.assertEqual("10", core.field_data[0].data)
        pnr_list: List[Munch] = rsp.pnr
        self.assertEqual("HFAX != ITIN", pnr_list[4].variation_name)
        self.assertEqual(1, pnr_list[4].variation)
        self.assertEqual("fqtv", pnr_list[2].key)
        self.assertEqual("DGHWCL", pnr_list[2].locator)
        self.assertEqual("PR00_60_FQT_FTN", pnr_list[2].field_data[1].field)
        self.assertEqual("D5D2C5F9F0F8F7", pnr_list[2].field_data[1].data)
        self.assertEqual(1, pnr_list[2].field_data[1].item_number)
        self.assertListEqual(["SSRFQTUAA2812Y20OCTDFW  ORD  0510GLD*DGHWCL RR"], pnr_list[0].text)
        tpfdf: Munch = rsp.tpfdf[0]
        self.assertEqual("HFAX == TR1G", tpfdf.variation_name)
        self.assertEqual("TR1GAA", tpfdf.macro_name)
        self.assertEqual("40", tpfdf.key)
        self.assertEqual("TR1G_40_OCC", tpfdf.field_data[0].field)
        self.assertEqual("C1C1", tpfdf.field_data[0].data)
        self.assertEqual("TR1G_40_PTI", tpfdf.field_data[4].field)
        self.assertEqual("80", tpfdf.field_data[4].data)
        # Test Update Comment
        comment_body = Munch()
        comment_body.comment_type = "user_comment"
        comment_body.comment = "Some test user comment."
        rsp: Munch = api_post(f"/test_results/{result.id}/comment", json=comment_body.__dict__)
        self.assertEqual(False, rsp.error)
        self.assertEqual("Comment updated successfully.", rsp.message)
        comment_body.comment_type = "pnr_comment"
        comment_body.comment = "Some test pnr comment."
        rsp: Munch = api_post(f"/test_results/{result.id}/comment", json=comment_body.__dict__)
        self.assertEqual(False, rsp.error)
        self.assertEqual("Comment updated successfully.", rsp.message)
        comment_body.comment_type = "core_comment"
        comment_body.comment = "Some test core comment."
        rsp: Munch = api_post(f"/test_results/{result.id}/comment", json=comment_body.__dict__)
        self.assertEqual(False, rsp.error)
        self.assertEqual("Comment updated successfully.", rsp.message)
        comment_body.comment_type = "general_comment"
        comment_body.comment = "A common comment."
        rsp: Munch = api_post(f"/test_results/{result.id}/comment", json=comment_body.__dict__)
        self.assertEqual(False, rsp.error)
        self.assertEqual("Comment updated successfully.", rsp.message)
        comment_body.comment_type = "core_comment"
        comment_body.comment = ""  # Test removing comment
        rsp: Munch = api_post(f"/test_results/{result.id}/comment", json=comment_body.__dict__)
        self.assertEqual(False, rsp.error)
        self.assertEqual("Comment updated successfully.", rsp.message)
        rsp: Munch = api_get(f"/test_results", query_string=body.__dict__)
        result: Munch = rsp.results[0]
        self.assertEqual("A common comment.", result.general_comment)
        self.assertEqual("Some test user comment.", result.user_comment)
        self.assertEqual("Some test pnr comment.", result.pnr_comment)
        self.assertEqual("", result.core_comment)
        # Test Result Delete
        rsp: Munch = api_delete(f"/test_results/delete", query_string=body.__dict__)
        self.td_deleted = True
        self.assertEqual(False, rsp.error, rsp.message or rsp.error_fields.name)
        self.assertEqual("Test Result deleted successfully.", rsp.message)

    def test_read_file(self):
        body = Munch()
        body.name = self.nz07_name
        rsp: Munch = api_post(f"/test_data/{self.nz07_td_id}/save_results", json=body.__dict__)
        self.assertEqual(False, rsp.error, rsp.message or rsp.error_fields.name)
        self.assertEqual("Test Result saved successfully.", rsp.message)
        self.td_deleted = False
        # Test Result Read
        rsp: Munch = api_get(f"/test_results", query_string=body.__dict__)
        self.assertEqual(16, len(rsp.results))
        file: Munch = rsp.files[0]
        self.assertEqual("TJ0TJ", file.fixed_macro_name)
        self.assertEqual("E3D1", file.fixed_rec_id)
        self.assertEqual(94, file.fixed_type)
        self.assertEqual(383, file.fixed_ordinal)
        self.assertEqual("IY1IY", file.pool_macro_name)
        self.assertEqual("C9E8", file.pool_rec_id)
        self.assertEqual("TJ0ATH", file.pool_fixed_label)
        self.assertEqual("IY1ATH", file.pool_item_label)
        self.assertEqual("IY1CTR", file.pool_item_count_label)
        self.assertEqual(False, file.pool_item_adjust)
        self.assertEqual(1, file.pool_item_repeat)
        self.assertEqual("IY9AON", file.pool_item_field_data[0].field)
        self.assertEqual("00006F2F", file.pool_item_field_data[0].data)
        self.assertEqual("IY9AGY", file.pool_item_field_data[1].field)
        self.assertEqual("00", file.pool_item_field_data[1].data)

    def test_read_errors(self):
        body = Munch()
        body.name = "Some invalid name which is not present!! 12345"
        rsp: Munch = api_get(f"/test_results", query_string=body.__dict__)
        self.assertListEqual(list(), rsp.headers)
        # If an invalid parameter is passed then it will return header of all test results
        body = Munch()
        body.some_invalid_param = "Some invalid name which is not present!! 12345"
        rsp: Munch = api_get(f"/test_results", query_string=body.__dict__)
        if not rsp.headers:
            self.assertListEqual(list(), rsp.headers)
        else:
            self.assertNotEqual(list(), rsp.headers)

    def test_create_errors_invalid_body(self):
        rsp: Munch = api_post(f"/test_data/{self.nz04_td_id}/save_results", json=dict())
        self.assertTrue(rsp.error)
        self.assertEqual("Invalid request. Request cannot be empty.", rsp.message)
        rsp: Munch = api_post(f"/test_data/{self.nz04_td_id}/save_results", json={"com": "error"})
        self.assertTrue(rsp.error)
        self.assertEqual("Invalid request. Only 1 field (name) allowed and it is mandatory.", rsp.message)
        rsp: Munch = api_post(f"/test_data/{self.nz04_td_id}/save_results", json={"name": ["error"]})
        self.assertTrue(rsp.error)
        self.assertEqual("Invalid data type.", rsp.error_fields.name)

    def test_create_errors_others(self):
        td_dummy = TestData()
        td_dummy.name = "NZTestResults - Dummy for testing. 12345"
        td_dummy.seg_name = "Invalid segment"
        td_id = td_dummy.create()
        rsp: Munch = api_post(f"/test_data/{td_id}/save_results", json={"name": ""})
        self.assertTrue(rsp.error)
        self.assertEqual("Name of the Test Result cannot be blank.", rsp.error_fields.name)
        self.assertEqual("The start seg of the test data does not exists. This test data cannot be executed.",
                         rsp.message)

    def test_comment_errors_invalid_body(self):
        rsp: Munch = api_post(f"/test_results/abcd/comment", json={"com": "error"})
        self.assertEqual(True, rsp.error)
        self.assertEqual("Invalid request. Only 2 fields (comment_type, comment) allowed and they are mandatory.",
                         rsp.message)

    def test_comment_errors_others(self):
        comment_body = Munch()
        comment_body.comment_type = "Some invalid comment type"
        comment_body.comment = "Some test user comment."
        rsp: Munch = api_post(f"/test_results/abcd/comment", json=comment_body.__dict__)
        self.assertEqual(True, rsp.error)
        self.assertEqual("Invalid comment type.", rsp.error_fields.comment_type)
        self.assertEqual("Saved result not found for this variation.", rsp.message)

    def test_delete_error(self):
        body = Munch()
        body.name = "Some invalid name which is not present!! 12345"
        rsp: Munch = api_delete(f"/test_results/delete", query_string=body.__dict__)
        self.assertEqual(True, rsp.error)
        self.assertEqual("Test Result with this name not found.", rsp.message)
        # If an invalid param is passed then it will NOT delete and return the same error
        body = Munch()
        body.some_invalid_param = "Some invalid name which is not present!! 12345"
        rsp: Munch = api_delete(f"/test_results/delete", query_string=body.__dict__)
        self.assertEqual(True, rsp.error)
        self.assertEqual("Test Result with this name not found.", rsp.message)
