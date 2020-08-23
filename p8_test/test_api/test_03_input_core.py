from config import config
from p7_flask_app.api.api0_constants import TYPE, Types, FIELD_DATA, FIELD, DATA, MACRO_NAME, Actions, ACTION, NAME, \
    SEG_NAME, SuccessMsg, ErrorMsg, VARIATION, VARIATION_NAME, NEW_VARIATION_NAME
from p8_test.test_api import TestAPI


class InputCoreBlock(TestAPI):

    def setUp(self):
        super().setUp()
        self.update_body = {
            NAME: TestAPI.NAME,
            ACTION: Actions.UPDATE,
            TYPE: Types.INPUT_CORE_BLOCK,
            FIELD_DATA: [
                {FIELD: "WA0BBR", DATA: "F1F2"}
            ]
        }
        self.response = {
            "id": str(),
            NAME: TestAPI.NAME,
            TYPE: Types.INPUT_CORE_BLOCK,
            MACRO_NAME: "WA0AA",
            VARIATION: 1,
            VARIATION_NAME: config.DEFAULT_VARIATION_NAME,
            FIELD_DATA: [
                {FIELD: "WA0BBR", DATA: "F1F2"}
            ],
        }
        self.delete_body = {
            NAME: TestAPI.NAME,
            ACTION: Actions.DELETE,
            TYPE: Types.INPUT_CORE_BLOCK,
            VARIATION: 1,
            MACRO_NAME: "WA0AA",
            FIELD_DATA: [  # IF field data is not specified then the entire core block is deleted
                {FIELD: "WA0BBR"}
            ]
        }

    def test_create_update_delete(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        # Test Create with one field
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.response["id"] = response.get_json()["id"]
        self.assertDictEqual(self.response, response.get_json())
        # Update the same core block
        self.update_body[FIELD_DATA] = [
            {FIELD: "  wa0bbr  ", DATA: " f3f4"},
            {FIELD: "#wa0tty", DATA: "01"}
        ]
        self.response[FIELD_DATA] = [
            {FIELD: "WA0BBR", DATA: " f3f4"},
            {FIELD: "#WA0TTY", DATA: "01"}
        ]
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertDictEqual(self.response, response.get_json())
        # Delete one field
        self.delete_body[FIELD_DATA][0][FIELD] = "Wa0bbr "
        self.response[FIELD_DATA] = [{FIELD: "#WA0TTY", DATA: "01"}]
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertDictEqual(self.response, response.get_json())
        # Delete the last remaining field
        self.delete_body[FIELD_DATA][0][FIELD] = " #Wa0tty"
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertDictEqual({Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}, response.get_json())

    def test_create_multiple_and_delete_all(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        # Test create with multiple field
        self.update_body[FIELD_DATA] = self.response[FIELD_DATA] = [
            {FIELD: "WA0BBR", DATA: "F1F2"},
            {FIELD: "#WA0TTY", DATA: "01"}
        ]
        self.update_body[NAME] = f"  {TestAPI.NAME}  "
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.response["id"] = response.get_json()["id"]
        self.assertDictEqual(self.response, response.get_json())
        # Test delete all
        del self.delete_body[FIELD_DATA]
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertDictEqual({Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}, response.get_json())

    def test_multiple_variations(self):
        self.cleanup.append(TestAPI.NAME)
        response = self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME,
                                                      SEG_NAME: TestAPI.SEG_NAME})
        responses = [response.get_json()]
        # Add first variation
        self.update_body[NEW_VARIATION_NAME] = self.response[VARIATION_NAME] = "First variation"
        self.response[VARIATION] = 1
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.response["id"] = response.get_json()["id"]
        self.assertEqual(self.response, response.get_json())
        responses.append(self.response.copy())
        # Add second variation
        self.update_body[NEW_VARIATION_NAME] = self.response[VARIATION_NAME] = "Second variation"
        self.response[VARIATION] = 2
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.response["id"] = response.get_json()["id"]
        self.assertEqual(self.response, response.get_json())
        responses.append(self.response.copy())
        # Check test data
        response = self.get(f"/api/test_data", query_string={NAME: TestAPI.NAME})
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertCountEqual(responses, response.get_json())
        # Delete second variation
        self.delete_body[VARIATION] = 2
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertEqual({Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}, response.get_json())
        # Delete first variation
        self.delete_body[VARIATION] = 1
        del self.delete_body[FIELD_DATA]
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertEqual({Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}, response.get_json())
        # Check test data
        response = self.get(f"/api/test_data", query_string={NAME: TestAPI.NAME})
        self.assertListEqual([responses[0]], response.get_json())

    # noinspection DuplicatedCode
    def test_basic_errors_for_update(self):
        # No type
        response = self.post(f"/api/test_data", json={ACTION: Actions.UPDATE})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({TYPE: ErrorMsg.NOT_EMPTY}, response.get_json())
        # Invalid type
        response = self.post(f"/api/test_data", json={ACTION: Actions.UPDATE, TYPE: "Invalid Type"})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({TYPE: ErrorMsg.INVALID_TYPE}, response.get_json())
        # No Test data name
        update_body = {ACTION: Actions.UPDATE, TYPE: Types.INPUT_CORE_BLOCK}
        response = self.post(f"/api/test_data", json=update_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_EMPTY, FIELD_DATA: ErrorMsg.NOT_EMPTY}, response.get_json())
        # Empty Test data name
        update_body[NAME] = "  "
        response = self.post(f"/api/test_data", json=update_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_EMPTY, FIELD_DATA: ErrorMsg.NOT_EMPTY}, response.get_json())
        # Invalid Test data name
        update_body[NAME] = "Invalid name"
        response = self.post(f"/api/test_data", json=update_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_FOUND, FIELD_DATA: ErrorMsg.NOT_EMPTY}, response.get_json())

    def test_field_data_errors_for_update(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        self.post(f"/api/test_data", json=self.update_body)
        # Test various field_data errors
        self.update_body[FIELD_DATA] = [
            {DATA: "12"},
            {FIELD: " #wa0tty ", DATA: "12"},
            {FIELD: "#WA0TTY"},
            {FIELD: "EBW000", DATA: "12"},
            {},
            {FIELD: "invalid field", DATA: "any data"},
            {FIELD: " wa0bbr ", DATA: "F1F2"},
        ]
        error_response = {
            FIELD_DATA: [
                {FIELD: ErrorMsg.NOT_EMPTY},
                {},
                {FIELD: ErrorMsg.UNIQUE, DATA: ErrorMsg.NOT_EMPTY},
                {FIELD: f"{ErrorMsg.MACRO_SAME} WA0AA"},
                {FIELD: ErrorMsg.NOT_EMPTY, DATA: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_LIBRARY},
                {DATA: ErrorMsg.DATA_SAME}
            ]
        }
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
        # Test name errors along with field data and with no valid field
        self.update_body[NAME] = "invalid name"
        self.update_body[VARIATION] = 1
        self.update_body[NEW_VARIATION_NAME] = "any other name"
        self.update_body[FIELD_DATA] = [
            {DATA: "12"},
            {FIELD: "invalid field"},
            {FIELD: " - ", DATA: "12"},
            {FIELD: "  "},
        ]
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            VARIATION: ErrorMsg.VARIATION_NAME,
            NEW_VARIATION_NAME: ErrorMsg.VARIATION_NAME,
            FIELD_DATA: [
                {FIELD: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_NOT_FOUND, DATA: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_NOT_FOUND},
                {FIELD: ErrorMsg.NOT_EMPTY, DATA: ErrorMsg.NOT_EMPTY}
            ]
        }
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())

    def test_variation_errors_for_update(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        self.update_body[NEW_VARIATION_NAME] = "First variation"
        self.post(f"/api/test_data", json=self.update_body)
        # Test duplicate new variation name
        self.update_body[NEW_VARIATION_NAME] = "First variation"
        error_response = {NEW_VARIATION_NAME: ErrorMsg.UNIQUE}
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
        # Test new variation name too long
        self.update_body[NEW_VARIATION_NAME] = self.NAME_101
        error_response = {NEW_VARIATION_NAME: ErrorMsg.LESS_100}
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
        # Test variation not found
        del self.update_body[NEW_VARIATION_NAME]
        self.update_body[VARIATION] = 100
        error_response = {VARIATION: ErrorMsg.NOT_FOUND}
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
        # Test variation not empty and data not same
        del self.update_body[VARIATION]
        error_response = {
            VARIATION: ErrorMsg.NOT_EMPTY,
            FIELD_DATA: [{DATA: ErrorMsg.DATA_SAME}]
        }
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())

    # noinspection DuplicatedCode
    def test_basic_errors_for_delete(self):
        # No type
        response = self.post(f"/api/test_data", json={ACTION: Actions.UPDATE})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({TYPE: ErrorMsg.NOT_EMPTY}, response.get_json())
        # Invalid type
        response = self.post(f"/api/test_data", json={ACTION: Actions.DELETE, TYPE: "Invalid Type"})
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({TYPE: ErrorMsg.INVALID_TYPE}, response.get_json())
        # No test data name
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            MACRO_NAME: ErrorMsg.NOT_EMPTY,
            VARIATION: ErrorMsg.NOT_EMPTY
        }
        delete_body = {ACTION: Actions.DELETE, TYPE: Types.INPUT_CORE_BLOCK}
        response = self.post(f"/api/test_data", json=delete_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Empty Test data name
        delete_body[NAME] = "  "
        delete_body[MACRO_NAME] = "      "
        response = self.post(f"/api/test_data", json=delete_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())
        # Invalid Test data name and variation is 0
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            MACRO_NAME: ErrorMsg.NOT_EMPTY,
            VARIATION: ErrorMsg.NOT_EMPTY
        }
        delete_body[NAME] = "Invalid name"
        delete_body[VARIATION] = 0
        response = self.post(f"/api/test_data", json=delete_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(error_response, response.get_json())

    def test_errors_for_delete(self):
        self.cleanup.append(TestAPI.NAME)
        self.post(f"/api/test_data", json={ACTION: Actions.CREATE, NAME: TestAPI.NAME, SEG_NAME: TestAPI.SEG_NAME})
        self.post(f"/api/test_data", json=self.update_body)
        # Test various field_data errors
        self.delete_body[FIELD_DATA] = [
            {DATA: "12"},
            {FIELD: " Wa0bbr  ", DATA: "12"},
            {FIELD: " #wa0tty "},
            {FIELD: "EBW000"},
            {},
            {FIELD: "invalid field", DATA: "any data"},
            {FIELD: "WA0BBR"},
        ]
        error_response = {
            FIELD_DATA: [
                {FIELD: ErrorMsg.NOT_EMPTY},
                {},
                {FIELD: ErrorMsg.NOT_FOUND},
                {FIELD: f"{ErrorMsg.MACRO_SAME} WA0AA"},
                {FIELD: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_LIBRARY},
                {FIELD: ErrorMsg.UNIQUE}
            ]
        }
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
        # Test no macro name and no name
        del self.delete_body[NAME]
        del self.delete_body[MACRO_NAME]
        self.delete_body[FIELD_DATA] = [
            {FIELD: "WA0BBR"},
            {FIELD: " wa0bbr "},
            {FIELD: "EBW000"},
            {FIELD: "     "}
        ]
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            MACRO_NAME: ErrorMsg.NOT_EMPTY,
            VARIATION: ErrorMsg.NOT_FOUND,
            FIELD_DATA: [
                {FIELD: ErrorMsg.MACRO_NOT_FOUND},
                {FIELD: ErrorMsg.UNIQUE},
                {FIELD: ErrorMsg.MACRO_NOT_FOUND},
                {FIELD: ErrorMsg.NOT_EMPTY},
            ]
        }
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
        # Test invalid macro name and  invalid name
        self.delete_body[NAME] = "Invalid name"
        self.delete_body[MACRO_NAME] = "Invalid name"
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            MACRO_NAME: ErrorMsg.MACRO_LIBRARY,
            VARIATION: ErrorMsg.NOT_FOUND,
            FIELD_DATA: [
                {FIELD: f"{ErrorMsg.MACRO_SAME} INVALID NAME"},
                {FIELD: ErrorMsg.UNIQUE},
                {FIELD: f"{ErrorMsg.MACRO_SAME} INVALID NAME"},
                {FIELD: ErrorMsg.NOT_EMPTY},
            ]
        }
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
        # Test different macro name
        self.delete_body[NAME] = f"  {TestAPI.NAME}  "
        self.delete_body[MACRO_NAME] = "EB0EB"
        self.delete_body[VARIATION] = 2
        error_response = {
            MACRO_NAME: ErrorMsg.NOT_FOUND,
            VARIATION: ErrorMsg.NOT_FOUND,
            FIELD_DATA: [
                {FIELD: f"{ErrorMsg.MACRO_SAME} EB0EB"},
                {FIELD: ErrorMsg.UNIQUE},
                {FIELD: ErrorMsg.NOT_FOUND},
                {FIELD: ErrorMsg.NOT_EMPTY}
            ]
        }
        response = self.post(f"/api/test_data", json=self.delete_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
