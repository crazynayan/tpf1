from flask_app.api.api0_constants import TYPE, Types, FIELD_DATA, FIELD, DATA, MACRO_NAME, Actions, ACTION, NAME, \
    SEG_NAME, SuccessMsg, ErrorMsg, VARIATION, LENGTH
from test.test_api import TestAPI


class OutputCoreBlock(TestAPI):

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.update_body = {
            NAME: TestAPI.NAME,
            ACTION: Actions.UPDATE,
            TYPE: Types.OUTPUT_CORE_BLOCK,
            FIELD_DATA: [
                {FIELD: "WA0BBR"}
            ]
        }
        self.response = {
            "id": str(),
            NAME: TestAPI.NAME,
            TYPE: Types.OUTPUT_CORE_BLOCK,
            MACRO_NAME: "WA0AA",
            FIELD_DATA: [
                {FIELD: "WA0BBR", LENGTH: 2}
            ],
        }
        self.delete_body = {
            NAME: TestAPI.NAME,
            ACTION: Actions.DELETE,
            TYPE: Types.OUTPUT_CORE_BLOCK,
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
            {FIELD: "  wa0bbr  ", LENGTH: 3},
            {FIELD: "#wa0tty", DATA: "F1F2"}  # Data is ignored in output core block
        ]
        self.response[FIELD_DATA] = [
            {FIELD: "WA0BBR", LENGTH: 3},
            {FIELD: "#WA0TTY", LENGTH: 1}
        ]
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertDictEqual(self.response, response.get_json())
        # Delete one field
        self.delete_body[FIELD_DATA][0][FIELD] = "Wa0bbr "
        self.response[FIELD_DATA] = [{FIELD: "#WA0TTY", LENGTH: 1}]
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
            {FIELD: "WA0BBR", LENGTH: 1},
            {FIELD: "#WA0TTY", LENGTH: 1}
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
        # No Test data name and no field data
        update_body = {ACTION: Actions.UPDATE, TYPE: Types.INPUT_CORE_BLOCK}
        response = self.post(f"/api/test_data", json=update_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_EMPTY, FIELD_DATA: ErrorMsg.NOT_EMPTY}, response.get_json())
        # Empty Test data name
        update_body[NAME] = "  "
        update_body[FIELD_DATA] = list()
        response = self.post(f"/api/test_data", json=update_body)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual({NAME: ErrorMsg.NOT_EMPTY, FIELD_DATA: ErrorMsg.NOT_EMPTY}, response.get_json())
        # Invalid Test data name
        update_body[NAME] = "Invalid name"
        update_body[FIELD_DATA] = {FIELD: "field_data is a list of dict and not a dict"}
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
            {FIELD: " #wa0tty "},
            {FIELD: "#WA0TTY", LENGTH: 0},
            {FIELD: "EBW000", DATA: "12"},
            {},
            {FIELD: "invalid field", LENGTH: -1},
            {FIELD: " wa0bbr ", LENGTH: 2},
        ]
        error_response = {
            FIELD_DATA: [
                {FIELD: ErrorMsg.NOT_EMPTY},
                {},
                {FIELD: ErrorMsg.UNIQUE, LENGTH: ErrorMsg.GREATER_0},
                {FIELD: f"{ErrorMsg.MACRO_SAME} WA0AA"},
                {FIELD: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_LIBRARY, LENGTH: ErrorMsg.GREATER_0},
                {LENGTH: ErrorMsg.DATA_SAME}
            ]
        }
        response = self.post(f"/api/test_data", json=self.update_body)
        self.assertEqual(400, response.status_code, response.get_json())
        self.assertDictEqual(error_response, response.get_json())
        # Test name errors along with field data and with no valid field
        self.update_body[NAME] = "invalid name"
        self.update_body[FIELD_DATA] = [
            {DATA: "12"},
            {FIELD: "invalid field", LENGTH: "1"},
            {FIELD: " - "},
            {FIELD: "  ", LENGTH: [1]},
        ]
        error_response = {
            NAME: ErrorMsg.NOT_FOUND,
            FIELD_DATA: [
                {FIELD: ErrorMsg.NOT_EMPTY},
                {FIELD: ErrorMsg.MACRO_NOT_FOUND, LENGTH: ErrorMsg.GREATER_0},
                {FIELD: ErrorMsg.MACRO_NOT_FOUND},
                {FIELD: ErrorMsg.NOT_EMPTY, LENGTH: ErrorMsg.GREATER_0}
            ]
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
        }
        delete_body = {ACTION: Actions.DELETE, TYPE: Types.OUTPUT_CORE_BLOCK}
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
        }
        delete_body[NAME] = "Invalid name"
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
            {FIELD: " Wa0bbr  ", LENGTH: 1},
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
            {FIELD: "EBW000", LENGTH: 2},
            {FIELD: "     "}
        ]
        error_response = {
            NAME: ErrorMsg.NOT_EMPTY,
            MACRO_NAME: ErrorMsg.NOT_EMPTY,
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
        self.delete_body[VARIATION] = 2  # Variation is ignored in output core block
        error_response = {
            MACRO_NAME: ErrorMsg.NOT_FOUND,
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
