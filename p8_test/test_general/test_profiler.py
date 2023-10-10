from unittest import TestCase

from munch import Munch

from p8_test.test_api import api_post_using_general_domain_auth


class TestProfiler(TestCase):

    def setUp(self):
        self.body: Munch = Munch()

    def test_profiler_api(self):
        self.body.seg_name = "TSJ1"
        self.body.test_data_ids = ["wgCfTpeA1prwHVU684OC"]
        rsp: Munch = api_post_using_general_domain_auth("/profiler/run", json=self.body.__dict__)
        self.assertEqual("Profiler ran successfully.", rsp.message, rsp.error_fields)
        print(f"Documentation coverage: {rsp.data.documentation_coverage}")
        print(f"Total requirements: {rsp.data.total_requirements}")
        print(f"Covered requirement: {rsp.data.covered_requirements}")
        print(f"Requirement coverage: {rsp.data.requirement_coverage}")
        for instruction_path in rsp.data.missing_instruction_paths:
            print(f"{instruction_path.label:10}:{instruction_path.command:6}:{instruction_path.next_label}:{instruction_path.hit_counter}"
                  f":{instruction_path.operand}")
