from functools import wraps

from flask import g

from p3_db.test_data import TestData
from p3_db.test_data_get import get_whole_test_data
from p7_flask_app.errors import error_response


def test_data_required(func):
    @wraps(func)
    def test_data_wrapper(test_data_id, *args, **kwargs):
        test_data: TestData = get_whole_test_data(test_data_id, link=False)
        if not test_data:
            return error_response(404, "Test data id not found")
        kwargs[test_data_id] = test_data
        return func(test_data_id, *args, **kwargs)

    return test_data_wrapper


def test_data_with_links_required(func):
    @wraps(func)
    def test_data_wrapper(test_data_id, *args, **kwargs):
        test_data: TestData = get_whole_test_data(test_data_id, link=True)
        if not test_data:
            return error_response(404, "Test data id not found")
        kwargs[test_data_id] = test_data
        return func(test_data_id, *args, **kwargs)

    return test_data_wrapper


# role_check_required should only be used after test_data_required
def role_check_required(func):
    @wraps(func)
    def role_check_wrapper(test_data_id, *args, **kwargs):
        test_data: TestData = kwargs[test_data_id]
        if test_data.owner != g.current_user.email:
            return error_response(403, "Insufficient privileges to perform this action")
        return func(test_data_id, *args, **kwargs)

    return role_check_wrapper
