from unittest import TestCase

from munch import Munch

from d21_backend.p8_test.test_api import api_post_using_general_domain_auth, api_post


class TestProfiler(TestCase):

    def setUp(self):
        self.body: Munch = Munch()

    def test_profiler_api(self):
        self.body.seg_name = "TSJ1"
        self.body.test_data_ids = ["wgCfTpeA1prwHVU684OC"]
        rsp: Munch = api_post_using_general_domain_auth("/profiler/run", json=self.body.__dict__)
        self.assertEqual("Profiler ran successfully.", rsp.message, rsp.error_fields)
        print(f"Documentation coverage: {rsp.data.documentation_coverage}")
        for instruction_path in rsp.data.missing_instruction_paths:
            print(f"{instruction_path.label:10}:{instruction_path.command:6}:{instruction_path.next_label}:{instruction_path.hit_counter}"
                  f":{instruction_path.operand}")

    def test_profiler_api_eta5(self):
        self.body.seg_name = "ETA5"
        self.body.test_data_ids = ["8lHL7BUIVuYdZ8rMCI1Y", "4BGZntTgPVKbJWcSpWd0", "YTxEmSmxTAFbpNVwr4zC", "O0J1350AiIoCBO6zIOzh"]
        rsp: Munch = api_post("/profiler/run", json=self.body.__dict__)
        self.assertEqual("Profiler ran successfully.", rsp.message, rsp.error_fields)
        print(f"Documentation coverage: {rsp.data.documentation_coverage}")
        for instruction_path in rsp.data.missing_instruction_paths:
            print(f"{instruction_path.label:10}:{instruction_path.command:6}:{instruction_path.next_label}:{instruction_path.hit_counter}"
                  f":{instruction_path.operand}")

    def test_test_data_not_provided(self):
        self.body.seg_name = "TSJ1"
        self.body.test_data_ids = list()
        rsp: Munch = api_post_using_general_domain_auth("/profiler/run", json=self.body.__dict__)
        self.assertTrue(rsp.error, rsp.message)
        self.assertEqual("At least one test data is required.", rsp.error_fields.test_data_ids, rsp.error_fields)

    def test_seg_name_not_provided(self):
        self.body.seg_name = str()
        self.body.test_data_ids = list()
        rsp: Munch = api_post_using_general_domain_auth("/profiler/run", json=self.body.__dict__)
        self.assertTrue(rsp.error, rsp.message)
        self.assertEqual("Segment is not present in the library.", rsp.error_fields.seg_name, rsp.error_fields)
