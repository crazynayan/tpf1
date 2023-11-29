from d21_backend.config import config
from d21_backend.p7_flask_app.api import Types, NAME, SEG_NAME, TYPE, ACTION, Actions, ErrorMsg, NEW_NAME, VARIATION, \
    NEW_VARIATION_NAME, VARIATION_NAME, MACRO_NAME, FIELD_DATA, FIELD, DATA
from d21_backend.p8_test.test_refactor_api import TestAPI


class Rename(TestAPI):

    def setUp(self):
        super().setUp()
        self.rename_body = {
            ACTION: Actions.RENAME,
            NAME: TestAPI.NAME,
            NEW_NAME: str()
        }
        self.rename_response = {
            "id": str(),
            NAME: str(),
            SEG_NAME: TestAPI.SEG_NAME,
            TYPE: Types.INPUT_HEADER
        }
        response = self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME,
                                                      SEG_NAME: TestAPI.SEG_NAME})
        self.rename_response["id"] = response.get_json()["id"]
        self.cleanup = [TestAPI.NAME]

    def _rename_test_data(self, new_name: str):
        self.cleanup.append(new_name)
        self.rename_body[NEW_NAME] = new_name
        self.rename_response[NAME] = new_name
        response = self.post(f"/api/test_data", json=self.rename_body)
        return response

    def tearDown(self):
        for name in self.cleanup:
            self.delete(f"/api/test_data", query_string={NAME: name})

    def test_rename(self):
        response = self._rename_test_data(f"{TestAPI.NAME} - 2")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.rename_response, response.get_json())

    def test_basic_errors(self):
        # Test invalid type
        self.rename_body[TYPE] = "Invalid type"
        error_response = {
            TYPE: ErrorMsg.INVALID_TYPE
        }
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test no name and and no new_name
        self.rename_body[TYPE] = Types.INPUT_HEADER
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            NEW_NAME: ErrorMsg.NOT_EMPTY
        }
        response = self.post("/api/test_data", json={ACTION: Actions.RENAME})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test empty name and new_name
        self.rename_body[NAME] = "  "
        self.rename_body[NEW_NAME] = "       "
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test name not found and new_name not unique
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            NEW_NAME: ErrorMsg.UNIQUE
        }
        self.rename_body[NAME] = "some invalid name"
        self.rename_body[NEW_NAME] = TestAPI.NAME
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())

    def test_long_names(self):
        # Test invalid name
        error_response = {
            NEW_NAME: ErrorMsg.LESS_100
        }
        self.rename_body[NEW_NAME] = self.NAME_101
        response = self.post(f"/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test valid longest name with Input Header type
        self.rename_body[TYPE] = Types.INPUT_HEADER
        response = self._rename_test_data(self.NAME_100)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(self.rename_response, response.get_json())


class RenameVariation(TestAPI):

    def setUp(self):
        super().setUp()
        self.rename_body = {
            ACTION: Actions.RENAME,
            NAME: TestAPI.NAME,
            TYPE: Types.INPUT_CORE_BLOCK,
            VARIATION: 1,
            NEW_VARIATION_NAME: str(),
        }
        self.rename_response = [{
            "id": str(),
            NAME: TestAPI.NAME,
            TYPE: Types.INPUT_CORE_BLOCK,
            VARIATION: 1,
            VARIATION_NAME: str(),
            MACRO_NAME: "WA0AA",
            FIELD_DATA: [{FIELD: "WA0BBR", DATA: "F1F2"}]
        }]
        self.cleanup.append(self.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: self.NAME, SEG_NAME: self.SEG_NAME})
        response = self.post("/api/test_data", json={ACTION: Actions.UPDATE, TYPE: Types.INPUT_CORE_BLOCK,
                                                     NAME: self.NAME, FIELD_DATA: [{FIELD: "WA0BBR", DATA: "F1F2"}]})
        self.rename_response[0]["id"] = response.get_json()["id"]

    def _rename_variation(self, new_name: str):
        self.cleanup.append(new_name)
        self.rename_body[NEW_VARIATION_NAME] = new_name
        self.rename_response[0][VARIATION_NAME] = new_name
        response = self.post(f"/api/test_data", json=self.rename_body)
        return response

    def test_rename(self):
        response = self._rename_variation("First variation")
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertCountEqual(self.rename_response, response.get_json())

    def test_basic_errors(self):
        # Test invalid type
        self.rename_body[TYPE] = "Invalid type"
        error_response = {
            TYPE: ErrorMsg.INVALID_TYPE
        }
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test no new_variation_name and no variation
        error_response = {
            VARIATION: ErrorMsg.NOT_EMPTY,
            NEW_VARIATION_NAME: ErrorMsg.NOT_EMPTY
        }
        self.rename_body[TYPE] = Types.INPUT_CORE_BLOCK
        del self.rename_body[VARIATION]
        del self.rename_body[NEW_VARIATION_NAME]
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test empty new_variation_name and variation 0
        self.rename_body[NEW_VARIATION_NAME] = "       "
        self.rename_body[VARIATION] = 0
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test name not found and new_name not unique
        error_response = {
            VARIATION: ErrorMsg.NOT_FOUND,
            NEW_VARIATION_NAME: ErrorMsg.UNIQUE
        }
        self.rename_body[VARIATION] = -23
        self.rename_body[NEW_VARIATION_NAME] = config.DEFAULT_VARIATION_NAME
        response = self.post("/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())

    def test_long_names(self):
        # Test invalid name
        error_response = {
            NEW_VARIATION_NAME: ErrorMsg.LESS_100
        }
        self.rename_body[NEW_VARIATION_NAME] = self.NAME_101
        response = self.post(f"/api/test_data", json=self.rename_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test valid longest name
        response = self._rename_variation(self.NAME_100)
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertCountEqual(self.rename_response, response.get_json())


class Copy(TestAPI):

    def setUp(self):
        super().setUp()
        self.copy_body = {
            ACTION: Actions.COPY,
            NAME: TestAPI.NAME,
            NEW_NAME: str()
        }
        self.copy_response = [{
            "id": str(),
            NAME: str(),
            SEG_NAME: TestAPI.SEG_NAME,
            TYPE: Types.INPUT_HEADER
        }]
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})

    def _copy_test_data(self, new_name: str):
        self.cleanup.append(new_name)
        self.copy_body[NEW_NAME] = new_name
        response = self.post(f"/api/test_data", json=self.copy_body)
        self.copy_response[0][NAME] = new_name
        self.copy_response[0]["id"] = response.get_json()[0]["id"]
        return response

    def test_copy(self):
        response = self._copy_test_data(f"{TestAPI.NAME} - 2")
        self.assertEqual(200, response.status_code)
        self.assertListEqual(self.copy_response, response.get_json())

    def test_basic_errors(self):
        # Test no name and and no new_name
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            NEW_NAME: ErrorMsg.NOT_EMPTY
        }
        response = self.post("/api/test_data", json={ACTION: Actions.COPY})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test empty name and new_name
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            NEW_NAME: ErrorMsg.NOT_EMPTY
        }
        self.copy_body[NAME] = "  "
        self.copy_body[NEW_NAME] = "       "
        response = self.post("/api/test_data", json=self.copy_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test name not found and new_name not unique
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            NEW_NAME: ErrorMsg.UNIQUE
        }
        self.copy_body[NAME] = "some invalid name"
        self.copy_body[NEW_NAME] = TestAPI.NAME
        response = self.post("/api/test_data", json=self.copy_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())

    def test_long_names(self):
        # Test invalid name
        error_response = {
            NEW_NAME: ErrorMsg.LESS_100
        }
        self.copy_body[NEW_NAME] = self.NAME_101
        response = self.post(f"/api/test_data", json=self.copy_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Test valid longest name
        response = self._copy_test_data(self.NAME_100)
        self.assertEqual(200, response.status_code)
        self.assertListEqual(self.copy_response, response.get_json())
