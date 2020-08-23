from flask_app.api.api0_constants import Types, NAME, SEG_NAME, TYPE, ACTION, Actions, ErrorMsg, TEST_DATA, SuccessMsg
from p8_test.test_api import TestAPI


class InputHeader(TestAPI):

    def setUp(self):
        super().setUp()
        self.create_body: dict = {
            NAME: TestAPI.NAME,
            SEG_NAME: TestAPI.SEG_NAME,
            ACTION: Actions.CREATE
        }
        self.create_response: dict = {
            "id": str(),
            TYPE: Types.INPUT_HEADER,
            NAME: str(),
            SEG_NAME: TestAPI.SEG_NAME
        }
        self.cleanup = list()

    def tearDown(self):
        for name in self.cleanup:
            self.delete(f"/api/test_data", query_string={NAME: name})

    def _create_test_data(self, name: str):
        self.cleanup.append(name)
        self.create_body[NAME] = name
        response = self.post("/api/test_data", json=self.create_body)
        self.create_response["id"] = response.get_json()["id"]
        self.create_response[NAME] = name
        return response

    def test_create(self):
        response = self._create_test_data(TestAPI.NAME)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.create_response, response.get_json())

    def test_duplicate(self):
        error_response = {
            NAME: ErrorMsg.UNIQUE
        }
        self._create_test_data(TestAPI.NAME)
        response = self.post("/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())

    def test_long_name_and_seg_not_in_library(self):
        error_response = {
            NAME: ErrorMsg.LESS_100,
            SEG_NAME: ErrorMsg.SEG_LIBRARY
        }
        self.create_body[NAME] = self.NAME_101
        self.create_body[SEG_NAME] = "some invalid segment"
        response = self.post("/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())

    def test_invalid_type_and_lower_case_seg_name_and_space_padding_in_name(self):
        create_body = {
            NAME: f"  {TestAPI.NAME}  ",
            SEG_NAME: TestAPI.SEG_NAME.lower(),
            TYPE: Types.INPUT_CORE_BLOCK,
            ACTION: Actions.CREATE
        }
        response = self.post("/api/test_data", json=create_body)
        self.cleanup.append(TestAPI.NAME)
        self.assertEqual(200, response.status_code)
        self.create_response["id"] = response.get_json()["id"]
        self.create_response[NAME] = TestAPI.NAME
        self.assertDictEqual(self.create_response, response.get_json())

    def test_empty_body(self):
        # Complete empty body will give action not empty
        error_response = {
            ACTION: ErrorMsg.NOT_EMPTY
        }
        response = self.post("/api/test_data", json=dict())
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # If name and seg_name not specified then those will be indicated
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            SEG_NAME: ErrorMsg.NOT_EMPTY
        }
        response = self.post("/api/test_data", json={ACTION: Actions.CREATE})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Space padding
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            SEG_NAME: ErrorMsg.NOT_EMPTY
        }
        self.create_body[NAME] = "    "
        self.create_body[SEG_NAME] = "              "
        response = self.post("/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())

    def test_longest_name_and_invalid_extra_fields(self):
        self.create_body["error"] = "invalid"
        response = self._create_test_data(self.NAME_100)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.create_response, response.get_json())

    def test_delete_success(self):
        success_response = {
            TEST_DATA: SuccessMsg.DELETE
        }
        self.post("/api/test_data", json=self.create_body)
        response = self.delete(f"/api/test_data", query_string={NAME: TestAPI.NAME})
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(success_response, response.get_json())

    def test_delete_fail(self):
        # Name is not present in the db
        error_response = {
            TEST_DATA: ErrorMsg.NOT_FOUND
        }
        response = self.delete(f"/api/test_data", query_string={NAME: TestAPI.NAME})
        self.assertEqual(404, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # No params
        error_response = {
            TEST_DATA: ErrorMsg.NOT_FOUND
        }
        response = self.delete(f"/api/test_data")
        self.assertEqual(404, response.status_code)
        self.assertDictEqual(error_response, response.get_json())

    def test_get_all_and_get_by_name(self):
        # Setup
        get_all_response = list()
        response = self._create_test_data(TestAPI.NAME)
        get_by_name_response = [response.get_json()]
        get_all_response.append(response.get_json())
        response = self._create_test_data(f"{TestAPI.NAME} - 2")
        get_all_response.append(response.get_json())
        # Get All Headers
        response = self.get(f"/api/test_data")
        self.assertEqual(200, response.status_code)
        self.assertListEqual(get_all_response, response.get_json())
        # Get by name - All Types
        response = self.get(f"/api/test_data", query_string={NAME: TestAPI.NAME})
        self.assertEqual(200, response.status_code)
        self.assertListEqual(get_by_name_response, response.get_json())
        # Invalid Name - Will return an empty list
        response = self.get(f"/api/test_data", query_string={NAME: "invalid name"})
        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertListEqual(list(), response_body)
        # Empty Name - Will return an empty list
        response = self.get(f"/api/test_data", query_string={NAME: ""})
        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertListEqual(list(), response_body)
        # Invalid Parameter - Will work as get all
        response = self.get(f"/api/test_data", query_string={"invalid": "invalid"})
        self.assertEqual(200, response.status_code)
        self.assertListEqual(get_all_response, response.get_json())

    def test_invalid_action(self):
        # No action
        error_response = {
            ACTION: ErrorMsg.NOT_EMPTY
        }
        response = self.post(f"/api/test_data")
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Action with just spaces
        error_response = {
            ACTION: ErrorMsg.NOT_EMPTY
        }
        self.create_body[ACTION] = " "
        response = self.post(f"/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Invalid Action
        error_response = {
            ACTION: ErrorMsg.INVALID_ACTION
        }
        self.create_body[ACTION] = " invalid "
        response = self.post(f"/api/test_data", json=self.create_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
