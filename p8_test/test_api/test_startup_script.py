from unittest import TestCase

from munch import Munch

from p3_db.response import StandardResponse
from p3_db.startup_script import StartupMsg
from p3_db.test_data import TestData
from p8_test.test_api import api_post, api_get


class StartupScript(TestCase):
    UNIQUE_NAME = "Some unique test data 12356"
    NEW_NAME = f"{UNIQUE_NAME}-Addition number 51262718218"

    def setUp(self) -> None:
        self.body: Munch = Munch()
        self.body.name = self.UNIQUE_NAME
        self.body.seg_name = "TS14"
        self.body.stop_segments = ""
        self.body.startup_script = ""
        self.requires_deletion = False

    def tearDown(self) -> None:
        if not self.requires_deletion:
            return
        TestData.objects.filter_by(name=self.body.name).delete()

    def test_happy_path(self) -> None:
        self.requires_deletion = True
        self.body.startup_script = " L R1,CE1CR1\n AHI R1,2"
        rsp: Munch = api_post("/test_data", json=self.body.__dict__)
        self.assertEqual(False, rsp.error, rsp.error_fields)
        self.assertEqual(StartupMsg.SUCCESS_CREATE, rsp.message)
        test_data: TestData = TestData.objects.filter_by(name=self.body.name).first()
        self.assertEqual(self.body.name, test_data.name)
        self.assertEqual(self.body.seg_name, test_data.seg_name)
        self.assertEqual(list(), test_data.stop_segments)
        self.assertEqual(self.body.startup_script, test_data.startup_script)
        rsp: Munch = api_get(f"/test_data/{rsp.id}/run")
        self.assertEqual("47:$$TS14$$.45:EXITC", rsp.outputs[0].last_node.strip())
        # Test Unique name error
        rsp: Munch = api_post("/test_data", json=self.body.__dict__)
        self.assertEqual(True, rsp.error)
        self.assertEqual(StartupMsg.NAME_UNIQUE, rsp.error_fields.name)
        # Test updating everything
        self.body.name = self.NEW_NAME
        self.body.seg_name = "TS15"
        self.body.stop_segments = "TS14, TS15"
        self.body.startup_script = " GETFC D2,ID=X'C1C2',BLOCK=YES\n"
        rsp: Munch = api_post(f"/test_data/{test_data.id}/rename", json=self.body.__dict__)
        self.assertEqual(False, rsp.error, rsp.error_fields)
        self.assertEqual(StartupMsg.SUCCESS_UPDATE, rsp.message)
        test_data: TestData = TestData.objects.filter_by(name=self.body.name).first()
        self.assertEqual(self.body.name, test_data.name)
        self.assertEqual(self.body.seg_name, test_data.seg_name)
        self.assertEqual(["TS14", "TS15"], test_data.stop_segments)
        self.assertEqual(self.body.startup_script, test_data.startup_script)
        # Test updating without changing the name
        self.body.seg_name = "TS14"
        rsp: Munch = api_post(f"/test_data/{test_data.id}/rename", json=self.body.__dict__)
        self.assertEqual(False, rsp.error, rsp.error_fields)
        self.assertEqual(StartupMsg.SUCCESS_UPDATE, rsp.message)
        # Test update request with invalid body
        rsp: Munch = api_post(f"/test_data/{test_data.id}/rename", json="abc")
        self.assertEqual(True, rsp.error, rsp.error_fields)
        self.assertEqual(StandardResponse.EMPTY_RESPONSE, rsp.message)
        # Test assembly error at update
        self.body.startup_script = " LR R1,CE1CR2"
        rsp: Munch = api_post(f"/test_data/{test_data.id}/rename", json=self.body.__dict__)
        self.assertEqual(True, rsp.error, rsp.error_fields)
        message = rsp.error_fields.startup_script[:len(StartupMsg.ASSEMBLY_ERROR_PREFIX)]
        self.assertEqual(StartupMsg.ASSEMBLY_ERROR_PREFIX, message)

    def test_invalid_request(self):
        rsp: Munch = api_post("/test_data", json={})
        self.assertEqual(True, rsp.error, rsp.error_fields)
        self.assertEqual(StandardResponse.EMPTY_RESPONSE, rsp.message)
        self.body.invalid_field = "invalid data"
        rsp: Munch = api_post("/test_data", json=self.body.__dict__)
        self.assertEqual(True, rsp.error, rsp.error_fields)
        self.assertEqual(StandardResponse.INVALID_PREFIX, rsp.message[:len(StandardResponse.INVALID_PREFIX)])

    def test_assembly_error(self):
        self.body.startup_script = " ENTRC TS14\n AHI R1,2"
        rsp: Munch = api_post("/test_data", json=self.body.__dict__)
        self.assertEqual(True, rsp.error, rsp.error_fields)
        message = rsp.error_fields.startup_script[:len(StartupMsg.ASSEMBLY_ERROR_PREFIX)]
        self.assertEqual(StartupMsg.ASSEMBLY_ERROR_PREFIX, message)

    def test_execution_error(self):
        self.body.startup_script = " AHI R1,2\n INVALID_MACRO\n "
        rsp: Munch = api_post("/test_data", json=self.body.__dict__)
        self.assertEqual(True, rsp.error, rsp.error_fields)
        message = rsp.error_fields.startup_script[:len(StartupMsg.EXECUTION_ERROR_PREFIX)]
        self.assertEqual(StartupMsg.EXECUTION_ERROR_PREFIX, message)

    def test_combination_errors(self):
        self.body.name = ""
        self.body.seg_name = "INVALID"
        self.body.stop_segments = "TS15, INVALID"
        rsp: Munch = api_post("/test_data", json=self.body.__dict__)
        self.assertEqual(True, rsp.error, rsp.error_fields)
        self.assertEqual(StartupMsg.NAME_EMPTY, rsp.error_fields.name, rsp.message)
        self.assertEqual(StartupMsg.SEG_NOT_FOUND, rsp.error_fields.seg_name)
        self.assertEqual(StartupMsg.STOP_SEG_4_CHAR, rsp.error_fields.stop_segments)
