from typing import Dict

from flask import jsonify, Response
from werkzeug.http import HTTP_STATUS_CODES

from flask_app import tpf1_app


def error_response(status_code: int, message: str = None) -> Response:
    error_dict: Dict[str, str] = dict()
    error_dict['error'] = HTTP_STATUS_CODES.get(status_code, 'Unknown error')
    if message:
        error_dict['message'] = message
    response: Response = jsonify(error_dict)
    response.status_code = status_code
    return response


@tpf1_app.errorhandler(404)
def not_found_error(_):
    return error_response(404)


@tpf1_app.errorhandler(500)
def system_error(_):
    return error_response(500)
